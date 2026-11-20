
"""
BharatScheme AI - Advanced Official Government Source Discovery

Discovers potential scheme pages from registered Indian government portals.

Features:
1. Multi-level website crawling.
2. Nested government department and scheme-page discovery.
3. Sitemap-based discovery.
4. PDF and document link discovery.
5. Duplicate URL prevention.
6. Robots.txt compliance.
7. Central, State, UT and district source support.

Note:
This module discovers potential scheme pages.
It does not independently verify scheme details or eligibility.
"""

from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

from source_registry import get_official_sources


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BharatSchemeAI/1.0; "
        "+https://www.india.gov.in/)"
    )
}

REQUEST_TIMEOUT = 20

# Maximum number of pages visited on one government portal.
DEFAULT_MAX_PAGES_PER_SOURCE = 30

# Maximum nested link levels.
DEFAULT_MAX_DEPTH = 2

# Avoid downloading very large HTML/XML responses.
MAX_RESPONSE_SIZE = 5 * 1024 * 1024

KEYWORDS = [
    "scheme",
    "schemes",
    "yojana",
    "welfare",
    "scholarship",
    "scholarships",
    "pension",
    "subsidy",
    "benefit",
    "benefits",
    "social security",
    "financial assistance",
    "women",
    "woman",
    "girl",
    "girls",
    "child",
    "children",
    "farmer",
    "farmers",
    "agriculture",
    "student",
    "students",
    "education",
    "employment",
    "unemployment",
    "disability",
    "disabled",
    "senior citizen",
    "senior citizens",
    "minority",
    "minorities",
    "sc st",
    "backward class",
    "housing",
    "health",
    "healthcare",
    "ration",
    "food security",
    "livelihood",
    "entrepreneur",
    "entrepreneurship",
    "rural development",
    "social welfare",
    "financial support",
    "assistance",
    "application",
    "beneficiary",
    "beneficiaries",
    "department",
    "program",
    "programme",
    "grant",
    "loan",
    "insurance",
    "maternity",
    "pregnancy",
    "widow",
    "widows",
    "self employment",
    "skill development",
    "training",
    "fisheries",
    "labour",
    "labor",
    "tribal",
    "panchayat",
    "district",
]

DOCUMENT_EXTENSIONS = (
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
)

OFFICIAL_SUFFIXES = (
    ".gov.in",
    ".nic.in",
    ".gov",
)

ROBOTS_CACHE = {}


def get_domain(url):
    """Return a normalised hostname."""
    try:
        hostname = urlparse(url).hostname or ""
        return hostname.lower().removeprefix("www.")
    except (AttributeError, TypeError, ValueError):
        return ""


def normalize_url(url):
    """Remove URL fragments and surrounding whitespace."""
    if not url:
        return ""

    url = url.strip()
    url, _ = urldefrag(url)

    return url.rstrip("/")


def is_official_domain(url, source_url):
    """
    Allow the registered source domain and recognised
    Indian government domain suffixes.
    """
    host = get_domain(url)
    source_host = get_domain(source_url)

    if not host:
        return False

    if host == source_host:
        return True

    if source_host and host.endswith("." + source_host):
        return True

    return host.endswith(OFFICIAL_SUFFIXES)


def get_robots_parser(url):
    """Load and cache robots.txt for each website."""
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    if origin in ROBOTS_CACHE:
        return ROBOTS_CACHE[origin]

    robots_url = f"{origin}/robots.txt"

    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        response = requests.get(
            robots_url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 404:
            parser.parse(["User-agent: *", "Allow: /"])

        else:
            response.raise_for_status()
            parser.parse(response.text.splitlines())

        ROBOTS_CACHE[origin] = parser
        return parser

    except requests.RequestException:
        # Do not crawl when robots permission cannot be checked.
        return None


def check_robots_permission(url):
    """Check whether crawling a URL is permitted."""
    parser = get_robots_parser(url)

    if parser is None:
        return False

    try:
        return parser.can_fetch(HEADERS["User-Agent"], url)
    except Exception:
        return False


def contains_scheme_keyword(text):
    """Check whether text contains a relevant welfare keyword."""
    text = (text or "").lower()
    return any(keyword in text for keyword in KEYWORDS)


def is_document_url(url):
    """Identify document links such as PDFs."""
    path = urlparse(url).path.lower()
    return path.endswith(DOCUMENT_EXTENSIONS)


def add_candidate(
    discovered,
    seen_urls,
    url,
    title,
    parent_url,
    source,
):
    """Add a unique candidate scheme URL."""
    url = normalize_url(url)

    if not url or url in seen_urls:
        return

    if not is_official_domain(url, source.get("url", "")):
        return

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return

    seen_urls.add(url)

    discovered.append({
        "title": title or "Potential government scheme page",
        "url": url,
        "parent_url": parent_url,
        "source_name": source.get("name", "Unknown source"),
        "level": source.get("level", "Unknown"),
        "state": source.get("state"),
        "source_type": "official",
        "discovery_status": "Candidate - not yet verified",
    })


def fetch_page(url):
    """Download a page after checking robots.txt permission."""
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

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        content_length = response.headers.get("Content-Length")

        if content_length:
            try:
                if int(content_length) > MAX_RESPONSE_SIZE:
                    response.close()
                    return None
            except ValueError:
                pass

        content = response.raw.read(MAX_RESPONSE_SIZE + 1)
        response.close()

        if len(content) > MAX_RESPONSE_SIZE:
            return None

        return {
            "content": content,
            "content_type": content_type,
            "url": response.url,
        }

    except requests.RequestException:
        return None


def discover_sitemap_links(source, max_links=100):
    """
    Discover potential scheme URLs from common sitemap locations.

    Supports sitemap files and one level of sitemap indexes.
    """
    source_url = source.get("url", "").strip()

    if not source_url:
        return []

    parsed = urlparse(source_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    sitemap_urls = [
        urljoin(origin, "/sitemap.xml"),
        urljoin(origin, "/sitemap_index.xml"),
    ]

    discovered = []
    seen_urls = set()

    for sitemap_url in sitemap_urls:
        page = fetch_page(sitemap_url)

        if not page:
            continue

        try:
            root = ET.fromstring(page["content"])
        except ET.ParseError:
            continue

        namespace = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
        }

        # Read regular sitemap entries and sitemap indexes.
        locations = root.findall(".//sm:loc", namespace)

        if not locations:
            locations = root.findall(".//{*}loc")

        for location in locations:
            url = normalize_url(location.text or "")

            if not url:
                continue

            if not is_official_domain(url, source_url):
                continue

            if url in seen_urls:
                continue

            seen_urls.add(url)

            if contains_scheme_keyword(url) or is_document_url(url):
                add_candidate(
                    discovered=discovered,
                    seen_urls=set(),
                    url=url,
                    title="Scheme page discovered through sitemap",
                    parent_url=sitemap_url,
                    source=source,
                )

            if len(discovered) >= max_links:
                return discovered

    return discovered


def discover_scheme_links(
    source,
    max_links=100,
    max_depth=DEFAULT_MAX_DEPTH,
    max_pages=DEFAULT_MAX_PAGES_PER_SOURCE,
):
    """
    Discover potential scheme pages from one registered source.

    Crawls relevant nested pages instead of checking only
    the portal homepage.

    Returns candidate links with source information.
    """
    source_url = normalize_url(source.get("url", ""))

    if not source_url:
        return []

    if source.get("type") != "official":
        return []

    if not is_official_domain(source_url, source_url):
        return []

    discovered = []
    seen_urls = set()
    visited_pages = set()

    # Add sitemap discoveries first.
    sitemap_results = discover_sitemap_links(
        source,
        max_links=max_links,
    )

    for item in sitemap_results:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            discovered.append(item)

    if len(discovered) >= max_links:
        return discovered[:max_links]

    # Queue starts from the registered government portal.
    queue = deque([(source_url, 0)])

    while queue and len(visited_pages) < max_pages:
        current_url, depth = queue.popleft()
        current_url = normalize_url(current_url)

        if current_url in visited_pages:
            continue

        if not is_official_domain(current_url, source_url):
            continue

        visited_pages.add(current_url)

        page = fetch_page(current_url)

        if not page:
            continue

        content_type = page["content_type"]

        # Only HTML pages are crawled for nested links.
        if (
            "html" not in content_type
            and "xml" not in content_type
            and not content_type.startswith("text/")
        ):
            continue

        try:
            soup = BeautifulSoup(page["content"], "lxml")
        except Exception:
            continue

        page_title = ""

        if soup.title:
            page_title = soup.title.get_text(" ", strip=True)

        page_path = urlparse(current_url).path

        # Include a relevant nested page itself.
        if depth > 0 and contains_scheme_keyword(
            f"{page_title} {page_path}"
        ):
            add_candidate(
                discovered,
                seen_urls,
                current_url,
                page_title,
                current_url,
                source,
            )

        if len(discovered) >= max_links:
            break

        # Stop crawling deeper after the configured depth.
        if depth >= max_depth:
            continue

        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "").strip()

            if not href:
                continue

            full_url = normalize_url(urljoin(current_url, href))

            parsed = urlparse(full_url)

            if parsed.scheme not in ("http", "https"):
                continue

            if not is_official_domain(full_url, source_url):
                continue

            if full_url in visited_pages:
                continue

            link_title = anchor.get_text(" ", strip=True)

            combined_text = (
                f"{link_title} "
                f"{parsed.path} "
                f"{parsed.query}"
            )

            relevant = contains_scheme_keyword(combined_text)
            document = is_document_url(full_url)

            # Save relevant scheme pages and document links.
            if relevant or document:
                add_candidate(
                    discovered,
                    seen_urls,
                    full_url,
                    link_title or "Potential government scheme page",
                    current_url,
                    source,
                )

            # Crawl only relevant links to avoid excessive crawling.
            if relevant and not document:
                queue.append((full_url, depth + 1))

            if len(discovered) >= max_links:
                break

    return discovered[:max_links]


def discover_all_sources(
    max_links_per_source=100,
    max_depth=DEFAULT_MAX_DEPTH,
    max_pages_per_source=DEFAULT_MAX_PAGES_PER_SOURCE,
):
    """
    Discover candidate scheme pages from every registered
    official government source.
    """
    all_links = []
    seen_urls = set()

    sources = get_official_sources()

    for index, source in enumerate(sources, start=1):
        source_name = source.get("name", "Unknown source")

        print(
            f"[{index}/{len(sources)}] Discovering: {source_name}"
        )

        try:
            links = discover_scheme_links(
                source,
                max_links=max_links_per_source,
                max_depth=max_depth,
                max_pages=max_pages_per_source,
            )

            for link in links:
                if link["url"] not in seen_urls:
                    seen_urls.add(link["url"])
                    all_links.append(link)

            print(f"    Found {len(links)} candidate links")

        except Exception as error:
            print(f"    Discovery failed: {error}")

    print("\n========== DISCOVERY SUMMARY ==========")
    print(f"Government portals checked: {len(sources)}")
    print(f"Unique candidate links found: {len(all_links)}")
    print("=======================================")

    return all_links
