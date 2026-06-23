"""
arcade/common/demo.py
──────────────────────
공통 모듈 쇼케이스 데모

모든 공통 컴포넌트를 한 화면에서 확인할 수 있는 데모 앱입니다.
실행: streamlit run common/demo.py --server.port 8510

탭 구성:
    Tab 1 — INSERT COIN   (동전 투입 UI)
    Tab 2 — SCOREBOARD    (스코어보드 & 랭킹)
    Tab 3 — BGM & SFX     (사운드 토글)
    Tab 4 — FULLSCREEN    (전체화면)
    Tab 5 — KEY GUIDE     (조작키 안내)
    Tab 6 — CREDITS       (저작권 크레딧)
    Tab 7 — THEME         (테마 팔레트 전체)
"""

import sys, os
# 상위 폴더를 path에 추가 (arcade/에서 실행 시 common import 가능)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

# ── 공통 모듈 임포트 ────────────────────────────────────────────
from common.theme       import apply_theme, THEMES, get_game_css
from common.insert_coin import render_coin_screen, credit_display, add_credit
from common.scoreboard  import (render_ranking_table, render_nickname_entry,
                                 render_all_rankings, save_score, get_hi_score)
from common.bgm         import render_bgm_toggle, play_sfx
from common.fullscreen  import (render_fullscreen_btn, render_fullscreen_wrapper,
                                 fullscreen_status_badge)
from common.key_guide   import render_key_guide, render_key_overlay, render_key_badge_row
from common.credits     import (render_credits_footer, render_credits_badge,
                                 render_credits_scroll, render_credits_screen)

# ── 페이지 설정 ─────────────────────────────────────────────────
st.set_page_config(
    page_title="🕹️ Common 모듈 데모",
    page_icon="🕹️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 테마 선택 (사이드바) ────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 테마 선택")
    selected_theme = st.selectbox(
        "게임 테마",
        options=list(THEMES.keys()),
        index=0,
        format_func=lambda k: THEMES[k]["name"],
    )
    t = THEMES[selected_theme]

    st.markdown("---")
    st.markdown("### 📁 공통 모듈 목록")
    st.markdown("""
    | 파일 | 요소 |
    |------|------|
    | `theme.py` | 테마·CSS |
    | `insert_coin.py` | ① 코인 투입 |
    | `scoreboard.py` | ② 스코어보드 |
    | `bgm.py` | ③ BGM·SFX |
    | `fullscreen.py` | ④ 전체화면 |
    | `key_guide.py` | ⑤ 조작키 안내 |
    | `credits.py` | ⑥ 크레딧 |
    | `__init__.py` | 패키지 초기화 |
    """)

    st.markdown("---")
    st.markdown("### 🔗 게임 포트")
    st.markdown("""
    - 🚀 갤러그 → `8501`
    - 🧱 테트리스 → `8502`
    - 😮 팩맨 → `8503`
    - 👾 인베이더 → `8504`
    - 🕹️ 허브 → `8500`
    - 🎨 데모 → `8510`
    """)

# ── 테마 적용 ───────────────────────────────────────────────────
apply_theme(selected_theme)

# ── 헤더 ───────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding:14px 0 6px; font-family:'Courier New',monospace;">
    <div style="font-size:1.8rem; font-weight:bold; color:{t['accent']};
                letter-spacing:0.2em; text-shadow:0 0 16px {t['glow']};">
        🕹️ COMMON MODULE DEMO
    </div>
    <div style="font-size:0.8rem; color:{t['sub_text']}; letter-spacing:0.12em; margin-top:4px;">
        arcade/common — 기획서 공통 요소 6종 쇼케이스
    </div>
</div>
""", unsafe_allow_html=True)

# ── 탭 구성 ─────────────────────────────────────────────────────
tabs = st.tabs([
    "① INSERT COIN",
    "② SCOREBOARD",
    "③ BGM & SFX",
    "④ FULLSCREEN",
    "⑤ KEY GUIDE",
    "⑥ CREDITS",
    "🎨 THEME",
])

# ═══════════════════════════════════════════════════════════════
# Tab 1 — INSERT COIN
# ═══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown(f"#### ① INSERT COIN — 동전 투입 UI")
    st.markdown(f"`arcade/common/insert_coin.py`")
    st.markdown("---")

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Free Play 모드** (코인 불필요)")
        if render_coin_screen(selected_theme, show_credits=False, free_play=True):
            st.success("✅ 게임 시작! (Free Play)")
            play_sfx("coin")

    with col_r:
        st.markdown("**크레딧 모드** (코인 충전 후 시작)")
        credit_display()
        if render_coin_screen(selected_theme, show_credits=True, free_play=False):
            st.success("✅ 게임 시작! (크레딧 소모)")
            play_sfx("coin")

    st.markdown("---")
    st.markdown("**코드 예시**")
    st.code("""
from common.insert_coin import render_coin_screen, add_credit

# 타이틀 화면에서 코인 화면 렌더링
if render_coin_screen("galaga", free_play=True):
    start_game()   # 버튼 눌리면 True 반환
""", language="python")

# ═══════════════════════════════════════════════════════════════
# Tab 2 — SCOREBOARD
# ═══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("#### ② SCOREBOARD — 스코어보드 & 랭킹")
    st.markdown("`arcade/common/scoreboard.py`")
    st.markdown("---")

    # 더미 점수 추가
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("**점수 등록 테스트**")
        test_game  = st.selectbox("게임", ["galaga","tetris","pacman","space_invaders"],
                                   format_func=lambda x: {"galaga":"🚀 갤러그","tetris":"🧱 테트리스",
                                                           "pacman":"😮 팩맨","space_invaders":"👾 인베이더"}[x])
        test_score = st.number_input("점수", min_value=0, max_value=999999, value=12500, step=500)
        test_nick  = st.text_input("닉네임 (3자)", value="AAA", max_chars=3).upper()

        if st.button("📝 점수 등록", key="demo_save_score"):
            rank = save_score(test_game, test_score, test_nick)
            st.success(f"🏆 {rank}위 등록 완료!")
            play_sfx("clear")

        if st.button("🎲 랜덤 점수 5개 추가", key="demo_random"):
            import random
            names = ["AAA","BBB","CCC","DDD","EEE","ZZZ","PRO","ACE","TOP","GOD"]
            for _ in range(5):
                save_score(test_game, random.randint(1000, 99999),
                           random.choice(names))
            st.success("5개 점수 추가 완료!")
            st.rerun()

        st.markdown("---")
        st.markdown(f"**현재 HI-SCORE**: `{get_hi_score(test_game):,}`")

    with col_b:
        st.markdown("**랭킹 테이블**")
        render_ranking_table(test_game, theme_key=selected_theme,
                              highlight_score=int(test_score))

    st.markdown("---")
    st.markdown("**전체 게임 통합 랭킹**")
    render_all_rankings(theme_key=selected_theme)

    st.markdown("---")
    st.markdown("**코드 예시**")
    st.code("""
from common.scoreboard import save_score, render_ranking_table, render_nickname_entry

# 점수 저장 (게임오버 시)
rank = save_score("galaga", score=15000, nickname="AAA")

# 닉네임 입력 화면
if render_nickname_entry("galaga", score=15000):
    st.success(f"{rank}위 등록!")

# 랭킹 테이블
render_ranking_table("galaga", highlight_score=15000)
""", language="python")

# ═══════════════════════════════════════════════════════════════
# Tab 3 — BGM & SFX
# ═══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("#### ③ BGM & SFX — 사운드 시스템")
    st.markdown("`arcade/common/bgm.py`")
    st.markdown("---")

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("**BGM & SFX 토글 패널 (풀 모드)**")
        render_bgm_toggle(theme_key=selected_theme, game=selected_theme, compact=False)

    with col_r:
        st.markdown("**컴팩트 모드**")
        render_bgm_toggle(theme_key=selected_theme, game=selected_theme, compact=True)

        st.markdown("---")
        st.markdown("**효과음 테스트**")
        sfx_list = [
            ("🔫 발사음",        "shoot"),
            ("💥 폭발음",        "explosion"),
            ("🪙 코인",          "coin"),
            ("💀 게임오버",      "gameover"),
            ("🎉 스테이지 클리어","clear"),
            ("⬆️ 파워업",        "powerup"),
            ("· 점 먹기",        "eat_dot"),
            ("👻 고스트 먹기",   "eat_ghost"),
            ("📏 줄 소거",       "line_clear"),
            ("🛸 UFO",           "ufo"),
        ]
        cols = st.columns(2)
        for i, (label, sfx) in enumerate(sfx_list):
            with cols[i % 2]:
                if st.button(label, key=f"sfx_{sfx}"):
                    play_sfx(sfx)

    st.markdown("---")
    st.markdown("**코드 예시**")
    st.code("""
from common.bgm import render_bgm_toggle, play_sfx, init_audio

# 게임 시작 시 BGM 초기화
init_audio("galaga")

# 사이드바에 토글 배치
with st.sidebar:
    render_bgm_toggle(theme_key="galaga", compact=True)

# 이벤트 시 효과음
if bullet_hit:
    play_sfx("explosion")
if game_over:
    play_sfx("gameover")
""", language="python")

# ═══════════════════════════════════════════════════════════════
# Tab 4 — FULLSCREEN
# ═══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("#### ④ FULLSCREEN — 전체화면 전환")
    st.markdown("`arcade/common/fullscreen.py`")
    st.markdown("---")

    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("**더블클릭 또는 버튼으로 전체화면 진입**")

        # 게임 보드 더미 + 전체화면 래퍼
        dummy_board = f"""
        <div style="background:{t['bg2']};border:2px solid {t['border']};
                    border-radius:10px;padding:40px;text-align:center;
                    font-family:'Courier New',monospace;">
            <div style="font-size:3rem;margin-bottom:12px;">🎮</div>
            <div style="color:{t['accent']};font-size:1rem;letter-spacing:0.15em;">
                GAME BOARD AREA
            </div>
            <div style="color:{t['sub_text']};font-size:0.75rem;margin-top:8px;">
                더블클릭 → 전체화면
            </div>
        </div>
        """
        from common.fullscreen import render_fullscreen_wrapper
        render_fullscreen_wrapper(dummy_board, theme_key=selected_theme,
                                   element_id="demo-fs-target")

    with col_r:
        st.markdown("**전체화면 버튼**")
        render_fullscreen_btn(
            theme_key=selected_theme,
            target_id="demo-fs-target",
            label="⛶  전체화면 전환",
            show_hint=True,
        )
        st.markdown("")
        st.markdown("**상태 뱃지**")
        fullscreen_status_badge(theme_key=selected_theme)

    st.markdown("---")
    st.markdown("**코드 예시**")
    st.code("""
from common.fullscreen import (
    inject_fullscreen_css, render_fullscreen_btn,
    render_fullscreen_wrapper
)

# 초기화 (1회)
inject_fullscreen_css("galaga")

# 게임 보드를 래퍼로 감싸기
board_html = render_board_html()
render_fullscreen_wrapper(board_html, theme_key="galaga",
                           element_id="galaga-board")

# 전체화면 버튼 배치
render_fullscreen_btn(theme_key="galaga", target_id="galaga-board")
""", language="python")

# ═══════════════════════════════════════════════════════════════
# Tab 5 — KEY GUIDE
# ═══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("#### ⑤ KEY GUIDE — 조작키 안내")
    st.markdown("`arcade/common/key_guide.py`")
    st.markdown("---")

    game_sel = st.radio("게임 선택", ["galaga","tetris","pacman","space_invaders"],
                         horizontal=True,
                         format_func=lambda x: {"galaga":"🚀 갤러그","tetris":"🧱 테트리스",
                                                 "pacman":"😮 팩맨","space_invaders":"👾 인베이더"}[x])

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**인라인 패널 (전체)**")
        render_key_guide(game_sel, theme_key=selected_theme,
                          show_tips=True, show_common=True)

    with col_r:
        st.markdown("**한 줄 뱃지 모드**")
        render_key_badge_row(game_sel, theme_key=selected_theme)

        st.markdown("---")
        st.markdown("**expander 팝업 모드**")
        render_key_overlay(game_sel, theme_key=selected_theme)

    st.markdown("---")
    st.markdown("**코드 예시**")
    st.code("""
from common.key_guide import render_key_guide, render_key_overlay

# 사이드바 전체 안내
with st.sidebar:
    render_key_guide("galaga", show_tips=True)

# 게임 화면 하단 한 줄 뱃지
render_key_badge_row("galaga")

# expander 팝업
render_key_overlay("galaga")
""", language="python")

# ═══════════════════════════════════════════════════════════════
# Tab 6 — CREDITS
# ═══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("#### ⑥ CREDITS — 저작권 크레딧")
    st.markdown("`arcade/common/credits.py`")
    st.markdown("---")

    st.markdown("**스크롤 크레딧 배너**")
    render_credits_scroll(theme_key=selected_theme)

    st.markdown("---")
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("**전체 크레딧 화면**")
        render_credits_screen(theme_key=selected_theme)
    with col_r:
        st.markdown("**게임별 뱃지**")
        for g in ["galaga","tetris","pacman","space_invaders"]:
            render_credits_badge(g, theme_key=selected_theme)
            st.markdown("")

        st.markdown("---")
        st.markdown("**푸터 (갤러그)**")
        render_credits_footer("galaga", theme_key=selected_theme)

    st.markdown("---")
    st.markdown("**코드 예시**")
    st.code("""
from common.credits import (
    render_credits_footer, render_credits_scroll, render_credits_screen
)

# 게임 하단 저작권 푸터
render_credits_footer("galaga")

# 허브 메인의 스크롤 배너
render_credits_scroll()

# 독립 크레딧 화면
render_credits_screen()
""", language="python")

# ═══════════════════════════════════════════════════════════════
# Tab 7 — THEME
# ═══════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("#### 🎨 THEME — 공통 테마 팔레트")
    st.markdown("`arcade/common/theme.py`")
    st.markdown("---")

    for tk, tv in THEMES.items():
        with st.expander(f"**{tv['name']}** (`{tk}`)"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**컬러 팔레트**")
                for key, val in tv.items():
                    if isinstance(val, str) and val.startswith("#"):
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:8px;'
                            f'margin:3px 0;font-family:monospace;font-size:0.8rem;">'
                            f'<div style="width:20px;height:20px;background:{val};'
                            f'border-radius:3px;border:1px solid #333;"></div>'
                            f'<span style="color:#888;">{key}:</span> '
                            f'<span style="color:#ccc;">{val}</span></div>',
                            unsafe_allow_html=True,
                        )
            with col2:
                st.markdown("**사용법**")
                st.code(f"""
from common.theme import apply_theme, THEMES

# 테마 적용
apply_theme("{tk}")

# 팔레트 직접 접근
t = THEMES["{tk}"]
primary = t["primary"]   # {tv['primary']}
accent  = t["accent"]    # {tv['accent']}
""", language="python")
