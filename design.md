# 🎨 DESIGN.md
UI/UX 및 CSS 관리 문서

---

## 디자인 컨셉

Retro Arcade

1980년대 오락실 분위기

---

## 컬러 시스템

### Hub

Primary

#534AB7

Secondary

#AFA9EC

---

### Galaga

#534AB7

### Tetris

#0F6E56

### Pacman

#854F0B

### Space Invaders

#993C1D

---

## Typography

기본

Courier New

Monospace

---

## 카드 규칙

hub-card

- border-radius 14px
- padding 22px
- hover scale 1.02

---

## 애니메이션 규칙

허용

- fade
- blink
- glow

금지

- 과도한 transform
- 무거운 JS 애니메이션

---

## 반응형 정책

Desktop 우선

최소폭

1200px

---

## CSS 관리 원칙

1. 공통 CSS → theme.py
2. 게임별 CSS → app.py
3. 클래스명 중복 금지
4. keyframes 이름 중복 금지

예)

galaga_blink

tetris_blink

pacman_blink

---

## UI 체크리스트

- [ ] 색상 일관성
- [ ] 폰트 일관성
- [ ] 모바일 깨짐 없음
- [ ] Hover 정상
- [ ] Dark Theme 유지

---

## 향후 개선

- CRT 효과
- Scanline 효과
- Pixel Font 적용
- Arcade Cabinet UI
- 게임별 테마 전환