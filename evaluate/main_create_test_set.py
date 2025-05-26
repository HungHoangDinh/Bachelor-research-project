
from utils.get_chat_answer import save_csv_to_exel,append_mode_answers_xlsx
from utils.gen_test import gen_testset
from utils.gen_QA import gen_qa
from utils.metrics_base_claim import gen_check_answer
def regas_eval():
    gen_testset()
    gen_qa()
    save_csv_to_exel(qa_file="results/qa2.csv", output_file="results/eval2.xlsx")
    append_mode_answers_xlsx(xlsx_file="results/eval2.xlsx", mode_index=0, mode_name="RAG")
    append_mode_answers_xlsx(xlsx_file="results/eval2.xlsx", mode_index=1, mode_name="Local Search")
    append_mode_answers_xlsx(xlsx_file="results/eval2.xlsx", mode_index=2, mode_name="Local Search Custom")  
    append_mode_answers_xlsx(xlsx_file="results/eval2.xlsx", mode_index=3, mode_name="Global Search")
    append_mode_answers_xlsx(xlsx_file="results/eval2.xlsx", mode_index=4, mode_name="Global Search Custom")
    append_mode_answers_xlsx(xlsx_file="results/eval2.xlsx", mode_index=5, mode_name="Drift Search")
    append_mode_answers_xlsx(xlsx_file="results/eval2.xlsx", mode_index=6, mode_name="Drift Search Custom")
    append_mode_answers_xlsx(xlsx_file="results/eval.xlsx", mode_index=7, mode_name="RAG")
    print("Evaluation completed and saved to results/eval.xlsx")
def no_ragas_eval():
    gen_check_answer(input_dir="data",input_file="results/eval.xlsx",output_file="results/data",start=0,end=18)
    gen_check_answer(input_dir="data1",input_file="results/eval.xlsx",output_file="results/data1",start=18,end=28)
    gen_check_answer(input_dir="data2",input_file="results/eval.xlsx",output_file="results/data2",start=28,end=50)

if __name__ == "__main__":
    regas_eval()
    no_ragas_eval()
    print("All evaluations completed successfully.")