"""
学习历史页面模块
包含学习统计、成绩趋势、历史记录列表和高频错词功能
"""
import streamlit as st
import pandas as pd


def render_history_page():
    """学习历史页"""
    st.title("📊 学习历史")

    # 返回按钮
    if st.button("← 返回词库"):
        st.session_state.page = 'vocabulary'
        st.rerun()

    history_manager = st.session_state.history_manager

    # 获取统计信息
    stats = history_manager.get_statistics()

    # 统计概览
    st.subheader("📈 学习统计")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("总听写次数", stats['total_sessions'])

    with col2:
        st.metric("总单词数", stats['total_words'])

    with col3:
        st.metric("平均正确率", f"{stats['average_score']:.1f}%")

    with col4:
        hours = stats['total_duration'] // 3600
        minutes = (stats['total_duration'] % 3600) // 60
        st.metric("总学习时长", f"{hours}h {minutes}m")

    # 模式统计
    if stats['mode_stats']:
        st.divider()
        st.subheader("📊 模式分布")

        mode_names = {
            "en_to_cn": "英译中",
            "cn_to_en": "中译英",
            "spell": "拼写"
        }

        col1, col2 = st.columns([2, 1])

        with col1:
            mode_data = []
            for mode, count in stats['mode_stats'].items():
                mode_data.append({
                    "模式": mode_names.get(mode, mode),
                    "次数": count
                })

            if mode_data:
                df = pd.DataFrame(mode_data)
                st.bar_chart(df.set_index("模式"))

        with col2:
            st.markdown("**详细数据**")
            for mode, count in stats['mode_stats'].items():
                st.markdown(f"- {mode_names.get(mode, mode)}: {count}次")

    # 成绩趋势
    if stats['recent_scores']:
        st.divider()
        st.subheader("📈 最近成绩趋势")

        # 准备数据（倒序显示，最新的在右边）
        scores = list(reversed(stats['recent_scores']))
        df = pd.DataFrame({
            "序号": range(1, len(scores) + 1),
            "分数": scores
        })

        st.line_chart(df.set_index("序号"))

    # 历史记录列表
    st.divider()
    st.subheader("📋 历史记录")

    # 操作按钮
    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        if st.button("🗑️ 清空所有记录"):
            if st.session_state.get('confirm_clear'):
                history_manager.clear_all_records()
                st.session_state.confirm_clear = False
                st.success("已清空所有记录")
                st.rerun()
            else:
                st.session_state.confirm_clear = True
                st.warning("再次点击确认清空")

    with col2:
        if st.button("📥 导出CSV"):
            output_file = "/tmp/history_export.csv"
            if history_manager.export_to_csv(output_file):
                with open(output_file, 'rb') as f:
                    st.download_button(
                        label="下载CSV文件",
                        data=f,
                        file_name="听写历史.csv",
                        mime="text/csv"
                    )

    # 获取所有记录
    records = history_manager.get_all_records()

    if not records:
        st.info("暂无历史记录")
        return

    # 显示记录
    mode_names = {
        "en_to_cn": "英译中",
        "cn_to_en": "中译英",
        "spell": "拼写"
    }

    for i, record in enumerate(records):
        with st.expander(
            f"📝 {record.get('date', '')[:10]} - {mode_names.get(record.get('mode'), record.get('mode'))} - "
            f"分数: {record.get('score', 0)}% ({record.get('correct_count', 0)}/{record.get('total_words', 0)})"
        ):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"**记录ID:** {record.get('id', '')}")
                st.markdown(f"**日期时间:** {record.get('date', '')}")
                st.markdown(f"**听写模式:** {mode_names.get(record.get('mode'), record.get('mode'))}")
                st.markdown(f"**词库名称:** {record.get('vocabulary_name', '')}")
                st.markdown(f"**总单词数:** {record.get('total_words', 0)}")
                st.markdown(f"**正确数量:** {record.get('correct_count', 0)}")
                st.markdown(f"**分数:** {record.get('score', 0)}%")

                duration = record.get('duration_seconds', 0)
                minutes = duration // 60
                seconds = duration % 60
                st.markdown(f"**用时:** {minutes}分{seconds}秒")

            with col2:
                # 成绩评级
                score = record.get('score', 0)
                if score >= 90:
                    st.success("🏆 优秀")
                elif score >= 80:
                    st.info("👍 良好")
                elif score >= 60:
                    st.warning("✓ 及格")
                else:
                    st.error("✗ 不及格")

                # 删除按钮
                if st.button("🗑️ 删除", key=f"del_record_{record.get('id')}"):
                    history_manager.delete_record(record.get('id'))
                    st.rerun()

            # 错题列表
            wrong_words = record.get('wrong_words', [])
            if wrong_words:
                st.markdown("**错题列表:**")
                for j, word in enumerate(wrong_words[:10]):  # 最多显示10个
                    st.markdown(
                        f"- {word.get('en', '')} ({word.get('cn', '')}) "
                        f"→ 你的答案: {word.get('user_answer', '未作答')}"
                    )
                if len(wrong_words) > 10:
                    st.markdown(f"...还有 {len(wrong_words) - 10} 个错题")

    # 高频错词
    st.divider()
    st.subheader("🔥 高频错词")

    wrong_freq = history_manager.get_wrong_words_frequency(limit=20)

    if wrong_freq:
        for i, word in enumerate(wrong_freq[:10]):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**{i+1}. {word['en']}**")
            with col2:
                st.markdown(f"_{word['cn']}_")
            with col3:
                st.markdown(f"错误 {word['count']} 次")
    else:
        st.info("暂无错词记录")
