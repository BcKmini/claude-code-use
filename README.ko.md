<div align="center">

<img src="assets/claude.png" alt="Claude Code Multi-Agent" width="420">

# Claude Code 멀티 에이전트 시스템

**Claude Code를 위한 11개의 전문 에이전트 + 7개의 생산성 도구**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange?style=flat-square&logo=rust)](https://www.rust-lang.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/BcKmini/Claudecode-Agent)
[![Claude Code](https://img.shields.io/badge/Claude_Code-Compatible-blueviolet?style=flat-square&logo=anthropic)](https://claude.ai/code)
[![Agents](https://img.shields.io/badge/Agents-11-green?style=flat-square)](#에이전트-구성)
[![Tools](https://img.shields.io/badge/Tools-7-informational?style=flat-square)](#도구)
[![Bilingual](https://img.shields.io/badge/Lang-EN%20%7C%20KO-orange?style=flat-square)](#)

**[English README](README.md)** · **[환경 세팅](docs/SETUP.ko.md)** · **[치트시트](docs/AGENT-CHEATSHEET.ko.md)** · **[하네스 가이드](docs/HARNESS-GUIDE.ko.md)** · **[연동 가이드](docs/INTEGRATION.ko.md)** · **[기여 가이드](docs/CONTRIBUTING.ko.md)**

</div>

---

## 이게 뭔가요?

**Claude Code**를 즉시 강화하는 도구 모음:

1. **11개의 전문 서브 에이전트** — 설계, 구현, 리뷰, 테스트, 보안, 하네스 설계, 파이프라인 관리 등 각자 하나에만 집중
2. **`snippet`** — 자주 쓰는 프롬프트를 저장하고 커맨드 한 번에 꺼내 쓰는 프롬프트 매니저
3. **`claude-handoff`** — 세션 전체 컨텍스트(git 상태, 할 일, 메모)를 저장하고 다음 세션에서 복원
4. **`claude-cost`** — 프롬프트 실행 전 비용 추정 및 실제 사용량 추적
5. **`claude-review-diff`** — git diff에서 구조화된 코드 리뷰 프롬프트 자동 생성
6. **`claude-remind`** — 세션 시작 시 TODO 미완료 항목을 자동으로 표시
7. **`claude-harness`** — 에이전트 하네스 정의를 검증하고 템플릿을 생성
8. **`claude-pipeline`** — 다단계 파이프라인 실행을 추적하고 보고서 생성

모든 도구는 Python CLI와 Claude Code 슬래시 커맨드로 제공됩니다. 핵심 도구는 단일 **Rust 바이너리**(`claude-tools`)로도 제공됩니다.

> **이중 언어 지원:** 모든 에이전트가 사용자의 언어를 감지해 영어(English)와 한국어로 응답합니다.

```
나                       Orchestrator
 │                           │
 └──► "OAuth 로그인 추가" ──► ├──► planner         (아키텍처 설계)
                             ├──► database-expert  (스키마 설계)
                             ├──► implementer      (코드 작성)
                             ├──► reviewer         (코드 리뷰)
                             └──► tester           (테스트 작성)
```

---

## 빠른 시작

### 1. Claude Code 설치

```bash
npm install -g @anthropic-ai/claude-code
claude   # 처음 실행 시 Anthropic 계정 인증
```

### 2. 클론 및 설치

```powershell
# Windows
git clone https://github.com/BcKmini/Claudecode-Agent.git
cd Claudecode-Agent
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# macOS / Linux
git clone https://github.com/BcKmini/Claudecode-Agent.git
cd Claudecode-Agent
bash setup-agents.sh
```

### 3. 도구 설치 (한 번에)

```bash
make install            # 에이전트 + 슬래시 커맨드 + Python 도구
make install-rust       # 선택: Rust 바이너리 (cargo 필요)
```

### 4. 확인

```
claude
/agents          # → 9개 에이전트 목록
/snippet list    # → 기본 스니펫 목록
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
| 09 | **harness-designer** | Opus | 타이트·느슨·적응형 AI 하네스 설계 |
| 10 | **pipeline-orchestrator** | Opus | 컨텍스트 격리 기반 다단계 파이프라인 실행 관리 |

> **모든 에이전트가 이중 언어를 지원합니다** — 사용자 언어를 감지해 한국어 또는 영어로 응답합니다.

> 각 에이전트는 자기 역할에 관련된 컨텍스트만 가집니다. 병렬 실행(planner + security-auditor 동시)으로 작업 시간도 단축됩니다.

> 바로 쓸 수 있는 프롬프트 24개 이상 → [AGENT-CHEATSHEET.ko.md](docs/AGENT-CHEATSHEET.ko.md)

---

## 도구

Claude Code가 기본으로 제공하지 않는 기능을 채우는 7가지 도구.

### 슬래시 커맨드 한눈에 보기

| 커맨드 | 기능 |
|--------|------|
| `/snippet` | 프롬프트 템플릿 실행·저장·목록 |
| `/handoff` | 세션 컨텍스트 저장/로드 |
| `/cost` | API 비용 추정 및 추적 |
| `/harness` | AI 하네스 정의 설계 및 검증 |
| `/pipeline` | 다단계 AI 파이프라인 실행 및 추적 |
| `/review-diff` | git diff 기반 코드 리뷰 프롬프트 |
| `/remind` | 세션 시작 시 TODO 미완료 항목 표시 |

---

### 도구 1 — `snippet` — 개인 프롬프트 매니저

Claude 프롬프트를 이름으로 저장하고, 한 커맨드로 꺼내 씁니다.

```bash
snippet list                                   # 전체 목록
snippet run full-pipeline | claude             # Claude에 바로 파이프
snippet save myfix "Fix {{BUG}} in {{FILE}}"   # 템플릿 변수 사용
snippet search security
snippet export my-backup.json
```

```
/snippet list
/snippet run full-pipeline
/snippet search security
```

**기본 스니펫 20개** — `full-pipeline`, `code-review`, `security-audit`, `write-tests`, `refactor`, `db-schema` 등. [snippets/defaults.json](snippets/defaults.json) 참고.

---

### 도구 2 — `claude-handoff` — 세션 연속성

세션 전체 컨텍스트를 저장하고 다음 세션에 바로 복원합니다.

```bash
claude-handoff save --note "OAuth 완료, 다음: 이메일 인증"
claude-handoff load | claude    # 바로 재개
claude-handoff list
claude-handoff clean --days 30
```

```
/handoff save
/handoff load
/handoff list
```

**핸드오프에 담기는 정보:** git 브랜치, 최근 커밋 5개, 워킹 트리 상태, diff stat, TODO.md 내용, 요약 메모, 재개 프롬프트.

---

### 도구 3 — `claude-cost` — 비용 추정 & 추적

실행 전에 프롬프트 비용을 확인하고 실제 사용량을 추적합니다.

```bash
claude-cost estimate --snippet full-pipeline --agents 9
claude-cost month
claude-cost set-budget 20.00
```

```
/cost estimate full-pipeline
/cost month
/cost agents
```

| 모델 | 입력 (100만 토큰) | 출력 (100만 토큰) |
|------|-----------------|-----------------|
| Opus | $15.00 | $75.00 |
| Sonnet | $3.00 | $15.00 |
| Haiku | $0.25 | $1.25 |

---

### 도구 4 — `claude-review-diff` — git diff 코드 리뷰

현재 git 변경사항을 구조화된 코드 리뷰 프롬프트로 변환해 Claude에 바로 파이프합니다.

```bash
claude-review-diff                       # 스테이징 전 변경사항 리뷰
claude-review-diff --staged              # 스테이징된 변경사항 리뷰
claude-review-diff --base main           # 브랜치를 main과 비교
claude-review-diff --focus security      # 보안 중점 리뷰
claude-review-diff | claude              # Claude에 바로 파이프
```

```
/review-diff
/review-diff --staged
/review-diff --base main --focus security
```

**Focus 옵션:** `security` · `performance` · `correctness` · `style` · `tests` · `all`

출력은 심각도 순 정렬: **Critical → Major → Minor → Nit**

---

### 도구 5 — `claude-remind` — 세션 시작 리마인더

TODO.md / TASKS.md / CLAUDE.md에서 미완료 체크박스(`- [ ]`)를 스캔해 세션 재개 프롬프트를 출력합니다.

```bash
claude-remind                # 미완료 항목 전체 + 재개 프롬프트
claude-remind --quiet        # 개수만 표시
claude-remind | claude       # Claude에 바로 파이프
```

```
/remind
/remind --quiet
```

**세션 종료/시작 워크플로우:**

```bash
# 세션 종료
claude-handoff save --note "Auth 완료, 다음: 이메일 인증"

# 세션 시작
claude-remind | claude         # 미완료 항목 확인
claude-handoff load | claude   # 전체 컨텍스트 복원
```

---

### Rust 바이너리 — `claude-tools`

모든 도구를 의존성 없는 단일 바이너리로 컴파일 — Python 불필요.

```bash
cd rust && cargo build --release
# 또는: make install-rust

claude-tools snippet list
claude-tools handoff save --note "완료"
claude-tools cost month
claude-tools watch              # 실시간 비용 모니터
claude-tools watch --interval 5
claude-tools env                # 환경 헬스체크
```

**`claude-tools env` 출력:**

```
Claude Code Environment

  ✓ ANTHROPIC_API_KEY   sk-ant-…abcd
  ✓ ~/.claude/           exists
  ✓ ~/.claude/agents/    9 agents installed
  ✓ ~/.claude/commands/  5 commands: snippet, handoff, cost, review-diff, remind
  ✓ handoffs             3 saved, latest: 20250608-143022.md
  ✓ sessions             4 projects, 12 session files
```

---

## Makefile

```bash
make help           # 전체 타겟 목록
make install        # 에이전트 + 슬래시 커맨드 + Python 도구
make install-rust   # Rust 바이너리 빌드 및 설치
make build          # cargo build --release
make test           # 전체 테스트
make lint           # clippy + ruff
make fmt            # rustfmt + ruff format
make status         # git log + 도구 설치 상태 확인
make env            # Claude 환경 헬스체크
make clean          # 빌드 아티팩트 제거
```

---

## 저장소 구조

```
Claudecode-Agent/
├── Makefile                          ← 빌드 / 설치 / 테스트 / 정리
├── setup-agents.ps1                  ← Windows 빠른 설치
├── setup-agents.sh                   ← macOS / Linux 빠른 설치
│
├── agents/                           ← 에이전트 정의 → ~/.claude/agents/
│   ├── 00-orchestrator.md  ·  01-planner.md  ·  02-implementer.md
│   ├── 03-reviewer.md  ·  04-tester.md  ·  05-security-auditor.md
│   ├── 06-performance-optimizer.md  ·  07-database-expert.md
│   └── 08-documenter.md
│
├── .claude/commands/                 ← 슬래시 커맨드 → ~/.claude/commands/
│   ├── snippet.md  ·  handoff.md  ·  cost.md
│   ├── review-diff.md                ← 신규
│   └── remind.md                     ← 신규
│
├── snippets/defaults.json            ← 기본 프롬프트 템플릿 20개
│
├── tools/
│   ├── snippet.py  ·  claude-handoff.py  ·  claude-cost.py
│   ├── claude-review-diff.py         ← 신규
│   ├── claude-remind.py              ← 신규
│   ├── install-tools.ps1  ·  install-tools.sh
│
├── rust/claude-tools/src/
│   ├── main.rs  ·  snippet.rs  ·  handoff.rs  ·  cost.rs
│   ├── watch.rs  ·  env.rs (신규)  ·  colors.rs
│
└── docs/
    ├── SETUP.md / SETUP.ko.md
    ├── AGENT-CHEATSHEET.md / .ko.md
    ├── INTEGRATION.md / .ko.md
    ├── CONTRIBUTING.md / .ko.md
    └── CLAUDE.md / .ko.md
```

---

## 컨텍스트 비용 관리

| 상황 | 명령 |
|------|------|
| 작업 단계 완료 후 | `/compact` |
| 완전히 다른 작업 시작 | `/clear` |
| 비용 확인 | `/cost` |
| 실시간 비용 모니터 | `claude-tools watch` |
| 환경 상태 확인 | `claude-tools env` |
| 미완료 작업으로 재개 | `claude-remind \| claude` |
| 전체 세션 복원 | `claude-handoff load \| claude` |

---

## 트러블슈팅

**에이전트가 `/agents`에 안 보임**
```bash
ls ~/.claude/agents/*.md   # 파일 존재 확인 후 Claude Code 재시작
```

**Agent Teams가 작동 안 함**
```powershell
# Windows — "1" 이 출력되어야 함
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS","User")
```
```bash
# macOS / Linux
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS   # "1" 이 출력되어야 함
```

**`make install-tools` 후 툴이 없다고 나올 때**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

**Windows에서 `make`가 없을 때**
```powershell
winget install GnuWin32.Make
```

---

## 전체 문서 목록

| 문서 | 한국어 | English |
|------|--------|---------|
| 환경 세팅 가이드 | [SETUP.ko.md](docs/SETUP.ko.md) | [SETUP.md](docs/SETUP.md) |
| 에이전트 치트시트 | [AGENT-CHEATSHEET.ko.md](docs/AGENT-CHEATSHEET.ko.md) | [AGENT-CHEATSHEET.md](docs/AGENT-CHEATSHEET.md) |
| 통합 가이드 | [INTEGRATION.ko.md](docs/INTEGRATION.ko.md) | [INTEGRATION.md](docs/INTEGRATION.md) |
| 기여 가이드 | [CONTRIBUTING.ko.md](docs/CONTRIBUTING.ko.md) | [CONTRIBUTING.md](docs/CONTRIBUTING.md) |
| 코딩 가이드라인 | [CLAUDE.ko.md](docs/CLAUDE.ko.md) | [CLAUDE.md](docs/CLAUDE.md) |

---

## 기여하기

- **새 도구 아이디어** → [Feature Request](https://github.com/BcKmini/Claudecode-Agent/issues/new?template=feature_request.md)
- **버그 발견** → [Bug Report](https://github.com/BcKmini/Claudecode-Agent/issues/new?template=bug_report.md)
- **새 스니펫** → `snippets/defaults.json`에 추가 후 PR

전체 가이드 → [CONTRIBUTING.ko.md](docs/CONTRIBUTING.ko.md)

---

## 라이선스

[MIT](LICENSE)
