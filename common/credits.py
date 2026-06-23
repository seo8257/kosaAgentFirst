"""
arcade/common/credits.py
크레딧 & 저작권 안내 컴포넌트 (수정 버전)
"""
import streamlit as st
from common.theme import THEMES

GAME_CREDITS = {
    "galaga": {
        "icon": "🚀", "title": "GALAGA", "title_kr": "갤러그",
        "developer": "NAMCO", "publisher": "MIDWAY (북미)", "year": "1981",
        "genre": "종스크롤 슈팅", "designer": "Kazunori Sawano",
        "trivia": [
            "전작 Galaxian(1979)의 후속작",
            "보스 갤러가의 트랙터 빔으로 전투기를 포획",
            "미국에서 2년간 가장 많이 팔린 아케이드 게임",
        ],
    },
    "tetris": {
        "icon": "🧱", "title": "TETRIS", "title_kr": "테트리스",
        "developer": "Alexey Pajitnov", "publisher": "Nintendo (게임보이)", "year": "1984",
        "genre": "낙하 퍼즐", "designer": "Alexey Pajitnov",
        "trivia": [
            "소련 컴퓨터 과학자 파지트노프가 개발",
            "게임보이 번들로 발매되어 게임보이 성공 견인",
            "'테트리스 효과' - 오래 하면 꿈에도 블록이 보임",
        ],
    },
    "pacman": {
        "icon": "😮", "title": "PAC-MAN", "title_kr": "팩맨",
        "developer": "NAMCO", "publisher": "MIDWAY (북미)", "year": "1980",
        "genre": "미로 액션", "designer": "Toru Iwatani",
        "trivia": [
            "이와타니 토루가 피자 조각에서 아이디어 얻음",
            "4마리 고스트: Blinky·Pinky·Inky·Clyde",
            "세계 최초 캐릭터 상품화 성공 게임",
        ],
    },
    "space_invaders": {
        "icon": "👾", "title": "SPACE INVADERS", "title_kr": "스페이스 인베이더",
        "developer": "TAITO", "publisher": "MIDWAY (북미)", "year": "1978",
        "genre": "고정 슈팅", "designer": "Tomohiro Nishikado",
        "trivia": [
            "일본에서 100엔 동전 부족 사태를 유발",
            "격추할수록 빨라지는 것은 CPU 성능 한계가 원인",
            "👾 이모지의 원형이 스페이스 인베이더",
        ],
    },
}

DEV_CREDITS = {
    "project": "추억의 오락실 — 4분할 웹 게임 컬렉션",
    "tech":    "Python 3 + Streamlit",
}


def render_credits_footer(game, theme_key=None):
    tk   = theme_key or game
    t    = THEMES.get(tk, THEMES["galaga"])
    info = GAME_CREDITS.get(game, GAME_CREDITS["galaga"])
    st.markdown(f"""
<div style="background:{t['bg2']};border-top:1px solid {t['border']};
     padding:8px 14px;font-family:'Courier New',monospace;font-size:0.7rem;
     color:{t['sub_text']};text-align:center;margin-top:10px;border-radius:0 0 8px 8px;">
  {info['icon']} <b style="color:{t['accent']};">{info['title']}</b>
  &nbsp;|&nbsp; © {info['year']} {info['developer']}
  &nbsp;|&nbsp; <span style="color:{t['accent']};">Python + Streamlit</span> 팬 재구현
  <div style="margin-top:3px;font-size:0.65rem;">
    오리지널 게임의 저작권은 해당 개발사에 있습니다.
  </div>
</div>
""", unsafe_allow_html=True)


def render_credits_badge(game, theme_key=None):
    tk   = theme_key or game
    t    = THEMES.get(tk, THEMES["galaga"])
    info = GAME_CREDITS.get(game, GAME_CREDITS["galaga"])
    st.markdown(f"""
<div style="display:inline-flex;align-items:center;gap:6px;
     background:{t['panel_bg']};border:1px solid {t['border']};
     border-radius:6px;padding:4px 10px;font-family:'Courier New',monospace;
     font-size:0.72rem;color:{t['sub_text']};">
  <span>{info['icon']}</span>
  <span>© {info['year']} {info['developer']} | 팬 재구현</span>
</div>
""", unsafe_allow_html=True)


def render_credits_scroll(theme_key="hub"):
    t = THEMES.get(theme_key, THEMES["hub"])
    parts = [f"{v['icon']} {v['title']} © {v['year']} {v['developer']}"
             for v in GAME_CREDITS.values()]
    scroll_text = "  ✦  ".join(parts) + "  ✦  " + "  ✦  ".join(parts)
    st.markdown(f"""
<div style="overflow:hidden;height:50px;position:relative;
     background:{t['bg2']};border-radius:6px;border:1px solid {t['border']};margin:8px 0;">
  <div style="position:absolute;white-space:nowrap;
       animation:arcadeScroll 20s linear infinite;
       font-size:0.8rem;color:{t['accent']};font-family:'Courier New',monospace;
       letter-spacing:0.12em;top:50%;transform:translateY(-50%);padding-left:100%;">
    {scroll_text}
  </div>
</div>
<style>
@keyframes arcadeScroll {{
  from {{ transform:translateX(0) translateY(-50%); }}
  to   {{ transform:translateX(-50%) translateY(-50%); }}
}}
</style>
""", unsafe_allow_html=True)


def render_credits_screen(theme_key="hub"):
    t = THEMES.get(theme_key, THEMES["hub"])
    st.markdown(f"""
<div style="font-family:'Courier New',monospace;font-size:1.1rem;
     font-weight:bold;color:{t['accent']};letter-spacing:0.15em;margin-bottom:14px;">
  🕹️ GAME CREDITS
</div>
""", unsafe_allow_html=True)

    for game, info in GAME_CREDITS.items():
        game_t  = THEMES.get(game, t)
        accent  = game_t["accent"]
        border  = game_t["border"]
        trivia  = "".join(f'<div style="font-size:0.72rem;color:{t["sub_text"]};padding:1px 0;">▸ {tr}</div>' for tr in info["trivia"])
        st.markdown(f"""
<div style="margin-bottom:14px;padding:12px 14px;background:{t['panel_bg']};
     border:1px solid {border};border-radius:8px;">
  <div style="font-size:0.95rem;font-weight:bold;color:{accent};margin-bottom:7px;letter-spacing:0.1em;">
    {info['icon']} {info['title']} — {info['title_kr']}
  </div>
  <div style="display:flex;justify-content:space-between;font-size:0.75rem;padding:2px 0;">
    <span style="color:{t['sub_text']};">개발사</span><span style="color:{t['text']};">{info['developer']}</span>
  </div>
  <div style="display:flex;justify-content:space-between;font-size:0.75rem;padding:2px 0;">
    <span style="color:{t['sub_text']};">출시연도</span><span style="color:{t['text']};">{info['year']}</span>
  </div>
  <div style="display:flex;justify-content:space-between;font-size:0.75rem;padding:2px 0;">
    <span style="color:{t['sub_text']};">장르</span><span style="color:{t['text']};">{info['genre']}</span>
  </div>
  <div style="margin-top:7px;padding-top:5px;border-top:1px solid {t['bg']};">{trivia}</div>
</div>
""", unsafe_allow_html=True)


def get_game_info(game):
    return GAME_CREDITS.get(game, {})
