"""
arcade/common/fullscreen.py
전체화면 컴포넌트 (수정 버전 - JS 오류 수정)
"""
import streamlit as st
from common.theme import THEMES


def inject_fullscreen_css(theme_key="galaga"):
    t = THEMES.get(theme_key, THEMES["galaga"])
    st.markdown(f"""
<style>
.fs-wrap {{ display:inline-block; cursor:pointer; }}
.fs-esc  {{ font-size:0.72rem; color:{t['sub_text']}; font-family:monospace;
            margin-left:8px; }}
</style>
""", unsafe_allow_html=True)


def render_fullscreen_btn(theme_key="galaga", target_id="game-board",
                          label="⛶  전체화면", show_hint=True):
    t = THEMES.get(theme_key, THEMES["galaga"])
    hint = f'<span class="fs-esc">ESC 키로 해제</span>' if show_hint else ""
    st.markdown(f"""
<button id="arcade-fs-btn-{target_id}"
  onclick="(function(){{
    var el=document.getElementById('{target_id}')||document.documentElement;
    if(document.fullscreenElement){{
      document.exitFullscreen&&document.exitFullscreen();
    }} else {{
      el.requestFullscreen&&el.requestFullscreen();
    }}
  }})()"
  style="background:{t['panel_bg']};color:{t['accent']};border:1px solid {t['border']};
         border-radius:6px;padding:6px 14px;font-family:'Courier New',monospace;
         font-size:0.85rem;letter-spacing:0.1em;cursor:pointer;">
  {label}
</button>{hint}
""", unsafe_allow_html=True)


def render_fullscreen_wrapper(content_html, theme_key="galaga", element_id="game-board"):
    t = THEMES.get(theme_key, THEMES["galaga"])
    st.markdown(f"""
<div id="{element_id}" ondblclick="(function(){{
  var el=document.getElementById('{element_id}');
  if(document.fullscreenElement){{
    document.exitFullscreen&&document.exitFullscreen();
  }} else {{
    el.requestFullscreen&&el.requestFullscreen();
  }}
}})()" title="더블클릭: 전체화면" style="display:inline-block;">
  {content_html}
</div>
<div style="font-size:0.7rem;color:{t['sub_text']};font-family:monospace;
     margin-top:3px;text-align:center;">더블클릭 → 전체화면</div>
""", unsafe_allow_html=True)


def fullscreen_status_badge(theme_key="galaga"):
    pass  # 간소화 - JS 복잡도 제거
