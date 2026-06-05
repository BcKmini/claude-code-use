---
description: 저장된 프롬프트 스니펫을 조회하거나 실행합니다. 사용법: /snippet [list|run <name>|show <name>|search <keyword>]
---

`~/.claude/snippets.json` 파일을 읽어서 아래 규칙에 따라 처리하세요.

요청: $ARGUMENTS

---

**처리 규칙**

`list` 또는 인수 없음:
- snippets.json의 모든 항목을 **이름 / 태그 / 프롬프트 첫줄** 컬럼으로 표 형식으로 출력하세요.
- 파일이 없거나 비어 있으면 "저장된 스니펫이 없습니다. 터미널에서 `python tools/snippet.py import snippets/defaults.json` 을 실행해 기본 스니펫을 불러오세요." 라고 안내하세요.

`run <name>`:
- snippets.json에서 `name`에 해당하는 `prompt` 값을 찾으세요.
- 찾으면 그 내용을 **그대로 실행**하세요 — 마치 사용자가 직접 입력한 프롬프트처럼 처리합니다.
- 없으면 "스니펫 '<name>'을 찾을 수 없습니다. `/snippet list` 로 목록을 확인하세요." 라고 안내하세요.

`show <name>`:
- 해당 스니펫의 이름, 태그, 생성일, 사용 횟수, 전체 프롬프트를 보기 좋게 출력하세요.

`search <keyword>`:
- 이름, 프롬프트 내용, 태그에서 키워드를 검색하고 결과를 표로 출력하세요.

---

**참고**
- snippets.json 경로: `~/.claude/snippets.json`
- 새 스니펫 저장은 터미널에서 `python tools/snippet.py save <name> <prompt>` 로 합니다.
- 기본 스니펫 임포트: `python tools/snippet.py import snippets/defaults.json`
