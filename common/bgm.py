"""
arcade/common/bgm.py
BGM 토글 & 사운드 시스템 (수정 버전)
"""
import streamlit as st
from common.theme import THEMES

_BGM_ON_KEY  = "audio_bgm_on"
_SFX_ON_KEY  = "audio_sfx_on"
_VOLUME_KEY  = "audio_volume"


def _ensure():
    st.session_state.setdefault(_BGM_ON_KEY, True)
    st.session_state.setdefault(_SFX_ON_KEY, True)
    st.session_state.setdefault(_VOLUME_KEY, 0.3)


def is_bgm_on():
    _ensure()
    return st.session_state[_BGM_ON_KEY]


def is_sfx_on():
    _ensure()
    return st.session_state[_SFX_ON_KEY]


def get_volume():
    _ensure()
    return st.session_state[_VOLUME_KEY]


# ── Web Audio 효과음 JS 스니펫 ─────────────────────────────────
_SFX_SCRIPTS = {
    "shoot": """
        var o=ctx.createOscillator(),g=ctx.createGain();
        o.connect(g);g.connect(ctx.destination);
        o.frequency.setValueAtTime(880,t);
        o.frequency.exponentialRampToValueAtTime(220,t+0.08);
        g.gain.setValueAtTime(vol,t);
        g.gain.exponentialRampToValueAtTime(0.001,t+0.09);
        o.start(t);o.stop(t+0.1);
    """,
    "explosion": """
        var buf=ctx.createBuffer(1,Math.floor(ctx.sampleRate*0.3),ctx.sampleRate);
        var d=buf.getChannelData(0);
        for(var i=0;i<d.length;i++) d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,1.5);
        var src=ctx.createBufferSource(),g=ctx.createGain();
        src.buffer=buf;src.connect(g);g.connect(ctx.destination);
        g.gain.setValueAtTime(vol,t);
        g.gain.exponentialRampToValueAtTime(0.001,t+0.3);
        src.start(t);
    """,
    "coin": """
        [523,659,784,1047].forEach(function(f,i){
            var o=ctx.createOscillator(),g=ctx.createGain();
            o.connect(g);g.connect(ctx.destination);
            o.type='square';o.frequency.value=f;
            g.gain.setValueAtTime(vol*0.5,t+i*0.07);
            g.gain.exponentialRampToValueAtTime(0.001,t+i*0.07+0.1);
            o.start(t+i*0.07);o.stop(t+i*0.07+0.12);
        });
    """,
    "gameover": """
        [440,392,349,262].forEach(function(f,i){
            var o=ctx.createOscillator(),g=ctx.createGain();
            o.connect(g);g.connect(ctx.destination);
            o.type='sawtooth';o.frequency.value=f;
            g.gain.setValueAtTime(vol*0.6,t+i*0.18);
            g.gain.exponentialRampToValueAtTime(0.001,t+i*0.18+0.22);
            o.start(t+i*0.18);o.stop(t+i*0.18+0.25);
        });
    """,
    "clear": """
        [523,659,784,880,1047].forEach(function(f,i){
            var o=ctx.createOscillator(),g=ctx.createGain();
            o.connect(g);g.connect(ctx.destination);
            o.type='square';o.frequency.value=f;
            g.gain.setValueAtTime(vol*0.5,t+i*0.09);
            g.gain.exponentialRampToValueAtTime(0.001,t+i*0.09+0.12);
            o.start(t+i*0.09);o.stop(t+i*0.09+0.14);
        });
    """,
    "powerup": """
        var o=ctx.createOscillator(),g=ctx.createGain();
        o.connect(g);g.connect(ctx.destination);
        o.type='square';
        o.frequency.setValueAtTime(220,t);
        o.frequency.exponentialRampToValueAtTime(880,t+0.2);
        g.gain.setValueAtTime(vol*0.4,t);
        g.gain.exponentialRampToValueAtTime(0.001,t+0.22);
        o.start(t);o.stop(t+0.25);
    """,
    "eat_dot": """
        var o=ctx.createOscillator(),g=ctx.createGain();
        o.connect(g);g.connect(ctx.destination);
        o.frequency.setValueAtTime(440,t);
        g.gain.setValueAtTime(vol*0.12,t);
        g.gain.exponentialRampToValueAtTime(0.001,t+0.04);
        o.start(t);o.stop(t+0.05);
    """,
    "eat_ghost": """
        [880,1047,880].forEach(function(f,i){
            var o=ctx.createOscillator(),g=ctx.createGain();
            o.connect(g);g.connect(ctx.destination);
            o.type='square';o.frequency.value=f;
            g.gain.setValueAtTime(vol*0.4,t+i*0.06);
            g.gain.exponentialRampToValueAtTime(0.001,t+i*0.06+0.07);
            o.start(t+i*0.06);o.stop(t+i*0.06+0.08);
        });
    """,
    "line_clear": """
        [262,330,392,523].forEach(function(f,i){
            var o=ctx.createOscillator(),g=ctx.createGain();
            o.connect(g);g.connect(ctx.destination);
            o.type='square';o.frequency.value=f;
            g.gain.setValueAtTime(vol*0.5,t+i*0.06);
            g.gain.exponentialRampToValueAtTime(0.001,t+i*0.06+0.1);
            o.start(t+i*0.06);o.stop(t+i*0.06+0.12);
        });
    """,
    "ufo": """
        var o=ctx.createOscillator(),g=ctx.createGain();
        o.connect(g);g.connect(ctx.destination);
        o.type='sawtooth';
        o.frequency.setValueAtTime(110,t);
        o.frequency.setValueAtTime(220,t+0.1);
        o.frequency.setValueAtTime(110,t+0.2);
        g.gain.setValueAtTime(vol*0.3,t);
        g.gain.exponentialRampToValueAtTime(0.001,t+0.3);
        o.start(t);o.stop(t+0.32);
    """,
}

_BGM_PATTERNS = {
    "galaga":         "[[262,0.15],[330,0.15],[392,0.15],[523,0.15],[392,0.15],[330,0.15]]",
    "tetris":         "[[659,0.2],[494,0.1],[523,0.1],[587,0.2],[523,0.1],[494,0.1],[440,0.2]]",
    "pacman":         "[[494,0.1],[523,0.1],[587,0.1],[659,0.1],[587,0.1],[523,0.1]]",
    "space_invaders": "[[110,0.1],[110,0.1],[165,0.1],[110,0.1]]",
}


def play_sfx(sfx_name):
    """효과음 재생 (SFX ON 상태에서만)."""
    _ensure()
    if not is_sfx_on():
        return
    script = _SFX_SCRIPTS.get(sfx_name, "")
    if not script:
        return
    vol = get_volume()
    html = f"""
<script>
(function(){{
  try {{
    var ctx=new(window.AudioContext||window.webkitAudioContext)();
    var vol={vol:.2f};
    var t=ctx.currentTime+0.01;
    {script}
  }} catch(e) {{ console.warn('SFX error:', e); }}
}})();
</script>"""
    st.markdown(html, unsafe_allow_html=True)


def init_audio(game="galaga"):
    """BGM 초기화."""
    _ensure()
    if not is_bgm_on():
        return
    vol     = get_volume()
    pattern = _BGM_PATTERNS.get(game, _BGM_PATTERNS["galaga"])
    html = f"""
<script>
(function(){{
  if(window._arcadeBgmActive) return;
  try {{
    var ctx=new(window.AudioContext||window.webkitAudioContext)();
    window._arcadeBgmActive=true;
    var vol={vol:.2f};
    var notes={pattern};
    var idx=0;
    var t=ctx.currentTime;
    function next(){{
      if(!window._arcadeBgmActive) return;
      var n=notes[idx%notes.length];
      var o=ctx.createOscillator();
      var g=ctx.createGain();
      o.connect(g);g.connect(ctx.destination);
      o.type='square';o.frequency.value=n[0];
      g.gain.setValueAtTime(vol*0.2,t);
      g.gain.exponentialRampToValueAtTime(0.001,t+n[1]*0.85);
      o.start(t);o.stop(t+n[1]);
      t+=n[1];idx++;
      setTimeout(next,n[1]*1000-20);
    }}
    next();
  }} catch(e){{ console.warn('BGM error:',e); }}
}})();
</script>"""
    st.markdown(html, unsafe_allow_html=True)


def render_bgm_toggle(theme_key="galaga", game=None, compact=False):
    """BGM + SFX 토글."""
    _ensure()
    t    = THEMES.get(theme_key, THEMES["galaga"])
    game = game or theme_key

    if compact:
        c1, c2 = st.columns(2)
        with c1:
            lbl = "🎵 ON" if is_bgm_on() else "🔇 OFF"
            if st.button(f"BGM {lbl}", key=f"bgm_c_{theme_key}"):
                st.session_state[_BGM_ON_KEY] = not is_bgm_on()
                if is_bgm_on():
                    init_audio(game)
                st.rerun()
        with c2:
            lbl2 = "🔊 ON" if is_sfx_on() else "🔕 OFF"
            if st.button(f"SFX {lbl2}", key=f"sfx_c_{theme_key}"):
                st.session_state[_SFX_ON_KEY] = not is_sfx_on()
                st.rerun()
        return

    # 풀 패널
    st.markdown(
        f'<div style="font-size:0.7rem;color:{t["accent"]};'
        f'letter-spacing:0.15em;margin-bottom:8px;font-family:monospace;">🎵 SOUND</div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        lbl = "🔇 BGM OFF" if is_bgm_on() else "🎵 BGM ON"
        if st.button(lbl, key=f"bgm_f_{theme_key}"):
            st.session_state[_BGM_ON_KEY] = not is_bgm_on()
            if is_bgm_on():
                init_audio(game)
            st.rerun()
    with c2:
        lbl2 = "🔕 SFX OFF" if is_sfx_on() else "🔊 SFX ON"
        if st.button(lbl2, key=f"sfx_f_{theme_key}"):
            st.session_state[_SFX_ON_KEY] = not is_sfx_on()
            st.rerun()

    new_vol = st.slider("볼륨", 0.0, 1.0, get_volume(), 0.05,
                        key=f"vol_{theme_key}", label_visibility="collapsed")
    if abs(new_vol - get_volume()) > 0.01:
        st.session_state[_VOLUME_KEY] = new_vol
