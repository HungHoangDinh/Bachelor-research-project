import csv
import ast
from dotenv import load_dotenv
import pandas as pd
from datasets import Dataset
from ragas import EvaluationDataset
from ragas.metrics._factual_correctness import FactualCorrectness
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, SemanticSimilarity,AnswerAccuracy,ResponseRelevancy
from ragas import evaluate
import os
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
load_dotenv(override=True)
def eval(excel_eval_file, output_file,mode:str):
    df = pd.read_excel(excel_eval_file)
    datalist = []
    for _, row in df.iterrows():
        try:
            ground_truths = row.get('ground_truths', '')
        except Exception as e:
            print(f"Error parsing ground_truths: {row.get('ground_truths', '')}")
            ground_truths = ""

        data = {
            'question': str(row.get('question', '')).strip(),
            'ground_truths': ground_truths,
            'answer': str(row.get(mode, '')).strip(),
        }
        datalist.append(data)

    dataset_dict = {
        'user_input': [item['question'] for item in datalist],
        'reference': [item['ground_truths'] for item in datalist],
        'response': [item['answer'] for item in datalist],
    }

    dataset = Dataset.from_dict(dataset_dict)
    # Đánh giá
    eval_dataset = EvaluationDataset.from_hf_dataset(dataset)
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
    evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
    metrics = [
        AnswerAccuracy(llm=evaluator_llm),
        ResponseRelevancy(llm=evaluator_llm,embeddings=evaluator_embeddings),
        FactualCorrectness(llm = evaluator_llm),
        SemanticSimilarity(embeddings=evaluator_embeddings),
    ]
    results = evaluate(dataset=eval_dataset, metrics=metrics)
    result_df = results.to_pandas()
    result_df.to_excel(output_file, index=False)
    return result_df.head()