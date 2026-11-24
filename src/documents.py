from dataclasses import dataclass
from pathlib import Path
from io import BytesIO

@dataclass(frozen=True)
class Passage:
    text: str
    source: str
    location: str

def load_document(name: str, data: bytes) -> list[Passage]:
    name = Path(name).name
    ext = Path(name).suffix.lower()
    if ext == '.pdf':
        import pymupdf
        with pymupdf.open(stream=data, filetype='pdf') as doc:
            if doc.needs_pass:
                raise ValueError('Encrypted PDF is not supported.')
            rows = [Passage(p.get_text(), name, f'Page {i+1}') for i,p in enumerate(doc)]
    elif ext == '.docx':
        from docx import Document
        doc = Document(BytesIO(data))
        rows = [Passage(p.text, name, f'Paragraph {i+1}') for i,p in enumerate(doc.paragraphs)]
        for i, table in enumerate(doc.tables):
            rows.append(Passage('\n'.join(' | '.join(c.text for c in r.cells) for r in table.rows),name,f'Table {i+1}'))
    elif ext in {'.txt','.md'}:
        rows = [Passage(data.decode('utf-8-sig'), name, 'Text')]
    else:
        raise ValueError(f'Unsupported file type: {ext}')
    rows = [r for r in rows if r.text.strip()]
    if not rows:
        raise ValueError('No extractable text. Scanned PDFs require OCR (not included).')
    return rows

def chunk_documents(rows, size=500, overlap=100):
    if not 0 <= overlap < size:
        raise ValueError('Require 0 <= overlap < size')
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    result=[]
    for row in rows:
        for i, part in enumerate(splitter.split_text(row.text)):
            result.append(Passage(part,row.source,f'{row.location}, chunk {i+1}'))
    return result
