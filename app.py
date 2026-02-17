"""
自动英语听写软件 - v3.0 重构版
三页流程：词库管理 -> 听写播放 -> 答案批改
"""
import streamlit as st
import time

# 设置页面
st.set_page_config(
    page_title="自动英语听写",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入模块
from src.audio_cache import AudioCache
from src.history_manager import HistoryManager
from src.wrong_answer_manager import WrongAnswerManager
from data.vocabulary_store import VocabularyStore
from src.theme_manager import load_theme, get_available_themes

# 导入页面模块
from pages import (
    render_vocabulary_page,
    render_dictation_page,
    render_answer_page,
    render_history_page,
    render_wrong_answers_page,
)


def init_session_state():
    """初始化 session state"""
    defaults = {
        'page': 'vocabulary',  # vocabulary | dictation | answer | history | wrong_answers
        'word_list': [],  # [{en, cn, checked}]
        'selected_words': [],  # 选中的听写单词
        'current_index': 0,
        'dictation_order': [],  # 听写顺序
        'user_answers': {},  # 用户答案
        'audio_cache': None,  # 延迟初始化
        'voice_en': "male_qn_qingse",
        'voice_cn': "female_shaonv",
        'playback_interval': 3,
        'shuffle_order': False,
        'dictation_mode': "en_to_cn",  # en_to_cn | cn_to_en | spell
        'grading_result': None,  # 拍照批改结果
        'vocab_store': None,  # 延迟初始化
        'current_vocabulary': "默认词库",
        'history_manager': None,  # 延迟初始化
        'dictation_start_time': None,
        'wrong_answer_manager': None,  # 延迟初始化
        'theme': "default",  # 默认主题
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # 延迟初始化复杂对象
    if st.session_state.audio_cache is None:
        st.session_state.audio_cache = AudioCache()

    if st.session_state.vocab_store is None:
        st.session_state.vocab_store = VocabularyStore()

    if st.session_state.history_manager is None:
        st.session_state.history_manager = HistoryManager()

    if st.session_state.wrong_answer_manager is None:
        st.session_state.wrong_answer_manager = WrongAnswerManager()

    # 尝试加载默认词库
    if not st.session_state.word_list and st.session_state.current_vocabulary == "默认词库":
        default_vocab = st.session_state.vocab_store.load_vocabulary("默认词库")
        if default_vocab and 'words' in default_vocab:
            st.session_state.word_list = default_vocab['words']


def render_theme_selector():
    """渲染主题选择器（在侧边栏）"""
    with st.sidebar:
        st.divider()
        st.subheader("🎨 主题设置")

        themes = get_available_themes()
        current_theme = st.session_state.get("theme", "default")

        selected_theme = st.selectbox(
            "选择主题",
            options=list(themes.keys()),
            format_func=lambda x: themes[x],
            index=list(themes.keys()).index(current_theme) if current_theme in themes else 0,
            help="选择你喜欢的界面风格，刷新后保持主题",
            key="theme_selector"
        )

        # 保存到 session state
        if selected_theme != current_theme:
            st.session_state.theme = selected_theme
            st.rerun()

        # 应用主题
        if selected_theme != "default":
            theme_css = load_theme(selected_theme)
            st.markdown(theme_css, unsafe_allow_html=True)

        # 显示当前主题信息
        theme_info = {
            "light": "☀️ 浅色模式：清新明亮，适合白天使用",
            "dark": "🌙 深色模式：护眼舒适，适合夜间使用",
            "cozy": "🌈 温馨学习：柔和色彩，适合儿童使用",
            "vintage": "📜 复古学院：经典风格，专业学习",
        }
        if selected_theme in theme_info:
            st.info(theme_info[selected_theme])


def render_header():
    """渲染顶部导航"""
    st.markdown("""
    <style>
        .nav-title {
            font-size: 2rem;
            font-weight: bold;
            color: #1f77b4;
        }
        .nav-btn {
            padding: 0.5rem 1.5rem;
            margin: 0 0.5rem;
            border-radius: 0.5rem;
            font-size: 1rem;
        }
        .nav-btn-active {
            background: #1f77b4;
            color: white;
        }
        .nav-btn-inactive {
            background: #e0e0e0;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)

    # 页面导航
    pages = [
        ('vocabulary', '📚 词库管理'),
        ('dictation', '🎧 听写播放'),
        ('answer', '✅ 答案批改'),
        ('wrong_answers', '📕 错题本'),
        ('history', '📊 学习历史')
    ]

    cols = st.columns([1, 1, 1, 1, 1, 1])
    for i, (page_id, page_name) in enumerate(pages):
        with cols[i]:
            if st.session_state.page == page_id:
                st.markdown(f'<button class="nav-btn nav-btn-active">{page_name}</button>', unsafe_allow_html=True)
            else:
                if st.button(page_name, key=f"nav_{page_id}"):
                    st.session_state.page = page_id
                    st.rerun()


def main():
    """主函数"""
    # 初始化 session state
    init_session_state()

    # 应用主题（在所有页面渲染之前）
    render_theme_selector()

    # 顶部导航
    render_header()

    # 页面路由
    page_routes = {
        'vocabulary': render_vocabulary_page,
        'dictation': render_dictation_page,
        'answer': render_answer_page,
        'history': render_history_page,
        'wrong_answers': render_wrong_answers_page,
    }

    current_page = st.session_state.page
    if current_page in page_routes:
        page_routes[current_page]()


if __name__ == "__main__":
    main()
