# 🕹️ 추억의 오락실 — 4분할 웹 게임 컬렉션 (v1.1 수정판)

Python + Streamlit으로 구현한 레트로 아케이드 게임 4종 모음입니다.

---

## 📁 폴더 구조

```
arcade/
├── main.py                    🕹️ 통합 허브 (게임 선택·전체 랭킹·크레딧)
├── README.md
├── common/                    🔧 공통 모듈 (8종)
│   ├── __init__.py            전체 export
│   ├── theme.py               테마·CSS 팔레트
│   ├── insert_coin.py         INSERT COIN UI
│   ├── scoreboard.py          스코어보드·랭킹·닉네임
│   ├── bgm.py                 BGM/SFX (Web Audio API)
│   ├── fullscreen.py          전체화면 전환
│   ├── key_guide.py           조작키 안내
│   ├── credits.py             저작권 크레딧
│   └── demo.py                모듈 쇼케이스
├── galaga/
│   ├── app.py                 🚀 갤러그
│   └── requirements.txt
├── tetris/
│   ├── app.py                 🧱 테트리스
│   └── requirements.txt
├── pacman/
│   ├── app.py                 😮 팩맨
│   └── requirements.txt
└── space_invaders/
    ├── app.py                 👾 스페이스 인베이더
    └── requirements.txt
```

---

## 🚀 빠른 시작

### 1. 패키지 설치

```bash
pip install streamlit
```

### 2. 각 게임 실행 (터미널 5개)

```bash
# 통합 허브 (메인 진입점)
cd arcade
streamlit run main.py --server.port 8500

# 각 게임 (별도 터미널)
cd arcade/galaga         && streamlit run app.py --server.port 8501
cd arcade/tetris         && streamlit run app.py --server.port 8502
cd arcade/pacman         && streamlit run app.py --server.port 8503
cd arcade/space_invaders && streamlit run app.py --server.port 8504
```

### 3. 허브에서 게임 이동

`http://localhost:8500` 접속 → 게임 카드 클릭 → 해당 포트로 이동

---

## 🎮 게임별 소개

### 🚀 갤러그 (galaga/app.py)
- **장르**: 종스크롤 슈팅 · Namco · 1981
- **조작**: ◀◀ ◀ 이동 | 🔴 FIRE 발사 | ▶ ▶▶ 이동
- **특징**: 4종 에일리언(👾🐝🦋🦟), 편대 이동, 보스 캡처 시스템

### 🧱 테트리스 (tetris/app.py)
- **장르**: 낙하 퍼즐 · Pajitnov · 1984
- **조작**: ◀▶ 이동 | ↺ 회전 | ▼ 소프트드롭 | ⬇ 하드드롭
- **특징**: 7종 테트로미노, 고스트 블록, 홀드 기능, 레벨 시스템

### 😮 팩맨 (pacman/app.py)
- **장르**: 미로 액션 · Namco · 1980
- **조작**: ▲▼◀▶ 방향 버튼
- **특징**: 22×19 미로, 4종 고스트 AI, 파워팰릿, 과일 아이템

### 👾 스페이스 인베이더 (space_invaders/app.py)
- **장르**: 고정 슈팅 · Taito · 1978
- **조작**: ◀◀ ◀ 이동 | 🔴 FIRE 발사 | ▶ ▶▶ 이동
- **특징**: 4행×10열 인베이더, 방어막 HP 시스템, UFO 랜덤 등장

---

## 🔧 공통 모듈 사용법

각 게임 `app.py` 상단에 공통 모듈을 임포트합니다:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from common.theme       import apply_theme, get_game_css
from common.insert_coin import render_coin_screen
from common.scoreboard  import render_ranking_table, render_nickname_entry, save_score
from common.bgm         import render_bgm_toggle, play_sfx, init_audio
from common.fullscreen  import render_fullscreen_btn, render_fullscreen_wrapper
from common.key_guide   import render_key_guide, render_key_badge_row
from common.credits     import render_credits_footer
```

---

## 🛠️ 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.8+ |
| 프레임워크 | Streamlit 1.35+ |
| UI 렌더링 | HTML/CSS (st.markdown) |
| 게임 루프 | `time.sleep()` + `st.rerun()` |
| 상태 관리 | `st.session_state` |
| 사운드 | Web Audio API (JavaScript) |
| 자료구조 | list, dict (문자열 키) — set/tuple 미사용 |

---

## ⚙️ 주요 수정 사항 (v1.1)

| 문제 | 원인 | 수정 |
|------|------|------|
| 화면 깨짐 | CSS 클래스명 충돌 (.blink 등) | 게임별 고유 prefix 적용 |
| session_state 오류 | `set()` 직렬화 불가 | `list`로 변환, dict는 문자열 키 |
| 타입 힌트 오류 | `str \| None` (Python 3.10+) | `Optional` 또는 기본값으로 대체 |
| JS 오류 | fullscreen 이벤트 리스너 중복 | 인라인 onclick으로 단순화 |
| CSS 애니메이션 충돌 | `@keyframes blink` 중복 | 파일별 고유 이름 적용 |
| 렌더링 중복 | insert_coin이 프리뷰+버튼 모두 출력 | 버튼만 렌더링, 프리뷰는 게임이 직접 그림 |
| 적 충돌 감지 오류 | tuple key dict 직렬화 | 문자열 키 `"r,c"` 방식으로 통일 |

---

## 📌 개발 참고사항

- Streamlit은 버튼 클릭마다 전체 스크립트 재실행 → 모든 상태를 `session_state`에 저장
- `session_state`에는 JSON 직렬화 가능한 타입만 사용 (list, dict, str, int, float, bool)
- `set`, `tuple`(key), `frozenset` 사용 금지
- dict key는 반드시 문자열 사용 (`"r,c"` 형식)
- 게임 루프: `time.sleep(N)` → `st.rerun()` 패턴으로 구현
- 키보드 이벤트 대신 화면 버튼으로 조작 (Streamlit 특성)
