import os

CUR_DIRECTORY = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')

SRC_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(CUR_DIRECTORY)))

DB_DIRECTORY = SRC_DIRECTORY + "/backend/rag/chromadb"

#database config
DATABASE_NAME="RAG_DATABASE"
OPENAI_EMBEDDING_MODEL="gpt-4o-mini"