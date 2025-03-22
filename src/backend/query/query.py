from .gpt_call.gpt_call_function import GPTCallingFunctions
from  ..rag.utils.database_managements import DatabaseManager
from ..graphrag.query.LocalQuery import local_query
from ..graphrag.query.GlobalQuery import global_query
from .constants.constants import NO_ANSWER_RESPONSE,SUGGEST_QUESTION_RESPONSE
class Query:

    def __init__(self):
        self.client = GPTCallingFunctions()
        self.database_manager = DatabaseManager()

    def query(self,question: str,mode:int = 0):
        
        try:
            question_type = self.client.question_classification(question=question)
            
            if question_type == True:
                try:
                    if mode==0:
                        document = self.database_manager.query_collection(questions=self.client.improve_question(question))
                       
                        if document == None:
                            return NO_ANSWER_RESPONSE
                        answer, cites=self.client.query_from_chatgpt(question=question, info=document)
                        
                        if cites ==[]:
                            if(document!=None and len(document[:3])>0):
                                new_question=f"\n  {SUGGEST_QUESTION_RESPONSE}\n"
                                infos=document[:3]
                                i=0
                                for info in infos:
                                    i=i+1
                                    begin_question=self.client.query_relevant_question(info)
                                    print(begin_question)
                                   
                                    new_question=new_question+"+ "+begin_question
                                     
                                    if i<len(info):
                                        new_question=new_question+"\n"
                            print(new_question)
                            return answer+new_question,cites
                        else:
                            return answer,cites
                    elif mode == 1:
                        return local_query(question),[]
                    else:
                        return global_query(question),[]
    

                except Exception as err:
                    return f'Error format from answer: {err}',[]
            else:
                answer = self.client.query_greeting(question=question)
                return answer,[]
                
        except Exception as e:
            return f"Error when query: {e}",[]


