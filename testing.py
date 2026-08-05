from markdown import markdown
import requests
import os
from Document_processor import html, md, txt
from shared import normalize_url, save_meta_raw, add_meta, META_RAW

FILE_NAME = "example.html"
INPUT = "D:\\Thanh\\WLU\\Spring 2026\\CP423\\Project\\Full-Stack-RAG\\Data\\raw\\doc_0000198.md"

url = "https://docs.spring.io/spring-framework/reference/data-access.html"

print(f"{html.prepare_base_url(url)}")