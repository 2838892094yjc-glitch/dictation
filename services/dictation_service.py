"""
听写服务模块

提供听写相关的业务逻辑，包括：
- 根据模式获取显示文本
- 根据模式获取正确答案
- 检查答案是否正确
- 获取模式的中文名称
- 获取输入框占位符文本
"""

from enum import Enum
from typing import TypedDict


class DictationMode(str, Enum):
    """听写模式枚举"""
    EN_TO_CN = "en_to_cn"  # 英译中
    CN_TO_EN = "cn_to_en"  # 中译英
    SPELL = "spell"        # 拼写


class Word(TypedDict):
    """单词类型定义"""
    en: str  # 英文
    cn: str  # 中文


# 模式名称映射
MODE_NAMES: dict[str, str] = {
    DictationMode.EN_TO_CN: "英译中 (听英文写中文)",
    DictationMode.CN_TO_EN: "中译英 (听中文写英文)",
    DictationMode.SPELL: "拼写 (听英文+中文拼写英文)",
}

# 占位符文本映射
PLACEHOLDER_TEXTS: dict[str, str] = {
    DictationMode.EN_TO_CN: "输入中文释义",
    DictationMode.CN_TO_EN: "输入英文单词",
    DictationMode.SPELL: "拼写英文单词",
}


def get_display_text(word: Word, mode: str) -> str:
    """
    根据模式获取显示文本。

    Args:
        word: 单词字典，包含 'en' 和 'cn' 键
        mode: 听写模式 ('en_to_cn', 'cn_to_en', 'spell')

    Returns:
        根据模式返回相应的显示文本
        - en_to_cn: 返回英文
        - cn_to_en: 返回中文
        - spell: 返回 "英文 / 中文" 格式

    Examples:
        >>> word = {'en': 'apple', 'cn': '苹果'}
        >>> get_display_text(word, 'en_to_cn')
        'apple'
        >>> get_display_text(word, 'cn_to_en')
        '苹果'
        >>> get_display_text(word, 'spell')
        'apple / 苹果'
    """
    if mode == DictationMode.EN_TO_CN:
        return word['en']
    elif mode == DictationMode.CN_TO_EN:
        return word['cn']
    else:  # spell
        return f"{word['en']} / {word['cn']}"


def get_correct_answer(word: Word, mode: str) -> str:
    """
    根据模式获取正确答案。

    Args:
        word: 单词字典，包含 'en' 和 'cn' 键
        mode: 听写模式 ('en_to_cn', 'cn_to_en', 'spell')

    Returns:
        根据模式返回相应的正确答案
        - en_to_cn: 返回中文
        - cn_to_en: 返回英文
        - spell: 返回英文

    Examples:
        >>> word = {'en': 'apple', 'cn': '苹果'}
        >>> get_correct_answer(word, 'en_to_cn')
        '苹果'
        >>> get_correct_answer(word, 'cn_to_en')
        'apple'
        >>> get_correct_answer(word, 'spell')
        'apple'
    """
    if mode == DictationMode.EN_TO_CN:
        return word['cn']
    elif mode == DictationMode.CN_TO_EN:
        return word['en']
    else:  # spell
        return word['en']


def check_answer(user_answer: str, correct_answer: str, mode: str = None) -> bool:
    """
    检查答案是否正确。

    比较时忽略大小写，并去除首尾空格。

    Args:
        user_answer: 用户输入的答案
        correct_answer: 正确答案
        mode: 听写模式（可选，预留用于未来扩展）

    Returns:
        如果答案正确返回 True，否则返回 False

    Examples:
        >>> check_answer('Apple', 'apple')
        True
        >>> check_answer('  apple  ', 'apple')
        True
        >>> check_answer('苹果', '苹果')
        True
        >>> check_answer('banana', 'apple')
        False
    """
    return user_answer.lower().strip() == correct_answer.lower().strip()


def get_mode_name(mode: str) -> str:
    """
    获取模式的中文名称。

    Args:
        mode: 听写模式 ('en_to_cn', 'cn_to_en', 'spell')

    Returns:
        模式的中文名称
        - en_to_cn: "英译中 (听英文写中文)"
        - cn_to_en: "中译英 (听中文写英文)"
        - spell: "拼写 (听英文+中文拼写英文)"

    Examples:
        >>> get_mode_name('en_to_cn')
        '英译中 (听英文写中文)'
        >>> get_mode_name('cn_to_en')
        '中译英 (听中文写英文)'
        >>> get_mode_name('spell')
        '拼写 (听英文+中文拼写英文)'
    """
    return MODE_NAMES.get(mode, MODE_NAMES[DictationMode.EN_TO_CN])


def get_placeholder_text(mode: str) -> str:
    """
    获取输入框占位符文本。

    Args:
        mode: 听写模式 ('en_to_cn', 'cn_to_en', 'spell')

    Returns:
        输入框的占位符文本
        - en_to_cn: "输入中文释义"
        - cn_to_en: "输入英文单词"
        - spell: "拼写英文单词"

    Examples:
        >>> get_placeholder_text('en_to_cn')
        '输入中文释义'
        >>> get_placeholder_text('cn_to_en')
        '输入英文单词'
        >>> get_placeholder_text('spell')
        '拼写英文单词'
    """
    return PLACEHOLDER_TEXTS.get(mode, PLACEHOLDER_TEXTS[DictationMode.EN_TO_CN])
