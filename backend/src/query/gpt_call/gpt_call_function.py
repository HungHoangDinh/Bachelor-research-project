import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..","..")))
import json
from .gpt_call_type import ChatGPTCallingType
from pydantic import BaseModel
class Question_Classification_Output(BaseModel):
    question_class: bool
class Query_Greeting_Output(BaseModel):
    answer: str
class Query_Relevant_Question_Output(BaseModel):
    question: str
class Query_From_Chatgpt_Output(BaseModel):
    answer: str
    citations: list[int]
class Improve_Question_Output(BaseModel):
    answer: str
    item: str
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


class GPTCallingFunctions:
    def __init__(self):
        self.client = ChatGPTCallingType()

    def question_classification(self, question: str) -> str:
        system_contents = (
            "1. Đọc câu hỏi mà tôi đưa ra.\n"
            "2. Xác định câu hỏi được đưa ra có phải câu chào hỏi thông thường (để làm quen, giới thiệu) hay không.\n"
            "3. Nếu là câu chào hỏi thông thường, hãy trả lời là 'false'.\n"
            "4. Nếu là câu hỏi về kiến thức, hãy trả về 'true'.\n"
            "5. Chỉ trả lời là 'true' hoặc 'false'.\n"
            "6. Không được thêm thông tin gì ngoài ngữ cảnh tôi cung cấp."
        )
        messages = create_message(system_contents, user_contents=question)
       
        return (self.client.default_chat_completion(messages,Question_Classification_Output)).question_class
    def query_greeting(self, question: str) -> str:
        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot y tế.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến thông tin y tế, sức khỏe và chăm sóc bệnh nhân.\n"
            "3. Đứng trên các vai trò trên, bạn hãy trả lời câu chào hỏi dưới đây khi người dùng gặp bạn.\n"
            "4. Trả lời bằng tiếng Việt."
        )
        messages = create_message(system_contents, user_contents=question)
        return self.client.default_chat_completion(messages,Query_Greeting_Output).answer

    def query_relevant_question(self,  info):

        system_contents = (
            "1. Bạn đang đóng vai trò là một chatbot hỗ trợ y tế.\n"
            "2. Bạn được xây dựng để trả lời các câu hỏi liên quan đến thông tin y tế, sức khỏe và chăm sóc bệnh nhân.\n"
            "3. Trả lời bằng tiếng Việt.\n"
            "4. Đọc thông tin được cung cấp sau đó sinh ra duy nhất một câu hỏi dựa trên thông tin đó.\n"
            "5. Chỉ trả về câu hỏi bạn sinh ra.\n"
            "6. Không được trả về các thông tin không có trong nội dung được tôi cung cấp hoặc bịa đặt thông tin sai sự thật."
        )

        user_contents = f' Thông tin:{info}'
        messages = create_message(system_contents, user_contents)

        return self.client.default_chat_completion(messages,Query_Relevant_Question_Output).question

    def query_from_chatgpt(self, question: str, info, histories=None):
        system_contents = (
            "1.  Bạn đang đóng vai trò là một chatbot y tế. Bạn được xây dựng để trả lời các câu hỏi liên quan đến thông tin y tế, sức khỏe và chăm sóc bệnh nhân.\n"
            "2. Trả lời bằng tiếng Việt.\n"
            "3. Đọc câu hỏi của user và câu trả lời của assistant được cung cấp.\n"
            "4. Đọc câu hỏi được đưa ra. Trả lời câu hỏi của user, dựa trên câu hỏi của user, câu trả lời của assistant trước đó và thông tin được cung cấp ngay phía sau câu hỏi.\n"
            "5. Nếu tìm thấy dữ liệu có liên quan đến câu hỏi,  thì đưa ra câu trả lời tương ứng.\n"
            "6. Kết quả gồm câu trả lời và một lít các citations, trong trong đó citation là số thứ tự của source mà bạn lấy thông tin để tạo ra câu trả lời, được đánh số bắt đầu từ 1\n "
            "7. Nếu không tìm thấy dữ liệu cho câu hỏi thì trả về 'Xin lỗi bạn, có thể dữ liệu được cung cấp không có thông tin về kiến thức này.' và khi đó citations là một mảng rỗng\n"
            "8. Không được trả về thông tin không có trong nội dung mà tôi cung cấp hoặc bịa đặt thông tin sai sự thật.\n"
            "9.Mọi câu hỏi được đề cập đều đến lĩnh vực y tế."
            
        )

        sources=""
        i=1
        for inf in info:
            source=f"Source: {i} \n Infomation: {inf}+\n\n"
            i=i+1
            sources=sources+source
        user_contents = f' Question: {question}? \n\n {sources}'
        messages = create_message(system_contents, user_contents, histories)
        response=self.client.default_chat_completion(messages,Query_From_Chatgpt_Output)
  
        if response.answer!="Xin lỗi bạn, có thể dữ liệu được cung cấp không có thông tin về kiến thức này.":
            cites=[]
            for i in range(len(response.citations)):
                cites.append(info[response.citations[i]-1])
            return response.answer,cites
        else:
            return response.answer,[]
    def improve_question(self, question: str):
        system_contents = """
            1.  Bạn đang đóng vai trò là một chatbot y tế. Bạn được xây dựng để trả lời các câu hỏi liên quan đến thông tin y tế, sức khỏe và chăm sóc bệnh nhân.\n
            2.Trả lời câu hỏi được đưa ra.
            3. Đưa ra đối tượng chính của câu hỏi đó
            4. Trả kết quả về dạng json chứa hai đối tượng là answer và item, tương ứng với 1 và 2
            5. Chỉ đưa ra nội dung tôi yêu cầu, không trả lời gì thêm. 
            6. Không được thêm thông tin gì ngoài ngữ cảnh tôi cung cấp.
            7 Ví dụ khi người dùng đưa ra câu hỏi:"Rối loạn nhịp thất là gì?" thì câu trả lời là: {
                                                      "answer": "Rối loạn nhịp thất là tình trạng bất thường của nhịp tim khi ổ phát nhịp ngoại lai khởi phát từ tâm thất không dẫn truyền theo đường dẫn truyền chính thống mà lan trực tiếp giữa các tế bào cơ tim, khiến cho trình tự khử cực tâm thất thay đổi",
                                                      "item": "Rối loạn nhịp thất"
                   
        )
        """
        messages = create_message(system_contents, user_contents=question)
        question_context=self.client.default_chat_completion(messages,Improve_Question_Output)
        
        try:
            answer=question_context.answer
            item=question_context.item
            return [question,answer,item]
        except:
            return [question]

    
