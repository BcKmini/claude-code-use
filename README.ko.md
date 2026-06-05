<div align="center">

<img src="assets/claude.png" alt="Claude Code Multi-Agent" width="420">

# Claude Code 멀티 에이전트 시스템

**Claude Code를 위한 9개의 전문 에이전트 + 개인 프롬프트 매니저**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/BcKmini/claude-code-multi-agent)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet?style=flat-square&logo=anthropic)](https://claude.ai/code)
[![Agents](https://img.shields.io/badge/Agents-9-green?style=flat-square)](#에이전트-구성)

**[English README](README.md)** · **[환경 세팅](SETUP.md)** · **[치트시트](AGENT-CHEATSHEET.md)** · **[claw-code 연동](INTEGRATION.md)**

</div>

---

## 이게 뭔가요?

**Claude Code**를 즉시 강화하는 두 가지 도구:

1. **9개의 전문 서브 에이전트** — 설계, 구현, 리뷰, 테스트, 보안 등 각자 하나에만 집중
2. **`snippet`** — 자주 쓰는 프롬프트를 저장하고 커맨드 한 번에 꺼내 쓰는 프롬프트 매니저

Claude 하나가 모든 일을 하는 대신, 각 작업을 가장 적합한 에이전트에게 라우팅합니다.

```
나                       Orchestrator
 │                           │
 └──► "OAuth 로그인 추가" ──► ├──► planner       (아키텍처 설계)
                             ├──► database-expert (스키마 설계)
                             ├──► implementer   (코드 작성)
                             ├──► reviewer      (코드 리뷰)
                             └──► tester        (테스트 작성)
```

---

## 에이전트 구성

| # | 에이전트 | 모델 | 역할 |
|---|---------|------|------|
| 00 | **orchestrator** | Opus | 작업 분해 및 서브 에이전트 위임 총괄 |
| 01 | **planner** | Opus | 아키텍처·설계 결정 — 읽기 전용 |
| 02 | **implementer** | Sonnet | 실제 코드 작성·수정 |
| 03 | **reviewer** | Sonnet | 버그·보안·품질·성능 리뷰 — 읽기 전용 |
| 04 | **tester** | Sonnet | 유닛·통합·E2E 테스트 작성 |
| 05 | **security-auditor** | Opus | OWASP Top 10 기준 보안 감사 — 읽기 전용 |
| 06 | **performance-optimizer** | Sonnet | 성능 병목 분석 및 최적화 |
| 07 | **database-expert** | Sonnet | DB 스키마 설계·쿼리·마이그레이션 |
| 08 | **documenter** | Haiku | README·API 문서·인라인 주석 작성 |

> **왜 에이전트를 분리하나요?**  
> 각 에이전트는 자기 역할에 관련된 컨텍스트만 가집니다. "설계 모드"와 "구현 모드"가 섞이지 않아요. 병렬 실행(planner + security-auditor 동시)으로 작업 시간도 단축됩니다.

---

## 빠른 시작

### 1. Claude Code 설치

```bash
npm install -g @anthropic-ai/claude-code
claude   # 처음 실행 시 Anthropic 계정 인증
```

### 2. 에이전트 설치

```powershell
# Windows
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# macOS / Linux
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
bash setup-agents.sh
```

### 3. 확인

```
claude
/agents          # → 9개 에이전트 목록 표시
```

---

## 에이전트 사용 예시

### 기능 전체 파이프라인

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

### 병렬 실행 (시간 단축)

```
Run these in parallel:
1. Have planner design the notification module
2. Have database-expert design the schema
3. Have security-auditor review the requirements
Then have implementer execute the combined plan.
```

> 20개 이상의 바로 쓸 수 있는 프롬프트는 [AGENT-CHEATSHEET.md](AGENT-CHEATSHEET.md) 참고.

---

## snippet — 개인 프롬프트 매니저

`snippet`은 Claude 프롬프트를 이름으로 저장하고, 터미널이나 Claude Code 세션 안에서 한 커맨드로 꺼내 씁니다.

### snippet 설치

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File tools\install-snippet.ps1
```

```bash
# macOS / Linux
bash tools/install-snippet.sh
```

설치 스크립트가 자동으로:
- `~/.claude/commands/snippet.md` 설치 → Claude Code `/snippet` 슬래시 커맨드 활성화
- `snippets/defaults.json`의 기본 스니펫 20개 임포트
- 쉘 프로파일에 `snippet` 단축 함수 등록

### 터미널에서 사용

```bash
snippet list                        # 전체 목록
snippet list --tag pipeline         # 태그로 필터
snippet list --sort-by uses         # 많이 쓴 순 정렬

snippet save myfix "Fix {{BUG}} in {{FILE}}" --tags bug
snippet run myfix --var BUG="null ref" --var FILE="auth.ts"
snippet run full-pipeline | claude  # 바로 Claude에 파이프

snippet search security
snippet show code-review
snippet edit code-review            # $EDITOR로 편집
snippet cp code-review my-review    # 복사
snippet delete my-review            # 삭제 (확인 절차 있음)
snippet stats                       # 사용 통계

snippet import snippets/defaults.json          # 파일에서 가져오기
snippet export my-backup.json                  # 전체 내보내기
snippet export my-backup.json --tag pipeline   # 태그별 내보내기
```

### Claude Code 안에서 사용

```
/snippet list
/snippet run full-pipeline
/snippet search security
/snippet show db-schema
```

### 템플릿 변수

프롬프트에 `{{변수명}}`을 넣으면 실행 시점에 값을 채울 수 있습니다:

```bash
# 저장된 프롬프트:
# "Use orchestrator to implement {{FEATURE}} in {{LANG}}. Requirements: {{REQUIREMENTS}}"

snippet run new-feature \
  --var FEATURE="사용자 알림" \
  --var LANG="TypeScript" \
  --var REQUIREMENTS="실시간 푸시, 이메일 다이제스트"
```

> 실행 전 미리 보기: `--dry-run` 플래그 추가

### 기본 제공 스니펫 (20개)

| 이름 | 태그 | 용도 |
|------|------|------|
| `full-pipeline` | pipeline | 템플릿 변수 포함 전체 파이프라인 |
| `new-feature` | pipeline, feature | 처음부터 기능 설계·구현 |
| `fix-bug` | bug | 버그 수정 + 회귀 테스트 |
| `hotfix` | bug, urgent | 긴급 프로덕션 핫픽스 |
| `code-review` | review | 파일 단위 코드 리뷰 |
| `pr-review` | review, pr | 머지 전 diff 리뷰 |
| `security-audit` | security | OWASP Top 10 감사 |
| `parallel-design` | parallel | 설계·스키마·보안 병렬 실행 |
| `db-schema` | database | 스키마 + 인덱스 전략 + 마이그레이션 |
| `db-migrate` | database, migration | 롤백 계획 포함 마이그레이션 |
| `performance` | performance | 성능 병목 분석 |
| `write-tests` | test | 종합 테스트 스위트 작성 |
| `write-docs` | docs | README + JSDoc 업데이트 |
| `refactor` | refactor | 테스트 통과 보장하는 안전한 리팩터링 |
| `explain` | explain | 낯선 코드 설명 요청 |
| `api-review` | review, api | REST API 설계 리뷰 |
| `nextjs-feature` | nextjs, frontend | Next.js 15 App Router 기능 구현 |
| `fastapi-endpoint` | fastapi, backend | FastAPI 엔드포인트 + 테스트 |
| `context-reset` | meta | 컨텍스트 요약 + 다음 단계 정리 |
| `cost-check` | meta | 세션 비용 확인 |

---

## 저장소 구조

```
claude-code-multi-agent/
├── agents/                   ← 에이전트 정의 (→ ~/.claude/agents/ 에 복사됨)
│   ├── 00-orchestrator.md
│   ├── 01-planner.md
│   ├── 02-implementer.md
│   ├── 03-reviewer.md
│   ├── 04-tester.md
│   ├── 05-security-auditor.md
│   ├── 06-performance-optimizer.md
│   ├── 07-database-expert.md
│   └── 08-documenter.md
├── .claude/
│   └── commands/
│       └── snippet.md        ← /snippet 슬래시 커맨드 정의
├── snippets/
│   └── defaults.json         ← 기본 프롬프트 템플릿 20개
├── tools/
│   ├── snippet.py            ← 프롬프트 매니저 CLI (Python 3.8+, 표준 라이브러리만 사용)
│   ├── install-snippet.ps1   ← Windows 설치 스크립트
│   └── install-snippet.sh    ← macOS / Linux 설치 스크립트
├── AGENT-CHEATSHEET.md       ← 바로 쓸 수 있는 프롬프트 모음
├── CLAUDE.md                 ← 개인 코딩 원칙 가이드라인
├── INTEGRATION.md            ← claw-code 연동 가이드
├── SETUP.md                  ← 전체 환경 세팅 (MCP, Docker, 플러그인 등)
├── setup-agents.ps1          ← Windows 에이전트 설치 스크립트
└── setup-agents.sh           ← macOS / Linux 에이전트 설치 스크립트
```

---

## 전체 문서 목록

| 문서 | 내용 |
|------|------|
| [SETUP.md](SETUP.md) | 전체 환경 세팅: MCP 서버·Docker·플러그인·환경변수 |
| [AGENT-CHEATSHEET.md](AGENT-CHEATSHEET.md) | 20개 이상 바로 복붙 가능한 프롬프트 |
| [INTEGRATION.md](INTEGRATION.md) | claw-code (Rust CLI 하네스) 연동 |
| [CLAUDE.md](CLAUDE.md) | 코딩 원칙 및 응답 스타일 가이드라인 |

---

## 컨텍스트 비용 관리

| 상황 | 명령 |
|------|------|
| 단계 완료 후 | `/compact` |
| 완전히 다른 작업 시작 | `/clear` |
| 특정 파일 참조 | `@src/auth.ts 이 파일 리뷰해줘` |
| 비용 확인 | `/cost` |

---

## 트러블슈팅

**에이전트가 `/agents`에 안 보임**
```bash
ls ~/.claude/agents/*.md   # 파일이 있는지 확인
# Claude Code 재시작
```

**Agent Teams가 작동 안 함**
```powershell
# Windows
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS","User")
# "1" 이 출력되어야 함
```
```bash
# macOS / Linux
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS   # "1" 이 출력되어야 함
```

**MCP 연결 오류 (-32000)**
```bash
docker ps   # GitHub MCP 컨테이너 실행 중인지 확인
# Claude Code 안에서:
/mcp        # 재연결
```

---

## 기여하기

기여는 언제나 환영합니다! 먼저 [CONTRIBUTING.md](CONTRIBUTING.md)를 읽어주세요.

- **새 에이전트 아이디어** → [Feature Request](https://github.com/BcKmini/claude-code-multi-agent/issues/new?template=feature_request.md) 열기
- **버그 발견** → [Bug Report](https://github.com/BcKmini/claude-code-multi-agent/issues/new?template=bug_report.md) 열기
- **새 스니펫 아이디어** → `snippets/defaults.json`에 추가 후 PR 보내기

---

## 라이선스

[MIT](LICENSE)

---

<div align="center">

Claude Code를 최대한 활용하고 싶은 개발자를 위해 만들었습니다.  
유용하셨다면 ⭐ 스타 하나가 다른 분들이 찾는 데 도움이 됩니다.

</div>
