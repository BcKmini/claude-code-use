**한국어** · **[English](CONTRIBUTING.md)**

# 기여 가이드

이 프로젝트를 개선하는 데 도움을 주셔서 감사합니다!

---

## 기여 방법

| 유형 | 방법 |
|------|------|
| 버그 수정 | Bug Report 이슈 열기 → 수정 후 PR |
| 새 스니펫 | `snippets/defaults.json`에 추가 → PR |
| 새 에이전트 | `agents/`에 `.md` 파일 추가 → README 테이블 업데이트 → PR |
| 새 도구 | `tools/`에 Python 도구 추가 + `.claude/commands/`에 슬래시 커맨드 → PR |
| 문서 개선 | `.md` 파일 수정 → PR (EN/KO 둘 다 업데이트) |
| 번역 개선 | `README.md` (EN) 또는 `README.ko.md` (KO) 개선 |
| 기능 아이디어 | Feature Request 이슈 먼저 열기 |

---

## 개발 환경 설정

```bash
git clone https://github.com/BcKmini/Claudecode-Agent.git
cd Claudecode-Agent
python --version   # 3.8+ 필요
make status        # 설치 상태 확인
```

`snippet.py`, `claude-handoff.py`, `claude-cost.py`, `claude-review-diff.py`, `claude-remind.py` 모두 Python 표준 라이브러리만 사용합니다 — `pip install` 불필요.

Rust 바이너리:

```bash
cd rust
cargo check   # 빌드 확인
cargo build --release
```

---

## 새 스니펫 추가

1. `snippets/defaults.json` 열기
2. 기존 형식에 맞게 항목 추가:

```json
"my-snippet": {
  "prompt": "프롬프트 내용. {{VARIABLE}}으로 템플릿 변수 사용 가능.",
  "tags": ["tag1", "tag2"],
  "created": "YYYY-MM-DD",
  "uses": 0
}
```

3. 로컬에서 테스트:
```bash
python tools/snippet.py import snippets/defaults.json --overwrite
python tools/snippet.py show my-snippet
python tools/snippet.py run my-snippet --dry-run
```

4. `README.md`와 `README.ko.md`의 스니펫 테이블 업데이트

---

## 새 에이전트 추가

1. 기존 에이전트 파일 형식을 참고해 `agents/NN-agent-name.md` 생성
2. `README.md`와 `README.ko.md`의 에이전트 테이블에 행 추가
3. 에이전트 이름을 하드코딩하는 경우 설치 스크립트 업데이트

---

## 새 도구 추가

1. `tools/claude-<name>.py` 추가 — 기존 도구 스타일 참고
   - stdlib만 사용, 외부 의존성 없음
   - Python 3.8+ 호환
   - `NO_COLOR` 환경변수 준수
2. `.claude/commands/<name>.md` 슬래시 커맨드 문서 추가
3. `Makefile` → `install-tools` 타겟과 `status` 타겟에 추가
4. Rust 구현 추가 시: `rust/claude-tools/src/<name>.rs` 작성 후 `main.rs`에 연결
5. `README.md`와 `README.ko.md`의 도구 섹션, 슬래시 커맨드 테이블, 저장소 구조 업데이트
6. `docs/AGENT-CHEATSHEET.md`와 `docs/AGENT-CHEATSHEET.ko.md` 업데이트

---

## 코드 스타일

### Python 도구
- 표준 라이브러리만 사용 — 외부 의존성 없음
- Python 3.8+ 호환
- 사용자에게 보이는 문자열은 모두 영어
- `NO_COLOR` 환경변수 반드시 준수
- 종료 코드: `0` 성공, `1` 찾을 수 없음/이미 존재, `2` 사용법 오류

### Rust (claude-tools)
- `cargo check` 에러 없어야 함
- `cargo clippy` 경고 최소화
- 새 서브커맨드는 `rust/claude-tools/src/` 기존 모듈 패턴 따르기
- 색상 출력은 `crate::colors` 함수 사용 (`green()`, `red()` 등)

---

## Pull Request 체크리스트

- [ ] `python tools/snippet.py --help` 정상 작동
- [ ] 기존 명령어 모두 정상 작동
- [ ] `snippet import snippets/defaults.json` 정상 작동
- [ ] `cargo check` 통과 (Rust 변경 시)
- [ ] `make test` 통과
- [ ] 새 스니펫·에이전트·도구 추가 시 README 테이블 업데이트됨
- [ ] **EN/KO 문서 쌍 모두 업데이트됨** (README, CHEATSHEET, SETUP, INTEGRATION 해당 항목)
- [ ] 새 도구 추가 시 슬래시 커맨드 `.md` 파일 추가됨
- [ ] 새 도구 추가 시 `Makefile` 업데이트됨
- [ ] 외부 의존성 새로 추가하지 않음

---

## 라이선스

기여하면 [MIT 라이선스](../LICENSE) 하에 배포된다는 것에 동의하는 것으로 간주합니다.
