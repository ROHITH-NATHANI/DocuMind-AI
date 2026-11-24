# DocuMind AI
A compact document RAG application. Python 3.11 recommended. No training or GPU required. First run downloads the embedding model (internet required). Gemini is optional and requires a supported model and API access.

## Setup in Antigravity (or any IDE)
1. Extract the ZIP. Open the `DocuMind-AI` folder as your workspace.
2. Open a terminal in that folder.
3. Windows PowerShell:
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   Copy-Item .env.example .env
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```
   macOS/Linux:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   cp .env.example .env
   python -m streamlit run app.py
   ```
4. Open http://localhost:8501. Upload `data/documents/cs_notes.txt`, click Process documents and ask “What does ACID stand for?”
5. For generated answers, enter a Gemini key in the sidebar or `.env` and restart. Get a key from https://aistudio.google.com/apikey. Change GEMINI_MODEL if the default is unavailable. Never commit your key.

## Six phases (already integrated)
1. Foundation: `src/documents.py` extracts PDF, DOCX, TXT and MD. PDF page numbers and DOCX paragraph/table locations are retained. Scanned PDFs require OCR, not included.
2. Retrieval: LangChain recursive splitting, MiniLM 384-dimensional embeddings, FAISS exact inner product on normalized vectors (cosine similarity). Index lives in session memory.
3. Generation: `src/rag.py` uses Gemini with retrieved context and numbered citations. A similarity cutoff rejects weak matches; citation validation checks IDs, not factual entailment. No API key means retrieved excerpts only.
4. UI: `app.py` handles multiple uploads, settings, chat, evidence expanders, export and excerpt summarization. Chat history is displayed but not passed to the model; questions should be standalone. Summarization covers retrieved excerpts, not necessarily all pages.
5. Evaluation: `evaluation/evaluate.py` measures hit rate, MRR, passage precision and latency on a small original demo dataset. Extend the dataset before making performance claims. Tests use a fake model/generator to avoid API calls.
6. Deployment: push the extracted folder contents to GitHub, then create an app at https://share.streamlit.io/ using `app.py` and Python 3.11. The key can be entered per session. The GitHub Actions workflow runs tests. Cloud memory limits may affect embedding model loading.

## Tests and evaluation
Activate the virtual environment or use its Python executable directly:
```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m evaluation.evaluate --k 3
```
Evaluation writes `evaluation/results.json`. No precomputed accuracy is claimed. The evidence marker is a lightweight relevance label; the small demo set is not a benchmark. To evaluate generated answers, compare responses with reference answers and retrieved text for correctness, faithfulness, citation accuracy and abstention. Optional RAGAS integration is described in `evaluation/README.md`.

## Privacy and limitations
Documents are held in memory rather than persisted to disk. With Gemini enabled, retrieved excerpts and the question are transmitted to Google. Do not upload confidential files without permission. The app is a local/demo system, not production authentication or security infrastructure. Prompt instructions and citation checks do not guarantee protection from prompt injection or hallucination. Thresholds need validation. Duplicate filenames can make references ambiguous; use distinct filenames.
