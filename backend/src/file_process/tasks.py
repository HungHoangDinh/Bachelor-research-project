import io
import os
from .celery_app import celery_app
from .minio_client import bucket_name, minio_client
from PIL import Image
from .data_process.parse_data import ParseHandler
from ..rag.utils.database_managements import DatabaseManager
from ..rag.utils.data_process import DataProcessing
dataProcess=DataProcessing()
databaseManager = DatabaseManager()
parserHandler = ParseHandler()
@celery_app.task(name='tasks.save_pdf_to_minio')
def save_pdf_to_minio(file_data: bytes, filename: str):
    try:
        file_stream = io.BytesIO(file_data)
        try:
            minio_client.stat_object(bucket_name, filename)
            return {"message":f"File đã tồn tại!"}
        except Exception as e:
            if "NoSuchKey" in str(e):
                pass
            else:
                return {"message": f"Error uploading file!"}
        content=parserHandler.get_content(file_stream)
        result=dataProcess.process_single_file(filename,content)
        if result:
            minio_client.put_object(
            bucket_name=bucket_name,
            object_name=filename,
            data=file_stream,
            length=len(file_data),
            content_type='application/pdf'
            )
        else:
            return {"message": f"Error processing file!"}

        return  {'message': f"File uploaded successfully!"}

    except Exception as e:
        return {"message": f"Error uploading file!"}


@celery_app.task(name='tasks.download_pdf_from_minio')
def download_pdf_from_minio(filename: str):
    try:
        response = minio_client.get_object(bucket_name, filename)

        file_stream = io.BytesIO(response.read())
        file_stream.seek(0)
        return file_stream.getvalue()

    except Exception as e:
        return str(e)


@celery_app.task(name='tasks.delete_pdf')
def delete_pdf(filename: str):
    try:
        minio_client.remove_object(bucket_name, filename)
        result=databaseManager.delete_data(filename=filename)
        if result:
            
            return f"Xóa tệp {filename} thành công."
        else:
            return f"Xóa tệp {filename} thất bại."

    except Exception as e:
        return str(e)