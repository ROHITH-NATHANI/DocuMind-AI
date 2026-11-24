import numpy as np

class Retriever:
    def __init__(self, chunks, model=None):
        import faiss
        if not chunks:
            raise ValueError('No chunks to index.')
        if model is None:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.model, self.chunks = model, list(chunks)
        vectors = self.embed([c.text for c in self.chunks])
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)

    def embed(self, texts):
        vectors = np.ascontiguousarray(self.model.encode(texts, normalize_embeddings=True), dtype=np.float32)
        return vectors

    def search(self, question, k=5, min_score=0.15):
        if not question.strip() or k < 1:
            return []
        scores, ids = self.index.search(self.embed([question]), min(k,len(self.chunks)))
        return [(self.chunks[int(i)],float(s)) for i,s in zip(ids[0],scores[0]) if i >= 0 and s >= min_score]
