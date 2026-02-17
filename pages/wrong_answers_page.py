"""
错题本页面模块
包含错题列表、错题统计和复习功能
"""
import streamlit as st
import random


def render_wrong_answers_page():
    """错题本页面"""
    st.title("📕 错题本")

    wrong_manager = st.session_state.wrong_answer_manager

    # 顶部操作栏
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        stats = wrong_manager.get_stats()
        st.markdown(f"**累计错误：{stats['total_wrong']} 次 | 不同单词：{stats['unique_words']} 个**")

    with col2:
        if st.button("🔄 开始复习"):
            # 从错题本加载单词到听写列表
            wrong_words = wrong_manager.get_all_wrong_answers()
            if wrong_words:
                st.session_state.selected_words = [
                    {'en': w['en'], 'cn': w['cn'], 'checked': True}
                    for w in wrong_words
                ]
                st.session_state.dictation_order = list(range(len(st.session_state.selected_words)))
                if st.session_state.shuffle_order:
                    random.shuffle(st.session_state.dictation_order)
                st.session_state.current_index = 0
                st.session_state.user_answers = {}
                st.session_state.page = 'dictation'
                st.rerun()
            else:
                st.warning("错题本为空")

    with col3:
        if st.button("🗑️ 清空错题本"):
            wrong_manager.clear_all()
            st.success("已清空错题本")
            st.rerun()

    # 错题列表
    st.divider()
    st.subheader("📋 错题列表")

    wrong_words = wrong_manager.get_review_words()

    if wrong_words:
        # 按错误次数分组显示
        st.markdown("**按错误次数排序（从高到低）**")

        for i, word in enumerate(wrong_words):
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])

            with col1:
                st.markdown(f"**{i+1}.**")

            with col2:
                st.markdown(f"**{word['en']}**")

            with col3:
                st.markdown(f"_{word['cn']}_")

            with col4:
                st.markdown(f"最后答案: `{word['user_answer']}`")

            with col5:
                # 错误次数徽章
                if word['wrong_count'] >= 5:
                    st.error(f"❌ {word['wrong_count']}次")
                elif word['wrong_count'] >= 3:
                    st.warning(f"⚠️ {word['wrong_count']}次")
                else:
                    st.info(f"📝 {word['wrong_count']}次")

            # 删除按钮
            col_del1, col_del2 = st.columns([5, 1])
            with col_del2:
                if st.button("删除", key=f"del_wrong_{i}"):
                    wrong_manager.remove_word(word['en'])
                    st.rerun()

        # 错题统计
        st.divider()
        st.subheader("📊 错题统计")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("累计错误次数", stats['total_wrong'])

        with col2:
            st.metric("不同错误单词", stats['unique_words'])

        with col3:
            # 高频错词（错误3次以上）
            high_freq = [w for w in wrong_words if w['wrong_count'] >= 3]
            st.metric("高频错词", len(high_freq))

        # 错误次数分布
        if wrong_words:
            st.markdown("**错误次数分布：**")
            count_1 = len([w for w in wrong_words if w['wrong_count'] == 1])
            count_2 = len([w for w in wrong_words if w['wrong_count'] == 2])
            count_3_5 = len([w for w in wrong_words if 3 <= w['wrong_count'] <= 5])
            count_5_plus = len([w for w in wrong_words if w['wrong_count'] > 5])

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.info(f"1次: {count_1}个")
            with col2:
                st.info(f"2次: {count_2}个")
            with col3:
                st.warning(f"3-5次: {count_3_5}个")
            with col4:
                st.error(f"5次以上: {count_5_plus}个")

    else:
        st.info("错题本为空，继续加油！")
