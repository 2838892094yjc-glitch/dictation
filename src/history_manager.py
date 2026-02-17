"""
学习历史记录管理模块
记录每次听写的成绩、时间、词库等信息
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class HistoryManager:
    """历史记录管理类"""

    def __init__(self, history_file: str = None):
        """
        初始化历史记录管理器

        Args:
            history_file: 历史记录文件路径，默认为 data/history.json
        """
        if history_file is None:
            # 获取项目根目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)
            history_file = os.path.join(project_dir, "data", "history.json")

        self.history_file = history_file

        # 确保目录存在
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

        # 如果文件不存在，创建空记录
        if not os.path.exists(self.history_file):
            self._save_data({"records": []})

    def _load_data(self) -> Dict:
        """加载历史记录数据"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}")
            return {"records": []}

    def _save_data(self, data: Dict) -> bool:
        """保存历史记录数据"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存历史记录失败: {e}")
            return False

    def add_record(
        self,
        mode: str,
        vocabulary_name: str,
        total_words: int,
        correct_count: int,
        duration_seconds: int,
        wrong_words: List[Dict] = None,
        user_answers: Dict = None
    ) -> str:
        """
        添加一条历史记录

        Args:
            mode: 听写模式 (en_to_cn, cn_to_en, spell)
            vocabulary_name: 词库名称
            total_words: 总单词数
            correct_count: 正确数量
            duration_seconds: 用时（秒）
            wrong_words: 错误的单词列表 [{"en": "apple", "cn": "苹果", "user_answer": "aple"}, ...]
            user_answers: 用户答案字典

        Returns:
            str: 记录ID
        """
        data = self._load_data()

        # 生成记录ID（时间戳）
        record_id = datetime.now().strftime("%Y%m%d%H%M%S")

        # 计算分数
        score = round((correct_count / total_words * 100) if total_words > 0 else 0, 2)

        # 构建记录
        record = {
            "id": record_id,
            "date": datetime.now().isoformat(),
            "mode": mode,
            "vocabulary_name": vocabulary_name,
            "total_words": total_words,
            "correct_count": correct_count,
            "score": score,
            "duration_seconds": duration_seconds,
            "wrong_words": wrong_words or [],
            "user_answers": user_answers or {}
        }

        # 添加到记录列表
        data["records"].append(record)

        # 保存
        if self._save_data(data):
            return record_id
        return ""

    def get_all_records(self, limit: int = None) -> List[Dict]:
        """
        获取所有历史记录

        Args:
            limit: 限制返回数量，None表示返回全部

        Returns:
            List[Dict]: 历史记录列表，按时间倒序
        """
        data = self._load_data()
        records = data.get("records", [])

        # 按时间倒序排序
        records.sort(key=lambda x: x.get("date", ""), reverse=True)

        if limit:
            return records[:limit]
        return records

    def get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """
        根据ID获取记录

        Args:
            record_id: 记录ID

        Returns:
            Dict: 记录详情，不存在返回None
        """
        data = self._load_data()
        records = data.get("records", [])

        for record in records:
            if record.get("id") == record_id:
                return record

        return None

    def delete_record(self, record_id: str) -> bool:
        """
        删除一条记录

        Args:
            record_id: 记录ID

        Returns:
            bool: 是否删除成功
        """
        data = self._load_data()
        records = data.get("records", [])

        # 过滤掉要删除的记录
        new_records = [r for r in records if r.get("id") != record_id]

        if len(new_records) < len(records):
            data["records"] = new_records
            return self._save_data(data)

        return False

    def clear_all_records(self) -> bool:
        """
        清空所有记录

        Returns:
            bool: 是否清空成功
        """
        return self._save_data({"records": []})

    def get_statistics(self) -> Dict:
        """
        获取统计信息

        Returns:
            Dict: 统计数据
            {
                "total_sessions": 总听写次数,
                "total_words": 总单词数,
                "total_correct": 总正确数,
                "average_score": 平均分,
                "total_duration": 总时长（秒）,
                "mode_stats": {模式: 次数},
                "recent_scores": [最近10次分数]
            }
        """
        records = self.get_all_records()

        if not records:
            return {
                "total_sessions": 0,
                "total_words": 0,
                "total_correct": 0,
                "average_score": 0,
                "total_duration": 0,
                "mode_stats": {},
                "recent_scores": []
            }

        total_sessions = len(records)
        total_words = sum(r.get("total_words", 0) for r in records)
        total_correct = sum(r.get("correct_count", 0) for r in records)
        total_duration = sum(r.get("duration_seconds", 0) for r in records)

        # 计算平均分
        scores = [r.get("score", 0) for r in records]
        average_score = round(sum(scores) / len(scores), 2) if scores else 0

        # 统计各模式次数
        mode_stats = {}
        for r in records:
            mode = r.get("mode", "unknown")
            mode_stats[mode] = mode_stats.get(mode, 0) + 1

        # 最近10次分数（按时间倒序）
        recent_scores = [r.get("score", 0) for r in records[:10]]

        return {
            "total_sessions": total_sessions,
            "total_words": total_words,
            "total_correct": total_correct,
            "average_score": average_score,
            "total_duration": total_duration,
            "mode_stats": mode_stats,
            "recent_scores": recent_scores
        }

    def get_wrong_words_frequency(self, limit: int = 20) -> List[Dict]:
        """
        获取错词频率统计

        Args:
            limit: 返回前N个高频错词

        Returns:
            List[Dict]: [{"word": "apple", "cn": "苹果", "count": 5}, ...]
        """
        records = self.get_all_records()

        # 统计错词频率
        wrong_freq = {}
        for record in records:
            wrong_words = record.get("wrong_words", [])
            for word in wrong_words:
                en = word.get("en", "")
                cn = word.get("cn", "")
                key = f"{en}|{cn}"

                if key not in wrong_freq:
                    wrong_freq[key] = {
                        "en": en,
                        "cn": cn,
                        "count": 0
                    }
                wrong_freq[key]["count"] += 1

        # 转换为列表并排序
        result = list(wrong_freq.values())
        result.sort(key=lambda x: x["count"], reverse=True)

        return result[:limit]

    def export_to_csv(self, output_file: str) -> bool:
        """
        导出历史记录为CSV

        Args:
            output_file: 输出文件路径

        Returns:
            bool: 是否导出成功
        """
        try:
            import csv

            records = self.get_all_records()

            with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)

                # 写入表头
                writer.writerow([
                    "记录ID", "日期", "模式", "词库", "总单词数",
                    "正确数", "分数", "用时(秒)"
                ])

                # 写入数据
                for record in records:
                    writer.writerow([
                        record.get("id", ""),
                        record.get("date", ""),
                        record.get("mode", ""),
                        record.get("vocabulary_name", ""),
                        record.get("total_words", 0),
                        record.get("correct_count", 0),
                        record.get("score", 0),
                        record.get("duration_seconds", 0)
                    ])

            return True

        except Exception as e:
            print(f"导出CSV失败: {e}")
            return False
