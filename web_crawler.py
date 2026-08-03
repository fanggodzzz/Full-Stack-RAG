from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse, urlsplit, urlunsplit
import requests
import threading
import os
from shared import document_queue, meta_raw, save_meta_raw, add_meta, META_RAW, normalize_url
import hashlib
from Document_processor import html, md, txt

SEED_URLS = []
SOURCES_FILE = "sources.txt"
USER_AGENT = "MyCRAWLER"
ROBOT_FILE = "robots.txt"
DOCNUM = 0
RAW = "./Data/raw"
META_RAW = "./Data/meta_raw.jsonl"
MAX_DOCS = 20000
# MAX_DOCS = 200  # Limit the number of documents to crawl for testing purposes


robots = {}
lock = threading.Lock()
visited = set()
content_hashes = set()  # To store hashes of the content to avoid duplicates

def import_sources():
    global SEED_URLS

    try:
        with open(SOURCES_FILE, "r") as file:
            SEED_URLS = [line.strip() for line in file if line.strip()]

    except FileNotFoundError:
        print(f"{SOURCES_FILE} file not found. Please create the file and add URLs to crawl.")
        exit(1)

def parse_robots_txt():
    global robots

    for url in SEED_URLS:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        robots_url = urljoin(
            f"{parsed_url.scheme}://{parsed_url.netloc}/",
            ROBOT_FILE
        )

        try:
            response = requests.get(
                robots_url,
                headers={"User-Agent": USER_AGENT},
                timeout=5
            )
            response.raise_for_status()
            rp = RobotFileParser()
            rp.parse(response.text.splitlines())
            robots[domain] = rp
        except requests.RequestException as e:
            robots[domain] = None

def save_raw_data(docno, title, normalized_url, content, ext):
    # Save content
    file_path = os.path.join(RAW, f"doc_{docno:07d}{ext}")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

    # Save metadata
    add_meta(docno, title, normalized_url, ext)

def process_and_save(response, normalized_url):
    global DOCNUM
    content_type = response.headers.get("Content-Type", "").lower()
    content = links = title = ext = None
    
    # Choose how to decode and what extension to save based on content type
    if content_type.startswith("text/markdown") or normalized_url.endswith(".md"):
        raw_content = response.content.decode("utf-8", errors="ignore")
        content, links, title = md.process_markdown(raw_content, normalized_url)
        ext = ".md"
    elif content_type.startswith("text/html") or normalized_url.endswith(".html"):
        raw_content = response.content.decode("utf-8", errors="ignore")
        content, links, title = html.process_html(raw_content, normalized_url)
        ext = ".html"
    elif content_type.startswith("text/plain") or normalized_url.endswith(".txt"):
        raw_content = response.content.decode("utf-8", errors="ignore") 
        content, links, title = txt.process_txt(raw_content, normalized_url)
        ext = ".txt"

    if content is None or title is None:
        print(f"Skipping invalid content for URL: {normalized_url}")
        return None, None, False  

    # Calculate the hash of the content
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    # Deduplicate text
    if content_hash in content_hashes:
        print(f"Skipping duplicate content for URL: {normalized_url}")
        return None, None, False  

    with lock:
        current_docno = DOCNUM
        DOCNUM += 1
        content_hashes.add(content_hash)

    save_raw_data(current_docno, title, normalized_url, content, ext)

    return current_docno, links, True  

def crawler_thread(url, rp):
    global DOCNUM
    queue = ["https://" + url]
    with lock:
        print(f"Thread started for URL: {url}")

    while queue:
        url = queue.pop(0)
        normalized_url = normalize_url(url)

        with lock:
            if DOCNUM >= MAX_DOCS:
                print(f"Reached maximum document limit of {MAX_DOCS}. Stopping crawler.")
                return
            if normalized_url in visited:
                continue
            visited.add(normalized_url)

        try:
            # Fetch the page content
            response = requests.get(
                normalized_url,
                headers={"User-Agent": USER_AGENT},
                timeout=5
            )
            response.raise_for_status()

            doc_num, links, processing = process_and_save(response, normalized_url)   
            if (processing):
                document_queue.put(doc_num)  # Add the document name to the queue for processing
                for link in links:
                    if rp is not None and rp.can_fetch(USER_AGENT, link):
                        queue.append(link)

        except requests.RequestException as e:
            print(f"Failed to fetch {normalized_url}: {e}")

def crawl():
    global DOCNUM
    threads = []

    # Start a thread for each seed URL
    for url, rp in robots.items():
        if rp is not None and rp.can_fetch(USER_AGENT, url):
            thread = threading.Thread(target=crawler_thread, args=(url, rp))
            threads.append(thread)
            thread.start()
        else:
            print(f"Skipping {url} due to robots.txt restrictions.")

    for thread in threads:
        thread.join()

def main():
    
    print("Getting seed urls from sources.txt...")
    import_sources()

    print("Parsing robots.txt files...")
    parse_robots_txt()

    print("Starting crawling process...")
    crawl()

    print("Crawling completed. Total documents crawled:", DOCNUM)
    print(f"Crawled documents are saved in the {RAW} directory.")

    save_meta_raw()  # Save the metadata after crawling is complete
    print(f"Metadata saved in {META_RAW} ")

    document_queue.put(None)  # Signal the data processing thread to exit

if __name__ == "__main__":
    main()