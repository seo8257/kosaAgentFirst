"""
arcade/common/scoreboard.py
스코어보드 컴포넌트 (수정 버전)
"""
import streamlit as st
from datetime import datetime
from common.theme import THEMES

MAX_RANKING = 10
_RANK_KEY   = "sb_rankings"
_NICK_KEY   = "sb_nickname"

GAME_META = {
    "galaga":         {"icon": "🚀", "label": "갤러그"},
    "tetris":         {"icon": "🧱", "label": "테트리스"},
    "pacman":         {"icon": "😮", "label": "팩맨"},
    "space_invaders": {"icon": "👾", "label": "스페이스 인베이더"},
}


def _ensure_storage():
    if _RANK_KEY not in st.session_state:
        st.session_state[_RANK_KEY] = {g: [] for g in GAME_META}
    if _NICK_KEY not in st.session_state:
        st.session_state[_NICK_KEY] = "AAA"


def _get_rankings(game):
    _ensure_storage()
    return st.session_state[_RANK_KEY].get(game, [])


def _set_rankings(game, data):
    _ensure_storage()
    st.session_state[_RANK_KEY][game] = data


def save_score(game, score, nickname=None):
    if nickname is None:
        nickname = st.session_state.get(_NICK_KEY, "AAA")
    nickname = (nickname.upper().strip()[:3] or "AAA")
    entry = {
        "rank": 0,
        "nickname": nickname,
        "score": score,
        "date": datetime.now().strftime("%m/%d"),
    }
    rankings = _get_rankings(game)
    rankings.append(entry)
    rankings.sort(key=lambda x: x["score"], reverse=True)
    rankings = rankings[:MAX_RANKING]
    for i, r in enumerate(rankings):
        r["rank"] = i + 1
    _set_rankings(game, rankings)
    for r in rankings:
        if r["nickname"] == nickname and r["score"] == score:
            return r["rank"]
    return -1


def get_hi_score(game):
    rankings = _get_rankings(game)
    return rankings[0]["score"] if rankings else 0


def get_nickname():
    _ensure_storage()
    return st.session_state.get(_NICK_KEY, "AAA")


def set_nickname(nick):
    st.session_state[_NICK_KEY] = (nick.upper().strip()[:3] or "AAA")


def clear_rankings(game=None):
    _ensure_storage()
    if game:
        st.session_state[_RANK_KEY][game] = []
    else:
        st.session_state[_RANK_KEY] = {g: [] for g in GAME_META}


def render_score_panel(game, current_score=0, theme_key=None):
    tk = theme_key or game
    t  = THEMES.get(tk, THEMES["galaga"])
    hi = get_hi_score(game)
    st.markdown(f"""
<div style="background:{t['panel_bg']};border:1px solid {t['border']};
     border-radius:10px;padding:12px 14px;margin-bottom:10px;
     font-family:'Courier New',monospace;text-align:center;">
  <div style="font-size:0.7rem;color:{t['accent']};letter-spacing:0.15em;">SCORE</div>
  <div style="font-size:1.8rem;font-weight:bold;color:{t['text']};">{current_score:,}</div>
</div>
<div style="background:{t['panel_bg']};border:1px solid {t['border']};
     border-radius:10px;padding:12px 14px;margin-bottom:10px;
     font-family:'Courier New',monospace;text-align:center;">
  <div style="font-size:0.7rem;color:{t['accent']};letter-spacing:0.15em;">HI-SCORE</div>
  <div style="font-size:1.3rem;font-weight:bold;color:{t['accent']};">{hi:,}</div>
</div>
""", unsafe_allow_html=True)


def render_ranking_table(game, theme_key=None, highlight_score=None):
    tk   = theme_key or game
    t    = THEMES.get(tk, THEMES["galaga"])
    meta = GAME_META.get(game, {"icon": "🎮", "label": game})
    rankings = _get_rankings(game)

    rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}
    rows_html  = ""

    if not rankings:
        rows_html = f'<tr><td colspan="4" style="text-align:center;color:{t["sub_text"]};padding:16px;">── 기록 없음 ──</td></tr>'
    else:
        for r in rankings:
            is_me   = highlight_score is not None and r["score"] == highlight_score
            rank_n  = r["rank"]
            icon    = rank_icons.get(rank_n, f"{rank_n}.")
            r_color = {1:"#FFE600", 2:"#C0C0C0", 3:"#CD7F32"}.get(rank_n, t["sub_text"])
            me_bold = "font-weight:bold;" if is_me else ""
            me_col  = f"color:{t['accent']};" if is_me else ""
            rows_html += f"""
<tr style="border-bottom:0.5px solid {t['border']};">
  <td style="padding:5px 8px;color:{r_color};font-weight:bold;">{icon}</td>
  <td style="padding:5px 8px;{me_bold}{me_col}">{r['nickname']}</td>
  <td style="padding:5px 8px;text-align:right;{me_bold}{me_col}">{r['score']:,}</td>
  <td style="padding:5px 8px;font-size:0.7rem;color:{t['sub_text']};">{r['date']}</td>
</tr>"""

    st.markdown(f"""
<div style="font-family:'Courier New',monospace;font-size:0.75rem;
     color:{t['sub_text']};letter-spacing:0.12em;margin-bottom:6px;">
  {meta['icon']} {meta['label'].upper()} · TOP {MAX_RANKING}
</div>
<table style="width:100%;border-collapse:collapse;font-family:'Courier New',monospace;font-size:0.82rem;">
  <thead>
    <tr style="border-bottom:1px solid {t['border']};">
      <th style="padding:5px 8px;text-align:left;color:{t['sub_text']};font-size:0.68rem;font-weight:500;">RANK</th>
      <th style="padding:5px 8px;text-align:left;color:{t['sub_text']};font-size:0.68rem;font-weight:500;">NAME</th>
      <th style="padding:5px 8px;text-align:right;color:{t['sub_text']};font-size:0.68rem;font-weight:500;">SCORE</th>
      <th style="padding:5px 8px;color:{t['sub_text']};font-size:0.68rem;font-weight:500;">DATE</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
""", unsafe_allow_html=True)


def render_nickname_entry(game, score, theme_key=None):
    tk = theme_key or game
    t  = THEMES.get(tk, THEMES["galaga"])
    hi = get_hi_score(game)
    is_new = score > hi

    if is_new:
        st.markdown(
            f'<div style="text-align:center;font-family:monospace;font-size:1rem;'
            f'color:#FFE600;animation:arcade-blink .7s step-end infinite;margin-bottom:8px;">'
            f'✨ NEW RECORD! ✨</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div style="text-align:center;font-family:monospace;font-size:1.8rem;'
        f'font-weight:bold;color:{t["accent"]};margin:8px 0;">{score:,}</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        nick = st.text_input("닉네임 (영문 3자)", value=get_nickname(),
                             max_chars=3, key=f"nick_input_{game}",
                             placeholder="AAA").upper().strip() or "AAA"
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ 등록", key=f"nick_submit_{game}"):
            set_nickname(nick)
            rank = save_score(game, score, nick)
            st.success(f"🏆 {rank}위 등록! ({nick})")
            return True
    return False


def render_all_rankings(theme_key="hub"):
    t = THEMES.get(theme_key, THEMES["hub"])
    st.markdown(
        f'<div style="font-family:monospace;font-size:1.1rem;font-weight:bold;'
        f'color:{t["accent"]};letter-spacing:0.15em;margin-bottom:14px;">'
        f'🏆 HALL OF FAME — 명예의 전당</div>',
        unsafe_allow_html=True,
    )
    tabs = st.tabs([f"{GAME_META[g]['icon']} {GAME_META[g]['label']}" for g in GAME_META])
    for tab, game in zip(tabs, GAME_META):
        with tab:
            render_ranking_table(game, theme_key=theme_key)
            if st.button("🗑️ 초기화", key=f"clear_{game}_{theme_key}"):
                clear_rankings(game)
                st.rerun()
