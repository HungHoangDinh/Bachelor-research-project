import os

CUR_DIRECTORY = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')

ROOT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(CUR_DIRECTORY)))

DB_DIRECTORY = ROOT_DIRECTORY + "/src/rag/chromadb"
DATA_DIRECTORY=ROOT_DIRECTORY+"/src/rag/data"
#database config
DATABASE_NAME="RAG_DB"
OPENAI_EMBEDDING_MODEL="text-embedding-ada-002"
CHUNK_SIZE= 512
CHUNK_OVERLAP=64
TOP_DOCUMENTS_TO_RETRIEVE=5