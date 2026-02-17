"""
词库管理页面模块
包含词库的选择、保存、删除、导入导出、单词输入和列表展示功能
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
    """预加载所有选中单词的音频"""
    if not st.session_state.selected_words:
        return

    cache = st.session_state.audio_cache
    voice_en = st.session_state.voice_en
    voice_cn = st.session_state.voice_cn

    # 预加载英文和中文音频
    for word in st.session_state.selected_words:
        cache.get_audio(word['en'], mode="en", voice_en=voice_en)
        cache.get_audio(word['cn'], mode="cn", voice_cn=voice_cn)


def render_vocabulary_manager():
    """渲染词库选择/保存/删除区域"""
    st.subheader("💾 词库管理")
    col_vocab1, col_vocab2, col_vocab3, col_vocab4 = st.columns([2, 1, 1, 1])

    with col_vocab1:
        # 当前词库选择
        vocab_list = st.session_state.vocab_store.list_vocabularies()
        vocab_names = [v['name'] for v in vocab_list]

        if not vocab_names:
            vocab_names = ["默认词库"]

        current_idx = 0
        if st.session_state.current_vocabulary in vocab_names:
            current_idx = vocab_names.index(st.session_state.current_vocabulary)

        selected_vocab = st.selectbox(
            "当前词库",
            options=vocab_names,
            index=current_idx,
            key="vocab_selector"
        )

        # 如果选择了不同的词库，加载它
        if selected_vocab != st.session_state.current_vocabulary:
            loaded = st.session_state.vocab_store.load_vocabulary(selected_vocab)
            if loaded and 'words' in loaded:
                st.session_state.word_list = loaded['words']
                st.session_state.current_vocabulary = selected_vocab
                st.rerun()

    with col_vocab2:
        st.write("")  # 占位
        st.write("")  # 占位
        if st.button("💾 保存词库"):
            if st.session_state.word_list:
                success = st.session_state.vocab_store.save_vocabulary(
                    st.session_state.current_vocabulary,
                    st.session_state.word_list
                )
                if success:
                    st.success(f"词库已保存: {st.session_state.current_vocabulary}")
                else:
                    st.error("保存失败")
            else:
                st.warning("词库为空，无法保存")

    with col_vocab3:
        st.write("")  # 占位
        st.write("")  # 占位
        if st.button("➕ 新建词库"):
            vocab_list = st.session_state.vocab_store.list_vocabularies()
            new_name = f"词库_{len(vocab_list) + 1}"
            st.session_state.current_vocabulary = new_name
            st.session_state.word_list = []
            st.rerun()

    with col_vocab4:
        st.write("")  # 占位
        st.write("")  # 占位
        if st.button("🗑️ 删除词库"):
            if st.session_state.current_vocabulary != "默认词库":
                success = st.session_state.vocab_store.delete_vocabulary(st.session_state.current_vocabulary)
                if success:
                    st.success("词库已删除")
                    st.session_state.current_vocabulary = "默认词库"
                    st.session_state.word_list = []
                    st.rerun()
            else:
                st.warning("不能删除默认词库")


def render_import_export():
    """渲染导入导出功能区域"""
    st.subheader("📥📤 导入/导出")

    tab1, tab2, tab3 = st.tabs(["📥 导入词库", "📤 导出词库", "📚 预置词库"])

    with tab1:
        _render_import_tab()

    with tab2:
        _render_export_tab()

    with tab3:
        _render_builtin_tab()


def _render_import_tab():
    """渲染导入标签页"""
    col_import1, col_import2 = st.columns(2)

    with col_import1:
        st.markdown("**从文件导入**")
        import_file = st.file_uploader("选择词库文件", type=['json', 'txt', 'csv'], key="import_file")
        import_name = st.text_input("导入后的词库名称", value="", placeholder="留空则使用文件中的名称")

        if import_file and st.button("开始导入"):
            file_ext = import_file.name.split('.')[-1].lower()
            temp_path = f"/tmp/{import_file.name}"

            with open(temp_path, 'wb') as f:
                f.write(import_file.getbuffer())

            result = None
            if file_ext == 'json':
                result = st.session_state.vocab_store.import_from_json(temp_path, import_name or None)
            elif file_ext == 'txt':
                if not import_name:
                    st.error("TXT格式需要指定词库名称")
                else:
                    result = st.session_state.vocab_store.import_from_txt(temp_path, import_name)
            elif file_ext == 'csv':
                if not import_name:
                    st.error("CSV格式需要指定词库名称")
                else:
                    result = st.session_state.vocab_store.import_from_csv(temp_path, import_name)

            if result:
                st.success(f"✅ 成功导入词库: {result['name']} ({result['word_count']}个单词)")
                st.rerun()
            else:
                st.error("❌ 导入失败，请检查文件格式")

    with col_import2:
        st.markdown("**支持的格式**")
        st.markdown("""
        **JSON格式：**
        ```json
        {
          "name": "我的词库",
          "words": [
            {"en": "apple", "cn": "苹果"},
            {"en": "banana", "cn": "香蕉"}
          ]
        }
        ```

        **TXT格式：**
        ```
        apple 苹果
        banana 香蕉
        computer 电脑
        ```

        **CSV格式：**
        ```
        en,cn
        apple,苹果
        banana,香蕉
        ```
        """)


def _render_export_tab():
    """渲染导出标签页"""
    col_export1, col_export2 = st.columns(2)

    with col_export1:
        st.markdown("**导出当前词库**")
        export_format = st.selectbox("选择导出格式", ["JSON", "TXT", "CSV"])

        if st.button("导出词库"):
            if not st.session_state.word_list:
                st.warning("当前词库为空，无法导出")
            else:
                # 先保存当前词库
                st.session_state.vocab_store.save_vocabulary(
                    st.session_state.current_vocabulary,
                    st.session_state.word_list
                )

                # 生成导出文件路径
                safe_name = "".join(c for c in st.session_state.current_vocabulary if c.isalnum() or c in (' ', '-', '_')).strip()
                export_path = f"/tmp/{safe_name}.{export_format.lower()}"

                success = False
                if export_format == "JSON":
                    success = st.session_state.vocab_store.export_to_json(
                        st.session_state.current_vocabulary, export_path
                    )
                elif export_format == "TXT":
                    success = st.session_state.vocab_store.export_to_txt(
                        st.session_state.current_vocabulary, export_path
                    )
                elif export_format == "CSV":
                    success = st.session_state.vocab_store.export_to_csv(
                        st.session_state.current_vocabulary, export_path
                    )

                if success:
                    with open(export_path, 'rb') as f:
                        st.download_button(
                            label=f"📥 下载 {safe_name}.{export_format.lower()}",
                            data=f,
                            file_name=f"{safe_name}.{export_format.lower()}",
                            mime="application/octet-stream"
                        )
                    st.success("✅ 导出成功！点击上方按钮下载")
                else:
                    st.error("❌ 导出失败")

    with col_export2:
        st.markdown("**导出说明**")
        st.info(f"""
        当前词库：**{st.session_state.current_vocabulary}**

        单词数量：**{len(st.session_state.word_list)}** 个

        导出的文件可以在其他设备上导入使用。
        """)


def _render_builtin_tab():
    """渲染预置词库标签页"""
    st.markdown("**预置词库列表**")
    builtin_vocabs = st.session_state.vocab_store.list_builtin_vocabularies()

    if builtin_vocabs:
        for vocab in builtin_vocabs:
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.markdown(f"**{vocab['name']}**")
                if vocab.get('description'):
                    st.markdown(f"*{vocab['description']}*")
                st.markdown(f"📝 {vocab['word_count']} 个单词")

            with col2:
                if st.button("预览", key=f"preview_{vocab['name']}"):
                    with open(vocab['file_path'], 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    with st.expander(f"预览 {vocab['name']}", expanded=True):
                        for i, word in enumerate(data['words'][:10]):
                            st.markdown(f"{i+1}. **{word['en']}** - {word['cn']}")
                        if len(data['words']) > 10:
                            st.markdown(f"...还有 {len(data['words'])-10} 个单词")

            with col3:
                load_name = st.text_input("", value=vocab['name'], key=f"name_{vocab['name']}", label_visibility="collapsed")
                if st.button("加载", key=f"load_{vocab['name']}"):
                    result = st.session_state.vocab_store.load_builtin_vocabulary(vocab['file_path'], load_name)
                    if result:
                        st.success(f"✅ 已加载: {result['name']}")
                        # 切换到新加载的词库
                        loaded = st.session_state.vocab_store.load_vocabulary(result['name'])
                        if loaded:
                            st.session_state.word_list = loaded['words']
                            st.session_state.current_vocabulary = result['name']
                        st.rerun()
                    else:
                        st.error("❌ 加载失败")

            st.divider()
    else:
        st.info("暂无预置词库")


def render_word_input():
    """渲染单词输入区域（OCR上传+手动输入）"""
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        _render_ocr_upload()

    with col2:
        _render_manual_input()

    with col3:
        _render_quick_operations()


def _render_ocr_upload():
    """渲染OCR拍照导入区域"""
    st.subheader("📷 拍照导入")
    uploaded_file = st.file_uploader("上传单词表照片", type=['jpg', 'png', 'jpeg'])
    use_ai_correct = st.checkbox("🤖 AI智能纠正拼写", value=True)

    if uploaded_file:
        with st.spinner("🔍 OCR识别中..."):
            # 保存上传的图片
            img_path = f"/tmp/{uploaded_file.name}"
            Image.open(uploaded_file).save(img_path)

            # OCR识别
            raw_words = extract_words_from_image(img_path)
            st.success(f"识别到 {len(raw_words)} 行文字")

            # AI纠正
            if use_ai_correct and raw_words:
                with st.spinner("🤖 AI纠正中..."):
                    corrected = correct_spelling(raw_words)
                    st.info(f"纠正了 {sum(1 for c in corrected if c.get('corrected'))} 个拼写错误")

                    # 显示纠正结果
                    corrections = [c for c in corrected if c.get('corrected')]
                    if corrections:
                        with st.expander(f"📝 查看纠正结果 ({len(corrections)}条)"):
                            for c in corrections[:10]:
                                st.markdown(f"- **{c['en']}** → **{c['corrected']}**")
                            if len(corrections) > 10:
                                st.markdown(f"...还有 {len(corrections)-10} 条")

                    # 合并纠正结果
                    final_words = corrected
            else:
                final_words = raw_words

            # 添加到词库
            if final_words:
                for w in final_words:
                    if w.get('en') and w.get('cn'):
                        # 检查是否已存在
                        exists = any(word['en'].lower() == w['en'].lower() for word in st.session_state.word_list)
                        if not exists:
                            st.session_state.word_list.append({
                                'en': w['en'],
                                'cn': w['cn'],
                                'checked': False
                            })
                st.success(f"已添加 {len(final_words)} 个单词到词库")
                # 自动保存
                st.session_state.vocab_store.save_vocabulary(
                    st.session_state.current_vocabulary,
                    st.session_state.word_list
                )


def _render_manual_input():
    """渲染手动输入区域"""
    st.subheader("✏️ 手动输入")
    manual_input = st.text_area("输入格式：英文 中文（每行一个）", height=150,
                                 placeholder="apple 苹果\nbanana 香蕉\ncomputer 电脑")

    if st.button("➕ 添加到词库"):
        if manual_input:
            lines = manual_input.strip().split('\n')
            count = 0
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 2:
                    en = parts[0].strip()
                    cn = ' '.join(parts[1:]).strip()
                    if en and cn:
                        exists = any(word['en'].lower() == en.lower() for word in st.session_state.word_list)
                        if not exists:
                            st.session_state.word_list.append({
                                'en': en,
                                'cn': cn,
                                'checked': False
                            })
                            count += 1
            if count > 0:
                st.success(f"添加了 {count} 个单词")
                # 自动保存
                st.session_state.vocab_store.save_vocabulary(
                    st.session_state.current_vocabulary,
                    st.session_state.word_list
                )
                st.rerun()


def _render_quick_operations():
    """渲染快速操作区域"""
    st.subheader("⚙️ 快速操作")
    if st.button("🗑️ 清空词库"):
        st.session_state.word_list = []
        st.session_state.selected_words = []
        # 自动保存空词库
        st.session_state.vocab_store.save_vocabulary(
            st.session_state.current_vocabulary,
            st.session_state.word_list
        )
        st.rerun()

    # 快捷选择
    word_count = len(st.session_state.word_list)
    if word_count > 0:
        st.markdown(f"**当前词库：{word_count} 个单词**")

        # 选择模式
        select_mode = st.radio("选择模式", ["全不选", "全选", "前n个", "字母A-Z", "字母Z-A"], horizontal=True)

        if select_mode == "全不选":
            for w in st.session_state.word_list:
                w['checked'] = False

        elif select_mode == "全选":
            for w in st.session_state.word_list:
                w['checked'] = True

        elif select_mode == "前n个":
            n_words = st.number_input("选择前几个", min_value=1, max_value=word_count, value=min(10, word_count))
            for i, w in enumerate(st.session_state.word_list):
                w['checked'] = i < n_words

        elif select_mode == "字母A-Z":
            # 按字母顺序选择从A到某字母
            letter_range = st.selectbox("选择范围", options=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"])

            for w in st.session_state.word_list:
                first_letter = w['en'].lower()[0] if w['en'] else ''
                if first_letter.isalpha():
                    w['checked'] = first_letter <= letter_range.lower()
                else:
                    w['checked'] = False

        elif select_mode == "字母Z-A":
            # 按字母顺序选择从某字母到Z
            letter_range = st.selectbox("选择范围", options=["Z", "Y", "X", "W", "V", "U", "T", "S", "R", "Q", "P", "O", "N", "M", "L", "K", "J", "I", "H", "G", "F", "E", "D", "C", "B", "A"])

            for w in st.session_state.word_list:
                first_letter = w['en'].lower()[0] if w['en'] else ''
                if first_letter.isalpha():
                    w['checked'] = first_letter >= letter_range.lower()
                else:
                    w['checked'] = False

        checked_count = sum(1 for w in st.session_state.word_list if w['checked'])
        st.markdown(f"**已选：{checked_count} 个**")

        # 听写模式选择
        st.session_state.dictation_mode = st.selectbox(
            "📝 听写模式",
            options=["en_to_cn", "cn_to_en", "spell"],
            format_func=lambda x: {
                "en_to_cn": "英译中（听英文写中文）",
                "cn_to_en": "中译英（听中文写英文）",
                "spell": "拼写（听英文+中文拼写英文）"
            }[x],
            index=["en_to_cn", "cn_to_en", "spell"].index(st.session_state.dictation_mode)
        )

        # 播放设置
        st.session_state.shuffle_order = st.checkbox("🔀 打乱顺序播放", value=st.session_state.shuffle_order)

        if checked_count > 0 and st.button("🎧 开始听写"):
            st.session_state.selected_words = [w for w in st.session_state.word_list if w['checked']]
            # 设置听写顺序
            st.session_state.dictation_order = list(range(len(st.session_state.selected_words)))
            if st.session_state.shuffle_order:
                random.shuffle(st.session_state.dictation_order)
            st.session_state.current_index = 0
            st.session_state.user_answers = {}  # 清空之前的答案
            st.session_state.dictation_start_time = time.time()  # 记录开始时间
            st.session_state.page = 'dictation'
            # 预加载音频
            threading.Thread(target=preload_all_audio, daemon=True).start()
            st.rerun()


def render_word_list():
    """渲染单词列表展示"""
    st.divider()
    st.subheader(f"📋 词库列表 ({len(st.session_state.word_list)}个)")

    if st.session_state.word_list:
        # 显示表格
        for i, word in enumerate(st.session_state.word_list):
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            with col1:
                word['checked'] = st.checkbox("", value=word.get('checked', False), key=f"check_{i}")
            with col2:
                st.markdown(f"**{word['en']}**")
            with col3:
                st.markdown(f"_{word['cn']}_")
            with col4:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.word_list.pop(i)
                    # 自动保存
                    st.session_state.vocab_store.save_vocabulary(
                        st.session_state.current_vocabulary,
                        st.session_state.word_list
                    )
                    st.rerun()
    else:
        st.info("词库为空，请上传图片或手动输入单词")


def render_vocabulary_page():
    """词库管理页主渲染函数"""
    st.title("📚 词库管理")

    # 词库管理区（选择/保存/删除）
    render_vocabulary_manager()

    st.divider()

    # 导入导出区
    render_import_export()

    st.divider()

    # 单词输入区（OCR上传+手动输入+快速操作）
    render_word_input()

    # 词库列表
    render_word_list()
