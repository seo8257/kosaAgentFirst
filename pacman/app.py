"""
팩맨 (Pac-Man) - Streamlit 웹 게임
폴더: arcade/pacman/
실행: streamlit run app.py --server.port 8503
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import random, time, copy

from common.theme       import apply_theme, get_game_css
from common.insert_coin import render_coin_screen
from common.scoreboard  import render_ranking_table, render_nickname_entry, save_score, get_hi_score
from common.bgm         import render_bgm_toggle, play_sfx, init_audio
from common.fullscreen  import render_fullscreen_btn, render_fullscreen_wrapper
from common.key_guide   import render_key_guide, render_key_badge_row
from common.credits     import render_credits_footer

GAME = "pacman"

st.set_page_config(page_title="🟡 팩맨", page_icon="🟡",
                   layout="wide", initial_sidebar_state="expanded")

apply_theme(GAME)
st.markdown(get_game_css(GAME), unsafe_allow_html=True)

st.markdown("""
<style>
.pm-wrap { display:inline-block; border:2px solid #0000cc; border-radius:4px;
           background:#000010; font-family:monospace; line-height:1; }
.pm-row  { display:flex; }
.pm-c    { width:22px; height:22px; display:flex; align-items:center;
           justify-content:center; font-size:.68rem; box-sizing:border-box; }
.pm-wall   { background:#0000cc; border-radius:2px; }
.pm-empty  { background:#000010; }
.pm-dot    { background:#000010; color:#ffff99; }
.pm-power  { background:#000010; color:#fff; font-size:.9rem; }
.pm-pac    { background:#000010; color:#FFE600; font-size:.95rem; }
.pm-ghost  { background:#000010; font-size:.9rem; }
.pm-scared { background:#000010; color:#2121DE; font-size:.9rem; }
.pm-fruit  { background:#000010; font-size:.9rem; }
.pm-panel  { background:#00001a; border:1px solid #0000cc; border-radius:8px;
             padding:10px 12px; margin-bottom:8px;
             font-family:'Courier New',monospace; text-align:center; }
.pm-slbl   { font-size:.7rem; color:#6666cc; letter-spacing:.15em; }
.pm-sval   { font-size:1.7rem; font-weight:bold; color:#FFE600; }
.pm-title  { font-family:'Courier New',monospace; font-size:1.7rem; font-weight:bold;
             color:#FFE600; text-align:center; letter-spacing:.2em;
             text-shadow:0 0 20px #FFE600; }
.pm-blink  { animation:pm-blink .8s step-end infinite; }
@keyframes pm-blink { 50%{ opacity:0; } }
</style>
""", unsafe_allow_html=True)

# ── 미로 (22×19) ──────────────────────────────────────────────────
MAZE_T = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
    [1,3,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,3,1],
    [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,0,1,0,1,1,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,1,1,4,1,1,0,1,2,1,1,1,1],
    [0,0,0,0,2,0,0,1,0,0,0,1,0,0,2,0,0,0,0],
    [1,1,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,0,0,0,0,0,0,1,2,1,1,1,1],
    [1,1,1,1,2,1,0,1,1,1,1,1,0,1,2,1,1,1,1],
    [1,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,1],
    [1,2,1,1,2,1,1,1,2,1,2,1,1,1,2,1,1,2,1],
    [1,3,2,1,2,2,2,2,2,2,2,2,2,2,2,1,2,3,1],
    [1,1,2,1,2,1,2,1,1,1,1,1,2,1,2,1,2,1,1],
    [1,2,2,2,2,1,2,2,2,1,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,1,1,1,1,2,1,2,1,1,1,1,1,1,2,1],
    [1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
MH = len(MAZE_T); MW = len(MAZE_T[0])
GHOST_COLORS = ["#FF4444", "#FFB8FF", "#00FFFF", "#FFB852"]
FRUITS = ["🍒", "🍓", "🍊", "🍋", "🍎", "🍇"]
DIRS = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}


def make_maze():
    return copy.deepcopy(MAZE_T)


def count_dots(maze):
    return sum(1 for row in maze for c in row if c in (2, 3))


def walkable(maze, r, c):
    if r == 10 and (c < 0 or c >= MW):
        return True
    if r < 0 or r >= MH or c < 0 or c >= MW:
        return False
    return maze[r][c] != 1


def wrap_pos(r, c):
    if c < 0: c = MW - 1
    elif c >= MW: c = 0
    return r, c


def ghost_move(maze, ghost, pac, scared):
    r, c = ghost["pos"]
    dirs = list(DIRS.values())
    random.shuffle(dirs)
    if scared:
        for dr, dc in dirs:
            nr, nc = wrap_pos(r + dr, c + dc)
            if walkable(maze, nr, nc):
                ghost["pos"] = [nr, nc]
                return
    else:
        pr, pc = pac
        best = None; best_d = float("inf")
        for dr, dc in dirs:
            nr, nc = wrap_pos(r + dr, c + dc)
            if walkable(maze, nr, nc):
                d = abs(pr - nr) + abs(pc - nc)
                if d < best_d:
                    best_d = d; best = [nr, nc]
        if best:
            ghost["pos"] = best


def init_state():
    maze = make_maze()
    defs = dict(
        pm_state="title", maze=maze,
        pac_pos=[16, 9], pac_dir="LEFT",
        ghosts=[{"pos": [9, 8 + i % 2], "color": GHOST_COLORS[i]} for i in range(4)],
        scared_ticks=0, score=0, lives=3, level=1, tick=0,
        fruit_pos=None, fruit_emoji="🍒", fruit_ticks=0,
        dots_left=count_dots(maze), eaten_ghosts=0,
        nick_done=False, last_score=0,
    )
    for k, v in defs.items():
        st.session_state.setdefault(k, v)


def start_game():
    maze = make_maze()
    st.session_state.update(
        maze=maze, pac_pos=[16, 9], pac_dir="LEFT",
        ghosts=[{"pos": [9, 8 + i % 2], "color": GHOST_COLORS[i]} for i in range(4)],
        scared_ticks=0, score=0, lives=3, level=1, tick=0,
        fruit_pos=None, fruit_emoji=FRUITS[0], fruit_ticks=0,
        dots_left=count_dots(maze), eaten_ghosts=0,
        nick_done=False, pm_state="playing",
    )


def game_step():
    st.session_state.tick += 1
    tick = st.session_state.tick
    maze = st.session_state.maze
    pr, pc = st.session_state.pac_pos
    dr, dc = DIRS[st.session_state.pac_dir]
    scared = st.session_state.scared_ticks > 0

    # 팩맨 이동
    nr, nc = wrap_pos(pr + dr, pc + dc)
    if walkable(maze, nr, nc):
        pr, pc = nr, nc
    st.session_state.pac_pos = [pr, pc]

    # 점 먹기
    cell = maze[pr][pc]
    if cell == 2:
        maze[pr][pc] = 0
        st.session_state.score += 10
        st.session_state.dots_left -= 1
        play_sfx("eat_dot")
    elif cell == 3:
        maze[pr][pc] = 0
        st.session_state.score += 50
        st.session_state.dots_left -= 1
        st.session_state.scared_ticks = 30
        st.session_state.eaten_ghosts = 0
        play_sfx("powerup")

    fp = st.session_state.fruit_pos
    if fp and fp[0] == pr and fp[1] == pc:
        st.session_state.score += 200
        st.session_state.fruit_pos = None
        play_sfx("clear")

    # 과일 생성
    if st.session_state.dots_left < 30 and not st.session_state.fruit_pos and tick % 40 == 0:
        st.session_state.fruit_pos = [9, 9]
        idx = min(st.session_state.level - 1, len(FRUITS) - 1)
        st.session_state.fruit_emoji = FRUITS[idx]
        st.session_state.fruit_ticks = 20

    if st.session_state.fruit_ticks > 0:
        st.session_state.fruit_ticks -= 1
        if st.session_state.fruit_ticks == 0:
            st.session_state.fruit_pos = None

    if scared:
        st.session_state.scared_ticks -= 1

    # 고스트 이동 (2틱마다)
    if tick % 2 == 0:
        for g in st.session_state.ghosts:
            ghost_move(maze, g, [pr, pc], st.session_state.scared_ticks > 0)

    # 충돌
    for g in st.session_state.ghosts:
        gr, gc = g["pos"]
        if gr == pr and gc == pc:
            if st.session_state.scared_ticks > 0:
                st.session_state.eaten_ghosts += 1
                pts = 200 * (2 ** (st.session_state.eaten_ghosts - 1))
                st.session_state.score += pts
                g["pos"] = [9, 9]
                play_sfx("eat_ghost")
            else:
                st.session_state.lives -= 1
                play_sfx("explosion")
                if st.session_state.lives <= 0:
                    st.session_state.last_score = st.session_state.score
                    st.session_state.pm_state = "gameover"
                    return
                st.session_state.pac_pos = [16, 9]
                st.session_state.pac_dir = "LEFT"
                for i, g2 in enumerate(st.session_state.ghosts):
                    g2["pos"] = [9, 8 + i % 2]
                return

    # 스테이지 클리어
    if st.session_state.dots_left <= 0:
        st.session_state.level += 1
        maze2 = make_maze()
        st.session_state.maze = maze2
        st.session_state.dots_left = count_dots(maze2)
        st.session_state.pac_pos = [16, 9]
        st.session_state.pac_dir = "LEFT"
        st.session_state.scared_ticks = 0
        st.session_state.score += 1000
        for i, g in enumerate(st.session_state.ghosts):
            g["pos"] = [9, 8 + i % 2]
        play_sfx("clear")


def render_maze():
    maze = st.session_state.maze
    pp = st.session_state.pac_pos
    scared = st.session_state.scared_ticks > 0
    fp = st.session_state.fruit_pos
    fe = st.session_state.fruit_emoji
    ghost_map = {(g["pos"][0], g["pos"][1]): g["color"] for g in st.session_state.ghosts}

    rows = []
    for r in range(MH):
        cells = []
        for c in range(MW):
            pos = (r, c)
            if pp[0] == r and pp[1] == c:
                cells.append('<div class="pm-c pm-pac">😮</div>')
            elif pos in ghost_map:
                col = ghost_map[pos]
                if scared:
                    cells.append('<div class="pm-c pm-scared">👻</div>')
                else:
                    cells.append(f'<div class="pm-c pm-ghost" style="color:{col};">👻</div>')
            elif fp and fp[0] == r and fp[1] == c:
                cells.append(f'<div class="pm-c pm-fruit">{fe}</div>')
            else:
                v = maze[r][c]
                if v == 1:
                    cells.append('<div class="pm-c pm-wall"></div>')
                elif v == 2:
                    cells.append('<div class="pm-c pm-dot">·</div>')
                elif v == 3:
                    cells.append('<div class="pm-c pm-power">●</div>')
                else:
                    cells.append('<div class="pm-c pm-empty"></div>')
        rows.append(f'<div class="pm-row">{"".join(cells)}</div>')
    return "\n".join(rows)


def sidebar():
    with st.sidebar:
        st.markdown('<div style="font-family:monospace;font-size:1rem;color:#FFE600;'
                    'letter-spacing:.15em;margin-bottom:10px;">😮 PAC-MAN</div>',
                    unsafe_allow_html=True)
        render_bgm_toggle(GAME, compact=True)
        st.markdown("---")
        render_key_guide(GAME, show_tips=True, show_common=False)
        st.markdown("---")
        render_ranking_table(GAME, highlight_score=st.session_state.get("last_score") or None)
        st.markdown("---")
        render_fullscreen_btn(GAME, target_id="pacman-board")


# ── 메인 ──────────────────────────────────────────────────────────
init_state()
sidebar()

if st.session_state.pm_state == "title":
    st.markdown('<div class="pm-title">🟡 PAC-MAN 팩맨</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center;color:#6666aa;font-family:monospace;'
                'letter-spacing:.1em;margin-bottom:16px;">NAMCO · 1980 · RETRO ARCADE</p>',
                unsafe_allow_html=True)
    st.markdown("---")
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
<div style="text-align:center;padding:18px;background:#000010;
     border:2px solid #0000cc;border-radius:12px;">
  <div style="font-size:1.8rem;margin:5px 0;">😮 · · · ·</div>
  <div style="font-size:1.3rem;margin:5px 0;color:#FF4444;">👻 👻 👻 👻</div>
  <div style="font-size:.82rem;color:#6666cc;margin:7px 0;font-family:monospace;">
    1UP &nbsp;&nbsp; HI-SCORE<br>
    <span style="color:#FFE600;">00000 &nbsp;&nbsp; 00000</span>
  </div>
  <div class="pm-blink" style="color:#FFE600;font-family:monospace;
       font-size:.95rem;margin-top:10px;letter-spacing:.2em;">
    ── INSERT COIN ──
  </div>
</div>""", unsafe_allow_html=True)
        st.markdown("")
        if render_coin_screen(GAME, show_credits=False, free_play=True):
            play_sfx("coin")
            init_audio(GAME)
            start_game()
            st.rerun()
    st.markdown("---")
    render_key_badge_row(GAME)
    render_credits_footer(GAME)

elif st.session_state.pm_state == "playing":
    game_step()

    left, mid, right = st.columns([1, 2.5, 1])
    with left:
        scared_bar = ""
        if st.session_state.scared_ticks > 0:
            pct = int(st.session_state.scared_ticks / 30 * 100)
            scared_bar = (f'<div style="margin-top:5px;">'
                          f'<div style="font-size:.7rem;color:#6666cc;">POWER</div>'
                          f'<div style="background:#2121DE;width:{pct}%;height:5px;border-radius:2px;"></div>'
                          f'</div>')
        lives_str = "😮 " * max(0, st.session_state.lives)
        hi = max(st.session_state.score, get_hi_score(GAME))
        fd = st.session_state.fruit_emoji if st.session_state.fruit_pos else "—"
        st.markdown(f"""
<div class="pm-panel"><div class="pm-slbl">1UP</div>
  <div class="pm-sval">{st.session_state.score:,}</div></div>
<div class="pm-panel"><div class="pm-slbl">LIVES</div>
  <div style="font-size:1.3rem;">{lives_str}</div>{scared_bar}</div>
<div class="pm-panel"><div class="pm-slbl">LEVEL</div>
  <div class="pm-sval">{st.session_state.level}</div></div>
<div class="pm-panel"><div class="pm-slbl">DOTS</div>
  <div class="pm-sval" style="font-size:1.2rem;">{st.session_state.dots_left}</div></div>
""", unsafe_allow_html=True)

    with mid:
        st.markdown(f'<div class="pm-title" style="font-size:1rem;margin-bottom:5px;">'
                    f'😮 PAC-MAN · LV.{st.session_state.level}</div>', unsafe_allow_html=True)
        inner = f'<div class="pm-wrap">{render_maze()}</div>'
        render_fullscreen_wrapper(inner, GAME, "pacman-board")

    with right:
        hi = max(st.session_state.score, get_hi_score(GAME))
        fd = st.session_state.fruit_emoji if st.session_state.fruit_pos else "—"
        st.markdown(f"""
<div class="pm-panel"><div class="pm-slbl">HI-SCORE</div>
  <div class="pm-sval" style="font-size:1.1rem;">{hi:,}</div></div>
<div class="pm-panel"><div class="pm-slbl">FRUIT</div>
  <div style="font-size:1.6rem;">{fd}</div></div>
<div class="pm-panel"><div class="pm-slbl">SCARED</div>
  <div class="pm-sval" style="font-size:1.1rem;">{st.session_state.scared_ticks}</div></div>
""", unsafe_allow_html=True)

    st.markdown("")
    _, ub, _ = st.columns([2, 1, 2])
    with ub:
        if st.button("▲ UP", key="pm_up"):
            st.session_state.pac_dir = "UP"
    lb, _, rb = st.columns([1, 1, 1])
    with lb:
        if st.button("◀ LEFT", key="pm_l"):
            st.session_state.pac_dir = "LEFT"
    with rb:
        if st.button("RIGHT ▶", key="pm_r"):
            st.session_state.pac_dir = "RIGHT"
    _, db, qb = st.columns([2, 1, 1])
    with db:
        if st.button("▼ DOWN", key="pm_d"):
            st.session_state.pac_dir = "DOWN"
    with qb:
        if st.button("⏹ 종료", key="pm_q"):
            save_score(GAME, st.session_state.score)
            st.session_state.last_score = st.session_state.score
            st.session_state.pm_state = "title"
            st.rerun()

    time.sleep(0.22)
    st.rerun()

elif st.session_state.pm_state == "gameover":
    play_sfx("gameover")
    st.markdown('<div class="pm-title">💀 GAME OVER 💀</div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if not st.session_state.nick_done:
            if render_nickname_entry(GAME, st.session_state.last_score):
                st.session_state.nick_done = True
                st.rerun()
        else:
            render_ranking_table(GAME, highlight_score=st.session_state.last_score)
        st.markdown("")
        if st.button("🔄 다시 도전", key="pm_retry"):
            start_game()
            st.rerun()
        if st.button("🏠 타이틀로", key="pm_title"):
            st.session_state.pm_state = "title"
            st.rerun()
    render_credits_footer(GAME)
