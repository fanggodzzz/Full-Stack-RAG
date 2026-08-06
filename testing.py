import json

from markdown import markdown
import requests
import os
from Document_processor import html, md, txt
from shared import normalize_url, save_meta_raw, add_meta, META_RAW, import_meta_raw, document_queue, filter_url
import data_processing as processor
import requests

FILE_NAME = "example.html"
INPUT = "D:\\Thanh\\WLU\\Spring 2026\\CP423\\Project\\Full-Stack-RAG\\Data\\raw\\doc_0000198.md"
PROCESSED = "D:\\Thanh\\WLU\\Spring 2026\\CP423\\Project\\Full-Stack-RAG\\Data\\processed.jsonl"
CHUNKED = "D:\\Thanh\\WLU\\Spring 2026\\CP423\\Project\\Full-Stack-RAG\\Data\\chunked.jsonl"
MAX = 5000
not_matched = [53]

meta = import_meta_raw()  # Load existing metadata
docs = {}

with open(PROCESSED, "r", encoding="utf-8") as f:
    for line in f:
        temp = json.loads(line)
        docs[int(temp["docno"])] = {
            "title": temp["title"],
            "content": temp["content"],
        }

# for i in range(MAX):
#     # print(f"Processing document {i}...")
#     url = meta[i]['url']
#     ext = meta[i]['ext']
#     # print(url, ext)
#     response = requests.get(
#         url,
#         headers={"User-Agent": "MyCRAWLER"},
#         timeout=5
#     )
#     # print(f"Response status code for document {i}: {response.status_code}")
#     response.raise_for_status()
#     content = links = title = None
#     raw_content = response.content.decode("utf-8", errors="ignore")  # Decode the content to a string


#     # Choose how to decode and what extension to save based on content type
#     if ext == ".md":
#         content, links, title = md.process_markdown(raw_content, url)
#         content = md.extract_text_from_md(content)  
#     elif ext == ".html":
#         content, links, title = html.process_html(raw_content, url)
#         content = html.extract_text_from_html(content)
#     elif ext == ".txt":
#         content, links, title = txt.process_txt(raw_content, url)
#         content = txt.extract_text_from_txt(content)

#     # print(f"Document {i} content: {content[:100]}")
#     if (content == docs[i]["content"] and title == docs[i]["title"]):
#         print(f"Document {i} content and title match.")
#         pass
#     elif (title != docs[i]["title"]):
#         print(f"Document {i} title does not match.")
#         not_matched.append(i)
#     elif (content != docs[i]["content"]):
#         print(f"Document {i} content does not match.")
#         not_matched.append(i)

print(f"Documents that did not match: {not_matched}")

# for i in not_matched:
#     print(f"Processing document {i}...")
#     url = meta[i]['url']
#     ext = meta[i]['ext']
#     # print(url, ext)
#     response = requests.get(
#         url,
#         headers={"User-Agent": "MyCRAWLER"},
#         timeout=5
#     )
#     # print(f"Response status code for document {i}: {response.status_code}")
#     response.raise_for_status()
#     content = links = title = None
#     raw_content = response.content.decode("utf-8", errors="ignore")  # Decode the content to a string


#     # Choose how to decode and what extension to save based on content type
#     if ext == ".md":
#         content, links, title = md.process_markdown(raw_content, url)
#         content = md.extract_text_from_md(content)  
#     elif ext == ".html":
#         content, links, title = html.process_html(raw_content, url)
#         content = html.extract_text_from_html(content)
#     elif ext == ".txt":
#         content, links, title = txt.process_txt(raw_content, url)
#         content = txt.extract_text_from_txt(content)

#     docs[i]["content"] = content
#     docs[i]["title"] = title

# for i in range(MAX):
#     document = {
#         "docno": i,
#         "title": docs[i]["title"],
#         "content": docs[i]["content"]
#     }
#     processor.save_processed_data(document)
#     processor.chunk_text(document)