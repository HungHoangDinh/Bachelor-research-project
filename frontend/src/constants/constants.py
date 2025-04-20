from dotenv import load_dotenv
import os
load_dotenv()
HOST_SERVER = os.getenv("HOST_SERVER", "http://localhost:8000")
CHAT_API=HOST_SERVER+"/api/v1/chat"
HISTORY_CHAT_API=HOST_SERVER+"/api/v1/chat/history"
UPLOAD_API=HOST_SERVER+"/api/v1/upload_pdf"
DELETE_API=HOST_SERVER+"/api/v1/delete_pdf"
CHECK_STATUS_API=HOST_SERVER+"/api/v1/task_status"
DOWNLOAD_API=HOST_SERVER+"/api/v1/download_file"
LIST_PDFS_API=HOST_SERVER+"/api/v1/list_pdfs"