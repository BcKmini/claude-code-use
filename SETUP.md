[← README로 돌아가기](./README.md)

# 환경 세팅 가이드

새 PC·계정에서 이 레포를 그대로 재현할 때 순서대로 따라가면 된다.

---

## 목차

1. [선수 조건](#1-선수-조건)
2. [Claude Code CLI 설치](#2-claude-code-cli-설치)
3. [멀티 에이전트 설치](#3-멀티-에이전트-설치)
4. [환경변수](#4-환경변수)
5. [MCP 서버](#5-mcp-서버)
6. [플러그인](#6-플러그인)
7. [기본 설정 파일](#7-기본-설정-파일)
8. [claw-code 연동 (선택)](#8-claw-code-연동-선택)
9. [전체 재설치 체크리스트](#9-전체-재설치-체크리스트)

---

## 1. 선수 조건

아래 항목이 먼저 설치되어 있어야 한다.

| 항목 | 최소 버전 | 확인 명령 |
|------|----------|----------|
| Node.js | 18+ | `node -v` |
| npm | 9+ | `npm -v` |
| Git | 2.x | `git --version` |
| Docker | — | `docker --version` *(GitHub MCP 사용 시 필요)* |

**Node.js 설치 (없을 때)**

```bash
# Mac — Homebrew
brew install node

# Windows — winget
winget install OpenJS.NodeJS.LTS

# Linux (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

---

## 2. Claude Code CLI 설치

### 설치

```bash
npm install -g @anthropic-ai/claude-code
```

### 인증

```bash
claude
```

처음 실행하면 브라우저 인증 화면이 뜬다. Anthropic 계정으로 로그인하면 자동으로 API 키가 설정된다.

> 이미 API 키가 있다면 환경변수로 직접 지정할 수 있다.
> ```bash
> export ANTHROPIC_API_KEY="sk-ant-..."   # Mac/Linux
> $env:ANTHROPIC_API_KEY = "sk-ant-..."  # Windows PowerShell
> ```

### 설치 확인

```bash
claude --version
```

---

## 3. 멀티 에이전트 설치

이 레포를 클론한 뒤 플랫폼에 맞는 스크립트를 실행한다.

```bash
git clone https://github.com/BcKmini/claude-code-multi-agent.git
cd claude-code-multi-agent
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# Mac / Linux
bash setup-agents.sh
```

스크립트가 자동으로 처리하는 것:
- `~/.claude/agents/` 에 9개 에이전트 파일 복사
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경변수 영구 설정
- `.claudeignore` 생성

**에이전트 설치 위치**

| 경로 | 적용 범위 |
|------|-----------|
| `~/.claude/agents/` | 글로벌 — 모든 프로젝트 |
| `.claude/agents/` (프로젝트 루트) | 로컬 — 해당 프로젝트만 |

**설치 확인** — Claude Code 실행 후:

```
/agents
```

9개 에이전트가 목록에 표시되면 완료.

---

## 4. 환경변수

```powershell
# Windows — 사용자 환경변수 영구 설정
[System.Environment]::SetEnvironmentVariable(
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS",
    "1",
    "User"
)
```

```bash
# Mac/Linux — ~/.zshrc 또는 ~/.bashrc 에 추가
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

**확인**

```powershell
# Windows
[System.Environment]::GetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "User")
# 출력: 1
```

```bash
# Mac/Linux
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
# 출력: 1
```

---

## 5. MCP 서버

### GitHub MCP (Docker)

공식 GitHub MCP 서버. PR 생성·리뷰·이슈 관리 등 GitHub 작업을 Claude에서 직접 수행.

**Token 발급 먼저**
- GitHub → Settings → Developer settings → Personal access tokens
- 필요 권한: `repo`, `read:org`

**컨테이너 실행**

```bash
docker run -d \
  --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here \
  ghcr.io/github/github-mcp-server \
  stdio
```

**Claude Code에 연결**

Claude Code 설정 → MCP Servers → 새 서버 추가 → Docker 컨테이너 stdio 연결

```bash
# 연결 상태 확인
/mcp

# 컨테이너 실행 확인
docker ps --filter ancestor=ghcr.io/github/github-mcp-server
```

> 연결 오류 (-32000) 발생 시: 컨테이너가 실행 중인지 확인 후 `/mcp` 로 재연결

---

### Google Drive MCP

claude.ai에서 제공. Google Docs·Sheets·Drive 파일 읽기.

**연결 방법**
- Claude Code 설정 → MCP Servers → claude.ai integrations → Google Drive 추가
- 최초 연결 시 OAuth 인증 (브라우저에서 구글 계정 승인)

---

### context7

라이브러리·프레임워크 최신 문서를 실시간으로 조회. 별도 설치 불필요 — Claude Code에서 자동으로 활성화.

**자동 활성화 조건**
- React, Next.js, FastAPI, Prisma 등 라이브러리 관련 질문
- API 문법·설정·버전 마이그레이션 확인

---

## 6. 플러그인

`~/.claude/settings.json` 의 `enabledPlugins` 에 등록.

| 플러그인 | 슬래시 명령 | 역할 |
|---------|------------|------|
| hookify | `/hookify` | 원하지 않는 Claude 동작 방지 훅 설정 |
| serena | — | 코드 심볼 분석·탐색 (LSP 기반) |
| session-report | `/session-report` | 세션 토큰 사용량 HTML 리포트 |
| claude-md-management | `/claude-md-improver` | CLAUDE.md 파일 감사·개선 |

**주요 명령**

```bash
# hookify — 동작 방지 훅
/hookify          # 현재 대화에서 방지할 동작 자동 탐지
/hookify list     # 설정된 훅 목록
/hookify configure

# session-report — 세션 분석
/session-report   # session-report-YYYYMMDD-HHMM.html 생성
```

---

## 7. 기본 설정 파일

`~/.claude/settings.json`

```json
{
  "effortLevel": "medium",
  "autoUpdatesChannel": "latest",
  "theme": "dark"
}
```

| 항목 | 값 | 설명 |
|------|-----|------|
| effortLevel | medium | 응답 품질/속도 균형 (low / medium / high) |
| theme | dark | UI 테마 |
| autoUpdatesChannel | latest | 자동 업데이트 채널 |

---

## 8. claw-code 연동 (선택)

claw-code는 Claude Code CLI와 함께 쓸 수 있는 오픈소스 Rust CLI 하네스다.
RAG(Qdrant 벡터 DB), clawhip 이벤트 라우팅, 다중 AI 프로바이더를 지원한다.

> 상세 연동 가이드 → [INTEGRATION.md](./INTEGRATION.md)

### 사전 요건

- Rust toolchain: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Docker (RAG 서비스 사용 시)

### 빌드

```powershell
# Windows PowerShell
git clone https://github.com/ultraworkers/claw-code
cd claw-code\rust
cargo build --workspace

$env:ANTHROPIC_API_KEY = "sk-ant-..."
.\target\debug\claw.exe doctor
```

```bash
# Mac / Linux
git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace

export ANTHROPIC_API_KEY="sk-ant-..."
./target/debug/claw doctor
```

### 프로젝트에 적용

```bash
# 프로젝트 루트에서
claw init

# 이 레포의 CLAUDE.md를 복사해 에이전트 가이드라인 적용
cp /path/to/claude-code-multi-agent/CLAUDE.md ./CLAUDE.md
```

---

## 9. 전체 재설치 체크리스트

새 환경 세팅 시 위에서 아래로 순서대로.

```
[ ] 1.  Node.js 18+ / npm 설치 확인
[ ] 2.  Claude Code CLI 설치  →  npm install -g @anthropic-ai/claude-code
[ ] 3.  claude 실행 → Anthropic 계정 인증
[ ] 4.  Docker 설치 → GitHub MCP 서버 컨테이너 실행
[ ] 5.  Claude Code에서 GitHub MCP 연결
[ ] 6.  claude.ai에서 Google Drive MCP 연결
[ ] 7.  이 레포 클론 후 setup-agents 스크립트 실행
[ ] 8.  CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 환경변수 설정
[ ] 9.  ~/.claude/settings.json 에 플러그인·설정 적용
[ ] 10. /agents 명령으로 9개 에이전트 확인
[ ] 11. /mcp 명령으로 MCP 연결 상태 확인
[ ] 12. (선택) claw-code 빌드 → claw doctor 헬스체크
```
