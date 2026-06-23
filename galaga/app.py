"""
갤러그 (Galaga) - Streamlit 웹 게임
폴더: arcade/galaga/
실행: streamlit run app.py --server.port 8501
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import random, time

from common.theme       import apply_theme, get_game_css
from common.insert_coin import render_coin_screen
from common.scoreboard  import render_ranking_table, render_nickname_entry, save_score, get_hi_score
from common.bgm         import render_bgm_toggle, play_sfx, init_audio
from common.fullscreen  import render_fullscreen_btn, render_fullscreen_wrapper
from common.key_guide   import render_key_guide, render_key_badge_row
from common.credits     import render_credits_footer

GAME = "galaga"

st.set_page_config(page_title="🚀 갤러그", page_icon="🚀",
                   layout="wide", initial_sidebar_state="expanded")

apply_theme(GAME)
st.markdown(get_game_css(GAME), unsafe_allow_html=True)

st.markdown("""
<style>
.g-row  { display:flex; justify-content:center; gap:5px; margin:2px 0; }
.g-cell { width:36px; height:36px; display:flex; align-items:center;
          justify-content:center; font-size:1.25rem; border-radius:4px; }
.g-enemy  { background:rgba(83,74,183,.15); border:1px solid #534AB7; }
.g-empty  { background:transparent; border:1px solid #0d0d22; }
.g-player { background:rgba(93,202,165,.15); border:1px solid #5DCAA5; }
.g-bullet { color:#AFA9EC; border:none; background:transparent; }
.g-ebullet{ color:#F0997B; border:none; background:transparent; }
.g-hit    { background:rgba(240,153,123,.3); border:1px solid #F0997B; }
.g-area   { background:#000010; border:2px solid #534AB7; border-radius:12px;
            padding:12px; font-family:'Courier New',monospace; }
.g-score  { background:#0a0a1e; border:1px solid #534AB7; border-radius:8px;
            padding:10px; text-align:center; font-family:'Courier New',monospace; }
.g-snum   { font-size:1.8rem; font-weight:bold; color:#AFA9EC; }
.g-slbl   { font-size:.72rem; color:#6B6880; letter-spacing:.12em; }
.g-title  { font-family:'Courier New',monospace; font-size:1.8rem; font-weight:bold;
            color:#AFA9EC; text-align:center; letter-spacing:.2em;
            text-shadow:0 0 20px #534AB7; }
.g-blink  { animation:g-blink 1s step-end infinite; }
@keyframes g-blink { 50%{ opacity:0; } }
</style>
""", unsafe_allow_html=True)

# ── 상수 ──────────────────────────────────────────────────────────
COLS = 11; ROWS = 14
ENEMY_ROWS = 4; ENEMY_COLS = 10; ENEMY_START_ROW = 1
ENEMY_TYPES = {0: ("👾", 80), 1: ("🐝", 50), 2: ("🦋", 30), 3: ("🦟", 10)}


def init_state():
    defs = dict(
        g_state="title", score=0, lives=3, stage=1,
        player_col=COLS // 2, bullets=[], enemy_bullets=[],
        enemies={}, tick=0, hit_cells=[],
        nick_done=False, last_score=0,
    )
    for k, v in defs.items():
        st.session_state.setdefault(k, v)


def make_enemies():
    e = {}
    for r in range(ENEMY_ROWS):
        for c in range(ENEMY_COLS):
            e[f"{ENEMY_START_ROW+r},{(COLS-ENEMY_COLS)//2+c}"] = min(r, 3)
    return e


def get_enemies_dict():
    """문자열 키 dict → (r,c): type dict"""
    result = {}
    for k, v in st.session_state.enemies.items():
        r, c = map(int, k.split(","))
        result[(r, c)] = v
    return result


def set_enemies_dict(d):
    """(r,c): type dict → 문자열 키 dict"""
    st.session_state.enemies = {f"{r},{c}": t for (r, c), t in d.items()}


def move_enemies():
    tick = st.session_state.tick
    stage = st.session_state.stage
    inv = max(3, 8 - stage)
    if tick % inv != 0:
        return
    d = 1 if (tick // inv) % 20 < 10 else -1
    em = get_enemies_dict()
    ne = {}
    for (r, c), t in em.items():
        nc = max(0, min(COLS - 1, c + d))
        ne[(r, nc)] = t
    if tick % (inv * 20) == 0 and tick > 0:
        ne = {(r + 1, c): t for (r, c), t in ne.items()}
    set_enemies_dict(ne)


def enemy_shoot():
    em = get_enemies_dict()
    if not em or random.random() > 0.15:
        return
    (r, c) = random.choice(list(em.keys()))
    st.session_state.enemy_bullets.append([r + 1, c])


def move_bullets():
    em = get_enemies_dict()
    nb = []; hit_cells = []
    for bullet in st.session_state.bullets:
        r, c = bullet
        nr = r - 1
        if nr < 0:
            continue
        if (nr, c) in em:
            _, pts = ENEMY_TYPES[em.pop((nr, c))]
            st.session_state.score += pts
            hit_cells.append([nr, c])
            play_sfx("explosion")
        else:
            nb.append([nr, c])
    st.session_state.bullets = nb
    st.session_state.hit_cells = hit_cells
    set_enemies_dict(em)


def move_enemy_bullets():
    pr = ROWS - 1; pc = st.session_state.player_col
    nb = []; hit = False
    for bullet in st.session_state.enemy_bullets:
        r, c = bullet
        nr = r + 1
        if nr >= ROWS:
            continue
        if nr == pr and c == pc:
            hit = True
        else:
            nb.append([nr, c])
    st.session_state.enemy_bullets = nb
    if hit:
        play_sfx("explosion")
        st.session_state.lives -= 1
        if st.session_state.lives <= 0:
            st.session_state.last_score = st.session_state.score
            st.session_state.g_state = "gameover"


def check_invasion():
    em = get_enemies_dict()
    if any(r >= ROWS - 1 for r, _ in em):
        st.session_state.last_score = st.session_state.score
        st.session_state.g_state = "gameover"


def render_grid():
    pr = ROWS - 1; pc = st.session_state.player_col
    em = get_enemies_dict()
    bullets  = {(r, c) for r, c in st.session_state.bullets}
    ebullets = {(r, c) for r, c in st.session_state.enemy_bullets}
    hit_set  = {(r, c) for r, c in st.session_state.hit_cells}
    rows = []
    for r in range(ROWS):
        cells = []
        for c in range(COLS):
            if r == pr and c == pc:
                cells.append('<div class="g-cell g-player">🚀</div>')
            elif (r, c) in hit_set:
                cells.append('<div class="g-cell g-hit">💥</div>')
            elif (r, c) in em:
                emoji, _ = ENEMY_TYPES[em[(r, c)]]
                cells.append(f'<div class="g-cell g-enemy">{emoji}</div>')
            elif (r, c) in bullets:
                cells.append('<div class="g-cell g-bullet">|</div>')
            elif (r, c) in ebullets:
                cells.append('<div class="g-cell g-ebullet">▼</div>')
            else:
                cells.append('<div class="g-cell g-empty"></div>')
        rows.append(f'<div class="g-row">{"".join(cells)}</div>')
    return "\n".join(rows)


def sidebar():
    with st.sidebar:
        st.markdown('<div style="font-family:monospace;font-size:1rem;color:#AFA9EC;'
                    'letter-spacing:.15em;margin-bottom:10px;">🚀 GALAGA</div>',
                    unsafe_allow_html=True)
        render_bgm_toggle(GAME, compact=True)
        st.markdown("---")
        render_key_guide(GAME, show_tips=True, show_common=False)
        st.markdown("---")
        render_ranking_table(GAME, highlight_score=st.session_state.get("last_score") or None)
        st.markdown("---")
        render_fullscreen_btn(GAME, target_id="galaga-board")


# ── 메인 ──────────────────────────────────────────────────────────
init_state()
sidebar()

# ── TITLE ─────────────────────────────────────────────────────────
if st.session_state.g_state == "title":
    st.markdown('<div class="g-title">🚀 GALAGA 갤러그</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#6B6880;font-family:monospace;'
                'letter-spacing:.1em;margin-bottom:16px;">NAMCO · 1981 · RETRO ARCADE</p>',
                unsafe_allow_html=True)
    st.markdown("---")

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
<div class="g-area" style="min-height:240px;display:flex;flex-direction:column;
     align-items:center;justify-content:center;">
  <div style="font-size:2.5rem;text-align:center;line-height:2.2;">
    👾 🐝 👾 🐝 👾<br>🦋 🦋 🦋 🦋 🦋<br>🦟 🦟 🦟 🦟 🦟
  </div>
  <div class="g-blink" style="font-family:monospace;color:#AFA9EC;
       font-size:0.95rem;margin-top:14px;letter-spacing:.2em;">
    ── INSERT COIN ──
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown("")
        if render_coin_screen(GAME, show_credits=False, free_play=True):
            play_sfx("coin")
            init_audio(GAME)
            st.session_state.update(
                g_state="playing", score=0, lives=3, stage=1,
                player_col=COLS // 2, bullets=[], enemy_bullets=[],
                enemies=make_enemies(), tick=0, hit_cells=[], nick_done=False,
            )
            st.rerun()

    st.markdown("---")
    render_key_badge_row(GAME)
    render_credits_footer(GAME)

# ── PLAYING ───────────────────────────────────────────────────────
elif st.session_state.g_state == "playing":
    st.session_state.tick += 1
    st.session_state.hit_cells = []
    move_enemies()
    enemy_shoot()
    move_bullets()
    move_enemy_bullets()
    check_invasion()

    # 스테이지 클리어
    if not st.session_state.enemies and st.session_state.g_state == "playing":
        st.session_state.stage += 1
        st.session_state.enemies = make_enemies()
        st.session_state.bullets = []
        st.session_state.enemy_bullets = []
        st.session_state.score += 500
        play_sfx("clear")

    # 헤더
    hc1, hc2, hc3 = st.columns([1, 3, 1])
    with hc1:
        st.markdown(f'<div class="g-score"><div class="g-slbl">SCORE</div>'
                    f'<div class="g-snum">{st.session_state.score:06d}</div></div>',
                    unsafe_allow_html=True)
    with hc2:
        st.markdown(f'<div class="g-title" style="font-size:1.2rem;">'
                    f'🚀 GALAGA · STAGE {st.session_state.stage}</div>',
                    unsafe_allow_html=True)
    with hc3:
        hi = max(st.session_state.score, get_hi_score(GAME))
        st.markdown(f'<div class="g-score"><div class="g-slbl">HI-SCORE</div>'
                    f'<div class="g-snum">{hi:06d}</div></div>',
                    unsafe_allow_html=True)

    lives_str = "🚀 " * max(0, st.session_state.lives)
    st.markdown(f'<div style="display:flex;gap:5px;justify-content:center;'
                f'margin:5px 0;">{lives_str}</div>', unsafe_allow_html=True)

    board_html = f'<div class="g-area">{render_grid()}</div>'
    render_fullscreen_wrapper(board_html, GAME, "galaga-board")

    st.markdown("")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("◀◀ 왼쪽", key="g_ll"):
            st.session_state.player_col = max(0, st.session_state.player_col - 2)
    with c2:
        if st.button("◀ LEFT", key="g_l"):
            st.session_state.player_col = max(0, st.session_state.player_col - 1)
    with c3:
        if st.button("🔴 FIRE!", key="g_fire"):
            st.session_state.bullets.append([ROWS - 2, st.session_state.player_col])
            play_sfx("shoot")
    with c4:
        if st.button("RIGHT ▶", key="g_r"):
            st.session_state.player_col = min(COLS - 1, st.session_state.player_col + 1)
    with c5:
        if st.button("오른쪽 ▶▶", key="g_rr"):
            st.session_state.player_col = min(COLS - 1, st.session_state.player_col + 2)

    ic, qc = st.columns([4, 1])
    with ic:
        em_count = len(st.session_state.enemies)
        st.caption(f"남은 적: {em_count}마리 | "
                   f"총알: {len(st.session_state.bullets)}발 | "
                   f"Tick: {st.session_state.tick}")
    with qc:
        if st.button("⏹ 종료", key="g_quit"):
            save_score(GAME, st.session_state.score)
            st.session_state.last_score = st.session_state.score
            st.session_state.g_state = "title"
            st.rerun()

    time.sleep(0.5)
    st.rerun()

# ── GAMEOVER ──────────────────────────────────────────────────────
elif st.session_state.g_state == "gameover":
    play_sfx("gameover")
    st.markdown('<div class="g-title">💀 GAME OVER 💀</div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if not st.session_state.nick_done:
            if render_nickname_entry(GAME, st.session_state.last_score):
                st.session_state.nick_done = True
                st.rerun()
        else:
            render_ranking_table(GAME, highlight_score=st.session_state.last_score)

        st.markdown("")
        if st.button("🔄 다시 도전", key="g_retry"):
            st.session_state.update(
                g_state="playing", score=0, lives=3, stage=1,
                player_col=COLS // 2, bullets=[], enemy_bullets=[],
                enemies=make_enemies(), tick=0, hit_cells=[], nick_done=False,
            )
            st.rerun()
        if st.button("🏠 타이틀로", key="g_title"):
            st.session_state.g_state = "title"
            st.rerun()

    render_credits_footer(GAME)
