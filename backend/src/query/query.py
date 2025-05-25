import sys
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))
from .gpt_call.gpt_call_function import GPTCallingFunctions
from  rag.utils.database_managements import DatabaseManager
from src.graphrag.query.local_search import GraphragLocalSearch
from src.graphrag.query.drift_search import GraphragDriftSearch
from src.graphrag.query.global_search import GraphragGlobalSearch
from .constants.constants import NO_ANSWER_RESPONSE
from .question_answer_log.log_process import ChatHistory
class Query:

    def __init__(self):
        self.client = GPTCallingFunctions()
        self.database_manager = DatabaseManager()
        self.local_search = GraphragLocalSearch()
        self.global_search = GraphragGlobalSearch()
        self.drift_search = GraphragDriftSearch()
        self.chat_history_db=ChatHistory()
    def rag_question(self,question: str):
        try:
            document = self.database_manager.query_collection(questions=self.client.improve_question(question))
            print(document)
            if document == None:
                self.chat_history_db.add_history_chat(question=question, answer=NO_ANSWER_RESPONSE, citations=[])
                return NO_ANSWER_RESPONSE,[]
            answer, cites= self.client.query_from_chatgpt(question=question, info=document)
            self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
            return answer,cites
        except Exception as err:
            answer=f'Error format from answer: {err}'
            self.chat_history_db.add_history_chat(question=question,answer=answer,citations=[])

            return answer,[]
        
    async def query(self,question: str,mode:int = 0):
        print(mode)
        try:
            question_type = self.client.question_classification(question=question)
            
            if question_type == True:
                try:
                    if mode==0:
                        document = self.database_manager.query_collection(questions=self.client.improve_question(question))
                       
                        if document == None:
                            self.chat_history_db.add_history_chat(question=question, answer=NO_ANSWER_RESPONSE, citations=[])
                            return NO_ANSWER_RESPONSE,[],[]
                        answer, cites= self.client.query_from_chatgpt(question=question, info=document)
                        follow_up_question=await self.local_search.question_gen(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer,cites,follow_up_question
                    elif mode==7:
                        document = self.database_manager.query_collection(questions=[question])
                        if document == None:
                            self.chat_history_db.add_history_chat(question=question, answer=NO_ANSWER_RESPONSE, citations=[])
                            return NO_ANSWER_RESPONSE,[],[]
                        answer, cites= self.client.query_from_chatgpt(question=question, info=document)
                        follow_up_question=await self.local_search.question_gen(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer,cites,follow_up_question
                    elif mode == 1:
                        answer, cites =await self.local_search.local_search(query=question)
                        follow_up_question=await self.local_search.question_gen(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer, cites,follow_up_question
                    elif mode ==2:
                        answer, cites=await self.local_search.local_search_custom(query=question)
                        follow_up_question=await self.local_search.question_gen(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer, cites,follow_up_question
                    elif mode == 3:
                        answer, cites =await self.global_search.global_search(prompt=question)
                        follow_up_question=await self.local_search.question_gen(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer, cites,follow_up_question
                    elif mode == 4:
                        answer, cites =await self.global_search.global_search_custom(prompt=question)
                        follow_up_question=await self.local_search.question_gen(query=question)   
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer, cites,follow_up_question
                    elif mode == 5:
                        answer, cites =await self.drift_search.drift_search(query=question)
                        follow_up_question=await self.local_search.question_gen(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer, cites,follow_up_question
                    elif mode == 6:
                        answer, cites =await self.drift_search.drift_search_custom(question)
                        follow_up_question=await self.local_search.question_gen(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer, cites,follow_up_question
    

                except Exception as err:
                    answer=f'Error format from answer: {err}'
                    self.chat_history_db.add_history_chat(question=question,answer=answer,citations=[])

                    return answer,[],[]

            else:
                answer = self.client.query_greeting(question=question)
                self.chat_history_db.add_history_chat(question=question, answer=answer, citations=[])
                return answer,[]
                
        except Exception as e:
            return f"Error when query: {e}",[]
    async def query_eval(self,question: str,mode:int = 0):
        print(mode)
        try:
            question_type = self.client.question_classification(question=question)
            
            if question_type == True:
                try:
                    if mode==0:
                        document = self.database_manager.query_collection(questions=self.client.improve_question(question))
                       
                        if document == None:
                            self.chat_history_db.add_history_chat(question=question, answer=NO_ANSWER_RESPONSE, citations=[])
                            return NO_ANSWER_RESPONSE
                        answer, cites= self.client.query_from_chatgpt(question=question, info=document)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer
                    elif mode==7:
                        document = self.database_manager.query_collection(questions=[question])
                        if document == None:
                            self.chat_history_db.add_history_chat(question=question, answer=NO_ANSWER_RESPONSE, citations=[])
                            return NO_ANSWER_RESPONSE
                        answer, cites= self.client.query_from_chatgpt(question=question, info=document)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer
                    elif mode == 1:
                        answer, cites =await self.local_search.local_search(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer
                    elif mode ==2:
                        answer, cites=await self.local_search.local_search_custom(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer
                    elif mode == 3:
                        answer, cites =await self.global_search.global_search(prompt=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer
                    elif mode == 4:
                        answer, cites =await self.global_search.global_search_custom(prompt=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer
                    elif mode == 5:
                        answer, cites =await self.drift_search.drift_search(query=question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer
                    elif mode == 6:
                        answer, cites =await self.drift_search.drift_search_custom(question)
                        self.chat_history_db.add_history_chat(question=question, answer=answer, citations=cites)
                        return answer
    

                except Exception as err:
                    answer=f'Error format from answer: {err}'
                    self.chat_history_db.add_history_chat(question=question,answer=answer,citations=[])

                    return answer

            else:
                answer = self.client.query_greeting(question=question)
                self.chat_history_db.add_history_chat(question=question, answer=answer, citations=[])
                return answer
                
        except Exception as e:
            return f"Error when query: {e}"


