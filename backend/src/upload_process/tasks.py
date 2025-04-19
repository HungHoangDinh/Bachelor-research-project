import io
import os
from .celery_app import celery_app
from .minio_client import bucket_name, minio_client
from PIL import Image


@celery_app.task(name='tasks.save_pdf_to_minio')
def save_pdf_to_minio(file_data: bytes, filename: str):
    try:
        file_stream = io.BytesIO(file_data)
        try:
            minio_client.stat_object(bucket_name, filename)
            return f"File {filename} đã tồn tại trong MinIO."
        except Exception as e:
            if "NoSuchKey" in str(e):
                pass
            else:
                return f"Error checking file existence: {str(e)}"
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=filename,
            data=file_stream,
            length=len(file_data),
            content_type='application/pdf'
        )

        return {"message": f"Tạo thư mục {filename.replace('.pdf', '')} và lưu cơ sở dữ liệu thành công."}

    except Exception as e:
        return f"Error uploading file {filename}: {str(e)}"


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

        # databaseManager = DatabaseManager()
        # databaseManager.delete_data(filename=filename)

        return f"File {filename} và dữ liệu liên quan được xóa thành công."

    except Exception as e:
        return str(e)