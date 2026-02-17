"""
错题本管理模块 - 自动收录和管理错误单词
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class WrongAnswerManager:
    """错题本管理器"""

    def __init__(self, data_file: str = None):
        """
        初始化错题本管理器

        Args:
            data_file: 错题数据文件路径
        """
        if data_file is None:
            # 默认路径
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_file = os.path.join(base_dir, 'data', 'wrong_answers.json')

        self.data_file = data_file
        self._ensure_data_file()

    def _ensure_data_file(self):
        """确保数据文件存在"""
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            self._save_data({
                'words': [],
                'stats': {
                    'total_wrong': 0,
                    'unique_words': 0
                }
            })

    def _load_data(self) -> Dict:
        """加载错题数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载错题数据失败: {e}")
            return {
                'words': [],
                'stats': {
                    'total_wrong': 0,
                    'unique_words': 0
                }
            }

    def _save_data(self, data: Dict):
        """保存错题数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存错题数据失败: {e}")

    def add_wrong_answer(self, en: str, cn: str, user_answer: str):
        """
        添加错题记录

        Args:
            en: 英文单词
            cn: 中文释义
            user_answer: 用户的错误答案
        """
        data = self._load_data()

        # 查找是否已存在该单词
        existing = None
        for word in data['words']:
            if word['en'].lower() == en.lower():
                existing = word
                break

        if existing:
            # 更新错误次数和时间
            existing['wrong_count'] += 1
            existing['last_wrong_time'] = datetime.now().isoformat()
            existing['user_answer'] = user_answer  # 更新最新的错误答案
        else:
            # 新增错题
            data['words'].append({
                'en': en,
                'cn': cn,
                'user_answer': user_answer,
                'wrong_count': 1,
                'last_wrong_time': datetime.now().isoformat()
            })

        # 更新统计
        data['stats']['total_wrong'] = sum(w['wrong_count'] for w in data['words'])
        data['stats']['unique_words'] = len(data['words'])

        self._save_data(data)

    def get_all_wrong_answers(self) -> List[Dict]:
        """
        获取所有错题

        Returns:
            错题列表
        """
        data = self._load_data()
        return data.get('words', [])

    def get_stats(self) -> Dict:
        """
        获取错题统计

        Returns:
            统计信息
        """
        data = self._load_data()
        return data.get('stats', {
            'total_wrong': 0,
            'unique_words': 0
        })

    def clear_all(self):
        """清空所有错题"""
        self._save_data({
            'words': [],
            'stats': {
                'total_wrong': 0,
                'unique_words': 0
            }
        })

    def remove_word(self, en: str):
        """
        移除指定单词的错题记录

        Args:
            en: 英文单词
        """
        data = self._load_data()
        data['words'] = [w for w in data['words'] if w['en'].lower() != en.lower()]

        # 更新统计
        data['stats']['total_wrong'] = sum(w['wrong_count'] for w in data['words'])
        data['stats']['unique_words'] = len(data['words'])

        self._save_data(data)

    def get_review_words(self, limit: Optional[int] = None) -> List[Dict]:
        """
        获取需要复习的单词（按错误次数排序）

        Args:
            limit: 限制返回数量

        Returns:
            单词列表
        """
        words = self.get_all_wrong_answers()
        # 按错误次数降序排序
        words.sort(key=lambda x: x['wrong_count'], reverse=True)

        if limit:
            return words[:limit]
        return words


if __name__ == '__main__':
    # 测试
    manager = WrongAnswerManager()

    # 添加错题
    manager.add_wrong_answer('apple', '苹果', 'aple')
    manager.add_wrong_answer('banana', '香蕉', 'bananq')
    manager.add_wrong_answer('apple', '苹果', 'appl')  # 再次错误

    # 查看错题
    print("所有错题:")
    for word in manager.get_all_wrong_answers():
        print(f"  {word['en']} ({word['cn']}) - 错误{word['wrong_count']}次, 最后答案: {word['user_answer']}")

    # 统计
    stats = manager.get_stats()
    print(f"\n统计: 累计错误{stats['total_wrong']}次, 不同单词{stats['unique_words']}个")
