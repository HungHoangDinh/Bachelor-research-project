import requests
from .constants.constants import UPLOAD_API, DELETE_API, DOWNLOAD_API, CHECK_STATUS_API, LIST_PDFS_API
def upload_file_request(uploaded_file):
    try:
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(UPLOAD_API, files=files)
        response.raise_for_status()
        return response.json().get("data", {}).get("task_id", "")
    except requests.exceptions.RequestException as e:
        raise(f"Failed to upload file: {e}")
def download_file_request(filename):
    try:
        response = requests.post(DOWNLOAD_API, json={"filename": filename})
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        raise(f"Failed to download file: {e}")
def delete_file_request(filename):
    try:
        response = requests.delete(DELETE_API, json={"filename": filename})
        response.raise_for_status()
        return response.json().get("message", "")
    except requests.exceptions.RequestException as e:
        raise(f"Failed to delete file: {e}")
def check_task_status_request(task_id):
    try:
        response = requests.post(CHECK_STATUS_API, json={"task_id": task_id})
        response.raise_for_status()
        result = response.json().get("data")
        return result["status"], result["result"]

    except requests.exceptions.RequestException as e:
        raise(f"Failed to check task status: {e}")
def list_pdfs_request():
    try:
        response = requests.get(LIST_PDFS_API)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        raise(f"Failed to list PDFs: {e}")