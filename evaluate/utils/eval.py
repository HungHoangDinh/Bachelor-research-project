import csv
import ast
from dotenv import load_dotenv
import pandas as pd
from datasets import Dataset
from ragas import EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness, SemanticSimilarity
from ragas import evaluate
import os
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
load_dotenv(override=True)
def eval(csv_eval_file,output_file):
    datalist = []
    with open(csv_eval_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data = {
                'question': row.get('question', '').strip(),
                'ground_truths': (ast.literal_eval(row.get('ground_truths', '')))[0],
                'answer': row.get('answer', '').strip(),
                'contexts':  row.get('contexts', '').strip(),
            }
            datalist.append(data)
            retrived=[]
            for item in datalist:
                retrived.append([item['contexts']])
            dataset_dict = {
                'user_input': [item['question'] for item in datalist],
                'reference': [item['ground_truths'] for item in datalist],
                'response': [item['answer'] for item in datalist],
                'retrieved_contexts': retrived,
            }

            dataset = Dataset.from_dict(dataset_dict)

    eval_dataset = EvaluationDataset.from_hf_dataset(dataset)
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini"))
    evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())
    metrics = [
        LLMContextRecall(llm=evaluator_llm),
        FactualCorrectness(llm=evaluator_llm),
        Faithfulness(llm=evaluator_llm),
        SemanticSimilarity(embeddings=evaluator_embeddings)
    ]
    results = evaluate(dataset=eval_dataset, metrics=metrics)
    df = results.to_pandas()
    df.to_excel(output_file, index=False)
    df.head()