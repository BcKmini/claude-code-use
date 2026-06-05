[← README로 돌아가기](../README.md)

**한국어** · **[English](INTEGRATION.md)**

# 통합 가이드 — claw-code & claude-tools

`Claudecode-Agent`와 `claw-code`는 서로 다른 층을 담당하며 함께 쓸 때 더 강력하다.

| 시스템 | 역할 | 링크 |
|--------|------|------|
| Claudecode-Agent | 에이전트 정의 + CLI 도구 (Python + Rust) | 이 레포 |
| claw-code | CLI 하네스 런타임 (Rust 기반 오픈소스) | [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) |

---

## claw-code 개요

**핵심 특징:**
- 다중 AI 프로바이더 지원 (Anthropic, OpenAI 호환)
- REPL 스타일 세션 관리
- RAG 서비스 (Qdrant + 벡터 DB)
- 컨테이너 지원 (Docker/Podman)
- 머신리더블 JSON 스테이트 출력
- clawhip 이벤트 라우팅

---

## 빠른 시작

```powershell
# Windows
git clone https://github.com/ultraworkers/claw-code
cd claw-code\rust
cargo build --workspace
$env:ANTHROPIC_API_KEY = "sk-ant-..."
.\target\debug\claw.exe doctor
```

```bash
# Mac/Linux
git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace
export ANTHROPIC_API_KEY="sk-ant-..."
./target/debug/claw doctor
```

```bash
claw init
cp /path/to/Claudecode-Agent/docs/CLAUDE.md ./CLAUDE.md
```

---

## 아키텍처

```
Claudecode-Agent                 claw-code
       |                               |
  9개 에이전트 정의          CLI 하네스 런타임
  (roles, tools, prompts)     (session, RAG, events)
       |                               |
  Claude Code CLI              claw CLI
  (claude 명령)              (claw 명령)
       \____________________________/
                   |
         동일한 agents/*.md 정의 공유 가능
```

**에이전트 정의 (`agents/*.md`)는 양쪽 런타임에서 모두 동작한다.**

---

## 통합 포인트

### 1. CLAUDE.md 공유

```bash
claw init
cp /path/to/Claudecode-Agent/docs/CLAUDE.md ./CLAUDE.md
```

### 2. orchestrator 패턴 (claw REPL 안에서)

```
Use the orchestrator to implement [feature].
Run the full pipeline: planner -> implementer -> reviewer -> tester
```

### 3. RAG 서비스 (Qdrant)

```bash
cd claw-code
docker compose up qdrant -d
docker compose up rag-serve -d
docker run -d --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token \
  ghcr.io/github/github-mcp-server stdio
docker compose run rag-ingest   # 코드베이스 인덱싱
```

### 4. 이벤트 라우팅 비교

| 기능 | Claude Code | claw-code |
|------|-------------|-----------|
| 동작 방지 훅 | hookify 플러그인 | clawhip 이벤트 |
| 알림 | 없음 | clawhip 채널 (Discord 등) |
| 세션 모니터링 | session-report 플러그인 | claw status / JSON 출력 |
| 멀티 에이전트 | orchestrator 에이전트 | oh-my-openagent (OmO) |

---

## claude-tools Rust 바이너리

Python 도구 세 가지 + watch 실시간 모니터를 하나의 바이너리로.

```
rust/
├── Cargo.toml
└── claude-tools/
    └── src/
        ├── main.rs       ← clap derive CLI 진입점
        ├── snippet.rs    ← ~/.claude/snippets.json 관리
        ├── handoff.rs    ← ~/.claude/handoffs/ 세션 문서
        ├── cost.rs       ← ~/.claude/projects/ JSONL 파싱 + 비용 추정
        ├── watch.rs      ← 실시간 비용 모니터 (신규)
        └── colors.rs     ← ANSI 컬러 헬퍼
```

### 빌드 및 설치

```bash
cd rust
cargo build --release
# 바이너리: rust/target/release/claude-tools

# 전역 설치
cargo install --path rust/claude-tools
```

### 전체 워크플로우 (Python 없이)

```bash
export PATH="$PATH:/path/to/claude-tools/target/release"
export PATH="$PATH:/path/to/claw-code/target/release"

# 세션 시작
claw

# 세션 중 실시간 비용 모니터링
claude-tools watch

# 세션 종료 전 핸드오프 저장
claude-tools handoff save --note "auth 완료, 다음: 테스트 작성"

# 다음 세션에서 컨텍스트 복원
claude-tools handoff load | claude
```

### claude-tools watch — 실시간 비용 모니터

```bash
claude-tools watch              # 최신 세션 모니터링 (2초 간격)
claude-tools watch --interval 5 # 5초 간격
```

토큰이 흐르는 동안 라이브 업데이트 테이블 표시:

```
Claude Code — 실시간 비용 모니터  (Ctrl+C 종료)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 TIME     MODEL    INPUT    OUTPUT   COST
 12:01:05 sonnet   1,240    3,100    $0.0501
 12:01:18 sonnet     892    2,230    $0.0361
 12:01:44 opus       456    1,596    $0.1263
─────────────────────────────────────────────
 TOTAL              2,588    6,926   $0.2125
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
- [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)
- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)
- [UltraWorkers Discord](https://discord.gg/5TUQKqFWd)
