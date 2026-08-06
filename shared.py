from datetime import datetime, timezone
import json
import re
from queue import Queue
import token
from urllib.parse import urlparse, urlunparse

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

META_RAW = "./Data/meta_raw.jsonl"
CHUNKS = "./Data/chunked.jsonl"
QUERIES = "./Data/queries.jsonl"
QUERY_RESULTS = "./Data/queries/"

document_queue = Queue()

# Format: {docno: {"url": url, "ext": ext, "time": timestamp, "title": title}}
meta_raw = {}
chunks = []
corpus = []

def import_meta_raw():
    global meta_raw
    meta_raw = {}
    try:
        with open(META_RAW, "r", encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                try:
                    temp = json.loads(line)
                    docno = temp["docno"]
                    meta_raw[docno] = {
                        "url": temp["url"],
                        "ext": temp["ext"],
                        "time": temp["time"],
                        "title": temp["title"]
                    }
                except Exception as e:
                    print(f"Error parsing line: {line}. Error: {e}")
                    continue
    except FileNotFoundError:
        print(f"{META_RAW} file not found. Starting with an empty meta_raw.")
    return meta_raw

def add_meta(docno, title, url, ext):
    meta_raw[docno] = {
        "url": url,
        "ext": ext,
        "time": datetime.now(timezone.utc).isoformat(),
        "title": title
    }
    if (len(meta_raw) % 100) == 0:  # Save every 100 entries
        save_meta_raw()  # Save the metadata after adding a new entry

def save_meta_raw():
    with open(META_RAW, "w", encoding="utf-8") as file:
        file.write("")  # Clear the file before writing new data
    for docno, meta in meta_raw.items():
        temp = {
            "docno": docno,
            "url": meta["url"],
            "ext": meta["ext"],
            "time": meta["time"],
            "title": meta["title"]
        }
        with open(META_RAW, "a", encoding="utf-8") as file:
            file.write(json.dumps(temp) + "\n")

def normalize_url(url):
    parsed_url = urlparse(url)
    normalized_path = parsed_url.path.rstrip("/")
    normalized_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, normalized_path, "", "", "")
    )
    return normalized_url

def import_chunks():
    global chunks
    if not chunks:
        try:
            with open(CHUNKS, "r", encoding="utf-8") as f:
                chunks = [json.loads(line) for line in f]
        except FileNotFoundError:
            print(f"{CHUNKS} file not found. Starting with an empty chunks list.")
            chunks = []
    return chunks

def load_corpus():
    global corpus

    import_chunks()

    if not corpus:
        corpus = [
            normalize_text_tokens(
                chunk.get("chunk_text", "") + " " + chunk.get("chunk_title", "")
            )
            for chunk in chunks
        ]
    return corpus

def filter_url(normalized_url):
    parsed = urlparse(normalized_url)

    # Only HTTP/HTTPS
    if parsed.scheme not in ["http", "https"]:
        return False

        # Remove authentication/user pages
    forbidden_keywords = {
        "login",
        "signin",
        "signup",
        "register",
        "logout",
        "account",
        "profile",
        "dashboard",
        "settings",
        "subscribe",
    }

    # Parse URL path into individual segments
    path_segments = {
        segment.lower()
        for segment in parsed.path.split("/")
        if segment
    }

    # Reject URLs containing an exact forbidden path segment
    if path_segments & forbidden_keywords:
        return False


    # Remove shopping/non-document pages
    forbidden_paths = {
        "cart",
        "checkout",
        "payment",
        "pricing",
        "store",
        "shop",
    }

    # Check exact path segments instead of arbitrary substrings
    if path_segments & forbidden_paths:
        return False

    # Remove files that are not documents
    forbidden_extensions = [
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".webp",
        ".css",
        ".js",
        ".json",
        ".xml",
        ".zip",
        ".tar",
        ".gz",
        ".exe",
        ".dmg",
        ".pdf",
        ".tar.gz",
    ]
    path_lower = parsed.path.lower()

    for ext in forbidden_extensions:
        if path_lower.endswith(ext):
            return False


    # Remove social media links
    forbidden_domains = [
        "facebook.com",
        "twitter.com",
        "x.com",
        "linkedin.com",
        "youtube.com",
        "github.com"
    ]

    for domain in forbidden_domains:
        if domain in parsed.netloc:
            return False

    return True

def _light_stem(word):
    suffixes = [
        "ingly",
        "edly",
        "ing",
        "ed",
        "ly",
        "ies",
        "es",
        "s"
    ]

    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]

    # Only remove plural s in safer cases
    if word.endswith("s") and not word.endswith(("ss", "us", "is")):
        if len(word) > 3:
            return word[:-1]

    return word

def normalize_text_tokens(text):
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    return [_light_stem(token) for token in tokens]