"""
테트리스 (Tetris) - Streamlit 웹 게임 (화면 하단 버튼 중복 렌더링 버그 완벽 수정 버전)
폴더: arcade/tetris/
실행: streamlit run app.py --server.port 8502
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

GAME = "tetris"

st.set_page_config(page_title="🧱 테트리스", page_icon="🧱",
                   layout="wide", initial_sidebar_state="expanded")

apply_theme(GAME)
st.markdown(get_game_css(GAME), unsafe_allow_html=True)

st.markdown("""
<style>
.t-wrap { display:inline-block; border:2px solid #5DCAA5; border-radius:8px;
          padding:4px; background:#050510; font-family:monospace; line-height:1; }
.t-row  { display:flex; }
.tc     { width:24px; height:24px; border:1px solid #111;
          display:flex; align-items:center; justify-content:center; box-sizing:border-box; }
.tc-empty { background:#0a0a18; }
.tc-ghost { background:#0a0a18; border:1px dashed #2a2a4a; }
.tc-I { background:#00f5ff; border-color:#00c8d4; }
.tc-O { background:#ffe600; border-color:#c8b400; }
.tc-T { background:#bf00ff; border-color:#9800cc; }
.tc-S { background:#00ff5e; border-color:#00cc4b; }
.tc-Z { background:#ff2d2d; border-color:#cc2424; }
.tc-J { background:#ff8c00; border-color:#cc7000; }
.tc-L { background:#0066ff; border-color:#0052cc; }
.t-panel { background:#0a0a1e; border:1px solid #5DCAA5; border-radius:8px;
           padding:10px 12px; margin-bottom:8px; font-family:'Courier New',monospace; }
.t-plbl  { font-size:.7rem; color:#5DCAA5; letter-spacing:.15em; margin-bottom:3px; }
.t-pval  { font-size:1.7rem; font-weight:bold; color:#fff; }
.t-next  { display:flex; justify-content:center; }
.tn-cell { width:20px; height:20px; display:inline-block;
           border:1px solid #111; box-sizing:border-box; }
.t-title { font-family:'Courier New',monospace; font-size:1.6rem; font-weight:bold;
           color:#5DCAA5; text-align:center; letter-spacing:.2em;
           text-shadow:0 0 20px #5DCAA5; }
.t-blink { animation:t-blink 1s step-end infinite; }
@keyframes t-blink { 50%{ opacity:0; } }
</style>
""", unsafe_allow_html=True)

# ── 상수 ──────────────────────────────────────────────────────────
BW = 10; BH = 20
TETROMINOS = {
    "I": {"shape": [[1,1,1,1]],        "color": "I"},
    "O": {"shape": [[1,1],[1,1]],      "color": "O"},
    "T": {"shape": [[0,1,0],[1,1,1]], "color": "T"},
    "S": {"shape": [[0,1,1],[1,1,0]], "color": "S"},
    "Z": {"shape": [[1,1,0],[0,1,1]], "color": "Z"},
    "J": {"shape": [[1,0,0],[1,1,1]], "color": "J"},
    "L": {"shape": [[0,0,1],[1,1,1]], "color": "L"},
}
SCORE_TABLE = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}


def new_board():
    return [[""] * BW for _ in range(BH)]


def rand_piece():
    n = random.choice(list(TETROMINOS))
    t = TETROMINOS[n]
    sh = [row[:] for row in t["shape"]]
    return {"name": n, "shape": sh, "color": t["color"],
            "row": 0, "col": BW // 2 - len(sh[0]) // 2}


def rotate(sh):
    return [list(row) for row in zip(*sh[::-1])]


def valid(board, sh, r, c):
    for dr, row in enumerate(sh):
        for dc, cell in enumerate(row):
            if cell:
                nr, nc = r + dr, c + dc
                if nr < 0 or nr >= BH or nc < 0 or nc >= BW:
                    return False
                if board[nr][nc]:
                    return False
    return True


def place(board, piece):
    b = copy.deepcopy(board)
    for dr, row in enumerate(piece["shape"]):
        for dc, cell in enumerate(row):
            if cell:
                nr, nc = piece["row"] + dr, piece["col"] + dc
                if 0 <= nr < BH and 0 <= nc < BW:
                    b[nr][nc] = piece["color"]
    return b


def ghost_row(board, piece):
    r = piece["row"]
    while valid(board, piece["shape"], r + 1, piece["col"]):
        r += 1
    return r


def clear_lines(board):
    nb = [row for row in board if any(c == "" for c in row)]
    cl = BH - len(nb)
    for _ in range(cl):
        nb.insert(0, [""] * BW)
    return nb, cl


def init_state():
    defs = dict(
        t_state="title", board=new_board(), current=None,
        next_piece=None, score=0, lines=0, level=1, tick=0,
        held=None, hold_used=False, nick_done=False, last_score=0,
        gameover_sfx_played=False,
    )
    for k, v in defs.items():
        st.session_state.setdefault(k, v)


def start_game():
    st.session_state.update(
        board=new_board(), current=rand_piece(),
        next_piece=rand_piece(), score=0, lines=0,
        level=1, tick=0, held=None, hold_used=False,
        nick_done=False, t_state="playing",
        gameover_sfx_played=False,
    )


def game_step():
    p = st.session_state.current
    board = st.session_state.board
    inv = max(1, 8 - st.session_state.level)
    st.session_state.tick += 1
    if st.session_state.tick % inv != 0:
        return
    nr = p["row"] + 1
    if valid(board, p["shape"], nr, p["col"]):
        p["row"] = nr
    else:
        st.session_state.board = place(board, p)
        st.session_state.board, cl = clear_lines(st.session_state.board)
        if cl > 0:
            play_sfx("line_clear")
        st.session_state.score += SCORE_TABLE.get(cl, 0) * st.session_state.level
        st.session_state.lines += cl
        st.session_state.level = st.session_state.lines // 10 + 1
        st.session_state.current = st.session_state.next_piece
        st.session_state.next_piece = rand_piece()
        st.session_state.hold_used = False
        if not valid(st.session_state.board, st.session_state.current["shape"],
                     st.session_state.current["row"], st.session_state.current["col"]):
            st.session_state.last_score = st.session_state.score
            st.session_state.t_state = "gameover"


def board_html():
    p = st.session_state.current
    board = st.session_state.board
    gr = ghost_row(board, p)
    disp = copy.deepcopy(board)
    for dr, row in enumerate(p["shape"]):
        for dc, cell in enumerate(row):
            if cell:
                nr, nc = gr + dr, p["col"] + dc
                if 0 <= nr < BH and 0 <= nc < BW and disp[nr][nc] == "":
                    disp[nr][nc] = "ghost"
    for dr, row in enumerate(p["shape"]):
        for dc, cell in enumerate(row):
            if cell:
                nr, nc = p["row"] + dr, p["col"] + dc
                if 0 <= nr < BH and 0 <= nc < BW:
                    disp[nr][nc] = p["color"]
    rows = []
    for r in range(BH):
        cells = []
        for c in range(BW):
            v = disp[r][c]
            if v == "":
                cells.append('<div class="tc tc-empty"></div>')
            elif v == "ghost":
                cells.append('<div class="tc tc-ghost"></div>')
            else:
                cells.append(f'<div class="tc tc-{v}"></div>')
        rows.append(f'<div class="t-row">{"".join(cells)}</div>')
    return "\n".join(rows)


def next_html(piece):
    if not piece:
        return '<div style="color:#333;font-size:.8rem;text-align:center;">EMPTY</div>'
    rows = []
    for row in piece["shape"]:
        cells = []
        for cell in row:
            if cell:
                cells.append(f'<div class="tn-cell tc-{piece["color"]}"></div>')
            else:
                cells.append('<div class="tn-cell" style="background:transparent;border:none;"></div>')
        rows.append(f'<div class="t-next">{"".join(cells)}</div>')
    return "\n".join(rows)


def sidebar():
    with st.sidebar:
        st.markdown('<div style="font-family:monospace;font-size:1rem;color:#5DCAA5;'
                    'letter-spacing:.15em;margin-bottom:10px;">🧱 TETRIS</div>',
                    unsafe_allow_html=True)
        render_bgm_toggle(GAME, compact=True)
        st.markdown("---")
        render_key_guide(GAME, show_tips=True, show_common=False)
        st.markdown("---")
        render_ranking_table(GAME, highlight_score=st.session_state.get("last_score") or None)
        st.markdown("---")
        render_fullscreen_btn(GAME, target_id="tetris-board")


# ── 메인 구조 정의 ───────────────────────────────────────────────
init_state()
sidebar()

# [중요 버그 완벽 수정] 각 상태별로 100% 분리된 독립형 뷰포트를 선언합니다.
# 상태가 전환되면 사용하지 않는 나머지 뷰포트를 무조건 .empty() 시켜 브라우저 DOM 캐싱 중복 오류를 예방합니다.
title_viewport = st.empty()
play_viewport = st.empty()
gameover_viewport = st.empty()

# ── TITLE ─────────────────────────────────────────────────────────
if st.session_state.t_state == "title":
    # 실행하지 않는 뷰포트 영역 완전 초기화 및 클리어
    play_viewport.empty()
    gameover_viewport.empty()
    
    with title_viewport.container():
        st.markdown('<div class="t-title">🧱 TETRIS 테트리스</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#5DCAA5;font-family:monospace;'
                    'letter-spacing:.1em;margin-bottom:16px;">ALEXEY PAJITNOV · 1984</p>',
                    unsafe_allow_html=True)
        st.markdown("---")
        _, col, _ = st.columns([1, 1.5, 1])
        with col:
            st.markdown("""
    <div style="text-align:center;padding:20px;background:#050510;
         border:2px solid #5DCAA5;border-radius:12px;">
      <div style="display:flex;justify-content:center;gap:3px;margin:3px 0;">
        <div class="tc tc-I" style="width:24px;height:24px;"></div>
        <div class="tc tc-I" style="width:24px;height:24px;"></div>
        <div class="tc tc-I" style="width:24px;height:24px;"></div>
        <div class="tc tc-I" style="width:24px;height:24px;"></div>
      </div>
      <div style="display:flex;justify-content:center;gap:3px;margin:3px 0;">
        <div class="tc tc-T" style="width:24px;height:24px;"></div>
        <div class="tc tc-T" style="width:24px;height:24px;"></div>
        <div class="tc tc-T" style="width:24px;height:24px;"></div>
      </div>
      <div style="display:flex;justify-content:center;gap:3px;margin:3px 0;">
        <div class="tc tc-S" style="width:24px;height:24px;"></div>
        <div class="tc tc-S" style="width:24px;height:24px;"></div>
        <div class="tc tc-Z" style="width:24px;height:24px;"></div>
        <div class="tc tc-Z" style="width:24px;height:24px;"></div>
      </div>
      <div class="t-blink" style="font-family:monospace;color:#5DCAA5;
           font-size:0.95rem;margin-top:14px;letter-spacing:.2em;">
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

# ── PLAYING ───────────────────────────────────────────────────────
elif st.session_state.t_state == "playing":
    game_step()
    
    # 이전 타이틀 찌꺼기 및 게임오버 요소를 완벽하게 증발시킵니다.
    title_viewport.empty()
    gameover_viewport.empty()

    with play_viewport.container():
        left, mid, right = st.columns([1, 2, 1])
        with left:
            held_html = next_html(st.session_state.held)
            st.markdown(f"""
    <div class="t-panel"><div class="t-plbl">SCORE</div>
      <div class="t-pval">{st.session_state.score:,}</div></div>
    <div class="t-panel"><div class="t-plbl">LINES</div>
      <div class="t-pval">{st.session_state.lines}</div></div>
    <div class="t-panel"><div class="t-plbl">LEVEL</div>
      <div class="t-pval">{st.session_state.level}</div></div>
    <div class="t-panel"><div class="t-plbl">HOLD</div>
      <div style="margin-top:5px;">{held_html}</div></div>
    """, unsafe_allow_html=True)

        with mid:
            st.markdown(f'<div class="t-title" style="font-size:1.1rem;margin-bottom:6px;">'
                        f'🧱 TETRIS · LV.{st.session_state.level}</div>', unsafe_allow_html=True)
            inner = f'<div class="t-wrap">{board_html()}</div>'
            render_fullscreen_wrapper(inner, GAME, "tetris-board")

        with right:
            hi = max(st.session_state.score, get_hi_score(GAME))
            st.markdown(f"""
    <div class="t-panel"><div class="t-plbl">NEXT</div>
      <div style="margin-top:5px;">{next_html(st.session_state.next_piece)}</div></div>
    <div class="t-panel"><div class="t-plbl">HI-SCORE</div>
      <div class="t-pval" style="font-size:1.2rem;">{hi:,}</div></div>
    """, unsafe_allow_html=True)

        st.markdown("")
        p = st.session_state.current
        board = st.session_state.board
        
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        with b1:
            if st.button("◀ LEFT", key="t_ml"):
                if valid(board, p["shape"], p["row"], p["col"] - 1):
                    p["col"] -= 1
                    st.rerun()
        with b2:
            if st.button("RIGHT ▶", key="t_mr"):
                if valid(board, p["shape"], p["row"], p["col"] + 1):
                    p["col"] += 1
                    st.rerun()
        with b3:
            if st.button("↺ ROT", key="t_rot"):
                ns = rotate(p["shape"])
                if valid(board, ns, p["row"], p["col"]):
                    p["shape"] = ns
                    st.rerun()
        with b4:
            if st.button("▼ SOFT", key="t_sd"):
                if valid(board, p["shape"], p["row"] + 1, p["col"]):
                    p["row"] += 1
                    st.session_state.score += 1
                    st.rerun()
        with b5:
            if st.button("⬇ HARD", key="t_hd"):
                gr = ghost_row(board, p)
                pts = (gr - p["row"]) * 2
                p["row"] = gr
                st.session_state.board = place(board, p)
                st.session_state.board, cl = clear_lines(st.session_state.board)
                if cl > 0:
                    play_sfx("line_clear")
                st.session_state.score += SCORE_TABLE.get(cl, 0) * st.session_state.level + pts
                st.session_state.lines += cl
                st.session_state.level = st.session_state.lines // 10 + 1
                st.session_state.current = st.session_state.next_piece
                st.session_state.next_piece = rand_piece()
                st.session_state.hold_used = False
                if not valid(st.session_state.board, st.session_state.current["shape"],
                             st.session_state.current["row"], st.session_state.current["col"]):
                    st.session_state.last_score = st.session_state.score
                    st.session_state.t_state = "gameover"
                st.rerun()
        with b6:
            if st.button("⏹ 종료", key="t_quit"):
                save_score(GAME, st.session_state.score)
                st.session_state.last_score = st.session_state.score
                st.session_state.t_state = "title"
                st.rerun()

        spd = max(0.25, 1.0 - st.session_state.level * 0.07)
        time.sleep(spd)
        st.rerun()

# ── GAMEOVER ──────────────────────────────────────────────────────
elif st.session_state.t_state == "gameover":
    if not st.session_state.get("gameover_sfx_played", False):
        play_sfx("gameover")
        st.session_state.gameover_sfx_played = True

    # 게임 진행중인 뷰포트와 타이틀 뷰포트 완전 박멸
    title_viewport.empty()
    play_viewport.empty()

    with gameover_viewport.container():
        st.markdown('<div class="t-title">💔 GAME OVER</div>', unsafe_allow_html=True)
        _, col, _ = st.columns([1, 2, 1])
        with col:
            if not st.session_state.nick_done:
                if render_nickname_entry(GAME, st.session_state.last_score):
                    st.session_state.nick_done = True
                    st.rerun()
            else:
                render_ranking_table(GAME, highlight_score=st.session_state.last_score)
            st.markdown("")
            if st.button("🔄 다시 도전", key="t_retry"):
                start_game()
                st.rerun()
            if st.button("🏠 타이틀로", key="t_title"):
                st.session_state.t_state = "title"
                st.rerun()
        render_credits_footer(GAME)