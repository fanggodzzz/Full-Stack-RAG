import os

os.environ.setdefault("NLTK_DISABLE_IMPORT_SECURITY", "1")

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import hashlib
from shared import document_queue, import_meta_raw, meta_raw
from Document_processor import html, md, txt
import json
import os
import dotenv

dotenv.load_dotenv()

DATA = "./Data/processed.jsonl"
RAW = "./Data/raw/"
CHUNK = "./Data/chunked.jsonl"
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 256))  # Default chunk size to 100 if not set in .env
OVERLAP = int(os.getenv("OVERLAP", 50))  # Default overlap to 20 if not set in .env
MAX_DOCS = int(os.getenv("MAX_DOCS", 5000))  # Limit the number of documents to process for testing purposes

# Stop words from NLTK
stopWords = set(nltk.corpus.stopwords.words("english"))

# Stemming function
stem = PorterStemmer().stem

text_hashes = set()  # Set to store hashes of processed texts
# meta_raw = {}  # Dictionary to store metadata for each document

def preprocessing_text(text):
    # Tokenization
    tokens = word_tokenize(text)

    # Stemming
    tokens = [stem(token.lower()) for token in tokens]

    # Remove stop words, punctuation and non-alphabetic tokens (numbers, etc.)
    tokens = [token for token in tokens if token.isalpha() and token not in stopWords]

    return tokens

def chunk_text(document):
    text = document["content"]
    tokens = text.split()
    start = 0
    id = 0

    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = " ".join(chunk_tokens)
        chunk = {
            "chunk_id": id,
            "docno": document["docno"],
            "title": document["title"],
            "chunk_text": chunk_text,
        }

        # Move the start index for the next chunk
        start += CHUNK_SIZE - OVERLAP
        id += 1
        save_chunked_data(chunk)

def process_raw_data(doc_num):
    meta = meta_raw[doc_num]
    try:
        with open(f"{RAW}doc_{doc_num:07d}{meta['ext']}", "r", encoding="utf-8") as f:
            content = f.read()

        if (meta["ext"] == ".html"):
            text = html.extract_text_from_html(content)
        elif (meta["ext"] == ".md"):
            text = md.extract_text_from_md(content)
        else:
            text = txt.extract_text_from_txt(content)

        document = {
            "docno": doc_num,
            "title": meta["title"],
            "content": text
        }

        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if text_hash in text_hashes:
            # print(f"Skipping duplicate text for doc_num {doc_num}")
            return
        text_hashes.add(text_hash)

        save_processed_data(document)
        chunk_text(document)
    except Exception as e:
        print(f"Error reading file for doc_num {doc_num}: {e}")
        return

def save_processed_data(document):
    with open(DATA, "at", encoding="utf-8") as f:
        f.write(json.dumps(
            document,
            ensure_ascii=False
        ) + "\n")

def save_chunked_data(document):
    with open(CHUNK, "at", encoding="utf-8") as f:
        f.write(json.dumps(
            document,
            ensure_ascii=False
        ) + "\n")

def main():
    # Clear output files before starting
    with open(DATA, "w", encoding="utf-8") as f:
        f.write("")  # Clear the file before writing new data

    with open(CHUNK, "w", encoding="utf-8") as f:
        f.write("")  # Clear the directory before writing new data

    # Concurrently with crawling
    while True:
        doc_num = document_queue.get()  # Wait for a document number from the queue
        if doc_num is None:  # Check for the sentinel value to exit
            break
        process_raw_data(doc_num)
        document_queue.task_done()  # Mark the task as done

    # global meta_raw
    # meta_raw = import_meta_raw()  # Load metadata from the raw data
    # for doc_num in range(0, MAX_DOCS):
    #     print(f"Processing document {doc_num}...", end="\r")
    #     process_raw_data(doc_num)

    print("Data processing completed. Processed documents are saved in the processed.jsonl and chunked.jsonl files.")

if __name__ == "__main__":
    main()