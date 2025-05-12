from src.rag.utils.data_process import DataProcessing
from src.graphrag.index import index
if __name__ == "__main__":
    data_processing=DataProcessing()
    data_processing.process_all_file()
    index()