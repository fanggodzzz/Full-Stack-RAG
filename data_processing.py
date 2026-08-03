from compression import gzip

from bs4 import BeautifulSoup
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from shared import document_queue

DATA = "./Data/processed.jsonl"
RAW = "./Data/raw/"
CHUNK = "./Data/chunked.jsonl"
MAX_DOCS = 10
CHUNK_SIZE = 256
OVERLAP = 50


# Stop words from NLTK
stopWords = set(nltk.corpus.stopwords.words("english"))

# Stemming function
stem = PorterStemmer().stem

def preprocessing_text(text):
    # Tokenization
    tokens = word_tokenize(text)

    # Stemming
    tokens = [stem(token.lower()) for token in tokens]

    # Remove stop words, punctuation and non-alphabetic tokens (numbers, etc.)
    tokens = [token for token in tokens if token.isalpha() and token not in stopWords]

    text = " ".join(tokens)

    return text

def extract_title_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title = soup.title.string if soup.title else ""
    return preprocessing_text(title)

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Get the text
    text = soup.get_text(separator=" ", strip=True)

    return text

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
    try:
        with open(RAW + f"doc_{doc_num:07d}.html", "r", encoding="utf-8") as f:
            content = f.read()
            text = preprocessing_text(extract_text_from_html(content))
            document = {
                "docno": doc_num,
                "token_num": len(text.split()),
                "title": extract_title_from_html(content),
                "content": text
            }
            save_processed_data(document)
            chunk_text(document)
    except Exception as e:
        print(f"Error processing document {doc_num}: {e}")

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
    with open("./DATA/processed.jsonl", "w", encoding="utf-8") as f:
        f.write("")  # Clear the directory before writing new data

    with open(CHUNK, "w", encoding="utf-8") as f:
        f.write("")  # Clear the directory before writing new data

    while True:
        doc_num = document_queue.get()  # Wait for a document number from the queue
        if doc_num is None:  # Check for the sentinel value to exit
            break
        process_raw_data(doc_num)
        document_queue.task_done()  # Mark the task as done

    print("Data processing completed. Processed documents are saved in the processed.jsonl and chunked.jsonl files.")

if __name__ == "__main__":
    main()