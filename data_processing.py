from compression import gzip

from bs4 import BeautifulSoup
import json
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

DATA = "./Data/processed.jsonl"
RAW = "./Data/raw/"
MAX_DOCS = 10
CHUNK_SIZE = 500
OVERLAP = 75

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
    return title

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Get the text
    text = soup.get_text(separator=" ", strip=True)

    return text

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
    except Exception as e:
        print(f"Error processing document {doc_num}: {e}")

def save_processed_data(document):
    with open(DATA, "at", encoding="utf-8") as f:
        f.write(json.dumps(
            document,
            ensure_ascii=False
        ) + "\n")

def chunk_text():
    pass

def main():
    chunk_text()

if __name__ == "__main__":
    main()