"""Run from repository root: python -m evaluation.evaluate"""
import json,time,argparse
from pathlib import Path
from src.documents import load_document,chunk_documents
from src.retrieval import Retriever

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--k',type=int,default=3); args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    p=root/'data/documents/cs_notes.txt'
    index=Retriever(chunk_documents(load_document(p.name,p.read_bytes())))
    cases=json.loads((root/'data/evaluation.json').read_text())
    ranks=[]; times=[]; precisions=[]
    for case in cases:
        start=time.perf_counter(); hits=index.search(case['question'],args.k,min_score=-1); times.append(time.perf_counter()-start)
        relevant=[case['evidence'].lower() in p.text.lower() for p,s in hits]
        rank=next((i for i,v in enumerate(relevant,1) if v),0); ranks.append(rank)
        precisions.append(sum(relevant)/len(hits) if hits else 0)
        print(f'Rank {rank or "miss"}: {case["question"]}')
    result={'questions':len(cases),'k':args.k,'hit_rate_at_k':sum(r>0 for r in ranks)/len(ranks),'mrr_at_k':sum(1/r if r else 0 for r in ranks)/len(ranks),'mean_passage_precision_at_k':sum(precisions)/len(precisions),'mean_retrieval_latency_ms':1000*sum(times)/len(times)}
    print(json.dumps(result,indent=2)); (root/'evaluation/results.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__': main()
