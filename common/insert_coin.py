"""
arcade/common/insert_coin.py
INSERT COIN 컴포넌트 (화면 깨짐 수정 버전)
"""
import streamlit as st
from common.theme import THEMES

_PREVIEW_CONFIGS = {
    "galaga": {
        "rows": [
            ("👾 🐝 👾 🐝 👾", "#AFA9EC", "1.5rem"),
            ("🦋 🦋 🦋 🦋 🦋", "#534AB7", "1.3rem"),
            ("🦟 🦟 🦟 🦟 🦟", "#3C3489", "1.2rem"),
        ],
        "player": ("🚀", "#5DCAA5"),
        "title":  "GALAGA 갤러그",
        "credit": "NAMCO · 1981",
    },
    "tetris": {
        "rows": [
            ("🟦🟦🟦🟦", "#00f5ff", "1.5rem"),
            ("🟨🟨 🟨🟨", "#ffe600", "1.4rem"),
            ("🟪🟪🟪", "#bf00ff", "1.4rem"),
        ],
        "player": ("⬇", "#5DCAA5"),
        "title":  "TETRIS 테트리스",
        "credit": "ALEXEY PAJITNOV · 1984",
    },
    "pacman": {
        "rows": [
            ("· · · · · · · ·", "#ffff99", "1.3rem"),
            ("😮 · · 👻 · · 👻", "#FFE600", "1.4rem"),
            ("· · · · · · · ·", "#ffff99", "1.3rem"),
        ],
        "player": ("😮", "#FFE600"),
        "title":  "PAC-MAN 팩맨",
        "credit": "NAMCO · 1980",
    },
    "space_invaders": {
        "rows": [
            ("🛸 🛸 🛸 🛸 🛸", "#FF4444", "1.4rem"),
            ("👾 👾 👾 👾 👾", "#F0997B", "1.4rem"),
            ("🐛 🐛 🐛 🐛 🐛", "#FFE600", "1.3rem"),
        ],
        "player": ("🚀", "#33ff33"),
        "title":  "SPACE INVADERS",
        "credit": "TAITO · 1978",
    },
}

_CREDIT_KEY = "arcade_credits"


def get_credits():
    return st.session_state.get(_CREDIT_KEY, 0)


def add_credit(n=1):
    st.session_state[_CREDIT_KEY] = get_credits() + n


def use_credit():
    if get_credits() > 0:
        st.session_state[_CREDIT_KEY] -= 1
        return True
    return False


def reset_credits():
    st.session_state[_CREDIT_KEY] = 0


def credit_display():
    credits = get_credits()
    st.markdown(
        f'<div style="font-family:monospace;font-size:0.8rem;color:#888;">'
        f'CREDIT: <b style="color:#FFE600;">{credits:02d}</b></div>',
        unsafe_allow_html=True,
    )


def render_coin_screen(theme_key="galaga", show_credits=True, free_play=False):
    """
    INSERT COIN 버튼만 렌더링 (프리뷰는 각 게임 타이틀에서 직접 그림).
    Returns True if start button was pressed.
    """
    t   = THEMES.get(theme_key, THEMES["galaga"])
    cfg = _PREVIEW_CONFIGS.get(theme_key, _PREVIEW_CONFIGS["galaga"])

    if show_credits and not free_play:
        credits = get_credits()
        st.markdown(
            f'<div style="text-align:center;font-family:monospace;font-size:0.82rem;'
            f'color:{t["sub_text"]};margin-bottom:6px;">CREDIT {credits:02d}</div>',
            unsafe_allow_html=True,
        )

    btn_label = f"🪙  INSERT COIN  —  {cfg['title']}"
    pressed = st.button(btn_label, key=f"coin_start_{theme_key}", use_container_width=True)

    if pressed:
        if free_play or use_credit():
            return True
        else:
            st.warning("크레딧이 없습니다! 코인을 충전하세요.")

    if show_credits and not free_play:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🪙 +1 CREDIT", key=f"coin_add1_{theme_key}"):
                add_credit(1)
                st.rerun()
        with c2:
            if st.button("🪙🪙 +3 CREDITS", key=f"coin_add3_{theme_key}"):
                add_credit(3)
                st.rerun()

    return False


def coin_button(theme_key="galaga", label="▶  START GAME", key_suffix=""):
    return st.button(f"🪙  {label}", key=f"coin_btn_{theme_key}_{key_suffix}",
                     use_container_width=True)
