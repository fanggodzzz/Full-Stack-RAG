from datetime import datetime, timezone
import json
from queue import Queue
from urllib.parse import urlparse, urlunparse

META_RAW = "meta_raw.jsonl"

document_queue = Queue()

# Format: {docno: {"url": url, "ext": ext, "time": timestamp, "title": title}}
meta_raw = {}

def add_meta(docno, title, url, ext):
    meta_raw[docno] = {
        "url": url,
        "ext": ext,
        "time": datetime.now(timezone.utc).isoformat(),
        "title": title
    }

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