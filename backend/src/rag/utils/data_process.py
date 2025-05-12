import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..","..","..")))
from ..constants.constants import DATA_DIRECTORY
from .chunking import Chunking
from .database_managements import DatabaseManager


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
    def process_single_file(self, file_name, content):
        # This function will be used to process a single file
        try:
            data, metadata, ids=self.chunking_function.chunking_documents(content,file_name)
            if self.database.collection:
                print(data)
                print(metadata)
                self.database.add_data(data,metadata,ids)
                return True
            else:
                print("No collection found")
                return False
                
        except Exception as e:
            print(f"Error processing file {file_name}: {e}")
            return False
            
