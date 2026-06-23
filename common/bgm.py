"""
arcade/common/bgm.py
BGM 토글 & 사운드 시스템 (싱글톤 오디오 매니저 수정 버전)
"""
import streamlit as st
from common.theme import THEMES
import streamlit.components.v1 as components
import json  # 패턴 데이터 직렬화를 위해 추가

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
    "galaga":         [[262,0.15],[330,0.15],[392,0.15],[523,0.15],[392,0.15],[330,0.15]],
    "tetris":         [[659,0.2],[494,0.1],[523,0.1],[587,0.2],[523,0.1],[494,0.1],[440,0.2]],
    "pacman":         [[494,0.1],[523,0.1],[587,0.1],[659,0.1],[587,0.1],[523,0.1]],
    "space_invaders": [[110,0.1],[110,0.1],[165,0.1],[110,0.1]],
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
    
    # JS 내부에 전달할 때 백슬래시 및 개행 안전하게 이스케이프 처리
    escaped_script = script.replace("\\", "\\\\").replace("`", "\\`").replace("\n", " ")
    
    html = f"""
<script>
(function(){{
  var parentWin = null;
  try {{
    if (window.parent && window.parent.document) {{
      parentWin = window.parent;
    }}
  }} catch (e) {{}}
  var win = parentWin || window;
  
  // 전역 매니저가 존재하는 경우 오디오 컨텍스트 재사용
  if (win.__arcade_audio_manager) {{
    win.__arcade_audio_manager.playSfx(`{escaped_script}`);
  }} else {{
    // 로컬 폴백 (매니저 로드 전이거나 크로스오리진 격리 상태 대비)
    try {{
      var ctx = new (window.AudioContext || window.webkitAudioContext)();
      var vol = {vol:.2f};
      var t = ctx.currentTime + 0.01;
      {script}
    }} catch(e) {{ console.warn('SFX Error:', e); }}
  }}
}})();
</script>"""
    components.html(
        html,
        height=0,
        scrolling=False
    )


def init_audio(game="galaga"):
    """BGM 초기화 및 오디오 상태 동기화 (MUTE 대응을 위해 항상 실행되어야 함)."""
    _ensure()
    vol     = get_volume()
    bgm_on  = "true" if is_bgm_on() else "false"
    sfx_on  = "true" if is_sfx_on() else "false"
    
    patterns_json = json.dumps(_BGM_PATTERNS)
    
    html = f"""
<script>
(function(){{
  // 1. 메인 창(부모 윈도우) 참조 시도 (크로스 도메인 에러 가드 구현)
  var parentDoc = null;
  var parentWin = null;
  try {{
    if (window.parent && window.parent.document) {{
      parentDoc = window.parent.document;
      parentWin = window.parent;
    }}
  }} catch (e) {{
    console.warn("Parent access blocked (cross-origin or sandboxed):", e);
  }}
  
  var doc = parentDoc || document;
  var win = parentWin || window;

  // 2. 부모 창 전역 스코프에 싱글톤 오디오 매니저 선언 (Streamlit Rerun 시 유지됨)
  if (!win.__arcade_audio_manager) {{
    win.__arcade_audio_manager = {{
      ctx: null,
      bgmActive: false,
      bgmCurrentGame: null,
      bgmTimeoutId: null,
      volume: {vol:.2f},
      bgmOn: {bgm_on},
      sfxOn: {sfx_on},
      bgmGame: null,
      
      initCtx: function() {{
        if (this.ctx) return this.ctx;
        try {{
          var AudioContextClass = win.AudioContext || win.webkitAudioContext;
          this.ctx = new AudioContextClass();
          this.setupUnlock();
        }} catch(e) {{
          console.error("AudioContext initialization failed:", e);
        }}
        return this.ctx;
      }},
      
      // 브라우저 자동 재생(Autoplay Policy) 해제를 위한 상호작용 리스너 등록
      setupUnlock: function() {{
        var self = this;
        function unlock() {{
          if (self.ctx && self.ctx.state === 'suspended') {{
            self.ctx.resume().then(function() {{
              console.log("AudioContext unlocked and resumed.");
            }});
          }}
          ['click', 'touchstart', 'keydown'].forEach(function(evt) {{
            doc.removeEventListener(evt, unlock);
            document.removeEventListener(evt, unlock);
          }});
        }}
        ['click', 'touchstart', 'keydown'].forEach(function(evt) {{
          doc.addEventListener(evt, unlock, {{ passive: true }});
          document.addEventListener(evt, unlock, {{ passive: true }});
        }});
      }},
      
      stopBgm: function() {{
        this.bgmActive = false;
        if (this.bgmTimeoutId) {{
          clearTimeout(this.bgmTimeoutId);
          this.bgmTimeoutId = null;
        }}
        this.bgmCurrentGame = null;
      }},
      
      playBgm: function(game, patterns) {{
        var self = this;
        this.bgmGame = game;
        if (!this.bgmOn) {{
          this.stopBgm();
          return;
        }}
        
        this.initCtx();
        if (!this.ctx) return;
        
        // 이미 해당 게임 BGM이 재생 중이라면 중복 플레이 차단 (핵심 버그 수정)
        if (this.bgmActive && this.bgmCurrentGame === game) {{
          return;
        }}
        
        this.stopBgm();
        this.bgmActive = true;
        this.bgmCurrentGame = game;
        
        var notes = patterns[game] || patterns["galaga"];
        var idx = 0;
        
        function next() {{
          if (!self.bgmActive || !self.bgmOn) return;
          
          // 오디오 상태가 대기 중(suspended)이라면 자동 재생이 풀릴 때까지 대기
          if (self.ctx.state === 'suspended') {{
            self.bgmTimeoutId = setTimeout(next, 500);
            return;
          }}
          
          var n = notes[idx % notes.length];
          var o = self.ctx.createOscillator();
          var g = self.ctx.createGain();
          o.connect(g);
          g.connect(self.ctx.destination);
          
          o.type = 'square';
          o.frequency.setValueAtTime(n[0], self.ctx.currentTime);
          
          // BGM의 전체적인 밸런스를 위해 기본 볼륨 스케일 조절
          var noteVolume = self.volume * 0.15;
          g.gain.setValueAtTime(noteVolume, self.ctx.currentTime);
          g.gain.exponentialRampToValueAtTime(0.001, self.ctx.currentTime + n[1] * 0.85);
          
          o.start(self.ctx.currentTime);
          o.stop(self.ctx.currentTime + n[1]);
          
          idx++;
          self.bgmTimeoutId = setTimeout(next, n[1] * 1000 - 15);
        }}
        
        next();
      }},
      
      playSfx: function(scriptStr) {{
        if (!this.sfxOn) return;
        this.initCtx();
        if (!this.ctx) return;
        
        var ctx = this.ctx;
        var vol = this.volume;
        var t = ctx.currentTime + 0.01;
        
        try {{
          eval(scriptStr);
        }} catch(e) {{
          console.warn("SFX Execution error:", e);
        }}
      }}
    }};
  }}
  
  // 3. 현재 Rerun을 통해 변경된 설정(볼륨, 온오프) 즉시 전역 매니저에 동기화
  var mgr = win.__arcade_audio_manager;
  mgr.volume = {vol:.2f};
  mgr.bgmOn = {bgm_on};
  mgr.sfxOn = {sfx_on};
  
  if (mgr.bgmOn) {{
    mgr.playBgm("{game}", {patterns_json});
  }} else {{
    mgr.stopBgm();
  }}
}})();
</script>"""
    components.html(
        html,
        height=0,
        scrolling=False
    )


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
                init_audio(game)  # 상태 변경 후 즉각적인 신호 전달을 위해 먼저 초기화
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
        lbl = "🎵 BGM ON" if is_bgm_on() else "🔇 BGM OFF"
        if st.button(lbl, key=f"bgm_f_{theme_key}"):
            st.session_state[_BGM_ON_KEY] = not is_bgm_on()
            init_audio(game)  # 상태 변경 후 즉각적인 신호 전달을 위해 먼저 초기화
            st.rerun()
    with c2:
        lbl2 = "🔊 SFX ON" if is_sfx_on() else "🔕 SFX OFF"
        if st.button(lbl2, key=f"sfx_f_{theme_key}"):
            st.session_state[_SFX_ON_KEY] = not is_sfx_on()
            st.rerun()

    new_vol = st.slider("볼륨", 0.0, 1.0, get_volume(), 0.05,
                        key=f"vol_{theme_key}", label_visibility="collapsed")
    if abs(new_vol - get_volume()) > 0.01:
        st.session_state[_VOLUME_KEY] = new_vol
        init_audio(game)  # 볼륨 변경 시 전역 오디오 매니저에 새로운 볼륨 설정값 실시간 전달