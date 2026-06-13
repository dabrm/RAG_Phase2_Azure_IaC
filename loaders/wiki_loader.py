import re
from bs4 import BeautifulSoup


def load_wikipedia_html(path: str) -> str:

    with open(path, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    content = soup.find(id="mw-content-text")

    if content:
        paragraphs = [
            p.get_text(" ", strip=True)
            for p in content.find_all("p")
            if p.get_text(" ", strip=True)
        ]

        text = "\n\n".join(paragraphs)

    else:
        text = soup.get_text(" ", strip=True)

    # [1], [ 1 ], [23]
    text = re.sub(r"\[\s*\d+\s*\]", "", text)

    # [T 1], [E 2], [Note 3]
    text = re.sub(r"\[\s*[A-Za-z]+\s*\d+\s*\]", "", text)

    return text.strip()