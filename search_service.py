"""
BharatScheme AI - Optimized Tavily Search Service
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from tavily import TavilyClient

import config
from models import UserProfile

OFFICIAL_DOMAINS = [
    "myscheme.gov.in",
    "india.gov.in",
    "gov.in",
    "nic.in",
    "pib.gov.in",
]


def build_search_queries(profile: UserProfile) -> list[str]:
    details = (
        f"age {profile.age}, {profile.gender.value}, "
        f"{profile.category.value} category, "
        f"annual household income INR {profile.annual_income}, "
        f"{profile.employment_status.value}, "
        f"{profile.area_type.value}, state {profile.state}"
    )

    if profile.is_differently_abled:
        details += ", person with disability"

    if profile.education:
        details += f", education {profile.education}"

    if profile.occupation:
        details += f", occupation {profile.occupation}"

    return [
        f"Indian central government welfare schemes eligibility benefits for {details}",
        f"{profile.state} state government welfare schemes eligibility benefits for {details}",
    ]


def search_schemes(profile: UserProfile) -> list[dict]:
    if not config.TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY is missing.")

    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    queries = build_search_queries(profile)

    def run_search(query: str, official_only: bool):
        kwargs = {
            "query": query,
            "search_depth": "basic",
            "max_results": 4,
        }

        if official_only:
            kwargs["include_domains"] = OFFICIAL_DOMAINS

        return client.search(**kwargs)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(run_search, queries[0], True),
            executor.submit(run_search, queries[1], False),
        ]

        responses = [future.result() for future in futures]

    collected_results = []
    seen_urls = set()

    for response in responses:
        for result in response.get("results", []):
            url = result.get("url", "").strip()

            if url and url not in seen_urls:
                seen_urls.add(url)
                collected_results.append(result)

    return collected_results
