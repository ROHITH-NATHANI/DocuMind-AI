from src.documents import Passage,load_document
from src.rag import ask,NO_ANSWER
class FakeRetriever:
    def __init__(self,hits): self.hits=hits
    def search(self,*args): return self.hits
hits=[(Passage('TCP is reliable.','notes.txt','Text'),0.9)]
def test_text_loader():
    assert load_document('a.txt',b'hello')[0].text=='hello'
def test_empty():
    assert ask(FakeRetriever([]),'question').text==NO_ANSWER
def test_offline():
    assert ask(FakeRetriever(hits),'TCP').mode=='retrieval only'
def test_generated():
    assert ask(FakeRetriever(hits),'TCP',generator=lambda p:'TCP is reliable [1].').mode=='generated'
def test_bad_citation():
    assert ask(FakeRetriever(hits),'TCP',generator=lambda p:'TCP [9]').mode=='citation check failed'
def test_missing_citation():
    assert ask(FakeRetriever(hits),'TCP',generator=lambda p:'TCP').mode=='citation check failed'
