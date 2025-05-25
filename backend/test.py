from src.rag.utils.database_managements import DatabaseManager
data_manager = DatabaseManager()
print(data_manager.collection.query(query_texts=["What is the capital of France?"], n_results=1))