import pytest
from src.documents import Passage,chunk_documents

def test_chunking():
    pytest.importorskip('langchain_text_splitters')
    chunks=chunk_documents([Passage('word '*300,'a.txt','Text')],100,20)
    assert len(chunks)>1 and all(len(c.text)<=100 for c in chunks)

def test_search():
    pytest.importorskip('faiss')
    import numpy as np
    from src.retrieval import Retriever
    class Model:
        def encode(self,texts,**kwargs):
            return np.array([[1,0] if 'tcp' in t.lower() else [0,1] for t in texts])
    r=Retriever([Passage('TCP reliable','a','1'),Passage('UDP datagrams','a','2')],Model())
    assert r.search('TCP',1)[0][0].text=='TCP reliable'
