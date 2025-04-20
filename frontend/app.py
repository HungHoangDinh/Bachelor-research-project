import streamlit as st
import time
from src.chat_process import get_chat_history_request, send_chat_request
from src.file_process import list_pdfs_request, upload_file_request,download_file_request, delete_file_request,check_task_status_request
st.set_page_config(page_title="QA Medical Bot")
@st.dialog("Citations")
def citation_function(cite):
    
    for item in cite:
        st.markdown(item)
@st.dialog("Suggested Questions")
def suggested_questions(questions):
    for item in questions:
        st.markdown(item)

if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = [
        "- Chào bạn!",
        "- Bạn có thể giúp gì cho mình không?",
    ]
if "files" not in st.session_state:
        st.session_state["files"] = list_pdfs_request()
with st.sidebar:
    st.title('QA Medical Bot')
    chat_mode = st.selectbox(
        "Choose chat mode to use!",
        ("RAG", "Local Graphrag", "Local Graphrag(Custom)", "Global Graphrag", "Global Graphrag(Custom)", "Drift Graphrag", "Drift Graphrag(Custom)"),
        index=0,
        placeholder="Select chat mode...",
    )
    if st.session_state.suggested_questions:
        if st.button("Suggested Questions"):
           suggested_questions(st.session_state.suggested_questions)
    st.header("📂 File Manager")
    status_placeholder = st.empty()
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])
    if uploaded_file is not None:
        status_placeholder.text("Uploading...")
        time.sleep(10) 
        uploaded_file=None
    #Todo: add file manager to upload files
    st.title("Available files")
    if st.session_state["files"]:
        for file_name in st.session_state["files"]:
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
            col1.write(file_name)
        #todo: add file manager to delete files
    
def get_answer(prompt):
    mode=0
    if chat_mode=="RAG":
        mode=0
    elif chat_mode=="Local Graphrag":
        mode=1
    elif chat_mode=="Local Graphrag(Custom)":
        mode=2
    elif chat_mode=="Global Graphrag":
        mode=3
    elif chat_mode=="Global Graphrag(Custom)":
        mode=4
    elif chat_mode=="Drift Graphrag":
        mode=5
    elif chat_mode=="Drift Graphrag(Custom)":
        mode=6
    
    answer, cites, suggested_question= send_chat_request(prompt, mode=mode)
    return answer,cites,suggested_question

if "messages" not in st.session_state:
    st.session_state.messages = []
    for item in reversed(get_chat_history_request(limit=20)):
        st.session_state.messages.append({"role": "user", "content": item["question"]})
        st.session_state.messages.append({"role": "assistant", "content": item["answer"]})
if "cites" not in st.session_state:
    st.session_state.cites=[]
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập nội dung câu hỏi?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        answer, cite, suggested_question = get_answer(prompt)
        if suggested_question is not None and suggested_question != []:
            st.session_state.suggested_questions = suggested_question

        st.markdown(answer)
        
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.cites=cite
   
if st.session_state.cites!=[]:

    if st.button("Citations"):
        citation_function(st.session_state.cites)
