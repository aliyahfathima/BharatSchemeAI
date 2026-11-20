
"""
BharatScheme AI - Scheme Content Collector

Extracts readable content from discovered official webpages
and PDF documents while preserving source information.
"""

import io
import time

import requests
import trafilatura

from bs4 import BeautifulSoup
from pypdf import PdfReader

from source_discovery import check_robots_permission


HEADERS = {
    "User-Agent": "BharatSchemeAI/1.0 (Government scheme information research)"
}

REQUEST_TIMEOUT = 20
MAX_PDF_SIZE = 12 * 1024 * 1024  # 12 MB
MAX_CONTENT_LENGTH = 15000


def extract_webpage(url):
    """Download and extract readable text from an HTML webpage."""

    if not check_robots_permission(url):
        return None

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if "html" not in content_type:
            return None

        downloaded = response.text

        # First try Trafilatura for cleaner main-page extraction.
        text = trafilatura.extract(
            downloaded,
            include_links=True,
            include_tables=True,
            favor_recall=True,
        )

        # Fallback to BeautifulSoup if Trafilatura finds no content.
        if not text:
            soup = BeautifulSoup(downloaded, "lxml")

            for element in soup([
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "noscript",
            ]):
                element.decompose()

            text = soup.get_text(" ", strip=True)

        if not text:
            return None

        soup = BeautifulSoup(downloaded, "lxml")
        title = (
            soup.title.get_text(strip=True)
            if soup.title
            else "Untitled page"
        )

        return {
            "title": title,
            "url": response.url,
            "content": text[:MAX_CONTENT_LENGTH],
            "content_type": "HTML",
            "extraction_status": "Extracted",
        }

    except requests.RequestException as error:
        print(f"Page download failed: {url} | {error}")
        return None

    except Exception as error:
        print(f"Page extraction failed: {url} | {error}")
        return None


def extract_pdf(url):
    """Download and extract text from an official PDF."""

    if not check_robots_permission(url):
        return None

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
            stream=True,
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if "pdf" not in content_type and not url.lower().endswith(".pdf"):
            return None

        content = response.content

        if len(content) > MAX_PDF_SIZE:
            print(f"PDF skipped because it exceeds size limit: {url}")
            return None

        reader = PdfReader(io.BytesIO(content))

        pages = []

        for page in reader.pages:
            page_text = page.extract_text() or ""

            if page_text:
                pages.append(page_text)

            if sum(len(item) for item in pages) >= MAX_CONTENT_LENGTH:
                break

        extracted_text = "\n".join(pages)

        if not extracted_text.strip():
            return None

        return {
            "title": url.rsplit("/", 1)[-1],
            "url": response.url,
            "content": extracted_text[:MAX_CONTENT_LENGTH],
            "content_type": "PDF",
            "extraction_status": "Extracted",
        }

    except requests.RequestException as error:
        print(f"PDF download failed: {url} | {error}")
        return None

    except Exception as error:
        print(f"PDF extraction failed: {url} | {error}")
        return None


def collect_scheme_content(discovered_links, max_documents=30):
    """
    Extract content from discovered candidate URLs.

    Returns extracted documents with source metadata.
    """

    documents = []
    seen_urls = set()

    for item in discovered_links[:max_documents]:

        url = item.get("url", "").strip()

        if not url or url in seen_urls:
            continue

        seen_urls.add(url)

        print(f"Collecting: {url}")

        if url.lower().split("?")[0].endswith(".pdf"):
            document = extract_pdf(url)
        else:
            document = extract_webpage(url)

        if document:
            document.update({
                "source_name": item.get("source_name", "Unknown"),
                "parent_url": item.get("parent_url", ""),
                "level": item.get("level", "Unknown"),
                "state": item.get("state"),
                "source_type": item.get("source_type", "unknown"),
                "discovery_status": item.get(
                    "discovery_status",
                    "Candidate - not yet verified",
                ),
            })

            documents.append(document)

        # Avoid sending rapid repeated requests.
        time.sleep(1)

    return documents
