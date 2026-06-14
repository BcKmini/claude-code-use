[← README로 돌아가기](../README.md)

**한국어** · **[English](AGENT-CHEATSHEET.md)**

# Claude Code 멀티 에이전트 치트시트

상황별 프롬프트 모음. 복사해서 바로 사용.

---

## 빠른 시작

```
/agents   # 에이전트 목록 확인

# 전체 파이프라인 (가장 많이 씀)
Use the orchestrator to [큰 작업 설명]
```

---

## 상황별 프롬프트

### 새 기능 개발 (전체 파이프라인)
```
Use the orchestrator to implement [기능명].
Requirements:
- [요구사항 1]
- [요구사항 2]
Run the full pipeline: planner -> implementer -> reviewer -> tester
```

### 버그 수정
```
Use the orchestrator to fix the bug where [버그 설명].
The issue seems to be in [파일/모듈].
After fixing, have reviewer verify and tester add regression tests.
```

### 코드 리뷰만
```
Have the reviewer subagent review src/[파일경로].
Focus on security and error handling.
```

### 보안 점검
```
Have security-auditor do a full OWASP audit of src/api/
Report all findings by severity.
```

### 성능 분석
```
Have performance-optimizer analyze [파일/기능].
The symptom is: [느린 부분 설명]
```

### DB 작업
```
Have database-expert design the schema for [기능].
Requirements:
- [요구사항]
Include migration files and index strategy.
```

### 문서화
```
Have documenter update README.md and add JSDoc to src/api/
Make it clear enough for a new developer to onboard in 30 minutes.
```

---

## 하네스 설계 & 파이프라인 (신규)

### AI 하네스 설계
```
Have harness-designer design a tight harness for the following task.

Task: [자동화할 작업 설명]
Domain: [예: Spring Boot/JPA, Python/FastAPI]
Expected output format: [예: unified diff, JSON report]

Deliver: specialist definitions, pipeline stages, context isolation plan,
human oversight checkpoints, token cost estimate.
```

### 다단계 파이프라인 실행
```
Have pipeline-orchestrator plan and execute a pipeline for:
[워크플로우 설명]

Use context isolation between stages.
Run independent stages in parallel.
Apply quality gates at every stage.
Produce a run report at the end.
```

### 컨텍스트 격리 — 병렬 정찰 패턴
```
다음 분석을 병렬 컨텍스트 격리 방식으로 재설계해줘:

현재: 에이전트 하나가 모든 것을 읽고 하나의 보고서를 만듦
목표: 4개의 에이전트가 각자 하나의 질문에 격리된 컨텍스트로 답변

병렬로 답할 질문들:
1. [질문 1]
2. [질문 2]
3. [질문 3]
4. [질문 4]

그 다음 최종 단계에서 4개의 답변을 합성.
```

### 다중 관점 리뷰 루프
```
[파일/diff/아티팩트]에 대한 리뷰 루프를 설정해줘.

리뷰 관점:
1. 정확성 (로직 오류, 엣지케이스)
2. 보안 (OWASP Top 10, 인젝션, 인증)
3. 성능 (N+1 쿼리, 인덱스 누락, O(n²))
4. 스타일 (네이밍, 복잡도, 유지보수성)

최대 반복: 3회
조기 종료 조건: 새 발견 사항 없거나 이전 라운드 대비 개선 없을 때.
```

### 모든 에이전트 하네스 검증
```bash
claude-harness check-all   # agents/ 폴더 전체 검증
```

### 파이프라인 추적 워크플로우
```bash
claude-pipeline init my-workflow
claude-pipeline stage "분석" start
claude-pipeline stage "분석" pass --note "이슈 3개 발견"
claude-pipeline stage "패치 생성" start
claude-pipeline report     # 마크다운 실행 보고서
```

---

## 병렬 실행 (시간 단축)

```
Run these in parallel:
1. Have planner design the auth module
2. Have database-expert design the user schema
3. Have security-auditor review current auth requirements
Then have implementer execute the combined plan.
```

---

## Agent Teams 모드

터미널 3개를 나란히 열고:

**터미널 1 (팀 리드)**
```bash
claude --model claude-opus-4-5
> Start an agent team. You are the team lead.
> Task: [큰 작업]
> Spawn: implementer, reviewer, tester as teammates
```

**터미널 2 (모니터링)**
```bash
watch -n 1 cat .claude/team-tasks.md
```

**터미널 3 (추가 지시)**
```bash
claude --agent reviewer "re-check src/auth after implementer changes"
```

---

## 슬래시 커맨드 — 도구

| 커맨드 | 기능 | 예시 |
|--------|------|------|
| `/snippet list` | 저장된 프롬프트 목록 | `/snippet list --tag security` |
| `/snippet run` | 프롬프트 템플릿 실행 | `/snippet run full-pipeline` |
| `/handoff save` | 세션 컨텍스트 저장 | `/handoff save` |
| `/handoff load` | 마지막 세션 복원 | `/handoff load` |
| `/cost estimate` | 실행 전 비용 추정 | `/cost estimate full-pipeline` |
| `/cost month` | 이번 달 사용량 요약 | `/cost month` |
| `/review-diff` | git diff로 코드 리뷰 | `/review-diff --focus security` |
| `/review-diff --staged` | 스테이징된 변경사항 리뷰 | `/review-diff --staged` |
| `/review-diff --base main` | 브랜치와 main 비교 | `/review-diff --base main` |
| `/remind` | 미완료 TODO 항목 표시 | `/remind` |
| `/remind --quiet` | 개수만 표시 | `/remind --quiet` |
| `/harness design` | AI 하네스 설계 | `/harness design 슬로우 쿼리 자동 분석` |
| `/harness validate` | 에이전트 하네스 검증 | `/harness validate agents/03-reviewer.md` |
| `/pipeline run` | 다단계 파이프라인 실행 | `/pipeline run 분석 및 패치 생성` |
| `/pipeline status` | 파이프라인 실행 현황 | `/pipeline status` |

---

## 컨텍스트 관리 (비용 절약)

| 상황 | 명령 |
|------|------|
| 작업 단계 완료 후 | `/compact` |
| 완전히 다른 작업 시작 | `/clear` |
| 비용 확인 | `/cost` |
| 실시간 비용 모니터 (다른 터미널) | `claude-tools watch` |
| 환경 헬스체크 | `claude-tools env` |
| 미완료 작업으로 재개 | `claude-remind \| claude` |
| 전체 세션 복원 | `claude-handoff load \| claude` |
| 특정 파일만 참조 | `@src/auth/login.ts 이 파일 리뷰해줘` |

---

## 세션 워크플로우

```bash
# 세션 종료
claude-handoff save --note "OAuth 완료, 다음: 이메일 인증"

# 세션 시작 (하나 또는 둘 다 사용)
claude-remind | claude          # 미완료 TODO 항목 확인
claude-handoff load | claude    # 전체 git 컨텍스트 복원
```

---

## 에이전트별 모델 & 비용

```
Opus   -> orchestrator, planner, security-auditor,   (복잡한 판단)
          harness-designer, pipeline-orchestrator
Sonnet -> implementer, reviewer, tester,             (실행 위주)
          performance-optimizer, database-expert
Haiku  -> documenter                                 (단순 반복, 최저 비용)
```

---

## 트러블슈팅

**에이전트가 안 보일 때**
```
/agents
```
`~/.claude/agents/` 폴더에 `.md` 파일 있는지 확인.

**에이전트가 범위를 벗어날 때**
```
Have reviewer ONLY review src/auth.ts.
Do NOT suggest changes to other files.
```

**전체 환경 확인**
```bash
claude-tools env   # 또는: make env
```
