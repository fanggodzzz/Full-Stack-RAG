import os
import re
import urllib.parse

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

def extract_links_from_txt(text):
    return set(re.findall(r"https?://[^\s]+", text))

def extract_text_from_txt(text):
    return text.strip()

def process_txt(txt, base_url):
    file_name = urllib.parse.urlparse(base_url).path.split("/")[-1]
    title = extract_title_from_txt(file_name, txt)
    links = extract_links_from_txt(txt)
    text = extract_text_from_txt(txt)

    return text, links, title