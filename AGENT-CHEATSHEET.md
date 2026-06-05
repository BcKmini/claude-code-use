[← README로 돌아가기](./README.md)

# Claude Code Multi-Agent Cheatsheet

상황별 프롬프트 모음. 복사해서 바로 사용.

---

## 빠른 시작

```
# 에이전트 목록 확인
/agents

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

## 컨텍스트 관리 (비용 절약)

| 상황 | 명령 |
|------|------|
| 작업 단계 완료 후 | `/compact` |
| 완전히 다른 작업 시작 | `/clear` |
| 비용 확인 | `/cost` |
| 특정 파일만 참조 | `@src/auth/login.ts 이 파일 리뷰해줘` |

---

## 에이전트별 모델 & 비용

```
Opus   -> orchestrator, planner, security-auditor   (복잡한 판단)
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
`.claude/agents/` 폴더에 `.md` 파일 있는지 확인.

**에이전트가 범위를 벗어날 때**
```
Have reviewer ONLY review src/auth.ts.
Do NOT suggest changes to other files.
```
