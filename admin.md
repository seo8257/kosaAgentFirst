# 🛠️ ADMIN.md
프로젝트 전체 운영 및 관리 문서

---

## 프로젝트 개요

프로젝트명: 추억의 오락실 (Retro Arcade Collection)

구성:

- Main Hub (8500)
- Galaga (8501)
- Tetris (8502)
- Pacman (8503)
- Space Invaders (8504)

기술스택

- Python 3.8+
- Streamlit
- HTML/CSS
- JavaScript(Web Audio API)

---

## 시스템 구조

main.py
│
├─ galaga/app.py
├─ tetris/app.py
├─ pacman/app.py
└─ space_invaders/app.py

공통모듈

common/

- theme.py
- bgm.py
- scoreboard.py
- insert_coin.py
- fullscreen.py
- credits.py
- key_guide.py

---

## 서비스 포트

| 서비스 | 포트 |
|---------|-------|
| Hub | 8500 |
| Galaga | 8501 |
| Tetris | 8502 |
| Pacman | 8503 |
| Space Invaders | 8504 |

---

## 배포 체크리스트

- [ ] Python 설치
- [ ] Streamlit 설치
- [ ] requirements 설치
- [ ] 포트 개방
- [ ] BGM 동작 확인
- [ ] Ranking DB 확인
- [ ] 게임 링크 확인

---

## 운영 정책

1. 모든 게임은 독립 실행 가능해야 함
2. Hub 장애가 게임 장애로 이어지면 안됨
3. 공통 모듈 수정 시 전체 게임 테스트 필수
4. CSS 변경 시 모든 게임 화면 확인

---

## 버전 이력

### v1.0

초기 릴리즈

### v1.1

- session_state 안정화
- CSS 충돌 수정
- Audio Manager 개선