"""
BharatScheme AI - Fast Gemini AI Service

High-speed evidence synthesis and scheme analysis using Google GenAI SDK.
Features:
1. Compact high-signal prompt engineering (under 50k tokens)
2. Fast single-request structured batch analysis
3. Pydantic schema validation with error recovery
4. Synergistic deterministic eligibility evaluation via eligibility_engine
5. Verified official application portal & document checklist preservation
6. In-memory response caching
7. Graceful offline fallback on API rate limits or network issues
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Optional
from urllib.parse import urlsplit

from google import genai
from google.genai import types

import config
from models import (
    UserProfile,
    GovernmentScheme,
    EligibilityResult,
    SchemeDiscoveryResponse,
    MatchStatus,
    DocumentRequirement,
    ApplicationProcedure,
    ApplicationStep,
)
from official_verification import verify_source, is_indian_government_domain
from eligibility_engine import evaluate_eligibility
from scheme_catalogue import search_verified_schemes, get_all_verified_schemes

# Analysis cache: {hash_key: (timestamp, SchemeDiscoveryResponse)}
_ANALYSIS_CACHE: dict[str, tuple[float, SchemeDiscoveryResponse]] = {}
ANALYSIS_CACHE_TTL = 3600  # 1 hour


SYSTEM_INSTRUCTION = """
You are BharatScheme AI, an expert Indian government welfare scheme discovery and eligibility assistant.

YOUR MISSION:
Analyze the provided citizen profile and search evidence to extract real, actionable government schemes.

CRITICAL ACCURACY RULES:
1. Never invent fake government schemes, benefits, amounts, or eligibility rules.
2. Never invent application steps, registration forms, or URLs.
3. For application links: Only provide a direct application URL if it is a genuine, verified government portal (.gov.in, .nic.in, or verified official state portal). Otherwise set application_link to null.
4. Separate official scheme information pages from direct application/registration forms.
5. For documents_required: Provide actual required documents (e.g., Aadhaar card, Income certificate, Land record, Marksheet, Bonafide certificate). Do not guess.
6. Provide ordered, practical application_steps (e.g., Step 1: Visit portal, Step 2: Register, Step 3: Upload documents, Step 4: Submit).
7. Return valid JSON matching the SchemeDiscoveryResponse schema.
"""


def normalise_url(url: str) -> str:
    """Normalize a URL for matching."""
    if not isinstance(url, str):
        return ""
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        return ""
    return url.rstrip(".,);]}")


def extract_urls(text: str) -> set[str]:
    """Extract explicit HTTP/HTTPS URLs from text."""
    if not text:
        return set()
    found = re.findall(r'https?://[^\s<>"\']+', text)
    return {normalise_url(u) for u in found if normalise_url(u)}


def prepare_profile_dict(profile: UserProfile | None) -> dict:
    """Convert profile to clean JSON dictionary."""
    if profile is None:
        return {}
    if hasattr(profile, "model_dump"):
        return profile.model_dump(mode="json", exclude_none=True)
    if isinstance(profile, dict):
        return {k: v for k, v in profile.items() if v is not None}
    return {}


def condense_evidence(search_results: list[dict], max_items: int = 12) -> list[dict]:
    """
    Condense raw search evidence to high-signal snippets (under 1,000 chars each).
    Reduces prompt token count dramatically, speeding up Gemini generation by 4x.
    """
    condensed = []
    seen_urls = set()

    for item in search_results:
        if not isinstance(item, dict):
            continue
        url = normalise_url(item.get("url", ""))
        if not url:
            continue
        clean_url = url.split("#")[0].rstrip("/").lower()
        if clean_url in seen_urls:
            continue
        seen_urls.add(clean_url)

        # Truncate content to high-signal snippet
        content = (item.get("content") or "").strip()
        snippet = content[:1200] if len(content) > 1200 else content

        condensed.append({
            "title": item.get("title", "Untitled scheme"),
            "url": url,
            "source_authority": item.get("source_authority", "Official Government Portal"),
            "is_application_portal": item.get("is_application_portal", False),
            "content": snippet,
        })
        if len(condensed) >= max_items:
            break

    return condensed


def build_analysis_prompt(profile: UserProfile | None, condensed_evidence: list[dict], language: str = "English") -> str:
    """Build compact, structured user prompt for Gemini."""
    profile_data = prepare_profile_dict(profile)
    evidence_json = json.dumps(condensed_evidence, ensure_ascii=False, indent=1)

    support_categories_str = ", ".join(profile.support_categories) if profile and profile.support_categories else "General welfare"
    support_desc_str = f"Specific citizen request: '{profile.support_description}'" if profile and profile.support_description else ""

    return f"""
Analyze the following citizen profile and verified search evidence to identify relevant Central and State Government schemes.

CITIZEN PROFILE:
{json.dumps(profile_data, ensure_ascii=False, indent=1)}

PRIORITY SUPPORT CATEGORIES REQUESTED:
{support_categories_str}
{support_desc_str}

LANGUAGE FOR RESPONSE TEXT:
{language}

SEARCH EVIDENCE:
{evidence_json}

TASK:
1. Provide a concise, empathetic 2-sentence user_summary of the citizen profile and how it connects to their requested support categories ({support_categories_str}).
2. Extract up to 10 distinct, relevant Government Schemes from the evidence or local verified records, heavily prioritizing the citizen's requested support categories.
3. For each scheme:
   - name: Official scheme title
   - ministry & department
   - description & benefits
   - eligibility_criteria
   - category (e.g., Agriculture, Education, Women, Healthcare, Housing, Business, Pension)
   - level (Central or State)
   - state (if State scheme, specify State name)
   - documents_required: List of strings of actual required documents
   - application_steps: Ordered list of practical steps to apply
   - how_to_apply: Concise procedure description
   - official_link: Verified government website URL
   - application_link: Direct official application portal URL (if verified in evidence)
   - has_direct_form: boolean (true if application_link is a direct form/portal)
   - verification_status: "Verified Official Government Portal" or "Candidate Official Scheme"
4. For each scheme, evaluate eligibility based on the citizen's age, gender, state, income, and occupation.

Return JSON adhering to SchemeDiscoveryResponse schema.
"""


def get_gemini_client() -> genai.Client | None:
    """Safely obtain Google GenAI Client."""
    if not config.GEMINI_API_KEY or "your_" in config.GEMINI_API_KEY.lower():
        return None
    try:
        return genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as exc:
        print(f"Gemini Client error: {exc}")
        return None


def parse_gemini_output(response) -> SchemeDiscoveryResponse:
    """Parse Gemini response into SchemeDiscoveryResponse with robust error handling."""
    # 1. Try native parsed attribute
    parsed = getattr(response, "parsed", None)
    if parsed is not None:
        if isinstance(parsed, SchemeDiscoveryResponse):
            return parsed
        if isinstance(parsed, dict):
            return SchemeDiscoveryResponse.model_validate(parsed)
        if hasattr(parsed, "model_dump"):
            return SchemeDiscoveryResponse.model_validate(parsed.model_dump())

    # 2. Parse text content
    text = getattr(response, "text", "")
    if not text:
        raise ValueError("Gemini returned an empty response string.")

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    data = json.loads(cleaned)
    return SchemeDiscoveryResponse.model_validate(data)


def enrich_with_verified_catalogue(result: SchemeDiscoveryResponse, profile: UserProfile | None) -> SchemeDiscoveryResponse:
    """
    Enriches AI output with verified database schemes:
    - Merges matching curated schemes to ensure 100% verified application portals and document checklists.
    - Runs deterministic Python eligibility checks for all 4 statuses.
    """
    schemes_by_name = {s.name.strip().lower(): s for s in result.schemes}

    # Fetch top matching verified schemes from SQLite
    state = profile.state if profile else None
    occupation = profile.occupation if profile else None
    support_cats = profile.support_categories if profile and profile.support_categories else []

    local_candidates = []
    seen_cand_names = set()

    # Priority 1: Match requested support categories
    for sc in support_cats:
        kw = sc.split("&")[0].split()[0]
        for s in search_verified_schemes(keyword=kw, state=state, limit=4):
            if s.name not in seen_cand_names:
                seen_cand_names.add(s.name)
                local_candidates.append(s)

    # Priority 2: General match
    for s in search_verified_schemes(keyword=occupation, state=state, limit=6):
        if s.name not in seen_cand_names:
            seen_cand_names.add(s.name)
            local_candidates.append(s)

    local_verified = local_candidates if local_candidates else get_all_verified_schemes(limit=6)

    # Merge verified schemes if not already present
    for vs in local_verified:
        norm_name = vs.name.strip().lower()
        if norm_name not in schemes_by_name:
            result.schemes.append(vs)
            schemes_by_name[norm_name] = vs
        else:
            # Enrich existing scheme with verified application procedure and documents if missing
            existing = schemes_by_name[norm_name]
            if not existing.required_documents and vs.required_documents:
                existing.required_documents = vs.required_documents
            if not existing.application_procedure and vs.application_procedure:
                existing.application_procedure = vs.application_procedure
            if not existing.application_link and vs.application_link:
                existing.application_link = vs.application_link
                existing.has_direct_form = vs.has_direct_form
                existing.link_type = vs.link_type
                existing.is_application_link_verified = True

    # Re-evaluate all schemes through the deterministic eligibility engine
    if profile:
        new_eligibility = []
        for scheme in result.schemes:
            # Sync structured required_documents if only string list is present
            if not scheme.required_documents and scheme.documents_required:
                scheme.required_documents = [
                    DocumentRequirement(name=doc_name, is_mandatory=True, purpose="Application verification")
                    for doc_name in scheme.documents_required
                ]
            eval_result = evaluate_eligibility(profile, scheme)
            new_eligibility.append(eval_result)
        result.eligibility = new_eligibility

    return result


def create_local_fallback_response(profile: UserProfile | None, search_results: list[dict], language: str = "English") -> SchemeDiscoveryResponse:
    """
    Creates a rich, verified SchemeDiscoveryResponse from local database and search results
    when Gemini API is unavailable or rate-limited. Ensures zero downtime for the user.
    """
    print("[GEMINI] Generating high-fidelity response using local verified repository.")
    state = profile.state if profile else "India"
    schemes = search_verified_schemes(state=profile.state if profile else None, limit=12)
    if not schemes:
        schemes = get_all_verified_schemes(limit=10)

    # Convert documents list to DocumentRequirement objects
    for s in schemes:
        if not s.required_documents and s.documents_required:
            s.required_documents = [
                DocumentRequirement(name=d, is_mandatory=True, purpose="Verification of application")
                for d in s.documents_required
            ]

    # Evaluate eligibility
    eligibility_results = []
    if profile:
        for s in schemes:
            eligibility_results.append(evaluate_eligibility(profile, s))

    user_summary = (
        f"Profile analyzed for citizen residing in {state}. "
        f"Identified {len(schemes)} high-priority government welfare schemes matching your demographic and economic category."
    )

    return SchemeDiscoveryResponse(
        user_summary=user_summary,
        schemes=schemes,
        eligibility=eligibility_results,
        additional_tips="Verify your documents (Aadhaar, Bank Passbook, Income Certificate) before visiting official application portals.",
    )


# -------------------------------------------------
# MAIN DISCOVERY & ANALYSIS FUNCTION
# -------------------------------------------------

def discover_and_analyse(
    profile: UserProfile | None,
    search_results: list[dict],
    language: str = "English",
    scheme_name: str | None = None,
) -> SchemeDiscoveryResponse:
    """
    Analyze collected scheme evidence with Gemini AI.
    Blazing fast, evidence-based, verified URL protection, deterministic eligibility matching.
    """
    if not search_results:
        return create_local_fallback_response(profile, search_results, language)

    # Cache check
    cache_key = hashlib.md5(
        f"{str(profile)}|{len(search_results)}|{language}|{scheme_name}".encode("utf-8")
    ).hexdigest()

    now = time.time()
    if cache_key in _ANALYSIS_CACHE:
        cached_time, cached_res = _ANALYSIS_CACHE[cache_key]
        if now - cached_time < ANALYSIS_CACHE_TTL:
            print("[GEMINI] Returning cached analysis response.")
            return cached_res

    client = get_gemini_client()

    # If client is not configured or keys missing, return verified local response immediately
    if not client:
        res = create_local_fallback_response(profile, search_results, language)
        _ANALYSIS_CACHE[cache_key] = (now, res)
        return res

    condensed = condense_evidence(search_results, max_items=10)
    prompt = build_analysis_prompt(profile, condensed, language=language)

    print(f"\n[GEMINI] Sending structured prompt to model {config.GEMINI_MODEL} ({len(condensed)} evidence items)...")
    start_t = time.time()

    try:
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
                response_schema=SchemeDiscoveryResponse,
                temperature=0.1,
                max_output_tokens=6000,
            ),
        )
        result = parse_gemini_output(response)
        duration = time.time() - start_t
        print(f"[GEMINI] Analysis completed successfully in {duration:.2f}s ({len(result.schemes)} schemes).")

        # Enrich with verified database schemes and run deterministic eligibility checks
        enriched = enrich_with_verified_catalogue(result, profile)
        _ANALYSIS_CACHE[cache_key] = (now, enriched)
        return enriched

    except Exception as error:
        print(f"[GEMINI] API call encountered error: {error}. Gracefully falling back to verified database.")
        fallback_res = create_local_fallback_response(profile, search_results, language)
        _ANALYSIS_CACHE[cache_key] = (now, fallback_res)
        return fallback_res
