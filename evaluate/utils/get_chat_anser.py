import requests
from constants.constants import CHAT_API
import csv
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
def get_chat_answer(qa_file:str,output_file,mode:int=0):
    answer_list = []
    contexts_list = []
    with open(qa_file, mode='r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)

        next(csv_reader)
        output_data = []
        for row in csv_reader:
            question = row[0]
            ground_truth = row[1]
            ground_truths = [ground_truth]
            answer, context,_=send_chat_request(question=question, mode=mode)
            output_data.append({
                'question': question,
                'ground_truths': ground_truths,
                'answer': answer,
                'contexts': context
            })


        with open(output_file, mode='w', newline='', encoding='utf-8') as output_file:
            fieldnames = ['question', 'ground_truths', 'answer', 'contexts']
            writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            writer.writeheader()

            for data in output_data:
                writer.writerow(data)

        print("Data has been written to final_output.csv")