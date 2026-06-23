"""
arcade/common/__init__.py
공통 모듈 패키지 초기화 (수정 버전)
"""

__version__ = "1.1.0"

__all__ = [
    "theme", "insert_coin", "scoreboard",
    "bgm", "fullscreen", "key_guide", "credits",
]

from common.theme import (
    THEMES, apply_theme, get_base_css, get_game_css,
)
from common.insert_coin import (
    render_coin_screen, coin_button, credit_display,
    get_credits, add_credit, use_credit, reset_credits,
)
from common.scoreboard import (
    save_score, get_hi_score, get_nickname, set_nickname,
    render_score_panel, render_ranking_table,
    render_nickname_entry, render_all_rankings,
    clear_rankings, GAME_META,
)
from common.bgm import (
    init_audio, play_sfx, render_bgm_toggle,
    is_bgm_on, is_sfx_on, get_volume,
)
from common.fullscreen import (
    inject_fullscreen_css, render_fullscreen_btn,
    render_fullscreen_wrapper, fullscreen_status_badge,
)
from common.key_guide import (
    render_key_guide, render_key_overlay,
    render_key_badge_row, get_key_map,
)
from common.credits import (
    render_credits_footer, render_credits_badge,
    render_credits_scroll, render_credits_screen,
    get_game_info, GAME_CREDITS, DEV_CREDITS,
)
