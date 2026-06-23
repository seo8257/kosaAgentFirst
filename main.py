"""
🕹️ 추억의 오락실 - 통합 허브
arcade/main.py
실행: streamlit run main.py --server.port 8500
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from common.theme       import apply_theme, THEMES
from common.insert_coin import add_credit, credit_display
from common.scoreboard  import render_all_rankings, get_hi_score, GAME_META
from common.fullscreen  import render_fullscreen_btn
from common.credits     import render_credits_scroll, render_credits_screen
from common.bgm import (
    render_bgm_toggle,
    play_sfx,
    init_audio,
    is_bgm_on
)

st.set_page_config(page_title="🕹️ 추억의 오락실", page_icon="🕹️",
                   layout="wide", initial_sidebar_state="expanded")

apply_theme("hub")

# BGM 초기화 (BGM ON/OFF 여부와 관계없이, 실시간 볼륨/스위치 동기화를 위해 매 run마다 항상 호출합니다)
init_audio("galaga")

st.markdown("""
<style>
.stApp { background:radial-gradient(ellipse at 20% 50%,#0a0a2e 0%,#000 60%) !important; }
.block-container { padding-top:.5rem !important; max-width:1400px; }

.hub-title { font-family:'Courier New',monospace; font-size:2rem; font-weight:bold;
             color:#fff; text-align:center; letter-spacing:.25em;
             text-shadow:0 0 12px #AFA9EC, 0 0 32px #534AB7; }
.hub-sub   { font-size:.82rem; color:#444; font-family:'Courier New',monospace;
             letter-spacing:.14em; text-align:center; margin-top:5px; }

.hub-grid  { display:grid; grid-template-columns:1fr 1fr; gap:14px; }
.hub-card  { border-radius:14px; padding:22px 18px; position:relative;
             overflow:hidden; min-height:200px;
             transition:transform .15s, filter .15s; }
.hub-card:hover { transform:scale(1.02); filter:brightness(1.08); }

.card-galaga   { background:linear-gradient(135deg,#0a0a2e,#1a1050);
                 border:1.5px solid #534AB7; box-shadow:0 0 18px rgba(83,74,183,.22); }
.card-tetris   { background:linear-gradient(135deg,#050f0a,#082e1e);
                 border:1.5px solid #0F6E56; box-shadow:0 0 18px rgba(15,110,86,.22); }
.card-pacman   { background:linear-gradient(135deg,#0f0f00,#2a2000);
                 border:1.5px solid #854F0B; box-shadow:0 0 18px rgba(133,79,11,.22); }
.card-invaders { background:linear-gradient(135deg,#0f0000,#1a0500);
                 border:1.5px solid #993C1D; box-shadow:0 0 18px rgba(153,60,29,.22); }

.card-num   { font-size:2.8rem; font-weight:bold; font-family:'Courier New',monospace;
              opacity:.12; position:absolute; top:8px; right:14px; }
.card-emoji { font-size:2.8rem; margin-bottom:8px; display:block; }
.card-title { font-size:1.3rem; font-weight:bold; font-family:'Courier New',monospace;
              letter-spacing:.1em; margin-bottom:2px; }
.card-meta  { font-size:.7rem; font-family:'Courier New',monospace;
              letter-spacing:.07em; opacity:.5; margin-bottom:9px; }
.card-desc  { font-size:.78rem; opacity:.7; line-height:1.5; margin-bottom:10px; }
.card-tags  { display:flex; gap:5px; flex-wrap:wrap; }
.hub-tag    { font-size:.66rem; padding:2px 6px; border-radius:4px;
              font-family:'Courier New',monospace; font-weight:bold; }
.card-btn   { display:inline-block; margin-top:10px; padding:6px 14px;
              border-radius:6px; font-family:'Courier New',monospace;
              font-size:.8rem; font-weight:bold; letter-spacing:.1em;
              text-decoration:none; }

.gc { color:#AFA9EC; } .gb { background:#534AB7; color:#fff; }
.tc { color:#5DCAA5; } .tb { background:#0F6E56; color:#fff; }
.pc { color:#FFE600; } .pb { background:#854F0B; color:#fff; }
.ic { color:#F0997B; } .ib { background:#993C1D; color:#fff; }

.tg { background:rgba(83,74,183,.2);  color:#AFA9EC; border:1px solid #534AB7; }
.tt { background:rgba(15,110,86,.2);  color:#5DCAA5; border:1px solid #0F6E56; }
.tp { background:rgba(133,79,11,.2);  color:#EF9F27; border:1px solid #854F0B; }
.ti { background:rgba(153,60,29,.2);  color:#F0997B; border:1px solid #993C1D; }

.hub-info   { background:#060606; border:1px solid #181818; border-radius:10px;
              padding:12px 16px; font-family:'Courier New',monospace;
              font-size:.74rem; color:#444; }
.hub-sb     { background:#050505; border:1px solid #1a1a1a; border-radius:10px;
              padding:10px 14px; font-family:'Courier New',monospace; }
.hub-sb-row { display:flex; justify-content:space-between; padding:4px 0;
              border-bottom:1px solid #0e0e0e; font-size:.76rem; }
.hub-sb-row:last-child { border:none; }

.hub-insert { text-align:center; font-family:'Courier New',monospace;
              font-size:.88rem; letter-spacing:.2em; color:#FFE600;
              animation:hub-blink 1s step-end infinite; }
@keyframes hub-blink { 50%{ opacity:0; } }

.pdiv { display:flex; gap:3px; justify-content:center; margin:10px 0; }
.pdot { width:5px; height:5px; border-radius:1px; display:inline-block; }
</style>
""", unsafe_allow_html=True)

# ── 사이드바 ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🕹️ 오락실 설정")
    render_bgm_toggle("hub", compact=False)
    st.markdown("---")

    st.markdown("### 🏆 HI-SCORE")
    for g, meta in GAME_META.items():
        hi = get_hi_score(g)
        col = {"galaga":"#AFA9EC","tetris":"#5DCAA5","pacman":"#FFE600","space_invaders":"#F0997B"}[g]
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;'
            f'font-family:monospace;font-size:.8rem;padding:3px 0;">'
            f'<span>{meta["icon"]} {meta["label"]}</span>'
            f'<span style="color:{col};">{hi:,}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🪙 크레딧")
    credit_display()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🪙 +1", key="sb_add1"):
            add_credit(1); play_sfx("coin"); st.rerun()
    with c2:
        if st.button("🪙🪙 +3", key="sb_add3"):
            add_credit(3); play_sfx("coin"); st.rerun()

    st.markdown("---")
    st.markdown("### 🔗 게임 포트")
    for label, port in [("🚀 갤러그","8501"),("🧱 테트리스","8502"),
                         ("😮 팩맨","8503"),("👾 인베이더","8504")]:
        st.markdown(
            f'<div style="font-family:monospace;font-size:.76rem;padding:2px 0;">'
            f'{label} → <span style="color:#AFA9EC;">:{port}</span></div>',
            unsafe_allow_html=True,
        )

# ── 헤더 ──────────────────────────────────────────────────────────
st.markdown('<div class="hub-title">🕹️ 추억의 오락실</div>', unsafe_allow_html=True)
st.markdown('<div class="hub-sub">RETRO ARCADE COLLECTION · PYTHON + STREAMLIT</div>',
            unsafe_allow_html=True)
st.markdown("")

# ── 탭 ────────────────────────────────────────────────────────────
tab_game, tab_rank, tab_credit = st.tabs(["🎮 게임 선택", "🏆 전체 랭킹", "📜 크레딧"])

# ── 게임 선택 탭 ──────────────────────────────────────────────────
with tab_game:
    st.markdown("""
<div class="hub-grid">
  <div class="hub-card card-galaga">
    <div class="card-num gc">①</div>
    <span class="card-emoji">🚀</span>
    <div class="card-title gc">GALAGA 갤러그</div>
    <div class="card-meta">NAMCO · 1981 · VERTICAL SHOOTER</div>
    <div class="card-desc">우주 편대를 격추하는 종스크롤 슈팅.<br>보스 캡처 빔을 역이용해 더블파이터!</div>
    <div class="card-tags">
      <span class="hub-tag tg">슈팅</span>
      <span class="hub-tag tg">편대</span>
      <span class="hub-tag tg">보스전</span>
    </div>
    <a href="http://localhost:8501" target="_blank" class="card-btn gb">▶ PLAY →</a>
  </div>
  <div class="hub-card card-tetris">
    <div class="card-num tc">②</div>
    <span class="card-emoji">🧱</span>
    <div class="card-title tc">TETRIS 테트리스</div>
    <div class="card-meta">ALEXEY PAJITNOV · 1984 · PUZZLE</div>
    <div class="card-desc">7종 테트로미노를 쌓는 블록 퍼즐.<br>4줄 동시 소거로 TETRIS 보너스!</div>
    <div class="card-tags">
      <span class="hub-tag tt">퍼즐</span>
      <span class="hub-tag tt">7종 블록</span>
      <span class="hub-tag tt">홀드</span>
    </div>
    <a href="http://localhost:8502" target="_blank" class="card-btn tb">▶ PLAY →</a>
  </div>
  <div class="hub-card card-pacman">
    <div class="card-num pc">③</div>
    <span class="card-emoji">😮</span>
    <div class="card-title pc">PAC-MAN 팩맨</div>
    <div class="card-meta">NAMCO · 1980 · MAZE ACTION</div>
    <div class="card-desc">파란 미로를 누비며 모든 점 먹기.<br>파워팰릿(●)으로 고스트를 역으로 잡아먹어요!</div>
    <div class="card-tags">
      <span class="hub-tag tp">미로</span>
      <span class="hub-tag tp">고스트 AI</span>
      <span class="hub-tag tp">파워업</span>
    </div>
    <a href="http://localhost:8503" target="_blank" class="card-btn pb">▶ PLAY →</a>
  </div>
  <div class="hub-card card-invaders">
    <div class="card-num ic">④</div>
    <span class="card-emoji">👾</span>
    <div class="card-title ic">SPACE INVADERS</div>
    <div class="card-meta">TAITO · 1978 · FIXED SHOOTER</div>
    <div class="card-desc">내려오는 침략자를 방어막으로 막으며 격추!<br>UFO를 맞추면 랜덤 보너스!</div>
    <div class="card-tags">
      <span class="hub-tag ti">슈팅</span>
      <span class="hub-tag ti">방어막</span>
      <span class="hub-tag ti">UFO</span>
    </div>
    <a href="http://localhost:8504" target="_blank" class="card-btn ib">▶ PLAY →</a>
  </div>
</div>
""", unsafe_allow_html=True)

    # 픽셀 구분선
    colors = ["#534AB7","#0F6E56","#854F0B","#993C1D"]
    dots = "".join(
        f'<div class="pdot" style="background:{colors[i%4]};opacity:{.28+.08*(i%3)};"></div>'
        for i in range(32)
    )
    st.markdown(f'<div class="pdiv">{dots}</div>', unsafe_allow_html=True)

    # 하단 실행 안내 + 포트 표
    col_info, col_sb = st.columns([2, 1])
    with col_info:
        st.markdown("""
<div class="hub-info">
  <b>🛠️ 실행 방법</b><br><br>
  <code>pip install streamlit</code><br><br>
  각 게임 폴더에서 아래 명령어를 실행하세요:<br><br>
  <code>cd galaga         &amp;&amp; streamlit run app.py --server.port 8501</code><br>
  <code>cd tetris         &amp;&amp; streamlit run app.py --server.port 8502</code><br>
  <code>cd pacman         &amp;&amp; streamlit run app.py --server.port 8503</code><br>
  <code>cd space_invaders &amp;&amp; streamlit run app.py --server.port 8504</code>
</div>
""", unsafe_allow_html=True)
    with col_sb:
        port_map = {"galaga":"8501","tetris":"8502","pacman":"8503","space_invaders":"8504"}
        acol_map = {"galaga":"#AFA9EC","tetris":"#5DCAA5","pacman":"#FFE600","space_invaders":"#F0997B"}
        rows_html = ""
        for g, meta in GAME_META.items():
            rows_html += (
                f'<div class="hub-sb-row">'
                f'<span>{meta["icon"]} {meta["label"]}</span>'
                f'<span style="color:{acol_map[g]};">:{port_map[g]}</span></div>'
            )
        st.markdown(f'<div class="hub-sb">{rows_html}</div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="hub-insert">── INSERT COIN TO PLAY ──</div>',
                unsafe_allow_html=True)

# ── 전체 랭킹 탭 ──────────────────────────────────────────────────
with tab_rank:
    render_all_rankings(theme_key="hub")

# ── 크레딧 탭 ─────────────────────────────────────────────────────
with tab_credit:
    render_credits_scroll(theme_key="hub")
    st.markdown("")
    render_credits_screen(theme_key="hub")