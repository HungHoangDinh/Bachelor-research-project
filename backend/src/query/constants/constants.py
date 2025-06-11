import os
OPENAI_CHAT_MODEL="gpt-4o-mini"
MAX_TOKENS=10000
NO_ANSWER_RESPONSE='Xin lỗi bạn, có thể dữ liệu được cung cấp không có thông tin về kiến thức này.'
SUGGEST_QUESTION_RESPONSE='Có thể bạn sẽ quan tâm đến các thông tin sau:'
CUR_DIRECTORY = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
DATALOG_DIRECTORY=os.path.dirname(CUR_DIRECTORY)+"/question_answer_log/sqlite3/chat_log.db"
GraphRAG_DATA_DIRECTORY=os.path.dirname(os.path.dirname(CUR_DIRECTORY))+"/graphrag/graphrag_db/input"

