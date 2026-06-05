# Claude Code Multi-Agent System
<div align="center">
<img src="https://img.shields.io/badge/Claude_Code-Compatible-blue?style=flat-square&logo=anthropic" />
<img src="https://img.shields.io/badge/Agents-9-green?style=flat-square" />
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey?style=flat-square" />
<img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" />
</div>

<div align="center">
  <img src="assets/claude.png" alt="Claude" width="500">
</div>


---

## 문서 목록

| 문서 | 내용 |
|------|------|
| [README](./README.md) | 프로젝트 소개 및 빠른 시작 (현재 페이지) |
| [SETUP.md](./SETUP.md) | 전체 환경 세팅 (MCP, Docker, 플러그인, 환경변수) |
| [AGENT-CHEATSHEET.md](./AGENT-CHEATSHEET.md) | 상황별 프롬프트 모음 및 빠른 참조 |
| [INTEGRATION.md](./INTEGRATION.md) | claw-code 연동 가이드 |
| [CLAUDE.md](./CLAUDE.md) | 개인 개발 원칙 및 코딩 가이드라인 |

---

## 왜 멀티 에이전트인가

단일 Claude 인스턴스는 만능이지만, 역할이 섞이면 집중력이 분산된다.

```
[일반 방식]
"로그인 기능 만들어줘" -> Claude 혼자 설계 + 구현 + 리뷰 + 테스트

[멀티 에이전트 방식]
orchestrator -> planner(설계) -> implementer(구현) -> reviewer(리뷰) -> tester(테스트)
```

**장점**
- 각 에이전트가 자기 역할에만 집중 — 컨텍스트 오염 없음
- 병렬 실행으로 시간 단축 (planner + security-auditor 동시 실행 가능)
- 모델별 비용 최적화 (단순 작업엔 Haiku, 중요 판단엔 Opus)
- reviewer가 implementer 결과를 독립적으로 검증

---

## 에이전트 구성

| # | 에이전트 | 모델 | 역할 |
|---|---------|------|------|
| 00 | orchestrator | Opus | 총괄 지휘, 작업 분해 및 위임 |
| 01 | planner | Opus | 설계·아키텍처 수립 (읽기 전용) |
| 02 | implementer | Sonnet | 실제 코드 작성·수정 |
| 03 | reviewer | Sonnet | 버그·보안·품질·성능 리뷰 (읽기 전용) |
| 04 | tester | Sonnet | 유닛·통합·E2E 테스트 작성 |
| 05 | security-auditor | Opus | OWASP Top 10 기준 보안 감사 |
| 06 | performance-optimizer | Sonnet | 성능 병목 분석 및 최적화 |
| 07 | database-expert | Sonnet | DB 스키마·쿼리·마이그레이션 |
| 08 | documenter | Haiku | README·API 문서·주석 작성 |

---

## 빠른 시작

### Windows

```powershell
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

### Mac / Linux

```bash
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
bash setup-agents.sh
```

스크립트가 자동으로:
- `~/.claude/agents/`에 에이전트 파일 복사
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경변수 영구 설정 (zsh/bash 자동 감지)
- `.claudeignore` 생성

### 설치 확인

Claude Code 실행 후:
```
/agents
```
9개 에이전트가 목록에 표시되면 완료.

> 전체 환경 세팅 (MCP 서버, Docker, 플러그인 등)은 [SETUP.md](./SETUP.md)를 참고.

---

## 사용 예시

### 새 기능 전체 파이프라인
```
Use the orchestrator to implement OAuth 2.0 login with Google.
Requirements:
- JWT 토큰 발급
- 기존 이메일 로그인과 연동
Run the full pipeline: planner -> implementer -> reviewer -> tester
```

### 코드 리뷰
```
Have the reviewer subagent review src/api/auth.ts
Focus on security vulnerabilities and error handling.
```

### 병렬 실행
```
Run these in parallel:
1. Have planner design the notification module
2. Have database-expert design the schema
3. Have security-auditor review requirements
Then have implementer execute the combined plan.
```

> 더 많은 프롬프트 예시는 [AGENT-CHEATSHEET.md](./AGENT-CHEATSHEET.md)를 참고.

---

## 파일 구조

```
claude-code-multi-agent/
├── agents/
│   ├── 00-orchestrator.md
│   ├── 01-planner.md
│   ├── 02-implementer.md
│   ├── 03-reviewer.md
│   ├── 04-tester.md
│   ├── 05-security-auditor.md
│   ├── 06-performance-optimizer.md
│   ├── 07-database-expert.md
│   └── 08-documenter.md
├── AGENT-CHEATSHEET.md   <- 상황별 프롬프트 모음
├── CLAUDE.md             <- 개발 원칙 가이드라인
├── INTEGRATION.md        <- claw-code 연동 가이드
├── SETUP.md              <- 전체 환경 세팅
├── setup-agents.ps1      <- Windows 설치 스크립트
├── setup-agents.sh       <- Mac/Linux 설치 스크립트
└── README.md
```

### 에이전트 설치 경로

| 위치 | 적용 범위 |
|------|-----------|
| `~/.claude/agents/` | 글로벌 — 모든 프로젝트에서 사용 |
| `.claude/agents/` (프로젝트 루트) | 로컬 — 해당 프로젝트에서만 사용 |

---

## 고급 사용법

### CLAUDE.md로 에이전트 동작 제어

프로젝트 루트에 `CLAUDE.md` 배치 시 Claude가 자동으로 읽는다.

```markdown
## 에이전트 시스템
복잡한 요청 -> orchestrator에게 먼저 위임하세요.

## 절대 수정 금지
- src/generated/
- .env.production
```

> 개발 원칙 전체는 [CLAUDE.md](./CLAUDE.md) 참고.

### 컨텍스트 비용 관리

| 상황 | 명령 |
|------|------|
| 단계 완료 후 | `/compact` |
| 완전히 다른 작업 시작 | `/clear` |
| 특정 파일만 참조 | `@src/auth/login.ts 리뷰해줘` |
| 비용 확인 | `/cost` |

---

## 트러블슈팅

**에이전트가 `/agents`에 안 보임**
- `~/.claude/agents/`에 `.md` 파일이 있는지 확인
- 파일 인코딩이 UTF-8인지 확인
- Claude Code 재시작

**Agent Teams가 작동 안 함**
```bash
# Mac/Linux
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
# "1" 이 출력되어야 함
```
```powershell
# Windows
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "User")
```

**컨텍스트가 너무 커질 때**
```
/compact "다음 단계는 테스트 작성"
```

---

## License

MIT
