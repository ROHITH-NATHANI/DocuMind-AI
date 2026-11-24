import os
import streamlit as st
from dotenv import load_dotenv
from src.documents import load_document, chunk_documents
from src.retrieval import Retriever
from src.rag import ask
load_dotenv()
st.set_page_config(page_title='DocuMind AI',page_icon='📚',layout='wide')
st.title('DocuMind AI')
st.caption('Ask questions about your documents • semantic search • source citations')
@st.cache_resource
def embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
for key,default in [('retriever',None),('messages',[]),('names',[])]:
    if key not in st.session_state: st.session_state[key]=default
with st.sidebar:
    st.header('Documents')
    files=st.file_uploader('Upload documents',type=['pdf','docx','txt','md'],accept_multiple_files=True)
    size=st.slider('Chunk size',200,1500,500,100)
    overlap=st.slider('Chunk overlap',0,min(150,size-1),100,25)
    k=st.slider('Retrieved passages',1,10,5)
    threshold=st.slider('Minimum similarity',0.0,1.0,0.25,0.05)
    api_key=st.text_input('Gemini API key (optional)',type='password',value=os.getenv('GEMINI_API_KEY',''))
    model=st.text_input('Gemini model',os.getenv('GEMINI_MODEL','gemini-2.5-flash'))
    st.caption('Without a key, the app returns retrieved passages. With a key, relevant passages and questions are sent to Google.')
    if st.button('Process documents',type='primary',disabled=not files):
        try:
            with st.spinner('Extracting and indexing documents…'):
                rows=[]
                for f in files:
                    rows.extend(load_document(f.name,f.getvalue()))
                chunks=chunk_documents(rows,size,overlap)
                index=Retriever(chunks,embedding_model())
                st.session_state.update(retriever=index,messages=[],names=[f.name for f in files])
            st.success(f'Indexed {len(chunks)} passages')
        except Exception as e:
            st.error(f'Indexing failed: {e}. Previous index (if any) is unchanged.')
    if st.session_state.retriever:
        st.write('Indexed files:',', '.join(st.session_state.names))
    if st.button('Clear session'):
        st.session_state.update(retriever=None,messages=[],names=[])
        st.rerun()
    if st.session_state.messages:
        st.download_button('Export chat','\n\n'.join(f'{m["role"]}: {m["text"]}' for m in st.session_state.messages),'chat.txt')

def display(m):
    with st.chat_message(m['role']):
        st.markdown(m['text'])
        if m.get('mode'): st.caption(m['mode'])
        for i,(p,s) in enumerate(m.get('sources',[]),1):
            with st.expander(f'[{i}] {p.source} — {p.location} (similarity {s:.2f})'):
                st.write(p.text)
for m in st.session_state.messages: display(m)
if not st.session_state.retriever:
    st.info('Upload and process documents to begin.')
summary=st.button('Summarize key topics',disabled=not st.session_state.retriever)
question=st.chat_input('Ask a question about your documents',disabled=not st.session_state.retriever)
if summary: question='Summarize the key topics in the retrieved document excerpts.'
if question:
    user=dict(role='user',text=question)
    st.session_state.messages.append(user); display(user)
    try:
        with st.spinner('Retrieving evidence…'):
            answer=ask(st.session_state.retriever,question,api_key,model,k,threshold)
        msg=dict(role='assistant',text=answer.text,sources=answer.sources,mode=answer.mode)
    except Exception as e:
        msg=dict(role='assistant',text=f'Answer generation failed ({type(e).__name__}: {e}). Check API key, model access, network or quota. You can remove the key to use retrieval-only mode.')
    st.session_state.messages.append(msg); display(msg)
