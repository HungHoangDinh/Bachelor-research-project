import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..","..")))
from datetime import datetime
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..constants.constants import CHUNK_SIZE, CHUNK_OVERLAP
class Chunking:
    def __init__(self):
        load_dotenv()
        self.open_api_key = os.environ.get('OPENAI_API_KEY')
        self.chunk_size = int(CHUNK_SIZE)
        self.chunk_overlap = int(CHUNK_OVERLAP)

    def chunking_documents(self, document,filename):
        data = []
        metadata = []

        
        headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
        md_header_splits = markdown_splitter.split_text(document)
       
        text_splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\n\n",
                "\n",
                ".",
            ],
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )
        splits = text_splitter.split_documents(md_header_splits)
        
        for text_split in splits:
            text_split.metadata["filename"]=filename
        for text_split in splits:
            content = text_split.page_content
            mts = text_split.metadata
            for md_header_split in md_header_splits:
                text = md_header_split.page_content
                if content in text:
                    mts['raw_text'] = text
                    break
            header_order = ["Header 2", "Header 1"]
         
            for header in header_order:
                for item in mts:
                    if header == item:
                        content = f"{mts[item]}: {content}"
                        mts["raw_text"]= mts[item]+": "+mts["raw_text"]
            
            

            data.append(content)
            metadata.append(mts)
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        ids = [f"{current_time}_{i}" for i in range(1, len(data) + 1)]
        return data, metadata, ids
