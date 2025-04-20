import requests
from .constants.constants import CHAT_API, HISTORY_CHAT_API
def get_chat_history_request(limit=None):
    try:
        params = {"limit": limit} if limit is not None else {}
        response = requests.post(HISTORY_CHAT_API, params=params)
        response.raise_for_status()
        return response.json().get("data", []).get("history", [])
    except requests.exceptions.RequestException as e:
        raise(f"Failed to get chat history: {e}")
def send_chat_request(question:str, mode:int=0):
    try:
        payload = {
            "question": question,
            "mode": mode
        }
        response = requests.post(CHAT_API, json=payload)
        response.raise_for_status()
        return response.json().get("data", {}).get("answer", ""), response.json().get("data", {}).get("cites", []), response.json().get("data", {}).get("follow_up_question", [])
    except requests.exceptions.RequestException as e:
        raise(f"Failed to get chat response: {e}")
    