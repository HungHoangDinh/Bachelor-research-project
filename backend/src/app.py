import os
from typing import Optional
from query.question_answer_log.log_process import ChatHistory,ChatHistoryData
from fastapi import FastAPI, File, HTTPException, UploadFile
from query.query import Query
from pydantic import BaseModel
from src.file_process.tasks import save_pdf_to_minio, download_pdf_from_minio,delete_pdf
from celery.result import AsyncResult
from fastapi.responses import StreamingResponse
from src.file_process.celery_app import celery_app
import urllib.parse
from src.file_process.minio_client import (bucket_name, minio_client)
from dotenv import load_dotenv
import asyncio
import uvicorn
import io
load_dotenv(override=True)
api_port = int(os.environ.get('API_PORT', 8000))  
api_host = os.environ.get("API_HOST", "0.0.0.0") 

app = FastAPI(title="Medical Chatbot API")

query = Query()
chat_history = ChatHistory()

class BaseResponse(BaseModel):
    code: int  # 0 if success, > 0 if failed, code value indicates error type
    message: str  # e.g: "Retrieve chat history successfully" or "Failed to retrieve chat history"
    data: Optional[BaseModel]  # Customized based on particular APIs
class ChatHistoryResponse(BaseResponse):
    data: Optional[ChatHistoryData]
class Query_From_Chatgpt_Output(BaseModel):
    answer: str
    cites: list[str]
    follow_up_question: list[str]
class ChatResponse(BaseResponse):
    data: Optional[Query_From_Chatgpt_Output]
class DeleteDBResponse(BaseResponse):
    data: Optional[str]
class FileTaskReturn(BaseModel):
    task_id: str
class UploadFileResponse(BaseResponse):
    data: Optional[FileTaskReturn]

class ChatRequest(BaseModel):
    question: str
    mode: int=0
class TaskStatusRequest(BaseModel):
    task_id: str
class TaskStatusResponse(BaseResponse):
    data: dict 
class DownloadFileRequest(BaseModel):
    filename: str
class ListPDFsResponse(BaseResponse):
    data: Optional[list[str]]
class DeletePDFRequest(BaseModel):
    filename: str
class DeletePDFResponse(BaseResponse):
    data: Optional[str]
@app.post("/api/v1/chat/history",response_model=ChatHistoryResponse)
def get_chat_history(limit: Optional[int] = None)-> ChatHistoryResponse:
    try:
        history = chat_history.get_history_chat(limit=limit)
        return ChatHistoryResponse(code=0,message="Retrieve chat history successfully", data=history)
    except Exception as e:
        return ChatHistoryResponse(code=1, message=f"Failed to retrieve chat history: {str(e)}",data=None)

@app.post("/api/v1/chat",response_model=ChatResponse)
async def chat(request: ChatRequest)-> ChatResponse:
    try:
        answer, cites,follow_up_question =await query.query(question=request.question, mode=request.mode)
        return ChatResponse(code=0, message="Chat response retrieved successfully",data=Query_From_Chatgpt_Output(answer=answer,cites=cites, follow_up_question=follow_up_question))
    except Exception as e:
        return ChatResponse(code=1, message=f"Failed to retrieve chat response: {str(e)}",data=None)
@app.delete("/api/v1/delete/chat_log",response_model=DeleteDBResponse)
def delete_database()->DeleteDBResponse:
    try:
        chat_history.clear_history_chat()
        return DeleteDBResponse(code=0,message="Chat log deleted successfully",data=None)
    except Exception as e:
        return DeleteDBResponse(code=1,message=f"Failed to delete chat log: {str(e)}",data=None)
    

@app.post("/api/v1/upload_pdf/",response_model=UploadFileResponse)
async def upload_pdf(file: UploadFile = File(...))-> UploadFileResponse:
    try:
        if file.content_type != "application/pdf":
            return UploadFileResponse(code=0, message="Chỉ chấp nhận tệp PDF.", data=None)
        file_data = await file.read()

        filename = file.filename

        task = save_pdf_to_minio.delay(file_data, filename)

        return UploadFileResponse(code=0, message="Tệp PDF đang được tải lên.", data=FileTaskReturn(task_id=task.id))
    except Exception as e:
        return UploadFileResponse(code=1, message=f"Tải lên thất bại: {str(e)}", data=None)

        


@app.post("/api/v1/task_status",response_model=TaskStatusResponse)
def get_task_status(request: TaskStatusRequest)-> TaskStatusResponse:
    task_id = request.task_id
    try:

        task_result = AsyncResult(task_id, app=celery_app)
    # Status is PENDING, SUCCESS, FAILURE
        return TaskStatusResponse(code=0, message="Lấy trạng thái tác vụ thành công", data={ "status": task_result.state, "result": task_result.info.get("message") if task_result.state == "SUCCESS" else "" })
    except Exception as e:
        return TaskStatusResponse(code=1, message=f"Lỗi khi lấy trạng thái tác vụ: {str(e)}", data=None)


@app.post("/api/v1/download_file")
async def download_file(request:DownloadFileRequest):
    filename = request.filename
    task = celery_app.send_task(
        'tasks.download_pdf_from_minio', args=[filename])
    while True:
        result = AsyncResult(task.id, app=celery_app)

        if result.state == "SUCCESS":
            file_data = result.result
            if isinstance(file_data, bytes):
                return StreamingResponse(
                    io.BytesIO(file_data),
                    media_type='application/pdf',
                    headers={
                        "Content-Disposition": f"attachment; filename*=UTF-8''{urllib.parse.quote(filename)}"
                    }
                )
            else:
                raise HTTPException(
                    status_code=500, detail="File không đúng định dạng.")

        elif result.state == "FAILURE":
            raise HTTPException(status_code=500, detail="Tải xuống thất bại.")

        elif result.state == "PENDING":
            await asyncio.sleep(1)

        else:
            raise HTTPException(status_code=500, detail="Lỗi không xác định.")


@app.get("/api/v1/list_pdfs",response_model=ListPDFsResponse)
async def list_pdfs()-> ListPDFsResponse:
    try:
        objects = minio_client.list_objects(bucket_name, recursive=True)
        pdf_files = [
            obj.object_name for obj in objects if obj.object_name.endswith('.pdf')]

        return ListPDFsResponse(code=0, message="Lấy danh sách tệp PDF thành công", data=pdf_files)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.delete("/api/v1/delete_pdf",response_model=DeletePDFResponse)
async def delete_pdf(request: DeletePDFRequest)-> DeletePDFResponse:
    try:
        filename = request.filename
        task = celery_app.send_task('tasks.delete_pdf', args=[filename])

        while True:
            result = AsyncResult(task.id, app=celery_app)

            if result.state == "SUCCESS":
                response_message = result.result
                if isinstance(response_message, str):
                    return DeletePDFResponse(code=0, message="Xóa tệp PDF thành công", data=response_message)
                else:
                    return DeletePDFResponse(code=1, message="Xóa tệp PDF thất bại", data=None)

            elif result.state == "FAILURE":
                response_message = result.result
                return DeletePDFResponse(code=1, message="Xóa tệp PDF thất bại", data=response_message)

            elif result.state == "PENDING":
                await asyncio.sleep(1)

            else:
                return DeletePDFResponse(code=1,message="Lỗi bất định",data=None)
    except Exception as e:
        return DeletePDFResponse(code=1, message=f"Lỗi khi xóa tệp PDF: {str(e)}", data=None)
        



if __name__ == "__main__":
    uvicorn.run(app, host=api_host, port=api_port)
