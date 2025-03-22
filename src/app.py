import streamlit as st
from backend.query.query import Query
st.set_page_config(page_title="QA Medical Bot")
query=Query()
@st.dialog("Citations")
def citation_function(cite):
    
    for item in cite:
        st.markdown(item)
with st.sidebar:
    st.title('QA Medical Bot')
    st.write("Choose chat mode to use!")
    chat_mode = st.radio("Chat mode", ["RAG","Local GraphRag", "Global GraphRag"])

    
def get_answer(prompt):
    mode=0
    if chat_mode=="Local GraphRag":
        mode=1
    elif chat_mode=="Global GraphRag":
        mode=2  
    
    answer, cites= query.query(prompt,mode)
    return answer,cites

if "messages" not in st.session_state:
    st.session_state.messages = []
if "cites" not in st.session_state:
    st.session_state.cites=[]
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Nhập nội dung câu hỏi?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        answer,cite=get_answer(prompt)
        st.markdown(answer)
        
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.cites=cite
   
if st.session_state.cites!=[]:

    if st.button("Citations"):
        print(st.session_state.cites)
        citation_function(st.session_state.cites)
