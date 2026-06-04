# 🤖 Claude Code Multi-Agent System

> Claude Code를 위한 9개 전문 에이전트 시스템 — 복잡한 작업을 역할별 AI에게 분산시켜 품질과 효율을 동시에 높인다.

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Compatible-blue?style=flat-square&logo=anthropic" alt="Claude Code Compatible">
  <img src="https://img.shields.io/badge/Agents-9-green?style=flat-square" alt="9 Agents">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Mac%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
</p>

---

## 📖 목차

- [왜 멀티 에이전트인가](#-왜-멀티-에이전트인가)
- [에이전트 구성](#-에이전트-구성)
- [빠른 시작](#-빠른-시작)
- [사용 예시](#-사용-예시)
- [파일 구조](#-파일-구조)
- [고급 사용법](#-고급-사용법)

---

## 💡 왜 멀티 에이전트인가

단일 Claude 인스턴스는 만능이지만, 역할이 섞이면 집중력이 분산된다.

```
❌ 일반 방식
"로그인 기능 만들어줘" → Claude 혼자 설계 + 구현 + 리뷰 + 테스트

✅ 멀티 에이전트 방식
orchestrator → planner(설계) → implementer(구현) → reviewer(리뷰) → tester(테스트)
              각 단계가 전문 역할에 집중 → 더 높은 품질
```

**장점:**
- 각 에이전트가 자기 역할에만 집중 (컨텍스트 오염 없음)
- 병렬 실행으로 시간 단축 (planner + security-auditor 동시 실행 가능)
- 모델별 비용 최적화 (단순 작업엔 Haiku, 중요 판단엔 Opus)
- reviewer가 implementer의 결과를 독립적으로 검증

---

## 🧩 에이전트 구성

| # | 에이전트 | 모델 | 역할 | 권한 |
|---|---------|------|------|------|
| 00 | **orchestrator** | Opus | 총괄 지휘, 작업 분해 및 위임 | Read, Glob, Grep, Task |
| 01 | **planner** | Opus | 설계·아키텍처 수립 (읽기 전용) | Read, Grep, Glob |
| 02 | **implementer** | Sonnet | 실제 코드 작성·수정 | Read, Write, Edit, Bash |
| 03 | **reviewer** | Sonnet | 버그·보안·품질·성능 리뷰 (읽기 전용) | Read, Grep, Glob |
| 04 | **tester** | Sonnet | 유닛·통합·E2E 테스트 작성 | Read, Write, Edit, Bash |
| 05 | **security-auditor** | Opus | OWASP Top 10 기준 보안 감사 | Read, Grep, Glob, Bash |
| 06 | **performance-optimizer** | Sonnet | 성능 병목 분석 및 최적화 | Read, Grep, Glob, Edit |
| 07 | **database-expert** | Sonnet | DB 스키마·쿼리·마이그레이션 | Read, Write, Edit, Bash |
| 08 | **documenter** | Haiku | README·API 문서·주석 작성 | Read, Write, Edit |

### 모델 선택 근거

```
Opus   → orchestrator, planner, security-auditor
         복잡한 판단·설계·보안 분석이 필요한 곳

Sonnet → implementer, reviewer, tester, performance-optimizer, database-expert
         실행 위주, 코드 작성·분석 — 비용 효율 최적

Haiku  → documenter
         단순 반복 작업, 최저 비용
```

---

## 🚀 빠른 시작

### 1. 에이전트 설치

**Windows (PowerShell)**
```powershell
# 이 레포 클론
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent

# 자동 설치 스크립트 실행
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

**Mac / Linux**
```bash
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent

# 에이전트 파일 복사
mkdir -p ~/.claude/agents
cp agents/*.md ~/.claude/agents/

# Agent Teams 활성화
echo 'export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1' >> ~/.zshrc  # 또는 ~/.bashrc
source ~/.zshrc
```

### 2. 설치 확인

Claude Code 실행 후:
```
/agents
```
9개 에이전트가 목록에 표시되면 완료.

---

## 🎯 사용 예시

### 새 기능 전체 파이프라인
```
Use the orchestrator to implement OAuth 2.0 login with Google.
Requirements:
- JWT 토큰 발급
- 기존 이메일 로그인과 연동
Run the full pipeline: planner → implementer → reviewer → tester
```

### 코드 리뷰만
```
Have the reviewer subagent review src/api/auth.ts
Focus on security vulnerabilities and error handling.
```

### 보안 감사
```
Have security-auditor do a full OWASP audit of src/api/
Report all findings by severity.
```

### 성능 분석
```
Have performance-optimizer analyze src/db/queries.ts
The symptom is: user list API is taking 3+ seconds
```

### DB 스키마 설계
```
Have database-expert design the schema for a notification system.
Requirements:
- 유저별 알림 설정
- 읽음/안읽음 상태
Include migration files and index strategy.
```

### 병렬 실행 (시간 단축)
```
Run these in parallel:
1. Have planner design the notification module architecture
2. Have database-expert design the notification schema
3. Have security-auditor review notification requirements
Then have implementer execute the combined plan.
```

---

## 📁 파일 구조

```
claude-code-multi-agent/
├── agents/                          # 에이전트 정의 파일
│   ├── 00-orchestrator.md           # 총괄 지휘자
│   ├── 01-planner.md                # 설계 전문가
│   ├── 02-implementer.md            # 구현 전문가
│   ├── 03-reviewer.md               # 코드 리뷰어
│   ├── 04-tester.md                 # 테스트 엔지니어
│   ├── 05-security-auditor.md       # 보안 감사관
│   ├── 06-performance-optimizer.md  # 성능 최적화
│   ├── 07-database-expert.md        # DB 전문가
│   └── 08-documenter.md             # 문서화 전문가
├── CLAUDE.md                        # 글로벌 Claude 가이드라인
├── AGENT-CHEATSHEET.md              # 빠른 참조 치트시트
├── setup-agents.ps1                 # Windows 자동 설치 스크립트
└── README.md
```

### 설치 경로

에이전트 파일은 두 위치에 놓을 수 있다:

| 위치 | 적용 범위 |
|------|----------|
| `~/.claude/agents/` | **글로벌** — 모든 프로젝트에서 사용 |
| `.claude/agents/` (프로젝트 루트) | **로컬** — 해당 프로젝트에서만 사용 |

---

## 🔧 고급 사용법

### CLAUDE.md로 에이전트 동작 제어

프로젝트 루트에 `CLAUDE.md` 배치 → Claude가 자동으로 읽음

```markdown
## 에이전트 시스템
복잡한 요청 → orchestrator에게 먼저 위임하세요.

## 절대 수정 금지
- src/generated/ (자동 생성)
- .env.production
```

### 컨텍스트 비용 관리

| 상황 | 명령 |
|------|------|
| 단계 완료 후 | `/compact` |
| 완전히 다른 작업 시작 | `/clear` |
| 특정 파일만 참조 | `@src/auth/login.ts 리뷰해줘` |
| 비용 확인 | `/cost` |

### 에이전트 범위 제한

에이전트가 범위를 벗어날 때:
```
Have reviewer ONLY review src/auth.ts.
Do NOT suggest changes to other files.
```

---

## 🔍 트러블슈팅

**에이전트가 `/agents`에 안 보임**
- `~/.claude/agents/`에 `.md` 파일이 있는지 확인
- 파일 인코딩이 UTF-8인지 확인
- Claude Code 재시작

**Agent Teams가 작동 안 함**
```powershell
# Windows — 환경변수 확인
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "User")
# "1" 이 출력되어야 함
```

**컨텍스트가 너무 커질 때**
```
/compact "다음 단계는 테스트 작성"
```

---

## 📄 License

MIT — 자유롭게 수정하고 팀에 배포하세요.
