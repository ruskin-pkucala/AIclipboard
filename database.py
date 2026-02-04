"""
数据存储模块 - SQLite 实现
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class Database:
    """剪贴板记录数据库"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path.home() / ".clipboard-polisher" / "records.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clipboard_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,
                content TEXT NOT NULL,
                image_path TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                corrected TEXT,
                correction_status TEXT DEFAULT 'pending'
            )
        """)

        conn.commit()
        conn.close()

    def add_record(self, content_type: str, content: str, image_path: str = None) -> int:
        """添加新记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO clipboard_records (content_type, content, image_path)
            VALUES (?, ?, ?)
        """, (content_type, content, image_path))

        record_id = cursor.lastrowid
        print(f"[DEBUG] 添加记录 ID={record_id}, 类型={content_type}, 内容长度={len(content)}")

        # 检查是否超过最大记录数，FIFO 删除
        cursor.execute("SELECT COUNT(*) FROM clipboard_records")
        count = cursor.fetchone()[0]

        from config.settings import config
        if count > config.max_records:
            cursor.execute("""
                DELETE FROM clipboard_records
                WHERE id IN (
                    SELECT id FROM clipboard_records
                    ORDER BY timestamp ASC
                    LIMIT ?
                )
            """, (count - config.max_records,))

        conn.commit()
        conn.close()

        return record_id

    def get_recent_records(self, limit: int = 50) -> List[Dict]:
        """获取最近的记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, content_type, content, image_path, timestamp, corrected, correction_status
            FROM clipboard_records
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        records = []
        for row in cursor.fetchall():
            records.append({
                "id": row[0],
                "content_type": row[1],
                "content": row[2],
                "image_path": row[3],
                "timestamp": row[4],
                "corrected": row[5],
                "correction_status": row[6]
            })

        conn.close()
        return records

    def update_correction(self, record_id: int, corrected_text: str, status: str = "completed"):
        """更新纠错结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE clipboard_records
            SET corrected = ?, correction_status = ?
            WHERE id = ?
        """, (corrected_text, status, record_id))

        conn.commit()
        conn.close()

    def delete_record(self, record_id: int):
        """删除记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM clipboard_records WHERE id = ?", (record_id,))

        conn.commit()
        conn.close()

    def clear_all(self):
        """清空所有记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM clipboard_records")

        conn.commit()
        conn.close()


# 全局数据库实例
db = Database()
