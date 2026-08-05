import os
import re
from urllib.parse import urljoin, urlparse
from shared import normalize_url

def extract_title_from_txt(filename, text):
    basename = os.path.splitext(os.path.basename(filename))[0]

    sentences = re.split(r"[.!?]\s+", text.strip())

    first_sentence = ""
    for s in sentences:
        s = s.strip()
        if s:
            first_sentence = s
            break

    if first_sentence:
        return f"{basename} - {first_sentence[:80]}"

    return basename

def extract_links_from_txt(text, base_url):
    links = set()
    for link in re.findall(r"https?://[^\s]+", text):
        try:
            absolute_url = urljoin(base_url, link)
            normalized_url = normalize_url(absolute_url)

            if urlparse(normalized_url).netloc == urlparse(base_url).netloc:
                links.add(normalized_url)

        except Exception as e:
            continue
    return links

def extract_text_from_txt(text):
    return text.strip()

def process_txt(txt, base_url):
    file_name = urlparse(base_url).path.split("/")[-1]
    title = extract_title_from_txt(file_name, txt)
    links = extract_links_from_txt(txt, base_url)
    text = extract_text_from_txt(txt)

    return text, links, title