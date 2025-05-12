import csv
import os
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from constants.constants import MODEL, RESULT_DIRECTORY
load_dotenv(override=True)
class QuestionAnswer(BaseModel):
    question: str
    answer: str
open_api_key = os.environ.get('OPEN_API_KEY')
client = OpenAI(api_key=open_api_key)


def process_csv(input_file, output_file):
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile)

        with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
            csv_writer = csv.writer(outfile)

            csv_writer.writerow(['question', 'answer'])

            next(csv_reader)

            for row in csv_reader:
                completion = client.beta.chat.completions.parse(
                    model=MODEL,
                    messages=[
                        {"role": "system",
                         "content": "Tôi cung cấp cho bạn 1 đoạn văn trong đó có cả câu hỏi và ngữ cảnh. Sinh cho tôi câu hỏi và câu trả lời tương ứng bằng tiếng việt."
                                    "Câu trả lời phải dựa trên ngữ cảnh tôi cung cấp, bạn không được phép thêm vào bất kỳ thông tin gì"},
                        {"role": "user", "content": f"{row}"}
                    ],
                    response_format=QuestionAnswer,
                )
                result = completion.choices[0].message.parsed

                question = result.question
                answer= result.answer
                csv_writer.writerow([question, answer])

def gen_qa():
    input_file = os.path.join(RESULT_DIRECTORY, "dataset.csv")
    output_file = os.path.join(RESULT_DIRECTORY, "qa.csv")
    process_csv(input_file, output_file)