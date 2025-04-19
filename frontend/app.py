import streamlit as st
import asyncio
st.set_page_config(page_title="QA Medical Bot")
@st.dialog("Citations")
def citation_function(cite):
    
    for item in cite:
        st.markdown(item)
@st.dialog("Suggested Questions")
def suggested_questions(questions):
    print(questions)
    for item in questions:
        st.markdown(item)
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = [
        "- Chào bạn!",
        "- Bạn có thể giúp gì cho mình không?",
    ]
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
    
async def get_answer(prompt):
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
    
    answer, cites, suggested_question=await query.query(prompt,mode)
    return answer,cites,suggested_question

if "messages" not in st.session_state:
    st.session_state.messages = []
    for item in reversed(chat_history.get_history_chat(limit=20).history):
        st.session_state.messages.append({"role": "user", "content": item.question})
        st.session_state.messages.append({"role": "assistant", "content": item.answer})
if "cites" not in st.session_state:
    st.session_state.cites=[]
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập nội dung câu hỏi?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        answer, cite, suggested_question = run_async(get_answer(prompt))
        if suggested_question is not None and suggested_question != []:
            st.session_state.suggested_questions = suggested_question

        st.markdown(answer)
        
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.cites=cite
   
if st.session_state.cites!=[]:

    if st.button("Citations"):
        citation_function(st.session_state.cites)
