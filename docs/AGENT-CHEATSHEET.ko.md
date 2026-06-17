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

## 외과적 코드 수정 (PR 가독성 최적화)

> 이 프롬프트들은 최소 diff를 강제해서 PR 리뷰 속도를 높입니다.
> Google/Stripe/Anthropic 모범 사례 기반: 리뷰 가능한 diff는 60% 빠르게 머지됩니다.

### 함수 하나만 수정
```
Have implementer fix ONLY the [함수명] function in [파일 경로].
Do NOT modify any other functions, imports, or formatting in that file.
Use Edit tool — do not rewrite the whole file.
Diff target: under 30 lines changed.
```

### 최소 패치 — 버그 수정
```
Bug is in [파일:함수명].
Have implementer change ONLY what's necessary to fix this bug.
Constraint: diff must stay under 30 lines.
If broader refactoring would help but isn't strictly needed, list it separately — don't apply it now.
```

### 기존 코드 건드리지 않고 기능 추가
```
Have implementer add [기능] to [파일].
Scope boundary: new code only — do not reformat, rename, or reorganize existing code.
Existing functions must be left exactly as they are unless the feature requires changing them.
```

### 큰 변경을 원자적 PR로 분리
```
This change affects [N] files. Have orchestrator split into separate atomic implementer tasks:
Task 1: [변경 설명] — files: [A, B only]
Task 2: [변경 설명] — file: [C only]
Task 3: [변경 설명] — file: [D only]
Each task should produce a diff under 150 lines.
Call implementer once per task, sequentially.
```

### 적용 전 diff 검토 요청
```
Before implementing, have planner output:
1. 수정할 파일 목록 (함수명과 라인 범위 포함)
2. 명시적인 "건드리지 말 것" 목록
3. 파일별 예상 변경 라인 수
I will approve the scope before implementer starts.
```

### Reviewer: 정확성 전에 diff 품질 먼저 확인
```
Have reviewer check [파일 또는 브랜치 diff] for diff quality BEFORE correctness:
- 요청된 함수/라인만 변경됐는가?
- 포맷 노이즈나 불필요한 이름 변경은 없는가?
- 전체 diff가 200줄 이내인가?
스코프가 작업 범위보다 넓으면 DIFF_BLOAT으로 표시해줘.
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

**implementer가 Edit 대신 파일 전체를 재작성했을 때**
```
변경사항을 되돌린 후:
Have implementer re-implement using Edit tool only.
Scope: modify ONLY [함수명] at [파일:line_start–line_end].
Do not use Write on an existing file.
```

**전체 환경 확인**
```bash
claude-tools env   # 또는: make env
```
