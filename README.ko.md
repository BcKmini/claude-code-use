<div align="center">

<img src="assets/claude.png" alt="Claude Code Multi-Agent" width="420">

# Claude Code 멀티 에이전트 시스템

**Claude Code를 위한 9개의 전문 에이전트 + 3개의 생산성 도구**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange?style=flat-square&logo=rust)](https://www.rust-lang.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/BcKmini/claude-code-multi-agent)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet?style=flat-square&logo=anthropic)](https://claude.ai/code)
[![Agents](https://img.shields.io/badge/Agents-9-green?style=flat-square)](#에이전트-구성)
[![Tools](https://img.shields.io/badge/Tools-3-informational?style=flat-square)](#도구)

**[English README](README.md)** · **[환경 세팅](SETUP.ko.md)** · **[치트시트](AGENT-CHEATSHEET.ko.md)** · **[연동 가이드](INTEGRATION.ko.md)** · **[기여 가이드](CONTRIBUTING.ko.md)**

</div>

---

## 이게 뭔가요?

**Claude Code**를 즉시 강화하는 네 가지:

1. **9개의 전문 서브 에이전트** — 설계, 구현, 리뷰, 테스트, 보안 등 각자 하나에만 집중
2. **`snippet`** — 자주 쓰는 프롬프트를 저장하고 커맨드 한 번에 꺼내 쓰는 프롬프트 매니저
3. **`claude-handoff`** — 세션 전체 컨텍스트(git 상태, 할 일, 메모)를 저장하고 다음 세션에서 복원
4. **`claude-cost`** — 프롬프트 실행 전 비용 추정 및 실제 사용량 추적

세 가지 도구 모두 Python CLI, Claude Code 슬래시 커맨드(`/snippet`, `/handoff`, `/cost`), 그리고 단일 **Rust 바이너리**(`claude-tools`)로 제공됩니다.

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

## 도구

Claude Code가 기본으로 제공하지 않는 기능을 채우는 세 가지 도구.

### 통합 설치 (한 번에)

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File tools\install-tools.ps1
```

```bash
# macOS / Linux
bash tools/install-tools.sh
```

설치 스크립트가 자동으로:
- `/snippet`, `/handoff`, `/cost` 슬래시 커맨드를 `~/.claude/commands/`에 설치
- `snippets/defaults.json`의 기본 스니펫 20개 임포트
- 쉘 프로파일에 `snippet`, `claude-handoff`, `claude-cost` 함수 등록

> Python 없이 사용하려면 → [Rust 바이너리](#rust-바이너리--claude-tools) 참고

---

### 도구 1 — `snippet` — 개인 프롬프트 매니저

Claude 프롬프트를 이름으로 저장하고, 터미널이나 Claude Code 안에서 한 커맨드로 꺼내 씁니다.

**터미널**

```bash
snippet list                          # 전체 목록
snippet list --tag pipeline           # 태그로 필터
snippet save myfix "Fix {{BUG}} in {{FILE}}" --tags bug
snippet run myfix --var BUG="null ref" --var FILE="auth.ts"
snippet run full-pipeline | claude    # 바로 Claude에 파이프

snippet search security
snippet show code-review
snippet cp code-review my-review
snippet delete my-review --force
snippet stats
snippet export my-backup.json
snippet import snippets/defaults.json
```

**Claude Code 안에서**

```
/snippet list
/snippet run full-pipeline
/snippet search security
```

**템플릿 변수** — `{{변수명}}`을 넣으면 실행 시점에 채웁니다:

```bash
snippet run new-feature \
  --var FEATURE="사용자 알림" \
  --var LANG="TypeScript" \
  --var REQUIREMENTS="실시간 푸시, 이메일 다이제스트"
```

**기본 제공 스니펫 (20개)**

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

### 도구 2 — `claude-handoff` — 세션 연속성

세션 전체 컨텍스트(git 상태, 열린 작업, 요약 메모)를 마크다운 파일로 저장합니다. 다음 세션에서 로드하면 "어디서 멈췄더라?"가 사라집니다.

**터미널**

```bash
claude-handoff save                    # 메모 입력 후 컨텍스트 저장
claude-handoff save --note "auth 완료, 다음: 테스트 작성"
claude-handoff load | claude           # 최근 핸드오프를 Claude에 로드
claude-handoff list                    # 저장된 핸드오프 목록
claude-handoff show --id 20250101-120000
claude-handoff clean --days 30 --force # 오래된 핸드오프 삭제
```

**Claude Code 안에서**

```
/handoff save
/handoff load
/handoff list
```

**핸드오프에 담기는 정보:**

- 현재 git 브랜치, 최근 커밋 5개, 워킹 트리 상태, diff stat
- 리모트 URL, 레포 루트 경로
- `TODO.md` / `TASKS.md` 내용 (있을 경우)
- 직접 입력한 요약 메모
- 다음 세션에 바로 쓸 수 있는 **재개 프롬프트**

**재개 워크플로우:**

```bash
# 세션 종료
claude-handoff save --note "OAuth 완료; 다음: 이메일 인증"

# 다음 세션 시작
claude-handoff load | claude
```

---

### 도구 3 — `claude-cost` — 비용 추정 & 추적

실행 전에 프롬프트 비용을 확인하세요. 세션 로그에서 실제 사용량을 추적하고 월 예산도 설정할 수 있습니다.

**터미널**

```bash
# 스니펫 기준 9개 에이전트 전체 비용 추정
claude-cost estimate --snippet full-pipeline --agents 9

# 임의 프롬프트 텍스트 추정
claude-cost estimate "auth 모듈 전체 리팩터링"

# 최근 7일 사용 내역
claude-cost history

# 월별 요약
claude-cost month

# 에이전트별 비용 분석
claude-cost agents

# 월 예산 설정 (추정치에 % 표시)
claude-cost set-budget 20.00
```

**Claude Code 안에서**

```
/cost estimate full-pipeline
/cost history
/cost month
/cost agents
```

**모델 가격표**

| 모델 | 입력 (100만 토큰) | 출력 (100만 토큰) |
|------|-----------------|-----------------|
| Opus | $15.00 | $75.00 |
| Sonnet | $3.00 | $15.00 |
| Haiku | $0.25 | $1.25 |

---

### Rust 바이너리 — `claude-tools`

세 가지 도구를 의존성 없는 단일 바이너리로 컴파일합니다 — Python 불필요.

```bash
cd rust
cargo build --release

# 사용
./target/release/claude-tools snippet list
./target/release/claude-tools handoff save --note "완료"
./target/release/claude-tools cost estimate --snippet full-pipeline
```

**전역 설치:**

```bash
cargo install --path rust/claude-tools

claude-tools snippet list
claude-tools handoff load | claude
claude-tools cost month
```

> `claude-tools`와 claw-code 연동 방법은 [INTEGRATION.md](INTEGRATION.md) 참고.

---

## 저장소 구조

```
Claudecode-Agent/
├── agents/                       ← 에이전트 정의 (→ ~/.claude/agents/ 에 복사됨)
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
│       ├── snippet.md            ← /snippet 슬래시 커맨드
│       ├── handoff.md            ← /handoff 슬래시 커맨드
│       └── cost.md               ← /cost 슬래시 커맨드
├── snippets/
│   └── defaults.json             ← 기본 프롬프트 템플릿 20개
├── tools/
│   ├── snippet.py                ← 프롬프트 매니저 CLI
│   ├── claude-handoff.py         ← 세션 연속성 CLI
│   ├── claude-cost.py            ← 비용 추정 CLI
│   ├── install-tools.ps1         ← Windows 통합 설치 스크립트
│   └── install-tools.sh          ← macOS / Linux 통합 설치 스크립트
├── rust/
│   ├── Cargo.toml                ← workspace 루트
│   └── claude-tools/             ← Rust 바이너리 (snippet + handoff + cost)
│       ├── Cargo.toml
│       └── src/
│           ├── main.rs
│           ├── snippet.rs
│           ├── handoff.rs
│           ├── cost.rs
│           └── colors.rs
├── AGENT-CHEATSHEET.md           ← 바로 쓸 수 있는 프롬프트 모음
├── CLAUDE.md                     ← 개인 코딩 원칙 가이드라인
├── INTEGRATION.md                ← claw-code + Rust 연동 가이드
├── SETUP.md                      ← 전체 환경 세팅 (MCP, Docker, 플러그인 등)
├── setup-agents.ps1              ← Windows 에이전트 설치 스크립트
└── setup-agents.sh               ← macOS / Linux 에이전트 설치 스크립트
```

---

## 전체 문서 목록

| 문서 | 한국어 | English |
|------|--------|---------|
| 환경 세팅 가이드 | [SETUP.ko.md](SETUP.ko.md) | [SETUP.md](SETUP.md) |
| 에이전트 치트시트 | [AGENT-CHEATSHEET.ko.md](AGENT-CHEATSHEET.ko.md) | [AGENT-CHEATSHEET.md](AGENT-CHEATSHEET.md) |
| 통합 가이드 (claw-code + Rust) | [INTEGRATION.ko.md](INTEGRATION.ko.md) | [INTEGRATION.md](INTEGRATION.md) |
| 기여 가이드 | [CONTRIBUTING.ko.md](CONTRIBUTING.ko.md) | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 코딩 가이드라인 | [CLAUDE.ko.md](CLAUDE.ko.md) | [CLAUDE.md](CLAUDE.md) |
| README | [README.ko.md](README.ko.md) | [README.md](README.md) |

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

