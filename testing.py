from markdown import markdown
import requests
import os
from Document_processor import html, md, txt

FILE_NAME = "example.html"
INPUT = "D:\\Thanh\\WLU\\Spring 2026\\CP423\\Project\\Full-Stack-RAG\\Data\\raw\\doc_0000198.md"
# response = requests.get("https://nextjs.org/docs/app/api-reference/components/link", headers={"User-Agent": "MyAgent"})

with open(INPUT, "r", encoding="utf-8") as f:
    content = f.read()

print(md.extract_title_from_md(content))
print(md.extract_links_from_md(content, "https://nextjs.org/docs/app/api-reference/components/link"))
print(md.extract_text_from_md(content))