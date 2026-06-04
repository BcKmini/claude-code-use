# Claude Code 세팅 가이드

이 문서는 현재 구성된 Claude Code 환경 전체를 기록한다.
새 PC나 새 계정에서 동일한 환경을 재현할 때 참고.

---

## 기본 설정

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
| effortLevel | medium | 응답 품질/속도 균형 (low/medium/high) |
| theme | dark | UI 테마 |
| autoUpdatesChannel | latest | 자동 업데이트 채널 |

---

## 환경변수

```powershell
# Windows — 영구 설정 (사용자 환경변수)
[System.Environment]::SetEnvironmentVariable(
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS",
    "1",
    "User"
)
```

```bash
# Mac/Linux
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
```

| 변수 | 값 | 설명 |
|------|----|------|
| CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS | 1 | 에이전트 간 직접 소통 활성화 |

---

## 멀티 에이전트 시스템

에이전트 파일 위치: `~/.claude/agents/` (글로벌) 또는 `.claude/agents/` (프로젝트)

| 파일 | 에이전트 | 모델 | 역할 |
|------|---------|------|------|
| 00-orchestrator.md | orchestrator | claude-opus-4-5 | 총괄 지휘, 작업 분해 |
| 01-planner.md | planner | claude-opus-4-5 | 설계·아키텍처 (읽기 전용) |
| 02-implementer.md | implementer | claude-sonnet-4-5 | 코드 작성·수정 |
| 03-reviewer.md | reviewer | claude-sonnet-4-5 | 코드 리뷰 (읽기 전용) |
| 04-tester.md | tester | claude-sonnet-4-5 | 테스트 작성 |
| 05-security-auditor.md | security-auditor | claude-opus-4-5 | 보안 감사 (읽기 전용) |
| 06-performance-optimizer.md | performance-optimizer | claude-sonnet-4-5 | 성능 분석 |
| 07-database-expert.md | database-expert | claude-sonnet-4-5 | DB 설계·쿼리 |
| 08-documenter.md | documenter | claude-haiku-4-5 | 문서 작성 |

**설치 방법**

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File setup-agents.ps1
```

```bash
# Mac/Linux
mkdir -p ~/.claude/agents
cp agents/*.md ~/.claude/agents/
```

**확인**
```
/agents
```

---

## MCP 서버

### 1. GitHub MCP (Docker)

공식 GitHub MCP 서버를 Docker로 실행.

**실행 명령**
```bash
docker run -d \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here \
  ghcr.io/github/github-mcp-server \
  stdio
```

**현재 실행 중인 컨테이너 확인**
```bash
docker ps --filter ancestor=ghcr.io/github/github-mcp-server
```

**제공 기능**
- 이슈 생성·조회·업데이트
- PR 생성·리뷰·머지
- 파일 생성·수정·푸시 (단일 커밋으로 여러 파일)
- 레포지토리 생성
- 브랜치 관리
- 코드·이슈·PR 검색

**Token 발급**
- GitHub → Settings → Developer settings → Personal access tokens
- 필요 권한: `repo`, `read:org`

**Claude Code 연결**
Claude Code 설정 → MCP Servers → 새 서버 추가 → Docker 컨테이너 stdio 연결

> 연결 오류 (-32000) 발생 시: 컨테이너가 실행 중인지 확인 후 `/mcp`로 재연결

---

### 2. Google Drive MCP (claude.ai 연동)

claude.ai에서 제공하는 Google Drive MCP.

**연결 방법**
- Claude Code 설정 → MCP Servers → claude.ai integrations에서 Google Drive 추가
- 최초 연결 시 OAuth 인증 필요 (브라우저에서 구글 계정 승인)

**제공 기능**
- Google Docs, Sheets, Drive 파일 읽기

---

### 3. context7

라이브러리·프레임워크 최신 문서를 실시간으로 조회.

**사용 시점**
- React, Next.js, FastAPI, Prisma 등 라이브러리 관련 질문
- API 문법·설정·버전 마이그레이션 확인
- 훈련 데이터와 최신 문서가 다를 수 있는 경우

**사용 예시**
```
next.js 15의 app router에서 middleware 설정 방법 알려줘
```
*(Claude가 자동으로 context7에서 최신 문서 조회)*

---

## 플러그인

`~/.claude/settings.json`의 `enabledPlugins`에 등록됨.

| 플러그인 | 슬래시 명령 | 역할 |
|---------|------------|------|
| hookify | `/hookify` | 특정 동작 방지 훅 설정 |
| serena | — | 코드 심볼 분석·탐색 (LSP 기반) |
| session-report | `/session-report` | 세션 토큰 사용량 HTML 리포트 생성 |
| claude-md-management | `/claude-md-improver` | CLAUDE.md 파일 감사·개선 |

### hookify

원하지 않는 Claude 동작을 훅으로 방지.

```
/hookify          # 대화에서 방지할 동작 자동 탐지
/hookify list     # 현재 설정된 훅 목록
/hookify configure  # 훅 활성화/비활성화
```

### session-report

```
/session-report
```
실행하면 `session-report-YYYYMMDD-HHMM.html` 파일 생성.
토큰 사용량, 캐시 히트율, 가장 비싼 프롬프트 등 확인 가능.

### serena

프로젝트 활성화 후 심볼 탐색, 함수 정의 찾기, 참조 분석 등 LSP 수준의 코드 탐색 지원.

---

## Docker 활용 팁

### GitHub MCP 서버 재시작

```bash
# 컨테이너 목록 확인
docker ps -a --filter ancestor=ghcr.io/github/github-mcp-server

# 중지된 컨테이너 재시작
docker start [CONTAINER_ID]

# 새로 실행
docker run -d \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here \
  ghcr.io/github/github-mcp-server \
  stdio
```

### 컨테이너 자동 시작 설정

```bash
# --restart always 옵션으로 PC 재부팅 후에도 자동 실행
docker run -d \
  --restart always \
  -e GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here \
  ghcr.io/github/github-mcp-server \
  stdio
```

---

## 전체 재설치 체크리스트

새 환경 세팅 시 순서:

```
[ ] 1. Claude Code 설치
[ ] 2. Docker 설치 및 GitHub MCP 서버 컨테이너 실행
[ ] 3. Claude Code에서 GitHub MCP 연결
[ ] 4. claude.ai에서 Google Drive MCP 연결
[ ] 5. 이 레포 클론 후 setup-agents.ps1 실행
[ ] 6. 환경변수 CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 설정
[ ] 7. ~/.claude/settings.json에 플러그인·설정 적용
[ ] 8. /agents 명령으로 9개 에이전트 확인
[ ] 9. /mcp 명령으로 MCP 연결 상태 확인
```
