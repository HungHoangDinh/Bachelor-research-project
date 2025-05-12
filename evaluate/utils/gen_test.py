import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from dotenv import load_dotenv
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from ragas.testset import TestsetGenerator
import logging
from typing import List
from langchain.schema import Document
from constants.constants import DATA_DIRECTORY, MODEL, RESULT_DIRECTORY, TESTSET_SIZE
load_dotenv(override=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def load_markdown_documents(directory: str) -> List[Document]:
    """
    Load all Markdown files with debug information.
    """
    documents = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".md"):
                file_path = os.path.join(root, file)
                logging.info(f"Đang xử lý file: {file_path}")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        doc = Document(
                            page_content=content.strip(),
                            metadata={"source": file_path}
                        )
                        documents.append(doc)
                except Exception as e:
                    logging.error(f"Lỗi khi đọc file {file_path}: {e}")
                    raise e
    logging.info(f"Tổng số file đã tải: {len(documents)}")
    return documents

def gen_testset():
    try:
        logging.info('Begin loader documents')
        docs = load_markdown_documents(DATA_DIRECTORY)
        logging.info("End loader documents")
        generator_llm = LangchainLLMWrapper(ChatOpenAI(model=MODEL))
        generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
        generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
        dataset = generator.generate_with_langchain_docs(docs, testset_size=TESTSET_SIZE)
        df=dataset.to_pandas()
        df.to_csv(f"{RESULT_DIRECTORY}/dataset.csv", index=False, encoding="utf-8")
    except Exception as e:
        logging.error(f"Error in gen_testset: {e}")
        raise e