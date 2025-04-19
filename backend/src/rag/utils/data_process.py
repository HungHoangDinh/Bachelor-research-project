import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..","..")))
from backend.src.rag.constants.constants import DATA_DIRECTORY
from backend.src.rag.utils.chunking import Chunking
from backend.src.rag.utils.database_managements import DatabaseManager


class DataProcessing():
    def __init__(self, data_directory=DATA_DIRECTORY):
        self.data_directory = data_directory
        self.database=DatabaseManager()
        self.chunking_function=Chunking()
    def process_all_file(self):
        # This function will be used to process all the files in the data directory
        for filename in os.listdir(self.data_directory):
            if filename.endswith(".md"):
                file_path=os.path.join(self.data_directory,filename)
                with open(file_path, "r", encoding="utf-8") as file:
                     content = file.read()
                data, metadata, ids=self.chunking_function.chunking_documents(content,filename)
            
                if self.database.collection:
                    
                    self.database.add_data(data,metadata,ids)
                    
                else:
                    print("No collection found")
data_processing=DataProcessing()
data_processing.process_all_file()

