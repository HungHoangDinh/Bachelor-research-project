import os
import requests
import pandas as pd
from constants.constants import CHAT_API
import numpy as np

def send_chat_request(question: str, mode: int = 0):
    try:
        payload = {
            "question": question,
            "mode": mode
        }
        response = requests.post(CHAT_API, json=payload)
        response.raise_for_status()
        return response.json().get("data", {}).get("answer", ""), None, None
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to get chat response: {e}")

def save_csv_to_exel(qa_file: str, output_file: str):
    df_input = pd.read_csv(qa_file)
    data = {
        'question': [],
        'ground_truths': [],
    }

    for idx, row in df_input.iterrows():
        question = row['question']
        ground_truth = row['answer']
        data['question'].append(question)
        data['ground_truths'].append(ground_truth)
    df_output = pd.DataFrame(data)
    df_output.to_excel(output_file, index=False)
    print(f"Saved RAG-only output to {output_file}")
def append_mode_answers_xlsx(xlsx_file: str, mode_index: int, mode_name: str):
    df = pd.read_excel(xlsx_file)

    # Nếu cột chưa tồn tại, tạo một cột mới với giá trị NaN
    if mode_name not in df.columns:
        df[mode_name] = np.nan

    answers = df[mode_name].tolist()  # Lấy danh sách hiện tại của cột (bao gồm cả NaN)
    updated = False

    for i, question in enumerate(df['question']):
        if pd.isna(answers[i]):  # Chỉ xử lý nếu giá trị hiện tại là NaN
            print(f"Processing row {i}: {question}")
            answer, _, _ = send_chat_request(question, mode=mode_index)
            print(f"Answer: {answer}")
            answers[i] = answer
            updated = True

    if updated:
        df[mode_name] = answers
        df.to_excel(xlsx_file, index=False)
        print(f"Updated column '{mode_name}' in {xlsx_file}")
    else:
        print(f"No missing data in column '{mode_name}'. Nothing updated.")
