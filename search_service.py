"""
BharatScheme AI - Fast Scheme Discovery Service

High-speed, multi-source scheme search combining:
1. Local SQLite Verified Catalogue (Instant 0-latency results)
2. Targeted Parallel Official Government Search (Tavily with ThreadPoolExecutor)
3. Smart In-Memory TTL Caching
4. Strict Domain Verification & Deduplication
5. Automatic graceful fallback if network/API limits are encountered.
"""

from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

from tavily import TavilyClient

import config
from official_verification import verify_source, is_indian_government_domain, is_registered_domain
from scheme_catalogue import search_documents, search_verified_schemes, get_all_verified_schemes
from models import UserProfile, GovernmentScheme

# In-memory search cache with timestamps: {cache_key: (timestamp, results)}
_SEARCH_CACHE: dict[str, tuple[float, list[dict]]] = {}
CACHE_TTL = 3600  # 1 hour cache TTL


def get_value(value):
    """Convert Enum values to readable strings."""
    if value is None:
        return None
    return value.value if hasattr(value, "value") else str(value)


def get_profile_value(profile, field):
    """Safely read an optional profile field."""
    if profile is None:
        return None
    if isinstance(profile, dict):
        return profile.get(field)
    return getattr(profile, field, None)


def get_domain(url: str) -> str:
    """Extract a normalized hostname."""
    try:
        return (urlparse(url).hostname or "").lower().removeprefix("www.")
    except Exception:
        return ""


def get_cache_key(profile: UserProfile | None, scheme_name: str | None) -> str:
    """Generate deterministic cache key."""
    if scheme_name:
        return f"scheme:{scheme_name.strip().lower()}"
    if profile:
        profile_dict = profile.model_dump() if hasattr(profile, "model_dump") else str(profile)
        raw_key = json.dumps(profile_dict, sort_keys=True, default=str)
        return "profile:" + hashlib.md5(raw_key.encode("utf-8")).hexdigest()
    return "general_discovery"


# -------------------------------------------------
# FOCUSED SEARCH QUERY BUILDER
# -------------------------------------------------

def build_search_queries(profile: UserProfile | None = None, scheme_name: str | None = None) -> list[str]:
    """
    Generate 2 to 3 high-impact, focused queries instead of a dozen redundant ones.
    Tightly couples beneficiary attributes with official domain keywords.
    """
    if scheme_name and scheme_name.strip():
        name = scheme_name.strip()
        return [
            f'"{name}" official portal apply online registration',
            f'"{name}" scheme eligibility benefits required documents gov in',
        ]

    if profile is None:
        return [
            "Indian government welfare schemes official portal apply online",
            "Central and State government welfare schemes eligibility benefits gov in",
        ]

    queries = []
    state = get_profile_value(profile, "state")
    gender = get_value(get_profile_value(profile, "gender"))
    occupation = (get_profile_value(profile, "occupation") or "").strip()
    is_farmer = get_profile_value(profile, "is_farmer") or "farmer" in occupation.lower()
    is_student = get_profile_value(profile, "is_student") or "student" in occupation.lower()
    disability = get_profile_value(profile, "is_differently_abled")
    category = get_value(get_profile_value(profile, "category"))
    support_categories = get_profile_value(profile, "support_categories") or []
    support_description = (get_profile_value(profile, "support_description") or "").strip()

    # If user provided specific support description text, build a high-priority targeted query
    if support_description:
        loc = f"{state} " if state else ""
        queries.append(f"{loc}{support_description} government scheme official portal apply")

    # Target user's explicit support categories
    category_keywords = {
        "Education & Scholarships": "scholarship education student portal apply",
        "Employment & Job Opportunities": "employment job opportunities livelihood portal",
        "Self Employment & Business Loans": "business loan mudra subsidy MSME apply online",
        "Women Empowerment": "women welfare financial assistance scheme official apply",
        "Agriculture & Farmers Support": "farmer agriculture subsidy PM Kisan official portal",
        "Housing & Home Loans": "PMAY housing home subsidy loan official apply",
        "Healthcare & Medical Assistance": "health insurance Ayushman Bharat medical cover portal",
        "Pension & Old Age Support": "pension Atal Pension Yojana old age social security apply",
        "Disability Support": "disability UDID Swavlamban card Divyangjan pension portal",
        "Skill Development & Training": "skill development PMKVY vocational training portal",
        "Financial Assistance": "financial assistance direct benefit transfer DBT scheme portal",
        "Food & Ration Benefits": "ration card food security NFSA food benefits portal",
        "Marriage Assistance": "marriage financial assistance scheme official apply",
        "Child & Family Welfare": "child maternity family welfare PMMVY scheme portal",
    }

    for sc in support_categories:
        kw = category_keywords.get(sc)
        if kw:
            loc = f"{state} " if state else "Central and State "
            queries.append(f"{loc}{kw} official")
            if len(queries) >= 3:
                break

    # If still have slots, use demographic queries
    if len(queries) < 3:
        if is_farmer:
            if state:
                queries.append(f"{state} farmer agriculture welfare subsidy schemes official portal apply")
            else:
                queries.append("Central government farmer welfare schemes PM Kisan subsidy official portal")

        elif is_student:
            if state:
                queries.append(f"{state} student scholarship higher education scheme official apply")
            else:
                queries.append("National Scholarship Portal central government student scholarships official apply")

        elif disability is True:
            queries.append("Divyangjan welfare schemes UDID Swavlamban card disability pension official portal")

        elif gender == "Female":
            if state:
                queries.append(f"{state} women empowerment welfare financial assistance scheme official apply")
            else:
                queries.append("Central government women welfare schemes financial assistance official portal apply")

        elif occupation:
            if state:
                queries.append(f"{state} government schemes for {occupation} workers official apply")

    # Secondary State-specific query
    if state and len(queries) < 2:
        queries.append(f"{state} government welfare schemes official portal benefits apply online")

    # Always ensure at least one strong official query
    if not queries:
        queries.append("Central and State government welfare schemes eligibility benefits official portal")

    return queries[:3]


# -------------------------------------------------
# TAVILY RESULT NORMALISATION
# -------------------------------------------------

def normalise_results(response: dict, query: str) -> list[dict]:
    """Convert Tavily search results into BharatScheme verified format."""
    results = []
    for item in response.get("results", []):
        url = (item.get("url") or "").strip()
        if not url:
            continue

        verification = verify_source(url)
        content = item.get("content") or ""

        results.append({
            "title": item.get("title") or "Untitled government scheme",
            "url": url,
            "content": content,
            "source_name": get_domain(url),
            "source_type": "official" if verification.get("is_official_domain") else "secondary" if verification.get("source_authority") == "Secondary" else "unknown",
            "source_authority": verification.get("source_authority"),
            "verification_status": verification.get("verification_status"),
            "is_application_portal": verification.get("is_application_portal", False),
            "link_type": verification.get("link_type", "Unverified"),
            "search_query": query,
        })
    return results


# -------------------------------------------------
# TAVILY CLIENT & EXECUTION
# -------------------------------------------------

def get_tavily_client() -> TavilyClient | None:
    """Safely obtain configured Tavily client."""
    if not config.TAVILY_API_KEY or "your_" in config.TAVILY_API_KEY.lower():
        return None
    try:
        return TavilyClient(api_key=config.TAVILY_API_KEY)
    except Exception as exc:
        print(f"Tavily client initialization error: {exc}")
        return None


def execute_single_tavily_query(client: TavilyClient, query: str) -> list[dict]:
    """Run a single query on Tavily with error isolation."""
    try:
        response = client.search(
            query=query,
            search_depth=config.TAVILY_SEARCH_DEPTH,
            max_results=config.TAVILY_MAX_RESULTS,
        )
        return normalise_results(response, query)
    except Exception as error:
        print(f"Tavily query warning ('{query}'): {error}")
        return []


# -------------------------------------------------
# DEDUPLICATION
# -------------------------------------------------

def deduplicate_results(results: list[dict]) -> list[dict]:
    """Deduplicate results keeping the richest content item per URL."""
    unique: dict[str, dict] = {}
    for item in results:
        url = (item.get("url") or "").strip()
        if not url:
            continue
        key = url.split("#")[0].rstrip("/").lower()
        if key not in unique or len(item.get("content", "")) > len(unique[key].get("content", "")):
            unique[key] = item
    return list(unique.values())


# -------------------------------------------------
# MAIN SEARCH SERVICE
# -------------------------------------------------

def search_schemes(profile: UserProfile | None = None, scheme_name: str | None = None) -> list[dict]:
    """
    High performance scheme discovery.
    1. Checks in-memory cache first (instant return).
    2. Searches SQLite local verified database for exact matches.
    3. Runs focused web search with concurrent threads for fresh web evidence.
    4. Caches and returns deduplicated results.
    """
    cache_key = get_cache_key(profile, scheme_name)
    now = time.time()

    # Check cache
    if cache_key in _SEARCH_CACHE:
        cached_time, cached_data = _SEARCH_CACHE[cache_key]
        if now - cached_time < CACHE_TTL:
            print(f"[SEARCH] Cache hit for key '{cache_key}', returning {len(cached_data)} results.")
            return cached_data

    all_results: list[dict] = []

    # 1. Search Local SQLite Verified Schemes first
    state = get_profile_value(profile, "state")
    support_categories = get_profile_value(profile, "support_categories") or []
    support_desc = get_profile_value(profile, "support_description")

    # If support categories are specified, fetch schemes matching each category
    matched_verified = []
    seen_names = set()

    for sc in support_categories:
        # Search by keyword fragment of the support category
        first_word = sc.split("&")[0].split()[0]
        results_for_cat = search_verified_schemes(keyword=first_word, state=state, limit=8)
        for s in results_for_cat:
            if s.name not in seen_names:
                seen_names.add(s.name)
                matched_verified.append(s)

    # Also search by occupation / scheme_name or general state schemes
    general_verified = search_verified_schemes(
        keyword=scheme_name or support_desc or (get_profile_value(profile, "occupation") or None),
        state=state,
        limit=15,
    )
    for s in general_verified:
        if s.name not in seen_names:
            seen_names.add(s.name)
            matched_verified.append(s)

    verified_schemes = matched_verified if matched_verified else general_verified

    for vs in verified_schemes:
        content_summary = f"{vs.name}. {vs.description} Benefits: {vs.benefits} Eligibility: {vs.eligibility_criteria}"
        all_results.append({
            "title": vs.name,
            "url": vs.application_link or vs.official_link or vs.source or "https://india.gov.in",
            "content": content_summary,
            "source_name": get_domain(vs.official_link or vs.source or ""),
            "source_type": "official",
            "source_authority": "Official Government Portal",
            "verification_status": "Verified Official Scheme",
            "is_application_portal": vs.has_direct_form,
            "link_type": vs.link_type,
            "scheme_object": vs,
            "search_query": "sqlite_local_catalogue",
        })

    # Also search raw scheme documents in SQLite
    raw_docs = search_documents(keyword=scheme_name or "scheme", state=state, limit=10)
    for doc in raw_docs:
        all_results.append({
            "title": doc.get("title", "Untitled scheme"),
            "url": doc.get("url", ""),
            "content": doc.get("content", ""),
            "source_name": doc.get("source_name", ""),
            "source_type": doc.get("source_type", "unknown"),
            "source_authority": "Registered Government Portal" if doc.get("source_type") == "official" else "Secondary",
            "verification_status": "Candidate government document",
            "is_application_portal": False,
            "link_type": "Official Scheme Information Page" if doc.get("source_type") == "official" else "Secondary Source",
            "search_query": "sqlite_raw_catalogue",
        })

    # 2. Live Web Search (if Tavily API key is available)
    client = get_tavily_client()
    if client:
        queries = build_search_queries(profile=profile, scheme_name=scheme_name)
        print(f"[SEARCH] Executing {len(queries)} focused queries in parallel: {queries}")

        with ThreadPoolExecutor(max_workers=min(len(queries), config.MAX_PARALLEL_QUERIES)) as executor:
            future_to_query = {
                executor.submit(execute_single_tavily_query, client, q): q
                for q in queries
            }
            for future in as_completed(future_to_query):
                res = future.result()
                all_results.extend(res)

    # 3. Deduplicate and score
    final_results = deduplicate_results(all_results)

    # Prioritize official portals and items with direct application links
    final_results.sort(
        key=lambda item: (
            1 if item.get("is_application_portal") else 0,
            1 if item.get("source_type") == "official" else 0,
            len(item.get("content", ""))
        ),
        reverse=True,
    )

    trimmed_results = final_results[:40]
    _SEARCH_CACHE[cache_key] = (now, trimmed_results)

    print(f"[SEARCH] Complete. Total unique results: {len(trimmed_results)}")
    return trimmed_results
