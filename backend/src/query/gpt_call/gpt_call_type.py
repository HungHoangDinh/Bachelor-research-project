import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..","..")))
from dotenv import load_dotenv
from openai import OpenAI
from ..constants.constants import OPENAI_CHAT_MODEL,MAX_TOKENS
import tiktoken
def count_tokens(messages):
    encoding = tiktoken.encoding_for_model(OPENAI_CHAT_MODEL)
    return sum(len(encoding.encode(str(msg["content"]))) for msg in messages)
def trim_messages(messages):

    total_tokens = count_tokens(messages)
    while total_tokens > MAX_TOKENS and len(messages) > 1:
        messages.pop(len(messages)-1)  
        total_tokens = count_tokens(messages)

    return messages
class ChatGPTCallingType:
    def __init__(self):
        load_dotenv()

        self.open_api_key = os.environ.get('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.open_api_key)
        self.model = OPENAI_CHAT_MODEL

    def default_chat_completion(self, messages,response_format) -> str:
        messages = trim_messages(messages)
    
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            response_format=response_format
        )
        return completion.choices[0].message.parsed

    def stream_chat_completion(self, messages):
        messages = trim_messages(messages)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content