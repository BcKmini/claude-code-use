# claw-code 통합 가이드

`claude-code-multi-agent`와 `claw-code`는 서로 다른 층을 담당하며 함께 쓸 때 더 강력하다.

| 시스템 | 역할 | 링크 |
|--------|------|------|
| claude-code-multi-agent | 에이전트 정의 (9개 에이전트 역할·동작 규칙) | 이 레포 |
| claw-code | CLI 하네스 런타임 (Rust 기반 오픈소스 CLI) | [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) |

---

## claw-code 개요

claw-code는 Claude Code CLI와 함께 쓸 수 있는 오픈소스 Rust CLI 하네스다.

**핵심 특징:**
- 다중 AI 프로바이더 지원 (Anthropic, OpenAI 호환)
- REPL 스타일 세션 관리
- RAG 서비스 (Qdrant + 벡터 DB)
- 컨테이너 지원 (Docker/Podman)
- 머신리더블 JSON 스테이트 출력
- clawhip 이벤트 라우팅

---

## 빠른 시작

### claw-code 빌드 (Windows PowerShell)

```powershell
git clone https://github.com/ultraworkers/claw-code
cd claw-code\rust
cargo build --workspace

# 키 설정
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# 헬스체크
.\target\debug\claw.exe doctor
```

### claw-code 빌드 (Mac/Linux)

```bash
git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace

export ANTHROPIC_API_KEY="sk-ant-..."
./target/debug/claw doctor
```

### 프로젝트 초기화

```bash
# 프로젝트 루트에서
claw init
```

`.claw`, `.claw.json`, `CLAUDE.md` 생성. **이 레포의 `CLAUDE.md`를 복사해 덮어쓰면 에이전트 가이드라인이 claw-code에도 적용된다.**

---

## 두 시스템의 역할 분리

```
claude-code-multi-agent          claw-code
       |↓                               |↓
  9개 에이전트 정의          CLI 하네스 런타임
  (roles, tools, prompts)     (session, RAG, events)
       |↓                               |↓
  Claude Code CLI              claw CLI
  (claude 명령)              (claw 명령)
       \___________________________/
                 |↓
          동일한 agents/*.md 각복 가능
```

**에이전트 정의 (`agents/*.md`)는 양쪽 런타임에서 모두 동작한다.**
Claude Code의 `/agents`를 쓰든, claw-code의 REPL을 쓰든 동일한 에이전트 역할 정의가 적용된다.

---

## 통합 포인트

### 1. CLAUDE.md 공유

`claw init` 실행 후 생성된 `CLAUDE.md`를 이 레포의 `CLAUDE.md`로 덮어쓰면 된다.

```bash
# 프로젝트 루트에서
claw init
cp /path/to/claude-code-multi-agent/CLAUDE.md ./CLAUDE.md
```

이후 claw-code 세션에서도 에이전트 시스템 가이드라인이 적용된다.

### 2. 에이전트 정의 공유

claw-code는 `~/.claude/agents/`가 아닌 자체 에이전트 시스템을 쓴. 하지만 **orchestrator 패턴**은 claw-code에서도 적용 가능하다:

```
# claw REPL 안에서
Use the orchestrator to implement [feature].
Run the full pipeline: planner -> implementer -> reviewer -> tester
```

role prompt 자체는 claw-code REPL에 직접 활용.

### 3. RAG 서비스 (Qdrant)

claw-code는 Qdrant 벡터 DB를 이용한 RAG를 지원한다.
context7 MCP를 대체하거나 보완하는 방식으로 활용 가능.

```bash
# RAG 서비스 실행 (docker-compose)
cd claw-code
docker compose up qdrant rag-serve -d

# GitHub MCP 컨테이너도 함께 실행
docker run -d \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token \
  ghcr.io/github/github-mcp-server stdio
```

**Docker 실행 순서 (권장):**

```bash
# 1. Qdrant (RAG 벡터 DB)
docker compose up qdrant -d

# 2. RAG 서비스 (Qdrant 의존)
docker compose up rag-serve -d

# 3. GitHub MCP 서버
docker run -d --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token \
  ghcr.io/github/github-mcp-server stdio
```

### 4. 코드베이스 인덱싱 (RAG 입력)

```bash
# 워크스페이스를 Qdrant에 인덱싱
docker compose run rag-ingest
```

이후 claw 세션에서 코드베이스 관련 질문시 RAG가 관련 코드를 자동으로 참조.

### 5. 이벤트 라우팅 비교

| 기능 | Claude Code | claw-code |
|------|-------------|----------|
| 동작 방지 훅 | hookify 플러그인 | clawhip 이벤트 |
| 알림 | 없음 | clawhip 쳄널 (Discord 등) |
| 세션 모니터링 | session-report 플러그인 | claw status / JSON 출력 |
| 멀티 에이전트 | orchestrator 에이전트 | oh-my-openagent (OmO) |

---

## 권장 워크플로우

### 코드 작업 (Claude Code + 멀티 에이전트)

```
claude 실행
  -> orchestrator에게 작업 위임
  -> planner -> implementer -> reviewer -> tester 파이프라인
  -> GitHub MCP로 PR 생성
```

### 코드베이스 탐색 (claw-code + RAG)

```
docker compose up qdrant rag-serve -d
claw 실행
  -> /doctor
  -> RAG가 인덱싱된 코드베이스 관련 쿼리 지원
```

### 자동화 파이프라인 (claw-code + clawhip)

```
clawhip이 GitHub PR/Issue 이벤트 감지
  -> claw 세션 자동 시작
  -> orchestrator 패턴으로 작업 실행
  -> 결과를 Discord 등 채널로 전송
```

---

---

## claude-tools Rust 바이너리

이 레포에는 Python 도구 세 가지를 하나의 Rust 바이너리로 컴파일한 `claude-tools`가 포함되어 있다.

```
rust/
├── Cargo.toml                ← workspace
└── claude-tools/
    ├── Cargo.toml            ← clap 4, serde, chrono, dirs, anyhow, regex
    └── src/
        ├── main.rs           ← clap derive CLI (snippet / handoff / cost)
        ├── snippet.rs        ← ~/.claude/snippets.json 관리
        ├── handoff.rs        ← ~/.claude/handoffs/ 세션 문서
        ├── cost.rs           ← ~/.claude/projects/ JSONL 파싱 + 비용 추정
        └── colors.rs         ← ANSI 컬러 헬퍼
```

### 빌드

```bash
cd rust
cargo build --release
# 바이너리: rust/target/release/claude-tools
```

### claw-code와 함께 사용

`claude-tools`는 claw-code와 같은 Rust 생태계를 사용한다. 두 바이너리를 PATH에 함께 등록하면 Python 없이도 전체 워크플로우가 가능하다:

```bash
# ~/.bashrc 또는 ~/.zshrc
export PATH="$PATH:/path/to/claude-tools/target/release"
export PATH="$PATH:/path/to/claw-code/target/release"
```

#### 세션 워크플로우 (Python 없이)

```bash
# 1. claw로 코딩 세션 시작
claw

# 2. 세션 종료 전 핸드오프 저장
claude-tools handoff save --note "auth 완료, 다음: 테스트 작성"

# 3. 비용 확인
claude-tools cost month

# 4. 다음 세션에서 컨텍스트 복원
claude-tools handoff load | claude
# 또는
claude-tools handoff load | claw
```

### 의존성 비교

| | Python 도구 | claude-tools (Rust) |
|--|------------|---------------------|
| 런타임 | Python 3.8+ 필요 | 단일 바이너리, 의존성 없음 |
| 속도 | 보통 | 빠름 |
| 배포 | 파일 복사 | 바이너리 1개 복사 |
| claw-code 연동 | 별도 설치 필요 | 동일 Cargo workspace 가능 |

---

## 릴레이티드 링크

- [claw-code (ultraworkers)](https://github.com/ultraworkers/claw-code)
- [clawhip 이벤트 라우터](https://github.com/Yeachan-Heo/clawhip)
- [oh-my-openagent 멀티에이전트 조율](https://github.com/code-yeongyu/oh-my-openagent)
- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)
- [UltraWorkers Discord](https://discord.gg/5TUQKqFWd)
