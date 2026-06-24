import sys
import os

# 현재 파일(key_guide.py) 기준 프로젝트 상위 디렉토리를 찾아 sys.path에 수동으로 주입합니다.
# 이를 통해 하위 폴더에서 단독 실행 시에도 'common' 패키지를 정상 인식합니다.
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_CURRENT_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

import streamlit as st
from common.theme import THEMES

_KEY_MAPS = {
    "galaga": {
        "title": "🚀 갤러그 조작키",
        "controls": [
            ("◀ / ▶",    "전투기 좌우 이동"),
            ("◀◀ / ▶▶",  "2칸 빠른 이동"),
            ("🔴 FIRE",   "미사일 발사"),
        ],
        "tips": [
            "보스 갤러그의 캡처 빔을 역이용해 더블파이터!",
            "도전 스테이지에서 명중률 100%를 노려보세요!",
        ],
    },
    "tetris": {
        "title": "🧱 테트리스 조작키",
        "controls": [
            ("◀ LEFT",      "블록 왼쪽 이동"),
            ("RIGHT ▶",     "블록 오른쪽 이동"),
            ("↺ ROTATE",    "블록 회전"),
            ("▼ SOFT DROP", "천천히 낙하"),
            ("⬇ HARD DROP", "즉시 낙하"),
        ],
        "tips": [
            "고스트 블록으로 착지점을 예측하세요!",
            "4줄 동시 소거 = TETRIS 보너스!",
        ],
    },
    "pacman": {
        "title": "😮 팩맨 조작키",
        "controls": [
            ("▲ UP",    "위로 이동"),
            ("▼ DOWN",  "아래로 이동"),
            ("◀ LEFT",  "왼쪽으로 이동"),
            ("▶ RIGHT", "오른쪽으로 이동"),
        ],
        "tips": [
            "파워팰릿(●)으로 고스트를 잡아먹으세요!",
            "터널(좌↔우)로 고스트를 따돌리세요.",
        ],
    },
    "space_invaders": {
        "title": "👾 스페이스 인베이더 조작키",
        "controls": [
            ("◀ / ▶",    "포탑 이동"),
            ("◀◀ / ▶▶",  "2칸 빠른 이동"),
            ("🔴 FIRE",   "미사일 발사"),
        ],
        "tips": [
            "방어막 뒤에서 적 총알을 막으세요!",
            "UFO를 맞추면 최대 300점 보너스!",
        ],
    },
}

def render_key_guide(game, theme_key=None, show_tips=True, show_common=True):
    tk  = theme_key or game
    t   = THEMES.get(tk, THEMES["galaga"])
    cfg = _KEY_MAPS.get(game, _KEY_MAPS["galaga"])

    rows_html = ""
    for key, desc in cfg["controls"]:
        rows_html += f"""
<div style="display:flex;justify-content:space-between;align-items:center;
     padding:4px 0;border-bottom:0.5px solid {t['bg']};">
  <span style="display:inline-block;background:{t['bg']};border:1px solid {t['border']};
        border-radius:4px;padding:1px 8px;color:{t['accent']};
        font-size:0.78rem;min-width:90px;text-align:center;">{key}</span>
  <span style="font-size:0.78rem;color:{t['text']};opacity:0.85;">{desc}</span>
</div>"""

    tips_html = ""
    if show_tips:
        for tip in cfg["tips"]:
            tips_html += f'<div style="font-size:0.77rem;color:{t["sub_text"]};padding:2px 0;">▸ {tip}</div>'
        tips_html = f'<div style="margin-top:8px;padding-top:6px;border-top:1px solid {t["border"]};">{tips_html}</div>'

    common_html = ""
    if show_common:
        common_html = f"""
<div style="margin-top:8px;padding-top:6px;border-top:1px solid {t['border']};">
  <div style="font-size:0.68rem;color:{t['sub_text']};letter-spacing:0.12em;margin-bottom:4px;">── 공통 ──</div>
  <div style="font-size:0.77rem;color:{t['sub_text']};">🪙 INSERT COIN: 게임 시작</div>
  <div style="font-size:0.77rem;color:{t['sub_text']};">⛶ 전체화면: 더블클릭</div>
</div>"""

    # 🔗 조작키 정상 작동을 보장하는 스마트 포커싱 JavaScript 탑재
    focus_script = """
<script>
(function() {
  var doc = window.parent ? window.parent.document : document;
  
  function restoreGameFocus() {
    // 1. 메인 창 또는 iframe 내부의 canvas 요소 검색
    var canvas = document.querySelector('canvas');
    if (!canvas && window.parent && window.parent.document) {
      canvas = window.parent.document.querySelector('canvas');
    }
    if (canvas) {
      canvas.focus();
      return;
    }
    
    // 2. 만약 게임엔진이 별도의 대형 iframe 내에서 실행 중이라면 해당 iframe 포커싱
    var iframes = doc.querySelectorAll('iframe');
    for (var i = 0; i < iframes.length; i++) {
      var iframe = iframes[i];
      // 크기가 존재하고 사운드 전용(0px)이 아닌 실제 게임용 화면 iframe 감지
      if (iframe.offsetWidth > 100 && iframe.offsetHeight > 100) {
        iframe.focus();
        try {
          if (iframe.contentWindow && iframe.contentWindow.document) {
            var innerCanvas = iframe.contentWindow.document.querySelector('canvas');
            if (innerCanvas) {
              innerCanvas.focus();
            }
          }
        } catch(e) {}
        break;
      }
    }
  }

  // 사용자가 페이지의 빈 곳, 사이드바, 가이드 등을 클릭하면 자동으로 게임 화면으로 조작 포커스 리다이렉트
  doc.addEventListener('click', restoreGameFocus, true);
  document.addEventListener('click', restoreGameFocus, true);
  
  // 컴포넌트 마운트 즉시 0.5초 대기 후 게임 포커스 자동 확보
  setTimeout(restoreGameFocus, 500);
})();
</script>
"""

    st.markdown(f"""
<div style="background:{t['panel_bg']};border:1px solid {t['border']};
     border-radius:10px;padding:12px 14px;font-family:'Courier New',monospace;">
  <div style="font-size:0.88rem;font-weight:bold;color:{t['accent']};
       letter-spacing:0.12em;margin-bottom:8px;border-bottom:1px solid {t['border']};
       padding-bottom:5px;">{cfg['title']}</div>
  {rows_html}
  {tips_html}
  {common_html}
</div>
{focus_script}
""", unsafe_allow_html=True)

def render_key_overlay(game, theme_key=None):
    cfg = _KEY_MAPS.get(game, _KEY_MAPS["galaga"])
    with st.expander(f"❓ 조작키 안내 — {cfg['title']}", expanded=False):
        render_key_guide(game, theme_key=theme_key, show_tips=True, show_common=True)


def render_key_badge_row(game, theme_key=None):
    tk  = theme_key or game
    t   = THEMES.get(tk, THEMES["galaga"])
    cfg = _KEY_MAPS.get(game, _KEY_MAPS["galaga"])
    badges = " &nbsp; ".join(
        f'<span style="display:inline-block;background:{t["panel_bg"]};'
        f'border:1px solid {t["border"]};border-radius:4px;padding:1px 7px;'
        f'color:{t["accent"]};font-family:monospace;font-size:0.78rem;">{k}</span>'
        for k, _ in cfg["controls"]
    )
    st.markdown(
        f'<div style="font-family:monospace;font-size:0.75rem;color:{t["sub_text"]};'
        f'padding:6px 0;text-align:center;">{badges}</div>',
        unsafe_allow_html=True,
    )


def get_key_map(game):
    return _KEY_MAPS.get(game, {})