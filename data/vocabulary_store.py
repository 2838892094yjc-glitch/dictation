"""
词库持久化存储模块
支持词库的保存、加载、删除等操作
支持多种格式的导入导出：JSON、CSV、TXT
"""
import json
import os
import csv
from datetime import datetime
from typing import List, Dict, Optional


class VocabularyStore:
    """词库存储管理类"""

    def __init__(self, base_dir: str = None):
        """
        初始化词库存储

        Args:
            base_dir: 词库存储目录，默认为当前目录下的 data/vocabularies
        """
        if base_dir is None:
            # 获取当前文件所在目录的父目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.join(current_dir, "vocabularies")

        self.base_dir = base_dir

        # 确保目录存在
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def _get_file_path(self, name: str) -> str:
        """获取词库文件路径"""
        # 安全文件名处理
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        if not safe_name:
            safe_name = "vocabulary"
        return os.path.join(self.base_dir, f"{safe_name}.json")

    def save_vocabulary(self, name: str, words: List[Dict], update_time: bool = True) -> bool:
        """
        保存词库到JSON文件

        Args:
            name: 词库名称
            words: 单词列表 [{"en": "apple", "cn": "苹果", "checked": false}, ...]
            update_time: 是否更新时间戳

        Returns:
            bool: 保存是否成功
        """
        try:
            file_path = self._get_file_path(name)

            # 如果文件已存在，保留创建时间
            created_at = datetime.now().isoformat()
            if os.path.exists(file_path):
                existing_data = self.load_vocabulary(name)
                if existing_data and 'created_at' in existing_data:
                    created_at = existing_data['created_at']

            # 构建词库数据
            vocabulary_data = {
                "name": name,
                "words": words,
                "created_at": created_at,
                "updated_at": datetime.now().isoformat() if update_time else created_at
            }

            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(vocabulary_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"保存词库失败: {e}")
            return False

    def load_vocabulary(self, name: str) -> Optional[Dict]:
        """
        加载词库

        Args:
            name: 词库名称

        Returns:
            Dict: 词库数据 {"name": "...", "words": [...], "created_at": "...", "updated_at": "..."}
            None: 加载失败
        """
        try:
            file_path = self._get_file_path(name)

            if not os.path.exists(file_path):
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return data

        except Exception as e:
            print(f"加载词库失败: {e}")
            return None

    def list_vocabularies(self) -> List[Dict]:
        """
        列出所有词库

        Returns:
            List[Dict]: 词库列表 [{"name": "...", "word_count": 10, "updated_at": "..."}, ...]
        """
        try:
            vocabularies = []

            if not os.path.exists(self.base_dir):
                return vocabularies

            for filename in os.listdir(self.base_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.base_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        vocabularies.append({
                            "name": data.get("name", filename.replace('.json', '')),
                            "word_count": len(data.get("words", [])),
                            "created_at": data.get("created_at", ""),
                            "updated_at": data.get("updated_at", "")
                        })
                    except Exception as e:
                        print(f"读取词库 {filename} 失败: {e}")
                        continue

            # 按更新时间倒序排序
            vocabularies.sort(key=lambda x: x['updated_at'], reverse=True)

            return vocabularies

        except Exception as e:
            print(f"列出词库失败: {e}")
            return []

    def delete_vocabulary(self, name: str) -> bool:
        """
        删除词库

        Args:
            name: 词库名称

        Returns:
            bool: 删除是否成功
        """
        try:
            file_path = self._get_file_path(name)

            if not os.path.exists(file_path):
                return False

            os.remove(file_path)
            return True

        except Exception as e:
            print(f"删除词库失败: {e}")
            return False

    def vocabulary_exists(self, name: str) -> bool:
        """
        检查词库是否存在

        Args:
            name: 词库名称

        Returns:
            bool: 词库是否存在
        """
        file_path = self._get_file_path(name)
        return os.path.exists(file_path)

    def rename_vocabulary(self, old_name: str, new_name: str) -> bool:
        """
        重命名词库

        Args:
            old_name: 旧词库名称
            new_name: 新词库名称

        Returns:
            bool: 重命名是否成功
        """
        try:
            # 加载旧词库
            data = self.load_vocabulary(old_name)
            if not data:
                return False

            # 保存为新名称
            data['name'] = new_name
            if self.save_vocabulary(new_name, data['words'], update_time=False):
                # 删除旧词库
                self.delete_vocabulary(old_name)
                return True

            return False

        except Exception as e:
            print(f"重命名词库失败: {e}")
            return False

    def import_from_json(self, file_path: str, name: str = None) -> Optional[Dict]:
        """
        从JSON文件导入词库

        Args:
            file_path: JSON文件路径
            name: 词库名称（可选，如果不提供则使用文件中的名称）

        Returns:
            Dict: 导入的词库数据，失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证数据格式
            if 'words' not in data:
                print("JSON格��错误：缺少words字段")
                return None

            # 使用提供的名称或文件中的名称
            vocab_name = name or data.get('name', 'imported_vocabulary')

            # 保存词库
            if self.save_vocabulary(vocab_name, data['words']):
                return {'name': vocab_name, 'word_count': len(data['words'])}

            return None

        except Exception as e:
            print(f"导入JSON失败: {e}")
            return None

    def import_from_txt(self, file_path: str, name: str) -> Optional[Dict]:
        """
        从TXT文件导入词库
        格式：每行一个单词，英文和中文用空格分隔

        Args:
            file_path: TXT文件路径
            name: 词库名称

        Returns:
            Dict: 导入的词库数据，失败返回None
        """
        try:
            words = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split(maxsplit=1)
                    if len(parts) >= 2:
                        words.append({
                            'en': parts[0].strip(),
                            'cn': parts[1].strip(),
                            'checked': False
                        })

            if words:
                if self.save_vocabulary(name, words):
                    return {'name': name, 'word_count': len(words)}

            return None

        except Exception as e:
            print(f"导入TXT失败: {e}")
            return None

    def import_from_csv(self, file_path: str, name: str) -> Optional[Dict]:
        """
        从CSV文件导入词库
        格式：en,cn（第一行为标题）

        Args:
            file_path: CSV文件路径
            name: 词库名称

        Returns:
            Dict: 导入的词库数据，失败返回None
        """
        try:
            words = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'en' in row and 'cn' in row:
                        words.append({
                            'en': row['en'].strip(),
                            'cn': row['cn'].strip(),
                            'checked': False
                        })

            if words:
                if self.save_vocabulary(name, words):
                    return {'name': name, 'word_count': len(words)}

            return None

        except Exception as e:
            print(f"导入CSV失败: {e}")
            return None

    def export_to_json(self, name: str, output_path: str) -> bool:
        """
        导出词库为JSON格式

        Args:
            name: 词库名称
            output_path: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        try:
            data = self.load_vocabulary(name)
            if not data:
                return False

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"导出JSON失败: {e}")
            return False

    def export_to_txt(self, name: str, output_path: str) -> bool:
        """
        导出词库为TXT格式
        格式：每行一个单词，英文和中文用空格分隔

        Args:
            name: 词库名称
            output_path: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        try:
            data = self.load_vocabulary(name)
            if not data:
                return False

            with open(output_path, 'w', encoding='utf-8') as f:
                for word in data['words']:
                    f.write(f"{word['en']} {word['cn']}\n")

            return True

        except Exception as e:
            print(f"导出TXT失败: {e}")
            return False

    def export_to_csv(self, name: str, output_path: str) -> bool:
        """
        导出词库为CSV格式

        Args:
            name: 词库名称
            output_path: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        try:
            data = self.load_vocabulary(name)
            if not data:
                return False

            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['en', 'cn'])
                writer.writeheader()
                for word in data['words']:
                    writer.writerow({'en': word['en'], 'cn': word['cn']})

            return True

        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False

    def list_builtin_vocabularies(self) -> List[Dict]:
        """
        列出所有预置词库

        Returns:
            List[Dict]: 预置词库列表
        """
        try:
            builtin_dir = os.path.join(os.path.dirname(self.base_dir), "builtin")
            vocabularies = []

            if not os.path.exists(builtin_dir):
                return vocabularies

            for filename in os.listdir(builtin_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(builtin_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        vocabularies.append({
                            "name": data.get("name", filename.replace('.json', '')),
                            "word_count": len(data.get("words", [])),
                            "file_path": file_path,
                            "description": data.get("description", "")
                        })
                    except Exception as e:
                        print(f"读取预置词库 {filename} 失败: {e}")
                        continue

            return vocabularies

        except Exception as e:
            print(f"列出预置词库失败: {e}")
            return []

    def load_builtin_vocabulary(self, file_path: str, name: str = None) -> Optional[Dict]:
        """
        加载预置词库到用户词库

        Args:
            file_path: 预置词库文件路径
            name: 保存的词库名称（可选）

        Returns:
            Dict: 加载的词库信息，失败返回None
        """
        return self.import_from_json(file_path, name)
