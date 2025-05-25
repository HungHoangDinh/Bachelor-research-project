import os
from dotenv import load_dotenv
load_dotenv(override=True)
CUR_DIRECTORY = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')

ROOT_DIRECTORY =os.path.dirname(os.path.dirname(CUR_DIRECTORY))
DATA_DIRECTORY=ROOT_DIRECTORY+"/backend/src/rag/data"
MODEL="gpt-4o-mini"
RESULT_DIRECTORY=ROOT_DIRECTORY+"/evaluate/results"
TESTSET_SIZE=20
HOST_SERVER = os.getenv("HOST_SERVER", "http://localhost:8000")
CHAT_API=HOST_SERVER+"/api/v1/chat/eval"