import sqlite3
import json
from typing import List, Tuple, Optional
from pydantic import BaseModel
import os
from ..constants.constants import DATALOG_DIRECTORY
class ChatHistoryItem(BaseModel):
    id: int
    question: Optional[str]
    answer: Optional[str]
    citations: List[str]
class ChatHistoryData(BaseModel):
    history: List[ChatHistoryItem]

class ChatHistory:
    def __init__(self):
        self.db_path=DATALOG_DIRECTORY
        self._create_table()

    def _create_table(self):

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            cursor=conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS history_chat (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT ,
                    answer TEXT ,
                    citations TEXT 
                )
            """
            )
            conn.commit()
    def add_history_chat(self, question: str, answer: str, citations: List[str]):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            citations_json = json.dumps(citations) if citations else "[]"
            cursor.execute("""
                INSERT INTO history_chat (question, answer, citations) 
                VALUES (?, ?, ?)
            """, (question, answer, citations_json))
            conn.commit()

    def get_history_chat(self, limit: Optional[int] = None) -> ChatHistoryData:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if limit is None:
                cursor.execute("""
                    SELECT id, question, answer, citations FROM history_chat 
                    ORDER BY id DESC
                """)
            else:
                cursor.execute("""
                    SELECT id, question, answer, citations FROM history_chat
                    ORDER BY id DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
        history_items = [ChatHistoryItem(id=row[0], question=row[1], answer=row[2], citations=json.loads(row[3])) for row in rows]
        return ChatHistoryData(history=history_items)


    def clear_history_chat(self):
       
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM history_chat")
            conn.commit()

