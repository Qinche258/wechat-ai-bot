"""
对话记忆管理模块
使用 SQLite 存储对话历史，支持长期记忆
"""

import sqlite3
import json
from datetime import datetime
from config import MEMORY_DB_PATH, MEMORY_ROUNDS


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(MEMORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_id ON conversations(user_id)
    """)
    conn.commit()
    conn.close()


def save_message(user_id: str, role: str, content: str):
    """保存一条消息"""
    conn = sqlite3.connect(MEMORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    conn.commit()
    conn.close()


def get_history(user_id: str, rounds: int = None) -> list:
    """
    获取用户的对话历史
    返回格式：[ {"role": "user", "content": "..."}, ... ]
    """
    if rounds is None:
        rounds = MEMORY_ROUNDS

    conn = sqlite3.connect(MEMORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT role, content FROM conversations 
           WHERE user_id = ? 
           ORDER BY timestamp DESC 
           LIMIT ?""",
        (user_id, rounds * 2)  # 每轮包含 user + assistant
    )
    rows = cursor.fetchall()
    conn.close()

    # 反转顺序（从旧到新）
    history = []
    for row in reversed(rows):
        history.append({"role": row[0], "content": row[1]})

    return history


def clear_history(user_id: str):
    """清除某用户的所有对话历史"""
    conn = sqlite3.connect(MEMORY_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversations WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True
