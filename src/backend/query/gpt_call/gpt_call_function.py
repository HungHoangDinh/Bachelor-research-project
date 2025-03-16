import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..","..")))
import json
from src.backend.query.gpt_call.gpt_call_type import ChatGPTCallingType


def create_message(system_contents: str, user_contents: str, histories=None):
    messages = [{
        "role": "system",
        "content": [{"type": "text",
                     "text": f'{system_contents}'}]
    }]
    if histories:
        for history in histories:
            messages.append({
                "role": history["role"],
                "content": [{'type': "text",
                             "text": history['content']}]
            })

    messages.append({
        "role": "user",
        "content": [{"type": "text",
                     "text": f'{user_contents}'}]
    })
    return messages


class GPT_Calling_Functions:
    def __init__(self):
        self.client = ChatGPTCallingType()

    def question_classification(self, question: str) -> str:
        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot y tế.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến thông tin y tế, sức khỏe và chăm sóc bệnh nhân.\n"
            "3. Đọc câu hỏi mà tôi đưa ra.\n"
            "4. Xác định câu hỏi được đưa ra có phải câu chào hỏi thông thường (để làm quen, giới thiệu) hay không.\n"
            "5. Nếu là câu chào hỏi thông thường, hãy trả lời là 'false'.\n"
            "6. Nếu là câu hỏi về kiến thức, hãy trả về 'true'.\n"
            "7. Chỉ trả lời là 'true' hoặc 'false'.\n"
            "8. Không được thêm thông tin gì ngoài ngữ cảnh tôi cung cấp."
        )
        messages = create_message(system_contents, user_contents=question)
       
        return self.client.default_chat_completion(messages)
    def query_greeting(self, question: str) -> str:
        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot y tế.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến thông tin y tế, sức khỏe và chăm sóc bệnh nhân.\n"
            "3. Đứng trên các vai trò trên, bạn hãy trả lời câu chào hỏi dưới đây khi người dùng gặp bạn.\n"
            "4. Trả lời bằng tiếng Việt."
        )
        messages = create_message(system_contents, user_contents=question)
        return self.client.default_chat_completion(messages)

    def query_relevant_question(self,  info):

        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ y tế.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến thông tin y tế, sức khỏe và chăm sóc bệnh nhân.\n"
            "3. Trả lời bằng tiếng Việt.\n"
            "4. Đọc thông tin được cung cấp sau đó sinh ra duy nhất một câu hỏi và câu trả lời dựa trên thông tin đó. Các câu trả lời phải dựa trên thông tin mà tôi cung cấp.\n"
            "5. Trả về các câu hỏi, câu trả lời trên theo dạng 'Câu hỏi': 'abc?', 'Câu trả lời': 'xyz'.\n"
            "6. Không được trả về các thông tin không có trong nội dung được tôi cung cấp."
        )

        user_contents = f' Thông tin:{info}'
        messages = create_message(system_contents, user_contents)

        for chunk in self.client.stream_chat_completion(messages):
            yield chunk

    def query_from_chatgpt(self, question: str, info, histories=None):
        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot y tế.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến thông tin y tế, sức khỏe và chăm sóc bệnh nhân.\n"
            "3. Trả lời bằng tiếng Việt.\n"
            "4. Đọc câu hỏi của user và câu trả lời của assistant được cung cấp.\n"
            "5. Đọc câu hỏi được đưa ra. Trả lời câu hỏi của user, dựa trên câu hỏi của user, câu trả lời của assistant trước đó và thông tin được cung cấp ngay phía sau câu hỏi.\n"
            "6. Nếu tìm thấy dữ liệu có liên quan đến câu hỏi, dù ít hay nhiều, thì đưa ra câu trả lời tương ứng.\n"
            "7. Nếu không tìm thấy dữ liệu cho câu hỏi thì trả về 'Xin lỗi bạn, có thể dữ liệu được cung cấp không có thông tin về kiến thức này.'\n"
            "8. Không được trả về thông tin không có trong nội dung mà tôi không cung cấp."
        )


        user_contents = f' Câu hỏi: {question}, Thông tin liên quan:{info}'
        messages = create_message(system_contents, user_contents, histories)
        for chunk in self.client.stream_chat_completion(messages):
            yield chunk

