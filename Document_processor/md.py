import re
import markdown
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from shared import normalize_url


def extract_title_from_md(md_text):
    # YAML front matter
    match = re.search(r"^---\s*\n(.*?)\n---", md_text, re.DOTALL)
    if match:
        frontmatter = match.group(1)
        title = re.search(r"^title:\s*(.+)$", frontmatter, re.MULTILINE)
        if title:
            return title.group(1).strip().strip('"').strip("'")

    # First heading
    match = re.search(r"^#\s+(.+)$", md_text, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return None


def extract_links_from_md(md_text, base_url=""):
    links = set()

    # Markdown links
    pattern = r"\[[^\]]+\]\(([^)]+)\)"

    for href in re.findall(pattern, md_text):
        if base_url:
            href = normalize_url(urljoin(base_url, href))
        links.add(href)

    return links


def extract_text_from_md(md_text):
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def valid_doc_title_from_text(text):
    sentences = re.split(r"[.!?]\s+", text.strip())

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) >= 10:
            return sentence[:120]

    return None


def process_markdown(markdown_text, base_url):
    title = extract_title_from_md(markdown_text)

    if not title:
        title = valid_doc_title_from_text(markdown_text)

    text = extract_text_from_md(markdown_text)
    links = extract_links_from_md(markdown_text, base_url or "")

    if not title:
        return None, None, None

    return text, links, title