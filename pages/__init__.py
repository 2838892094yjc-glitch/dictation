"""
页面模块包
包含各个独立的页面组件
"""

from .vocabulary_page import render_vocabulary_page
from .dictation_page import render_dictation_page
from .answer_page import render_answer_page
from .history_page import render_history_page
from .wrong_answers_page import render_wrong_answers_page

__all__ = [
    'render_vocabulary_page',
    'render_dictation_page',
    'render_answer_page',
    'render_history_page',
    'render_wrong_answers_page',
]
