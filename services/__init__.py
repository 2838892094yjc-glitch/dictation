"""
听写服务模块

提供听写相关的业务逻辑服务。
"""

from .dictation_service import (
    get_display_text,
    get_correct_answer,
    check_answer,
    get_mode_name,
    get_placeholder_text,
    DictationMode,
)

__all__ = [
    'get_display_text',
    'get_correct_answer',
    'check_answer',
    'get_mode_name',
    'get_placeholder_text',
    'DictationMode',
]
