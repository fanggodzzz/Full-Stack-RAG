import re
from urllib.parse import urljoin, urlparse
from shared import normalize_url

from bs4 import BeautifulSoup

REMOVED_TAGS = ["script", "style", "noscript", "iframe", "meta", "link"]

def prepare_base_url(base_url):
    parsed = urlparse(base_url)
    path = parsed.path

    # Root URL
    if not path:
        return base_url.rstrip("/") + "/"

    # Already a directory URL
    if path.endswith("/"):
        return base_url

    # Get the last path component
    last_part = path.rsplit("/", 1)[-1]

    if "." in last_part:
        last_part = last_part.rsplit(".", 1)[0] + "/"
        return urljoin(base_url, last_part)

    # Otherwise, treat it as a directory
    return base_url + "/"

def extract_title_from_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Prefer <title>
    if soup.title and soup.title.get_text(strip=True):
        return soup.title.get_text(" ", strip=True)

    # Fallback to first heading
    for tag in ("h1", "h2", "h3"):
        heading = soup.find(tag)
        if heading and heading.get_text(strip=True):
            return heading.get_text(" ", strip=True)

    return None

def extract_links_from_html(html, base_url):
    links = set()
    soup = BeautifulSoup(html, "html.parser")
    base_url = prepare_base_url(base_url)
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        try:
            absolute_url = urljoin(base_url, href)
            normalized_url = normalize_url(absolute_url)

            if urlparse(normalized_url).netloc == urlparse(base_url).netloc:
                links.add(normalized_url)

        except Exception as e:
            continue

    return links

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()

def remove_unwanted_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in REMOVED_TAGS:
        for element in soup.find_all(tag):
            element.decompose()

    return str(soup)

def valid_doc_title(html):
    title = extract_title_from_html(html)

    if not title:
        return None
    
    title_lower = title.lower()

    if title_lower.startswith("index of"):
        return None

    if "404" in title_lower or "not found" in title_lower:
        return None

    return title

def process_html(content, base_url):
    title = valid_doc_title(content)
    links = extract_links_from_html(content, base_url)
    text = remove_unwanted_tags(content)
    # text = content

    if not text or not title:
        return None, None, None

    return text, links, title