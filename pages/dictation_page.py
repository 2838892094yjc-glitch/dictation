"""
听写播放页面模块 - 简洁版

纯报听写界面，不显示单词内容
三种模式：
- 报中文写英文
- 报英文写英文（拼写）
- 报英文写中文
"""
import streamlit as st
import time

from components.audio_player import create_audio_player_from_session
from src.minimax_tts import MiniMaxTTSEngine


def render_dictation_page():
    """听写播放页 - 简洁版"""

    if not st.session_state.selected_words:
        st.warning("请先选择要听写的单词")
        if st.button("← 返回词库"):
            st.session_state.page = 'vocabulary'
            st.rerun()
        return

    total = len(st.session_state.selected_words)
    current = st.session_state.current_index + 1
    mode = st.session_state.dictation_mode

    # 模式说明
    mode_info = {
        "cn_to_en": ("🔊 报中文 → 写英文", "听中文，写出对应的英文单词"),
        "spell": ("🔊 报英文 → 写英文", "听英文发音，拼写出单词"),
        "en_to_cn": ("🔊 报英文 → 写中文", "听英文，写出中文意思")
    }
    mode_title, mode_desc = mode_info.get(mode, ("听写", ""))

    # 顶部信息栏
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 返回"):
            st.session_state.page = 'vocabulary'
            st.rerun()
    with col2:
        st.markdown(f"<h3 style='text-align:center;margin:0;'>{mode_title}</h3>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<p style='text-align:right;margin:0;'><b>{current} / {total}</b></p>", unsafe_allow_html=True)

    st.divider()

    # 主播放区域 - 简洁大按钮
    st.markdown("""
    <style>
    .big-play-btn {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        if current > 1:
            if st.button("⏮️ 上一个", use_container_width=True):
                st.session_state.current_index -= 1
                st.rerun()

    with col2:
        # 大播放按钮
        if st.button("🔊 播放", type="primary", use_container_width=True, key="play_btn"):
            _play_current()

        # 进度条
        progress = current / total
        st.progress(progress)
        st.markdown(f"<p style='text-align:center;color:#666;'>{mode_desc}</p>", unsafe_allow_html=True)

    with col3:
        if current < total:
            if st.button("下一个 ⏭️", use_container_width=True):
                st.session_state.current_index += 1
                st.rerun()

    st.divider()

    # 连续播放设置
    with st.expander("⚙️ 播放设置"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.playback_interval = st.slider(
                "播放间隔（秒）",
                min_value=2,
                max_value=15,
                value=st.session_state.playback_interval,
                help="每个单词之间的间隔时间"
            )
        with col2:
            repeat_count = st.selectbox(
                "每词重复次数",
                options=[1, 2, 3],
                index=0,
                key="repeat_count"
            )

        # 音色设置（折叠）
        with st.expander("🎤 音色设置"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.voice_en = st.selectbox(
                    "英文音色",
                    options=list(MiniMaxTTSEngine.ENGLISH_VOICES.keys()),
                    index=list(MiniMaxTTSEngine.ENGLISH_VOICES.keys()).index(st.session_state.voice_en)
                )
            with col2:
                st.session_state.voice_cn = st.selectbox(
                    "中文音色",
                    options=list(MiniMaxTTSEngine.CHINESE_VOICES.keys()),
                    index=list(MiniMaxTTSEngine.CHINESE_VOICES.keys()).index(st.session_state.voice_cn)
                )

    # 连续播放按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ 从当前位置连续播放", use_container_width=True):
            _auto_play_from_current()

    with col2:
        if st.button("⏹️ 结束听写 → 批改", use_container_width=True):
            st.session_state.page = 'answer'
            st.rerun()


def _play_current():
    """播放当前单词"""
    player = create_audio_player_from_session()
    idx = st.session_state.dictation_order[st.session_state.current_index]
    word = st.session_state.selected_words[idx]
    mode = st.session_state.dictation_mode

    player.play_word(word, mode, use_js_delay=True)


def _auto_play_from_current():
    """从当前位置连续播放"""
    player = create_audio_player_from_session()
    words = st.session_state.selected_words
    order = st.session_state.dictation_order
    mode = st.session_state.dictation_mode
    interval = st.session_state.playback_interval
    start_idx = st.session_state.current_index

    total = len(words)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(start_idx, total):
        st.session_state.current_index = i
        idx = order[i]
        word = words[idx]

        # 更新进度
        progress = (i - start_idx + 1) / (total - start_idx)
        progress_bar.progress(progress)
        status_text.markdown(f"**正在播放: {i + 1} / {total}**")

        # 播放
        player.play_word(word, mode, use_js_delay=False)

        # 等待间隔
        if i < total - 1:
            time.sleep(interval)

    status_text.markdown("**✅ 播放完成！**")
    progress_bar.progress(1.0)
