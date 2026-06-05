[← README로 돌아가기](../README.md)

**한국어** · **[English](SETUP.md)**

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
8. [도구 설치 (snippet / handoff / cost)](#8-도구-설치)
9. [claw-code 연동 (선택)](#9-claw-code-연동-선택)
10. [전체 재설치 체크리스트](#10-전체-재설치-체크리스트)

---

## 1. 선수 조건

| 항목 | 최소 버전 | 확인 명령 |
|------|----------|----------|
| Node.js | 18+ | `node -v` |
| npm | 9+ | `npm -v` |
| Git | 2.x | `git --version` |
| Docker | — | `docker --version` *(GitHub MCP 사용 시 필요)* |

```bash
# Mac
brew install node
# Windows
winget install OpenJS.NodeJS.LTS
# Linux
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs
```

---

## 2. Claude Code CLI 설치

```bash
npm install -g @anthropic-ai/claude-code
claude   # 처음 실행 시 브라우저 인증
claude --version
```

> API 키가 있다면:
> ```bash
> export ANTHROPIC_API_KEY="sk-ant-..."   # Mac/Linux
> $env:ANTHROPIC_API_KEY = "sk-ant-..."  # Windows PowerShell
> ```

---

## 3. 멀티 에이전트 설치

```bash
git clone https://github.com/BcKmini/Claudecode-Agent.git
cd Claudecode-Agent
```

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# Mac / Linux
bash setup-agents.sh
```

`~/.claude/agents/` 에 9개 에이전트 복사 + `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 영구 설정.

Claude Code 안에서 확인:
```
/agents   # → 9개 에이전트 목록
```

---

## 4. 환경변수

```powershell
# Windows
[System.Environment]::SetEnvironmentVariable("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS","1","User")
```

```bash
# Mac/Linux (~/.zshrc 또는 ~/.bashrc)
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

---

## 5. MCP 서버

### GitHub MCP (Docker)

**Token 발급:** GitHub → Settings → Developer settings → Personal access tokens → 권한: `repo`, `read:org`

```bash
docker run -d --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token \
  ghcr.io/github/github-mcp-server stdio
```

연결: Claude Code 설정 → MCP Servers → 추가 → Docker stdio. `/mcp` 으로 확인.

### Google Drive MCP

Claude Code 설정 → MCP Servers → claude.ai integrations → Google Drive → OAuth 승인.

### context7

라이브러리·API·버전 마이그레이션 관련 질문 시 자동 활성화. 별도 설치 불필요.

---

## 6. 플러그인

`~/.claude/settings.json` → `enabledPlugins` 에 등록.

| 플러그인 | 명령 | 역할 |
|---------|------|------|
| hookify | `/hookify` | 원하지 않는 Claude 동작 방지 |
| serena | — | LSP 기반 코드 심볼 탐색 |
| session-report | `/session-report` | 토큰 사용량 HTML 리포트 |
| claude-md-management | `/claude-md-improver` | CLAUDE.md 감사·개선 |

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

---

## 8. 도구 설치

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File tools\install-tools.ps1
```

```bash
# macOS / Linux
bash tools/install-tools.sh
```

`/snippet`, `/handoff`, `/cost` 슬래시 커맨드 + 쉘 함수 + 기본 스니펫 20개 설치.

Rust 바이너리 사용 방법은 [INTEGRATION.md](INTEGRATION.md) 참고.

---

## 9. claw-code 연동 (선택)

> 상세 가이드 → [INTEGRATION.md](INTEGRATION.md)

```bash
# Rust toolchain 먼저 설치
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

git clone https://github.com/ultraworkers/claw-code
cd claw-code/rust
cargo build --workspace
export ANTHROPIC_API_KEY="sk-ant-..."
./target/debug/claw doctor
```

---

## 10. 전체 재설치 체크리스트

```
[ ] 1.  Node.js 18+ / npm 설치 확인
[ ] 2.  npm install -g @anthropic-ai/claude-code
[ ] 3.  claude → Anthropic 계정 인증
[ ] 4.  Docker → GitHub MCP 서버 컨테이너 실행
[ ] 5.  Claude Code에서 GitHub MCP 연결
[ ] 6.  claude.ai에서 Google Drive MCP 연결
[ ] 7.  레포 클론 → setup-agents 스크립트 실행
[ ] 8.  CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 설정
[ ] 9.  ~/.claude/settings.json 에 플러그인·설정 적용
[ ] 10. /agents → 9개 에이전트 확인
[ ] 11. /mcp → MCP 연결 확인
[ ] 12. bash tools/install-tools.sh
[ ] 13. (선택) claw doctor 헬스체크
```
