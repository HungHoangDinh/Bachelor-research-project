
from utils.get_chat_answer import save_csv_to_exel,append_mode_answers_xlsx
from utils.gen_test import gen_testset
from utils.gen_QA import gen_qa
if __name__ == "__main__":
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
    