import csv
import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
import pandas as pd
from constants.constants import MODEL, RESULT_DIRECTORY
load_dotenv(override=True)
class CheckAnswer(BaseModel):
    total_number_infomation: int
    informations: List[str] 
    correct_informations: List[str]
    number_correct_infomation: int
class CheckAnswerReturn(BaseModel):
    answer: List[CheckAnswer] 
open_api_key = os.environ.get('OPEN_API_KEY')
client = OpenAI(api_key=os.environ.get("GEMINI_API_KEY"),base_url=os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"))
def check_answer(documents: str,question:str, answers:str):
    system_prompt="""
    1. Bạn là một chuyên gia trong việc đánh giá tính chính xác của các câu trả lời dựa trên ngữ cảnh được cung cấp.
    2. Tôi sẽ cung cấp cho bạn một đoạn vài văn bản về lĩnh vực ý tế, một câu hỏi và một danh sách các câu trả lời cho câu hỏi đó. Các câu trả lời được sinh ra đọc lập bởi các hệ thống khác nhau.
    3.. Nhiệm vụ của bạn là đọc từng câu trả lời đó, trong mỗi câu trả lời thường có rất nhiều thông tin. Hãy đánh giá số lượng thông tin trong từng câu trả lời(total_number_infomation) và kiểm tra xem thông tin đấy có đúng không bằng cách so sánh với tài liệu, trả về số lượng thông tin được lấy ra từ tài liệu(total_number_infomation). Ngoài ra, bạn cũng phải đưa ra danh sách các thông tin(informations)và danh sách các thông tin được trích xuất từ tài liệu(correct_informations) tương ứng.
    4. Trả về kết quả dưới dạng JSON với các trường sau:
    - total_number_infomation: Tổng số lượng thông tin trong câu trả lời.
    - informations: Danh sách thông tin có trong câu trả lời.
    - correct_infomations: Danh sách các thông tin được trích xuất từ tài liệu.
    - number_correct_infomation: Số lượng thông tin được lấy ra từ tài liệu.
    5. Trả về danh sách là một mảng,sắp xếp đúng theo thứ tự xuất hiện các câu trả lời, mỗi phần tử là một đối tượng JSON chứa thông tin về từng câu trả lời."""
    user_prompt=f"""
    ## Dưới đây là đoạn văn bản về lĩnh vực y tế:
    {documents}
    ## Câu hỏi:
    {question}
    ## Dưới đây là danh sách các câu trả lời:
    {answers}
    """
    completion = client.beta.chat.completions.parse(
        model="gemini-2.5-flash-preview-04-17",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=CheckAnswerReturn,
    )
    result = completion.choices[0].message.parsed
    data=[]
    for re in result.answer:
        data.append({"total_number_infomation":re.total_number_infomation,"number_correct_infomation": re.number_correct_infomation})
    return data
def read_documents(input_dir):
    documents = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".md"):
            input_file=os.path.join(input_dir, file_name)
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
                content=content.replace("#","")
                documents.append(content.strip())
    documents_string=""
    for  index, document in enumerate(documents, start=1):
        documents_string+=f"### Tài liệu {index}\n{document}\n\n"
    return documents_string
def read_questions_answer(input_file):
    # input_file is a excel file
    df = pd.read_excel(input_file)
    questions =[]
    answers=[]
    for _, row in df.iterrows():
        question = str(row.get('question', '')).strip()
        mini_answers=[]
        mini_answers.append(str(row.get('RAG', '')).strip())
        mini_answers.append(str(row.get('RAG Custom', '')).strip())
        mini_answers.append(str(row.get('Local Search', '')).strip())
        mini_answers.append(str(row.get('Local Search Custom', '')).strip())
        mini_answers.append(str(row.get('Global Search', '')).strip())
        mini_answers.append(str(row.get('Global Search Custom', '')).strip())
        mini_answers.append(str(row.get('Drift Search', '')).strip())
        mini_answers.append(str(row.get('Drift Search Custom', '')).strip())
        mini_answers.append(str(row.get('Google AI Studio', '')).strip())
        mini_answers.append(str(row.get('ChatGPT', '')).strip())
        answers.append(mini_answers)
        questions.append(question)
    return questions, answers
def gen_check_answer(input_dir, input_file,output_file, start,end):
    documents= read_documents(input_dir)
    questions, answers = read_questions_answer(input_file)
    answer_strings=[]
    for answer in answers:
        answer_string = "\n".join([f"Answer {i+1}:\n {ans}\n\n" for i, ans in enumerate(answer) if ans])
        answer_strings.append(answer_string)

    data_total_info = {
        'question': [],
        'RAG': [],
        "RAG Custom":[],
        "Local Search":[],
        "Local Search Custom":[],
        "Global Search":[],
        "Global Search Custom":[],
        "Drift Search":[],
        "Drift Search Custom":[],
        "Google AI Studio":[],
        "ChatGPT":[]
    }
    data_correct_info = {
        'question': [],
        'RAG': [],
        "RAG Custom":[],
        "Local Search":[],
        "Local Search Custom":[],
        "Global Search":[],
        "Global Search Custom":[],
        "Drift Search":[],
        "Drift Search Custom":[],
        "Google AI Studio":[],
        "ChatGPT":[]
    }
    for i in range(start,end):
        print(questions[i])
        result=check_answer(documents=documents,question=questions[i],answers=answer_strings[i])
        data_total_info["question"].append(questions[i])
        data_total_info["RAG"].append(result[0]["total_number_infomation"])
        data_total_info["RAG Custom"].append(result[1]["total_number_infomation"])
        data_total_info["Local Search"].append(result[2]["total_number_infomation"])
        data_total_info["Local Search Custom"].append(result[3]["total_number_infomation"])
        data_total_info["Global Search"].append(result[4]["total_number_infomation"])
        data_total_info["Global Search Custom"].append(result[5]["total_number_infomation"])
        data_total_info["Drift Search"].append(result[6]["total_number_infomation"])
        data_total_info["Drift Search Custom"].append(result[7]["total_number_infomation"])
        data_total_info["Google AI Studio"].append(result[8]["total_number_infomation"])
        data_total_info["ChatGPT"].append(result[9]["total_number_infomation"])
        data_correct_info["question"].append(questions[i])
        data_correct_info["RAG"].append(result[0]["number_correct_infomation"])
        data_correct_info["RAG Custom"].append(result[1]["number_correct_infomation"])
        data_correct_info["Local Search"].append(result[2]["number_correct_infomation"])
        data_correct_info["Local Search Custom"].append(result[3]["number_correct_infomation"])
        data_correct_info["Global Search"].append(result[4]["number_correct_infomation"])
        data_correct_info["Global Search Custom"].append(result[5]["number_correct_infomation"])
        data_correct_info["Drift Search"].append(result[6]["number_correct_infomation"])
        data_correct_info["Drift Search Custom"].append(result[7]["number_correct_infomation"])
        data_correct_info["Google AI Studio"].append(result[8]["number_correct_infomation"])
        data_correct_info["ChatGPT"].append(result[9]["number_correct_infomation"])
    df_output1 = pd.DataFrame(data_total_info)
    df_output1.to_excel(f"{output_file}_total_info.xlsx", index=False)
    df_output2 = pd.DataFrame(data_correct_info)
    df_output2.to_excel(f"{output_file}_correct_info.xlsx", index=False)

    
