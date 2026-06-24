"""
스페이스 인베이더 (Space Invaders) - Streamlit 웹 게임 (화면 하단 버튼 중복 렌더링 및 레이아웃 틀어짐 버그 완벽 수정 버전)
폴더: arcade/space_invaders/
실행: streamlit run app.py --server.port 8504
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

GAME = "space_invaders"

st.set_page_config(page_title="👾 스페이스 인베이더", page_icon="👾",
                   layout="wide", initial_sidebar_state="expanded")

apply_theme(GAME)
st.markdown(get_game_css(GAME), unsafe_allow_html=True)

st.markdown("""
<style>
.si-board { background:#000; border:2px solid #993C1D; border-radius:8px;
            padding:7px 5px; font-family:'Courier New',monospace;
            line-height:1; display:inline-block; }
.si-row   { display:flex; justify-content:center; }
.si-c     { width:28px; height:26px; display:flex; align-items:center;
            justify-content:center; font-size:.9rem; box-sizing:border-box; }
.si-empty   { color:transparent; }
.si-inv-a   { color:#F0997B; }
.si-inv-b   { color:#EF9F27; }
.si-inv-c   { color:#FFE600; }
.si-ufo     { color:#FF4444; }
.si-player  { color:#33ff33; }
.si-bullet  { color:#33ff33; }
.si-ebullet { color:#F0997B; }
.si-shield  { color:#33aa33; }
.si-explode { color:#FF4444; }
.si-panel   { background:#000; border:1px solid #993C1D; border-radius:8px;
              padding:10px 12px; margin-bottom:8px;
              font-family:'Courier New',monospace; text-align:center; }
.si-slbl    { font-size:.7rem; color:#993C1D; letter-spacing:.15em; }
.si-sval    { font-size:1.7rem; font-weight:bold; color:#33ff33; }
.si-title   { font-family:'Courier New',monospace; font-size:1.7rem; font-weight:bold;
              color:#F0997B; text-align:center; letter-spacing:.2em;
              text-shadow:0 0 20px #993C1D; }
.si-sbar    { display:flex; gap:7px; justify-content:center;
              font-family:monospace; font-size:.82rem; color:#33aa33; margin:4px 0; }
.si-blink   { animation:si-blink .8s step-end infinite; }
@keyframes si-blink { 50%{ opacity:0; } }
</style>
""", unsafe_allow_html=True)

# ── 상수 ──────────────────────────────────────────────────────────
COLS          = 15
ROWS          = 18
PLAYER_ROW    = ROWS - 2
SHIELD_ROW    = ROWS - 4
INV_ROWS      = 4
INV_COLS      = 10
INV_START_ROW = 1
INV_START_COL = 2
INV_TYPES     = {0: ("🛸", 40), 1: ("👾", 20), 2: ("👾", 20), 3: ("🐛", 10)}
INV_EMOJIS    = {0: "🛸", 1: "👾", 2: "👾", 3: "🐛"}
INV_CSS       = {0: "si-inv-a", 1: "si-inv-b", 2: "si-inv-b", 3: "si-inv-c"}
UFO_SCORES    = [50, 100, 150, 300]
SHIELD_COLS   = [2, 5, 9, 12]
SHIELD_HP     = 4


def make_invaders():
    """인베이더 → {"r,c": type_idx} 문자열 키 딕셔너리"""
    inv = {}
    for r in range(INV_ROWS):
        for c in range(INV_COLS):
            key = f"{INV_START_ROW + r},{INV_START_COL + c}"
            inv[key] = r
    return inv


def make_shields():
    return {str(c): SHIELD_HP for c in SHIELD_COLS}


def inv_keys_to_set(inv_dict):
    """문자열 키 dict → (r,c) 집합 반환"""
    result = {}
    for k, v in inv_dict.items():
        r, c = map(int, k.split(","))
        result[(r, c)] = v
    return result


def init_state():
    defs = dict(
        si_state="title",
        player_col=COLS // 2,
        bullets=[],
        enemy_bullets=[],
        invaders=make_invaders(),
        shields=make_shields(),
        ufo_col=-1,          # -1: 없음
        score=0, lives=3, stage=1, tick=0,
        inv_dir=1,
        explosions=[],       # list of [r,c] — set 사용 금지
        move_interval=8,
        nick_done=False, last_score=0,
        gameover_sfx_played=False,
    )
    for k, v in defs.items():
        st.session_state.setdefault(k, v)


def start_game():
    st.session_state.update(
        player_col=COLS // 2, bullets=[], enemy_bullets=[],
        invaders=make_invaders(), shields=make_shields(),
        ufo_col=-1, score=0, lives=3, stage=1, tick=0,
        inv_dir=1, explosions=[], move_interval=8,
        nick_done=False, si_state="playing",
        gameover_sfx_played=False,
    )


def move_invaders():
    inv = st.session_state.invaders
    if not inv:
        return
    interval = max(1, st.session_state.move_interval - len(inv) // 5)
    if st.session_state.tick % interval != 0:
        return

    d = st.session_state.inv_dir
    inv_parsed = inv_keys_to_set(inv)
    all_cols = [c for _, c in inv_parsed.keys()]
    drop = (d == 1 and max(all_cols) >= COLS - 2) or (d == -1 and min(all_cols) <= 1)
    if drop:
        st.session_state.inv_dir *= -1

    new_inv = {}
    for (r, c), t in inv_parsed.items():
        nr = r + (1 if drop else 0)
        nc = c + (0 if drop else d)
        new_inv[f"{nr},{nc}"] = t
    st.session_state.invaders = new_inv


def invader_shoot():
    inv = st.session_state.invaders
    if not inv or random.random() > 0.12:
        return
    inv_parsed = inv_keys_to_set(inv)
    cols_map = {}
    for (r, c) in inv_parsed:
        if c not in cols_map or r > cols_map[c]:
            cols_map[c] = r
    if not cols_map:
        return
    col = random.choice(list(cols_map.keys()))
    row = cols_map[col]
    st.session_state.enemy_bullets.append([row + 1, col])


def spawn_ufo():
    if st.session_state.ufo_col == -1 and st.session_state.tick % 50 == 0 and random.random() < 0.3:
        st.session_state.ufo_col = 0


def move_ufo():
    if st.session_state.ufo_col == -1:
        return
    st.session_state.ufo_col += 1
    if st.session_state.ufo_col >= COLS:
        st.session_state.ufo_col = -1


def move_player_bullets():
    inv = st.session_state.invaders
    inv_parsed = inv_keys_to_set(inv)
    shields = st.session_state.shields
    new_b = []
    explosions = []

    for bullet in st.session_state.bullets:
        r, c = bullet
        nr = r - 1
        if nr < 0:
            continue
        hit = False

        # 인베이더 충돌
        if (nr, c) in inv_parsed:
            t = inv_parsed.pop((nr, c))
            _, pts = INV_TYPES[t]
            st.session_state.score += pts
            explosions.append([nr, c])
            st.session_state.move_interval = max(2, 8 - (40 - len(inv_parsed)) // 5)
            hit = True
            play_sfx("explosion")
            # 업데이트된 inv_parsed → 문자열 키로 복원
            st.session_state.invaders = {f"{row},{col}": tp for (row, col), tp in inv_parsed.items()}

        # UFO 충돌
        if not hit and st.session_state.ufo_col != -1 and c == st.session_state.ufo_col and nr == 0:
            pts = random.choice(UFO_SCORES)
            st.session_state.score += pts
            st.session_state.ufo_col = -1
            hit = True
            play_sfx("ufo")

        # 방어막 충돌
        sc = str(c)
        if not hit and nr == SHIELD_ROW and sc in shields:
            shields[sc] -= 1
            if shields[sc] <= 0:
                del shields[sc]
            hit = True

        if not hit:
            new_b.append([nr, c])

    st.session_state.bullets = new_b
    st.session_state.explosions = explosions


def move_enemy_bullets():
    new_b = []
    shields = st.session_state.shields
    pc = st.session_state.player_col

    for bullet in st.session_state.enemy_bullets:
        r, c = bullet
        nr = r + 1
        if nr >= ROWS:
            continue
        hit = False

        # 플레이어 충돌
        if nr == PLAYER_ROW and c == pc:
            st.session_state.lives -= 1
            play_sfx("explosion")
            hit = True
            if st.session_state.lives <= 0:
                st.session_state.last_score = st.session_state.score
                st.session_state.si_state = "gameover"
                return

        # 방어막 충돌
        sc = str(c)
        if not hit and nr == SHIELD_ROW and sc in shields:
            shields[sc] -= 1
            if shields[sc] <= 0:
                del shields[sc]
            hit = True

        if not hit:
            new_b.append([nr, c])

    st.session_state.enemy_bullets = new_b


def check_invasion():
    inv_parsed = inv_keys_to_set(st.session_state.invaders)
    if any(r >= PLAYER_ROW for r, _ in inv_parsed):
        st.session_state.last_score = st.session_state.score
        st.session_state.si_state = "gameover"


def render_board():
    pc      = st.session_state.player_col
    inv_parsed = inv_keys_to_set(st.session_state.invaders)
    bullets  = {(r, c) for r, c in st.session_state.bullets}
    ebullets = {(r, c) for r, c in st.session_state.enemy_bullets}
    shields  = st.session_state.shields
    ufo_col  = st.session_state.ufo_col
    expl     = {(r, c) for r, c in st.session_state.explosions}

    rows = []
    for r in range(ROWS):
        cells = []
        for c in range(COLS):
            if r == 0 and ufo_col != -1 and ufo_col == c:
                cells.append('<div class="si-c si-ufo">🛸</div>')
            elif (r, c) in expl:
                cells.append('<div class="si-c si-explode">💥</div>')
            elif (r, c) in inv_parsed:
                t = inv_parsed[(r, c)]
                cells.append(f'<div class="si-c {INV_CSS[t]}">{INV_EMOJIS[t]}</div>')
            elif r == PLAYER_ROW and c == pc:
                cells.append('<div class="si-c si-player">🚀</div>')
            elif r == SHIELD_ROW and str(c) in shields:
                op = 0.3 + shields[str(c)] * 0.18
                cells.append(f'<div class="si-c si-shield" style="opacity:{op:.1f};">▓</div>')
            elif (r, c) in bullets:
                cells.append('<div class="si-c si-bullet">|</div>')
            elif (r, c) in ebullets:
                cells.append('<div class="si-c si-ebullet">▼</div>')
            else:
                cells.append('<div class="si-c si-empty">.</div>')
        rows.append(f'<div class="si-row">{"".join(cells)}</div>')
    return "\n".join(rows)


def sidebar():
    with st.sidebar:
        st.markdown('<div style="font-family:monospace;font-size:1rem;color:#F0997B;'
                    'letter-spacing:.15em;margin-bottom:10px;">👾 SPACE INVADERS</div>',
                    unsafe_allow_html=True)
        render_bgm_toggle(GAME, compact=True)
        st.markdown("---")
        render_key_guide(GAME, show_tips=True, show_common=False)
        st.markdown("---")
        render_ranking_table(GAME, highlight_score=st.session_state.get("last_score") or None)
        st.markdown("---")
        render_fullscreen_btn(GAME, target_id="si-board")


# ── 메인 ──────────────────────────────────────────────────────────
init_state()
sidebar()

# [중요 버그 완벽 수정] 각 상태별로 100% 독립된 가상 뷰포트를 선언합니다.
# 상태 전환 시 미사용 뷰포트를 .empty()로 제거해 브라우저 렌더링 충돌 현상을 방지합니다.
title_viewport = st.empty()
play_viewport = st.empty()
gameover_viewport = st.empty()

# ── TITLE ─────────────────────────────────────────────────────────
if st.session_state.si_state == "title":
    play_viewport.empty()
    gameover_viewport.empty()

    with title_viewport.container():
        st.markdown('<div class="si-title">👾 SPACE INVADERS</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#663322;font-family:monospace;'
                    'letter-spacing:.1em;margin-bottom:16px;">TAITO · 1978 · RETRO ARCADE</p>',
                    unsafe_allow_html=True)
        st.markdown("---")
        _, col, _ = st.columns([1, 2, 1])
        with col:
            st.markdown("""
    <div style="text-align:center;padding:18px;background:#000;
         border:2px solid #993C1D;border-radius:12px;font-family:monospace;">
      <div style="color:#FF4444;font-size:1.3rem;margin:4px 0;">🛸 🛸 🛸 🛸 🛸</div>
      <div style="color:#F0997B;font-size:1.3rem;margin:4px 0;">👾 👾 👾 👾 👾</div>
      <div style="color:#EF9F27;font-size:1.3rem;margin:4px 0;">👾 👾 👾 👾 👾</div>
      <div style="color:#FFE600;font-size:1.3rem;margin:4px 0;">🐛 🐛 🐛 🐛 🐛</div>
      <div style="margin:10px 0;color:#33aa33;font-size:.85rem;">▓ ▓ ▓ &nbsp;&nbsp; ▓ ▓ ▓</div>
      <div style="font-size:1.1rem;color:#33ff33;margin:6px 0;">🚀</div>
      <div class="si-blink" style="color:#F0997B;margin-top:10px;font-size:.95rem;letter-spacing:.15em;">
        ── INSERT COIN ──
      </div>
    </div>""", unsafe_allow_html=True)
            st.markdown("")
            st.markdown("""
    <div style="display:flex;gap:14px;justify-content:center;
         font-family:monospace;font-size:.8rem;margin:7px 0;">
      <span style="color:#FF4444;">🛸=???점</span>
      <span style="color:#F0997B;">👾=20점</span>
      <span style="color:#EF9F27;">👾=20점</span>
      <span style="color:#FFE600;">🐛=10점</span>
    </div>""", unsafe_allow_html=True)
            if render_coin_screen(GAME, show_credits=False, free_play=True):
                play_sfx("coin")
                init_audio(GAME)
                start_game()
                st.rerun()
        st.markdown("---")
        render_key_badge_row(GAME)
        render_credits_footer(GAME)

# ── PLAYING ───────────────────────────────────────────────────────
elif st.session_state.si_state == "playing":
    st.session_state.tick += 1
    st.session_state.explosions = []

    move_invaders()
    invader_shoot()
    spawn_ufo()
    move_ufo()
    move_player_bullets()

    if st.session_state.si_state == "playing":
        move_enemy_bullets()
    if st.session_state.si_state == "playing":
        check_invasion()

    # 스테이지 클리어
    if not st.session_state.invaders and st.session_state.si_state == "playing":
        st.session_state.stage += 1
        st.session_state.invaders = make_invaders()
        st.session_state.shields  = make_shields()
        st.session_state.bullets  = []
        st.session_state.enemy_bullets = []
        st.session_state.score += 1000
        st.session_state.move_interval = max(2, 8 - st.session_state.stage)
        play_sfx("clear")

    title_viewport.empty()
    gameover_viewport.empty()

    with play_viewport.container():
        left, mid, right = st.columns([1, 2, 1])
        with left:
            st.markdown(f"""
    <div class="si-panel"><div class="si-slbl">SCORE</div>
      <div class="si-sval">{st.session_state.score:,}</div></div>
    <div class="si-panel"><div class="si-slbl">STAGE</div>
      <div class="si-sval">{st.session_state.stage}</div></div>
    <div class="si-panel"><div class="si-slbl">LIVES</div>
      <div style="font-size:1.2rem;color:#33ff33;">{"🚀 " * max(0, st.session_state.lives)}</div></div>
    <div class="si-panel"><div class="si-slbl">INVADERS</div>
      <div class="si-sval" style="font-size:1.1rem;">{len(st.session_state.invaders)}</div></div>
    """, unsafe_allow_html=True)

        with mid:
            ufo_txt = "🛸 UFO!" if st.session_state.ufo_col != -1 else ""
            st.markdown(
                f'<div class="si-title" style="font-size:1rem;margin-bottom:5px;">'
                f'👾 SPACE INVADERS · STAGE {st.session_state.stage} '
                f'<span style="color:#FF4444;font-size:.85rem;">{ufo_txt}</span></div>',
                unsafe_allow_html=True,
            )
            inner = f'<div class="si-board">{render_board()}</div>'
            render_fullscreen_wrapper(inner, GAME, "si-board")

            shields = st.session_state.shields
            shield_disp = " &nbsp; ".join(
                f"▓×{shields[str(c)]}" if str(c) in shields else "✗"
                for c in SHIELD_COLS
            )
            st.markdown(f'<div class="si-sbar">방어막: {shield_disp}</div>',
                        unsafe_allow_html=True)

        with right:
            hi = max(st.session_state.score, get_hi_score(GAME))
            st.markdown(f"""
    <div class="si-panel"><div class="si-slbl">HI-SCORE</div>
      <div class="si-sval" style="font-size:1.1rem;">{hi:,}</div></div>
    <div class="si-panel"><div class="si-slbl">UFO</div>
      <div style="font-size:1.4rem;">{"🛸" if st.session_state.ufo_col != -1 else "—"}</div></div>
    <div class="si-panel"><div class="si-slbl">TICK</div>
      <div class="si-sval" style="font-size:.95rem;">{st.session_state.tick}</div></div>
    """, unsafe_allow_html=True)

        st.markdown("")
        
        # [중요] 버튼이 중복 증식하지 않도록, 반드시 play_viewport 컨테이너 안에서 빌드합니다.
        # 조작 버튼들을 완벽한 대칭 아크 형태로 정렬하기 위해 가로 컬럼 비율 [1.5, 1, 2, 1, 1.5]과 use_container_width=True를 부여합니다.
        c1, c2, c3, c4, c5 = st.columns([1.5, 1, 2, 1, 1.5])
        with c1:
            if st.button("◀◀ 왼쪽", key="si_ll", use_container_width=True):
                st.session_state.player_col = max(0, st.session_state.player_col - 2)
                st.rerun()
        with c2:
            if st.button("◀ LEFT",  key="si_l", use_container_width=True):
                st.session_state.player_col = max(0, st.session_state.player_col - 1)
                st.rerun()
        with c3:
            if st.button("🔴 FIRE!", key="si_fire", use_container_width=True):
                st.session_state.bullets.append([PLAYER_ROW - 1, st.session_state.player_col])
                play_sfx("shoot")
                st.rerun()
        with c4:
            if st.button("RIGHT ▶", key="si_r", use_container_width=True):
                st.session_state.player_col = min(COLS - 1, st.session_state.player_col + 1)
                st.rerun()
        with c5:
            if st.button("오른쪽 ▶▶", key="si_rr", use_container_width=True):
                st.session_state.player_col = min(COLS - 1, st.session_state.player_col + 2)
                st.rerun()

        # 종료 버튼 정렬 일체감 보완
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        _, q_col_center, _ = st.columns([3.5, 3, 3.5])
        with q_col_center:
            if st.button("⏹ 종료", key="si_quit", use_container_width=True):
                save_score(GAME, st.session_state.score)
                st.session_state.last_score = st.session_state.score
                st.session_state.si_state = "title"
                st.rerun()

        time.sleep(0.45)
        st.rerun()

# ── GAMEOVER ──────────────────────────────────────────────────────
elif st.session_state.si_state == "gameover":
    if not st.session_state.get("gameover_sfx_played", False):
        play_sfx("gameover")
        st.session_state.gameover_sfx_played = True

    title_viewport.empty()
    play_viewport.empty()

    with gameover_viewport.container():
        st.markdown('<div class="si-title">💀 GAME OVER 💀</div>', unsafe_allow_html=True)
        _, col, _ = st.columns([1, 2, 1])
        with col:
            if not st.session_state.nick_done:
                if render_nickname_entry(GAME, st.session_state.last_score):
                    st.session_state.nick_done = True
                    st.rerun()
            else:
                render_ranking_table(GAME, highlight_score=st.session_state.last_score)
            st.markdown("")
            if st.button("🔄 다시 도전", key="si_retry", use_container_width=True):
                start_game()
                st.rerun()
            if st.button("🏠 타이틀로",  key="si_title", use_container_width=True):
                st.session_state.si_state = "title"
                st.rerun()
        render_credits_footer(GAME)