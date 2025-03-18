import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..")))
from src.backend.query.gpt_call.gpt_call_function import GPT_Calling_Functions
from  src.backend.rag.utils.database_managements import DatabaseManager
class Query:

    def __init__(self):
        self.client = GPT_Calling_Functions()
        self.database_manager = DatabaseManager()

    def query(self,question: str):
        try:
            question_type = self.client.question_classification(question=question)
          
            if question_type == "true":
                try:
                    document = self.database_manager.query_collection(questions=[question])
                    if document == None:
                        yield "Xin lỗi bạn, hiện tôi vẫn chưa có thông tin về câu hỏi này."
                        return
                    collected_result = ""
                    for chunk in self.client.query_from_chatgpt(question=question, info=document):
                        collected_result += chunk
                        yield chunk
                
                    if "Xin lỗi bạn, có thể dữ liệu được cung cấp không có thông tin về kiến thức này." in collected_result:
                        if(document!=None and len(document[:3])>0):

                            yield "\nCó thể bạn sẽ quan tâm đến các thông tin sau: "
                            infos=document[:3]
                            i=1
                            for info in infos:
                                yield f"\n{i}. "
                                i=i+1
                                for chunk in self.client.query_relevant_question(info):
                                    yield chunk
    

                except Exception as err:
                    yield f'Error format from answer: {err}'
            else:
                answer = self.client.query_greeting(question=question)
                yield answer
                
        except Exception as e:
            yield f"Error when query: {e}"
question="Cách điều trị rối loạn nhịp thất"
query=Query()
for i in query.query(question):
    print(i, end="")

