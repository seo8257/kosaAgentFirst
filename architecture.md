# 🏗️ ARCHITECTURE.md

추억의 오락실 시스템 아키텍처 문서

---

# 1. 시스템 개요

본 프로젝트는 Streamlit 기반의 멀티 게임 아케이드 플랫폼이다.

사용자는 Hub(Main)에서 게임을 선택하고 개별 게임 서버로 이동하여 플레이할 수 있다.

---

# 2. 전체 구조

```text
                    ┌─────────────┐
                    │   Browser   │
                    └──────┬──────┘
                           │
                   Port 8500 (Hub)
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼

   Port8501          Port8502          Port8503
    Galaga            Tetris            Pacman

                           │
                           ▼

                     Port8504
                  Space Invaders
```

---

# 3. 프로젝트 구조

```text
arcade/

main.py

common/
├── theme.py
├── bgm.py
├── scoreboard.py
├── insert_coin.py
├── fullscreen.py
├── key_guide.py
└── credits.py

galaga/
└── app.py

tetris/
└── app.py

pacman/
└── app.py

space_invaders/
└── app.py
```

---

# 4. 레이어 구조

## Presentation Layer

화면 표시 담당

구성

* Streamlit
* HTML
* CSS
* JavaScript

파일

* main.py
* 각 게임 app.py

---

## Business Layer

게임 규칙

구성

* 충돌 판정
* 점수 계산
* 레벨 계산
* 적 AI

---

## Shared Service Layer

공통 서비스

파일

* theme.py
* bgm.py
* scoreboard.py
* insert_coin.py

---

## Storage Layer

현재

Session State

향후

* SQLite
* PostgreSQL
* Redis

---

# 5. 데이터 흐름

사용자 입력

↓

Session State 변경

↓

게임 로직 실행

↓

점수 계산

↓

랭킹 저장

↓

UI 재렌더링

---

# 6. Audio 구조

```text
UI
 ↓
render_bgm_toggle()

 ↓

Audio Manager

 ↓

Web Audio API
```

---

# 7. Score 구조

```text
Game

 ↓

save_score()

 ↓

scoreboard.py

 ↓

Ranking Storage

 ↓

render_ranking_table()
```

---

# 8. 향후 아키텍처 목표

V2

* SQLite 영구 저장

V3

* REST API 서버

V4

* 멀티플레이

V5

* 클라우드 배포

---

# 9. 설계 원칙

1. 게임은 독립 실행 가능
2. 공통 기능은 common 모듈 사용
3. UI와 게임 로직 분리
4. CSS 중복 금지
5. Session State 의존 최소화
6. 확장 가능한 구조 유지
