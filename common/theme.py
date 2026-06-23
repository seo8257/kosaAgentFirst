"""
arcade/common/theme.py
공통 테마 & CSS 팔레트
"""
import streamlit as st

THEMES = {
    "galaga": {
        "name":        "갤러그",
        "bg":          "#0a0a2e",
        "bg2":         "#000000",
        "primary":     "#534AB7",
        "accent":      "#AFA9EC",
        "accent_dark": "#3C3489",
        "text":        "#ffffff",
        "sub_text":    "#6B6880",
        "border":      "#534AB7",
        "panel_bg":    "#0a0a1e",
        "btn_bg":      "#534AB7",
        "btn_hover":   "#3C3489",
        "glow":        "rgba(83,74,183,0.4)",
    },
    "tetris": {
        "name":        "테트리스",
        "bg":          "#0d0d1a",
        "bg2":         "#050510",
        "primary":     "#0F6E56",
        "accent":      "#5DCAA5",
        "accent_dark": "#085041",
        "text":        "#ffffff",
        "sub_text":    "#4a7a6a",
        "border":      "#5DCAA5",
        "panel_bg":    "#0a0a1e",
        "btn_bg":      "#0F6E56",
        "btn_hover":   "#085041",
        "glow":        "rgba(93,202,165,0.35)",
    },
    "pacman": {
        "name":        "팩맨",
        "bg":          "#000020",
        "bg2":         "#000010",
        "primary":     "#854F0B",
        "accent":      "#FFE600",
        "accent_dark": "#b39800",
        "text":        "#ffffff",
        "sub_text":    "#6666aa",
        "border":      "#0000cc",
        "panel_bg":    "#00001a",
        "btn_bg":      "#000066",
        "btn_hover":   "#000099",
        "glow":        "rgba(255,230,0,0.25)",
    },
    "space_invaders": {
        "name":        "스페이스 인베이더",
        "bg":          "#000000",
        "bg2":         "#050505",
        "primary":     "#993C1D",
        "accent":      "#33ff33",
        "accent_dark": "#22aa22",
        "text":        "#33ff33",
        "sub_text":    "#226622",
        "border":      "#993C1D",
        "panel_bg":    "#050505",
        "btn_bg":      "#1a0000",
        "btn_hover":   "#330000",
        "glow":        "rgba(240,153,123,0.3)",
    },
    "hub": {
        "name":        "오락실 허브",
        "bg":          "#000000",
        "bg2":         "#080808",
        "primary":     "#534AB7",
        "accent":      "#ffffff",
        "accent_dark": "#aaaaaa",
        "text":        "#ffffff",
        "sub_text":    "#555555",
        "border":      "#222222",
        "panel_bg":    "#080808",
        "btn_bg":      "#1a1a1a",
        "btn_hover":   "#333333",
        "glow":        "rgba(255,255,255,0.1)",
    },
}


def get_base_css(theme_key="hub"):
    t = THEMES.get(theme_key, THEMES["hub"])
    return f"""
<style>
.stApp {{
    background: radial-gradient(ellipse at center, {t['bg']} 0%, {t['bg2']} 100%) !important;
    color: {t['text']} !important;
}}
.block-container {{ padding-top: 1rem !important; }}

.arcade-panel {{
    background: {t['panel_bg']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 12px;
    font-family: 'Courier New', monospace;
}}
.arcade-panel-label {{
    font-size: 0.7rem;
    color: {t['accent']};
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}}
.arcade-panel-value {{
    font-size: 1.8rem;
    font-weight: bold;
    color: {t['text']};
}}

.pixel-title {{
    font-family: 'Courier New', monospace;
    font-size: 2rem;
    font-weight: bold;
    color: {t['accent']};
    text-align: center;
    letter-spacing: 0.2em;
    text-shadow: 0 0 20px {t['glow']};
    margin-bottom: 4px;
}}
.pixel-sub {{
    font-size: 0.82rem;
    color: {t['sub_text']};
    text-align: center;
    font-family: 'Courier New', monospace;
    letter-spacing: 0.12em;
}}

.stButton > button {{
    background: {t['btn_bg']} !important;
    color: {t['accent']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 6px !important;
    font-family: 'Courier New', monospace !important;
    letter-spacing: 0.08em !important;
    width: 100%;
    transition: background 0.15s;
}}
.stButton > button:hover {{
    background: {t['btn_hover']} !important;
    border-color: {t['accent']} !important;
}}

.arcade-blink {{ animation: arcade-blink 1s step-end infinite; }}
@keyframes arcade-blink {{ 50% {{ opacity: 0; }} }}

.pixel-divider {{
    display: flex; gap: 3px;
    justify-content: center;
    margin: 12px 0;
}}
.pixel-dot {{
    width: 5px; height: 5px;
    border-radius: 1px;
    display: inline-block;
}}

.arcade-insert-coin {{
    text-align: center;
    font-family: 'Courier New', monospace;
    font-size: 0.95rem;
    letter-spacing: 0.2em;
    color: {t['accent']};
    animation: arcade-blink 1s step-end infinite;
    padding: 8px 0;
}}

.key-badge {{
    display: inline-block;
    background: {t['panel_bg']};
    border: 1px solid {t['border']};
    border-radius: 4px;
    padding: 1px 7px;
    color: {t['accent']};
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    margin: 0 2px;
}}
</style>
"""


def apply_theme(theme_key="hub"):
    st.markdown(get_base_css(theme_key), unsafe_allow_html=True)


def get_game_css(theme_key):
    t = THEMES.get(theme_key, THEMES["hub"])
    return f"""
<style>
.game-board-wrap {{
    display: inline-block;
    border: 2px solid {t['border']};
    border-radius: 10px;
    padding: 6px;
    background: {t['bg2']};
    box-shadow: 0 0 24px {t['glow']};
}}
.game-title-bar {{
    font-family: 'Courier New', monospace;
    font-size: 1.15rem;
    font-weight: bold;
    color: {t['accent']};
    letter-spacing: 0.15em;
    text-align: center;
    margin-bottom: 8px;
}}
</style>
"""
