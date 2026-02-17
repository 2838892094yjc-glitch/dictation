"""
词库管理页面模块
流程：导入词库 → 选择听写范围 → 开始听写
"""
import streamlit as st
import json
import random
import time
import threading
from PIL import Image

from src.ocr_engine import extract_words_from_image
from src.ai_corrector import correct_spelling
from data.vocabulary_store import VocabularyStore


def preload_all_audio():
    """预加���所有选中单词的音频"""
    if not st.session_state.selected_words:
        return

    cache = st.session_state.audio_cache
    voice_en = st.session_state.voice_en
    voice_cn = st.session_state.voice_cn

    for word in st.session_state.selected_words:
        cache.get_audio(word['en'], mode="en", voice_en=voice_en)
        cache.get_audio(word['cn'], mode="cn", voice_cn=voice_cn)


def render_vocabulary_page():
    """词库管理页主渲染函数"""
    st.title("📚 词库管理")

    # 第一部分：词库选择
    _render_vocabulary_selector()

    st.divider()

    # 第二部分：导入词库（拍照为主）
    _render_import_section()

    st.divider()

    # 第三部分：选择听写范围
    _render_selection_section()

    # 第四部分：词库列表（可折叠）
    _render_word_list()


def _render_vocabulary_selector():
    """渲染词库选择器"""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

    with col1:
        vocab_list = st.session_state.vocab_store.list_vocabularies()
        vocab_names = [v['name'] for v in vocab_list] if vocab_list else ["默认词库"]

        current_idx = vocab_names.index(st.session_state.current_vocabulary) if st.session_state.current_vocabulary in vocab_names else 0

        selected_vocab = st.selectbox(
            "📂 当前词库",
            options=vocab_names,
            index=current_idx,
            key="vocab_selector"
        )

        if selected_vocab != st.session_state.current_vocabulary:
            loaded = st.session_state.vocab_store.load_vocabulary(selected_vocab)
            if loaded and 'words' in loaded:
                st.session_state.word_list = loaded['words']
                st.session_state.current_vocabulary = selected_vocab
                st.rerun()

    with col2:
        if st.button("💾 保存"):
            if st.session_state.word_list:
                st.session_state.vocab_store.save_vocabulary(
                    st.session_state.current_vocabulary,
                    st.session_state.word_list
                )
                st.success("已保存")

    with col3:
        if st.button("➕ 新建"):
            vocab_list = st.session_state.vocab_store.list_vocabularies()
            new_name = f"词库_{len(vocab_list) + 1}"
            st.session_state.current_vocabulary = new_name
            st.session_state.word_list = []
            st.rerun()

    with col4:
        if st.button("🗑️ 删除"):
            if st.session_state.current_vocabulary != "默认词库":
                st.session_state.vocab_store.delete_vocabulary(st.session_state.current_vocabulary)
                st.session_state.current_vocabulary = "默认词库"
                st.session_state.word_list = []
                st.rerun()


def _render_import_section():
    """渲染导入词库区域 - 拍照为主"""
    st.subheader("📷 导入词库")

    # 主要方式：拍照导入
    uploaded_file = st.file_uploader(
        "拍照上传单词表（推荐）",
        type=['jpg', 'png', 'jpeg'],
        help="拍摄单词表照片，系统自动识别英文和中文"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        use_ai_correct = st.checkbox("🤖 AI智能纠正拼写", value=True)

    if uploaded_file:
        with st.spinner("🔍 识别中..."):
            img_path = f"/tmp/{uploaded_file.name}"
            Image.open(uploaded_file).save(img_path)

            raw_words = extract_words_from_image(img_path)

            if use_ai_correct and raw_words:
                with st.spinner("🤖 AI纠正中..."):
                    final_words = correct_spelling(raw_words)
            else:
                final_words = raw_words

            # 添加到词库
            added_count = 0
            for w in final_words:
                if w.get('en') and w.get('cn'):
                    exists = any(word['en'].lower() == w['en'].lower() for word in st.session_state.word_list)
                    if not exists:
                        st.session_state.word_list.append({
                            'en': w.get('corrected', w['en']),
                            'cn': w['cn'],
                            'checked': False
                        })
                        added_count += 1

            if added_count > 0:
                st.success(f"✅ 已添加 {added_count} 个单词")
                st.session_state.vocab_store.save_vocabulary(
                    st.session_state.current_vocabulary,
                    st.session_state.word_list
                )
                st.rerun()
            else:
                st.warning("未识别到新单词")

    # 其他导入方式（折叠）
    with st.expander("📥 其他导入方式"):
        tab1, tab2, tab3 = st.tabs(["手动输入", "文件导入", "预置词库"])

        with tab1:
            manual_input = st.text_area(
                "每行一个：英文 中文",
                height=100,
                placeholder="apple 苹果\nbanana 香蕉"
            )
            if st.button("添加"):
                if manual_input:
                    count = 0
                    for line in manual_input.strip().split('\n'):
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            en, cn = parts[0], ' '.join(parts[1:])
                            if not any(w['en'].lower() == en.lower() for w in st.session_state.word_list):
                                st.session_state.word_list.append({'en': en, 'cn': cn, 'checked': False})
                                count += 1
                    if count > 0:
                        st.success(f"添加了 {count} 个")
                        st.session_state.vocab_store.save_vocabulary(
                            st.session_state.current_vocabulary,
                            st.session_state.word_list
                        )
                        st.rerun()

        with tab2:
            import_file = st.file_uploader("选择文件", type=['json', 'txt', 'csv'], key="import_file")
            if import_file and st.button("导入文件"):
                temp_path = f"/tmp/{import_file.name}"
                with open(temp_path, 'wb') as f:
                    f.write(import_file.getbuffer())

                ext = import_file.name.split('.')[-1].lower()
                result = None
                if ext == 'json':
                    result = st.session_state.vocab_store.import_from_json(temp_path)
                elif ext == 'txt':
                    result = st.session_state.vocab_store.import_from_txt(temp_path, st.session_state.current_vocabulary)
                elif ext == 'csv':
                    result = st.session_state.vocab_store.import_from_csv(temp_path, st.session_state.current_vocabulary)

                if result:
                    st.success(f"导入成功: {result['word_count']}个单词")
                    st.rerun()

        with tab3:
            builtin_vocabs = st.session_state.vocab_store.list_builtin_vocabularies()
            if builtin_vocabs:
                for vocab in builtin_vocabs:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{vocab['name']}** ({vocab['word_count']}词)")
                    with col2:
                        if st.button("加载", key=f"load_{vocab['name']}"):
                            result = st.session_state.vocab_store.load_builtin_vocabulary(vocab['file_path'], vocab['name'])
                            if result:
                                loaded = st.session_state.vocab_store.load_vocabulary(result['name'])
                                if loaded:
                                    st.session_state.word_list = loaded['words']
                                    st.session_state.current_vocabulary = result['name']
                                st.rerun()


def _render_selection_section():
    """渲染选择听写范围区域"""
    word_count = len(st.session_state.word_list)

    if word_count == 0:
        st.info("👆 请先导入词库")
        return

    st.subheader(f"🎯 选择听写范围（共 {word_count} 词）")

    # 选择方式
    col1, col2 = st.columns([2, 1])

    with col1:
        select_method = st.radio(
            "选择方式",
            ["全选", "前N个", "后N个", "随机N个", "按字母范围", "手动勾选"],
            horizontal=True,
            key="select_method"
        )

    # 根据选择方式处理
    if select_method == "全选":
        for w in st.session_state.word_list:
            w['checked'] = True

    elif select_method == "前N个":
        n = st.slider("选择前几个", 1, word_count, min(10, word_count), key="front_n")
        for i, w in enumerate(st.session_state.word_list):
            w['checked'] = i < n

    elif select_method == "后N个":
        n = st.slider("选择后几个", 1, word_count, min(10, word_count), key="back_n")
        for i, w in enumerate(st.session_state.word_list):
            w['checked'] = i >= word_count - n

    elif select_method == "随机N个":
        n = st.slider("随机选择几个", 1, word_count, min(10, word_count), key="random_n")
        if st.button("🎲 重新随机"):
            indices = random.sample(range(word_count), n)
            for i, w in enumerate(st.session_state.word_list):
                w['checked'] = i in indices
            st.rerun()
        else:
            # 首次或保持当前选择
            checked_count = sum(1 for w in st.session_state.word_list if w['checked'])
            if checked_count == 0:
                indices = random.sample(range(word_count), n)
                for i, w in enumerate(st.session_state.word_list):
                    w['checked'] = i in indices

    elif select_method == "按字母范围":
        col_a, col_b = st.columns(2)
        with col_a:
            start_letter = st.selectbox("从", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), key="start_letter")
        with col_b:
            end_letter = st.selectbox("到", list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), index=25, key="end_letter")

        for w in st.session_state.word_list:
            first = w['en'][0].upper() if w['en'] else ''
            w['checked'] = start_letter <= first <= end_letter

    elif select_method == "手动勾选":
        st.info("👇 在下方词库列表中手动勾选")

    # 显示已选数量
    checked_count = sum(1 for w in st.session_state.word_list if w['checked'])

    st.divider()

    # 听写设置和开始按钮
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.session_state.dictation_mode = st.selectbox(
            "📝 听写模式",
            options=["cn_to_en", "spell", "en_to_cn"],
            format_func=lambda x: {
                "cn_to_en": "🔊 报中文 → 写英文",
                "spell": "🔊 报英文 → 写英文（拼写）",
                "en_to_cn": "🔊 报英文 → 写中文"
            }[x],
            index=["cn_to_en", "spell", "en_to_cn"].index(st.session_state.dictation_mode) if st.session_state.dictation_mode in ["cn_to_en", "spell", "en_to_cn"] else 0
        )

    with col2:
        st.session_state.shuffle_order = st.checkbox("🔀 打乱顺序", value=st.session_state.shuffle_order)

    with col3:
        st.markdown(f"**已选: {checked_count} 词**")

    # 开始听写按钮
    if checked_count > 0:
        if st.button("🎧 开始听写", type="primary", use_container_width=True):
            st.session_state.selected_words = [w for w in st.session_state.word_list if w['checked']]
            st.session_state.dictation_order = list(range(len(st.session_state.selected_words)))
            if st.session_state.shuffle_order:
                random.shuffle(st.session_state.dictation_order)
            st.session_state.current_index = 0
            st.session_state.user_answers = {}
            st.session_state.dictation_start_time = time.time()
            st.session_state.page = 'dictation'
            threading.Thread(target=preload_all_audio, daemon=True).start()
            st.rerun()
    else:
        st.warning("请至少选择1个单词")


def _render_word_list():
    """渲染词库列表（可折叠）"""
    if not st.session_state.word_list:
        return

    with st.expander(f"📋 查看词库列表（{len(st.session_state.word_list)}词）", expanded=False):
        # 批量操作
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("全选"):
                for w in st.session_state.word_list:
                    w['checked'] = True
                st.rerun()
        with col2:
            if st.button("全不选"):
                for w in st.session_state.word_list:
                    w['checked'] = False
                st.rerun()
        with col3:
            if st.button("🗑️ 清空词库"):
                st.session_state.word_list = []
                st.session_state.selected_words = []
                st.session_state.vocab_store.save_vocabulary(
                    st.session_state.current_vocabulary,
                    st.session_state.word_list
                )
                st.rerun()

        st.divider()

        # 单词列表
        for i, word in enumerate(st.session_state.word_list):
            col1, col2, col3, col4 = st.columns([0.5, 2, 2, 0.5])
            with col1:
                word['checked'] = st.checkbox("", value=word.get('checked', False), key=f"check_{i}", label_visibility="collapsed")
            with col2:
                st.markdown(f"**{word['en']}**")
            with col3:
                st.markdown(f"{word['cn']}")
            with col4:
                if st.button("×", key=f"del_{i}"):
                    st.session_state.word_list.pop(i)
                    st.session_state.vocab_store.save_vocabulary(
                        st.session_state.current_vocabulary,
                        st.session_state.word_list
                    )
                    st.rerun()
