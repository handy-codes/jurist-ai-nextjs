import os
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import json
from utils.chunker import chunk_text
from utils.vector_db import add_chunk, create_tables

INGESTED_LOG = "data/ingested_files.json"


def load_ingested_log():
    if os.path.exists(INGESTED_LOG):
        with open(INGESTED_LOG, "r") as f:
            return set(json.load(f))
    return set()


def save_ingested_log(log_set):
    with open(INGESTED_LOG, "w") as f:
        json.dump(list(log_set), f, indent=2)


def extract_text_with_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()

        if text.strip():
            full_text += text + "\n"
        else:
            # OCR fallback for scanned pages
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(img)
            full_text += ocr_text + "\n"

    return full_text


def ingest_file(file_path, source=None):
    print(f"📄 Processing: {file_path}")
    text = extract_text_with_pymupdf(file_path)

    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        # Ensure chunk is a string, not numpy array or other type
        if hasattr(chunk, "tolist"):
            chunk = chunk.tolist()
        add_chunk(chunk, source or file_path)
        print(f"🧩 Chunk {i+1}/{len(chunks)} added.")
    print(f"✅ {len(chunks)} chunks added from: {file_path}")


def ingest_folder(folder_path):
    print(f"📂 Scanning folder: {folder_path}")
    create_tables()

    already_ingested = load_ingested_log()
    new_ingested = set(already_ingested)
    processed_files = 0

    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)
        if fname.lower().endswith(".pdf") and fpath not in already_ingested:
            ingest_file(fpath)
            new_ingested.add(fpath)
            processed_files += 1
        elif fpath in already_ingested:
            print(f"⏩ Skipping (already ingested): {fname}")

    save_ingested_log(new_ingested)
    print(f"🎉 Ingestion complete! {processed_files} new files processed.")


if __name__ == "__main__":
    folder = "data/legal_pdfs"
    ingest_folder(folder)


# import fitz  # PyMuPDF
# import pytesseract
# from PIL import Image
# import io
# import os
# import re
# from utils.chunker import chunk_text
# from utils.vector_db import add_chunk, create_tables

# def extract_text_with_fallback(pdf_path):
#     doc = fitz.open(pdf_path)
#     full_text = ""
#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         text = page.get_text()

#         if len(text.strip()) < 50:  # likely image-based page
#             pix = page.get_pixmap(dpi=300)
#             img = Image.open(io.BytesIO(pix.tobytes("png")))
#             ocr_text = pytesseract.image_to_string(img)
#             full_text += f"\n\n[OCR Page {page_num + 1}]\n{ocr_text}"
#         else:
#             full_text += f"\n\n[Page {page_num + 1}]\n{text}"
#     return full_text

# def clean_text(text):
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()

# def ingest_file(filepath, source="manual_upload"):
#     filename = os.path.basename(filepath)
#     print(f"Ingesting: {filename}")
#     text = extract_text_with_fallback(filepath)
#     cleaned_text = clean_text(text)
#     chunks = chunk_text(cleaned_text)
#     for chunk in chunks:
#         add_chunk(chunk=chunk, source_doc=filename, metadata={"source": source})

# def ingest_folder(folder_path):
#     create_tables()
#     for fname in os.listdir(folder_path):
#         if fname.lower().endswith((".pdf",)):
#             fpath = os.path.join(folder_path, fname)
#             ingest_file(fpath)

# if __name__ == "__main__":
#     ingest_folder("data/legal_pdfs")
#     print("Ingestion complete!")


# import os
# from utils.vector_db import add_chunk, create_tables
# from PyPDF2 import PdfReader
# import docx2txt

# def extract_text_from_pdf(pdf_path):
#     reader = PdfReader(pdf_path)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() + "\n"
#     return text

# def extract_text_from_docx(docx_path):
#     return docx2txt.process(docx_path)

# def chunk_text(text, chunk_size=500, overlap=50):
#     words = text.split()
#     chunks = []
#     for i in range(0, len(words), chunk_size - overlap):
#         chunk = " ".join(words[i:i+chunk_size])
#         chunks.append(chunk)
#     return chunks

# def ingest_file(file_path, source=None):
#     if file_path.lower().endswith(".pdf"):
#         text = extract_text_from_pdf(file_path)
#     elif file_path.lower().endswith(".docx"):
#         text = extract_text_from_docx(file_path)
#     else:
#         print(f"Skipping unsupported file: {file_path}")
#         return
#     chunks = chunk_text(text)
#     for chunk in chunks:
#         add_chunk(chunk, source=source or file_path)

# if __name__ == "__main__":
#     create_tables()
#     folder = "data/legal_pdfs"
#     for fname in os.listdir(folder):
#         if fname.lower().endswith((".pdf", ".docx")):
#             print(f"Ingesting: {fname}")
#             ingest_file(os.path.join(folder, fname))
#     print("Ingestion complete!")
