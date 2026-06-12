import re
from bs4 import BeautifulSoup


def load_wikipedia_html(path: str) -> str:

    with open(path, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    content = soup.find(id="mw-content-text")

    if content:
        text = content.get_text(" ", strip=True)
    else:
        text = soup.get_text(" ", strip=True)

    # [1], [ 1 ], [23]
    text = re.sub(r"\[\s*\d+\s*\]", "", text)

    # [T 1], [E 2], [Note 3]
    text = re.sub(r"\[\s*[A-Za-z]+\s*\d+\s*\]", "", text)

    return text.strip()