import streamlit as st
import time
import uuid
from src.chat_process import get_chat_history_request, send_chat_request
from src.file_process import list_pdfs_request, upload_file_request,download_file_request, delete_file_request,check_task_status_request
st.set_page_config(page_title="QA Medical Bot")
def delete_file(filename,file_status_placeholder):
    message=delete_file_request(filename=filename)
    if "thành công" in message:
        st.session_state["files"].remove(filename)
        file_status_placeholder.success(f"File {filename} đã được xóa thành công.")
        st.session_state["files_content"].pop(filename, None)
    else:
        file_status_placeholder.error(f"File {filename} không thể xóa!")
def upload_file(uploaded_file,status_placeholder):
    status_id=upload_file_request(uploaded_file)
    while True:
        status,message=check_task_status_request(status_id)
        if status == "SUCCESS":
            st.session_state["files"].append(uploaded_file.name)
            status_placeholder.success(message)
            st.session_state["files_content"][uploaded_file.name] = download_file_request(uploaded_file.name)
            break
        elif status == "FAILURE":
            status_placeholder.error(message)
            break
        else:
            status_placeholder.info("File is being processed...")
            time.sleep(10)
@st.dialog("Citations")
def citation_function(cite):
    
    for item in cite:
        st.markdown(item)
@st.dialog("Suggested Questions")
def suggested_questions(questions):
    for item in questions:
        st.markdown(item)
def update_key():
    st.session_state.uploader_key += 1
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = [
        "- Chào bạn!",
        "- Bạn có thể giúp gì cho mình không?",
    ]
if "files" not in st.session_state:
        st.session_state["files"] = list_pdfs_request()
if "files_content" not in st.session_state:
    st.session_state["files_content"] = {}
    for file_name in st.session_state["files"]:
        data_stream= download_file_request(file_name)
        st.session_state["files_content"][file_name] = data_stream
with st.sidebar:
    st.title('QA Medical Bot')
    chat_mode = st.selectbox(
        "Choose chat mode to use!",
        ("RAG","RAG(Custom)", "Local Graphrag", "Local Graphrag(Custom)", "Global Graphrag", "Global Graphrag(Custom)", "Drift Graphrag", "Drift Graphrag(Custom)"),
        index=0,
        placeholder="Select chat mode...",
    )
    if st.session_state.suggested_questions:
        if st.button("Suggested Questions"):
           suggested_questions(st.session_state.suggested_questions)
    st.header("📂 File Manager")
    status_placeholder = st.empty()
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"],key=f"uploader_{st.session_state.uploader_key}")
    if uploaded_file is not None:
        if uploaded_file.name not in st.session_state["files"]:
            upload_file(uploaded_file,status_placeholder)
            update_key()
        else:
            status_placeholder.warning("File already exists!")
            update_key()
        
    #Todo: add file manager to upload files
    st.title("Available files")
    file_status_placeholder = st.empty()
    if st.session_state["files"]:
        for file_name in st.session_state["files"]:
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
            col1.write(file_name)
            
            col2.download_button(label="⬇️", data=st.session_state["files_content"][file_name], file_name=file_name, mime="application/pdf")
            col3.button("🗑️",key=f"delete_{file_name}", on_click=delete_file,args=[file_name,file_status_placeholder])
    
def get_answer(prompt):
    mode=0
    if chat_mode=="RAG":
        mode=7
    elif chat_mode=="RAG(Custom)":
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
