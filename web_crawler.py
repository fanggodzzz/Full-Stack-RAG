from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse, urlsplit, urlunsplit
from bs4 import BeautifulSoup
import requests
import threading
import os
from datetime import datetime, timezone
import time
import data_processing as dp

SEED_URLS = []
SOURCES_FILE = "sources.txt"
USER_AGENT = "MyCRAWLER"
ROBOT_FILE = "robots.txt"
DOCNUM = 0
RAW = "./Data/raw"
REMOVED_TAGS = ["script", "style", "noscript", "iframe", "header", "footer", "nav", "aside", "meta", "link"]
MAX_DOCS = 1000000000


robots = {}
lock = threading.Lock()
visited = set()

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

def normalize_url(url):
    parts = urlsplit(url)
    path = parts.path or "/"
    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        path,
        "",   # remove query
        ""    # remove fragment
    ))

def extract_links(content, base_url):
    links = set()
    soup = BeautifulSoup(content, "html.parser")

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        absolute_url = urljoin(base_url, href)
        normalized_url = normalize_url(absolute_url)
        if urlparse(normalized_url).netloc == urlparse(base_url).netloc:
            links.add(normalized_url)
    return links

def add_crawler_metadata(html, url, docno):
    soup = BeautifulSoup(html, "html.parser")

    if soup.head is None:
        head = soup.new_tag("head")

        if soup.html:
            soup.html.insert(0, head)
        else:
            soup.insert(0, head)

    metadata = {
        "crawler-url": url,
        "crawler-docno": docno,
        "crawler-time": datetime.now(timezone.utc).isoformat()
    }

    for name, value in metadata.items():
        meta = soup.new_tag("meta")
        meta["name"] = name
        meta["content"] = value
        soup.head.append(meta)

    return str(soup)

def remove_unwanted_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in REMOVED_TAGS:
        for element in soup.find_all(tag):
            element.decompose()
    return str(soup)

def crawler_thread(url, rp):
    global DOCNUM
    queue = ["https://" + url]
    print(f"Thread started for URL: {url}")

    while queue:
        url = queue.pop(0)
        normalized_url = normalize_url(url)

        with lock:
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
            content_type = response.headers.get("Content-Type", "").lower()

            # Skip XML and JSON content types
            if ("xml" in content_type) or ("json" in content_type):
                continue

            content = response.content.decode(response.encoding or "utf-8", errors="ignore")
            content = remove_unwanted_tags(content)

            with lock:
                if DOCNUM >= MAX_DOCS:
                    print(f"Reached maximum document limit of {MAX_DOCS}. Stopping crawler.")
                    break
                current_docno = DOCNUM
                DOCNUM += 1

            content = add_crawler_metadata(content, normalized_url, current_docno)
            
            # Save the content to a file
            file_path = os.path.join(RAW, f"doc_{current_docno:07d}.html")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

            # Extract links and add to the queue
            links = extract_links(content, normalized_url)
            for link in links:
                if rp is not None and rp.can_fetch(USER_AGENT, link):
                    queue.append(link)

            dp.process_raw_data(current_docno)

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
    with open("./DATA/processed.jsonl", "w", encoding="utf-8") as f:
        f.write("")  # Clear the directory before writing new data

    print("Getting seed urls from sources.txt...")
    import_sources()

    print("Parsing robots.txt files...")
    parse_robots_txt()

    print("Starting crawling process...")
    crawl()

    print("Crawling completed. Total documents crawled:", DOCNUM)
    print(f"Crawled documents are saved in the {RAW} directory.")

if __name__ == "__main__":
    main()