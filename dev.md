# 👨‍💻 DEV.md
개발 가이드

---

## 개발 원칙

1. 공통 기능은 common 모듈에 구현
2. 게임별 기능은 해당 게임 디렉토리에 구현
3. 중복 코드 금지
4. Session State 사용

---

## 디렉토리 구조

arcade/

common/
galaga/
tetris/
pacman/
space_invaders/

---

## Session State 규칙

허용

- str
- int
- float
- bool
- list
- dict

금지

- set
- tuple key
- frozenset

---

## 네이밍 규칙

### 함수

snake_case

예)

render_bgm_toggle()

### 클래스

PascalCase

예)

AudioManager

### 상수

UPPER_CASE

예)

GAME_META

---

## 공통 모듈 담당

### theme.py

- CSS
- 색상 팔레트

### bgm.py

- 배경음
- 효과음

### scoreboard.py

- 점수 저장
- 랭킹

### insert_coin.py

- 코인 UI

---

## 신규 게임 추가 절차

1. games/new_game 생성
2. app.py 작성
3. GAME_META 등록
4. main.py 카드 추가
5. 포트 할당
6. QA 수행

---

## 코드 리뷰 체크리스트

- [ ] 예외처리
- [ ] Session State 확인
- [ ] 중복 제거
- [ ] 타입 오류 없음
- [ ] CSS 충돌 없음