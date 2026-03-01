"""
scraper.py
==========
Web scraping layer responsible for fetching a timetable page and extracting
all valid PDF links from it.

This module is intentionally decoupled from the GUI and from any
institution-specific logic: it works on any page that uses the
ReadSpeaker docreader pattern to embed PDF links.

License: MIT
"""

import urllib.parse

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT
from courses import BASE_STRAPI


def scrape_pdf_links(url: str) -> list[dict]:
    """
    Fetches the given URL and extracts all valid, non-duplicate PDF links
    found via the ReadSpeaker docreader pattern.

    Each result dict has the shape::

        {"label": "Human-readable title", "url": "https://example.com/file.pdf"}

    Filtering rules applied:
    - Only links containing ``docreader`` and a ``url=`` query parameter
      are considered; direct ``<a href="...pdf">`` links are ignored because
      they lack a reliable human-readable label.
    - URLs ending in ``.pdf.pdf`` are discarded (corrupted duplicates).
    - Entries whose label looks like a raw filename (ends in ``.pdf``) are
      discarded; when saved they would produce a ``.pdf.pdf`` file.
    - Duplicate URLs (same PDF linked more than once on the page) are skipped.

    @param url: Absolute URL of the timetable page to scrape.
    @return:    Ordered list of dicts, one per valid PDF found.
    @raises requests.HTTPError: If the server returns a non-2xx status code.
    @raises requests.ConnectionError: If the page cannot be reached.
    @raises requests.Timeout: If the request exceeds REQUEST_TIMEOUT seconds.
    """
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url.strip(), headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    results: list[dict] = []
    seen: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]

        if "docreader" not in href or "url=" not in href:
            continue

        pdf_url = _extract_pdf_url(href)
        if not pdf_url or pdf_url in seen or _is_double_pdf(pdf_url):
            continue
        seen.add(pdf_url)

        label = _extract_label(anchor)
        if not label or label.lower().endswith(".pdf"):
            continue

        results.append({"label": label, "url": pdf_url})

    return results


def _extract_pdf_url(href: str) -> str | None:
    """
    Parses a ReadSpeaker docreader href and returns the value of
    the embedded ``url`` query parameter.

    @param href: The raw href attribute of the anchor element.
    @return:     The stripped PDF URL string, or None if not found.
    """
    parsed = urllib.parse.urlparse(href)
    params = urllib.parse.parse_qs(parsed.query)
    pdf_url = params.get("url", [None])[0]
    return pdf_url.strip() if pdf_url else None


def _extract_label(anchor) -> str:
    """
    Walks up the DOM from the given anchor element looking for the nearest
    preceding heading tag (h3, h4, or h5) and returns its text content.

    This heading is used as the human-readable label for the PDF entry.
    If no heading is found, an empty string is returned.

    @param anchor: A BeautifulSoup Tag representing the ``<a>`` element.
    @return:       Stripped heading text, or an empty string.
    """
    parent = anchor.find_parent()
    while parent:
        heading = parent.find_previous(["h3", "h4", "h5"])
        if heading:
            return heading.get_text(strip=True)
        parent = parent.find_parent()
    return ""


def _is_double_pdf(url: str) -> bool:
    """
    Returns True if the URL ends with ``.pdf.pdf``, which indicates a
    corrupted or misnamed file that should be skipped.

    @param url: The PDF URL to check.
    @return:    True if the URL has a double .pdf extension.
    """
    return url.lower().endswith(".pdf.pdf")
