"""
BharatScheme AI - Official Source Verification

Verifies source provenance and assigns rigorous verification labels.
Distinguishes between:
1. Direct Official Application / Registration Portals
2. Official Scheme Information Pages
3. Secondary Sources
4. Unverified Sources
"""

from urllib.parse import urlparse
import re
from source_registry import SOURCE_REGISTRY


SECONDARY_DOMAINS = {
    "cgscheme.com",
    "pmmodiyojana.in",
    "sarkariyojana.com",
    "sarkariyojnaa.com",
    "yojanagov.in",
    "timesofindia.indiatimes.com",
    "hindustantimes.com",
    "thehindu.com",
    "indianexpress.com",
    "ndtv.com",
}

# Official government domain suffixes
GOVERNMENT_SUFFIXES = (
    ".gov.in",
    ".nic.in",
    ".ac.in",
    ".res.in",
)

# Known dedicated official portals that may not end in .gov.in
VERIFIED_OFFICIAL_PORTALS = {
    "jansamarth.in": "JanSamarth - National Credit-Linked Schemes Portal",
    "standupmitra.in": "Stand-Up India Portal (SIDBI)",
    "mudra.org.in": "Micro Units Development & Refinance Agency (MUDRA)",
    "cmchistn.com": "Chief Minister Comprehensive Health Insurance Scheme (TN)",
    "beneficiary.nha.gov.in": "National Health Authority Beneficiary Portal",
    "pmkisan.gov.in": "PM-KISAN Official Portal",
    "scholarships.gov.in": "National Scholarship Portal",
    "pmjay.gov.in": "Ayushman Bharat PM-JAY Portal",
    "myscheme.gov.in": "myScheme - Ministry of Electronics & IT",
    "india.gov.in": "National Portal of India",
    "umang.gov.in": "UMANG Government Portal",
    "swavlambancard.gov.in": "Unique Disability ID Portal",
    "pmsuryaghar.gov.in": "PM Surya Ghar National Portal",
    "pmvishwakarma.gov.in": "PM Vishwakarma Official Portal",
    "pmsvanidhi.mohua.gov.in": "PM SVANidhi Portal",
    "npscra.nsdl.co.in": "CRA - Atal Pension Yojana Portal",
    "kmut.tn.gov.in": "Kalaignar Magalir Urimai Thittam (TN)",
    "pudhumaipenn.tn.gov.in": "Pudhumai Penn Scheme Portal (TN)",
    "tamilpudhalvan.tn.gov.in": "Tamil Pudhalvan Portal (TN)",
    "ladakibahin.maharashtra.gov.in": "Mukhyamantri Ladki Bahin Yojana Portal (MH)",
    "sevasindhu.karnataka.gov.in": "Seva Sindhu Portal (Karnataka)",
    "mksy.up.gov.in": "Mukhyamantri Kanya Sumangala Yojana Portal (UP)",
}

# Regex to detect application / registration / login paths
APPLICATION_PATH_PATTERNS = re.compile(
    r"(register|registration|apply|application|apply-now|login|new-user|applicant|beneficiary|form|submission|enroll)",
    re.IGNORECASE,
)


def get_domain(url: str) -> str:
    """Return a normalized hostname."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        return host.lower().removeprefix("www.")
    except Exception:
        return ""


def is_registered_domain(url: str) -> bool:
    """Check whether a URL belongs to a registered official portal."""
    domain = get_domain(url)
    if not domain:
        return False

    if domain in VERIFIED_OFFICIAL_PORTALS:
        return True

    for source in SOURCE_REGISTRY:
        if source.get("type") != "official":
            continue
        registered_domain = get_domain(source.get("url", ""))
        if registered_domain and (domain == registered_domain or domain.endswith("." + registered_domain)):
            return True

    return False


def is_indian_government_domain(url: str) -> bool:
    """Identify verified Indian government domain suffixes and known portals."""
    domain = get_domain(url)
    if not domain:
        return False

    if domain in VERIFIED_OFFICIAL_PORTALS:
        return True

    for verified_host in VERIFIED_OFFICIAL_PORTALS:
        if domain == verified_host or domain.endswith("." + verified_host):
            return True

    return domain.endswith(GOVERNMENT_SUFFIXES)


def is_secondary_domain(url: str) -> bool:
    """Identify known secondary discovery domains."""
    domain = get_domain(url)
    if not domain:
        return False
    return any(
        domain == secondary or domain.endswith("." + secondary)
        for secondary in SECONDARY_DOMAINS
    )


def is_direct_application_link(url: str) -> bool:
    """Check if the URL path strongly indicates an interactive application/registration page."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        full_path = (parsed.path + "?" + parsed.query).lower()
        # Direct registration subdomains or query params
        return bool(APPLICATION_PATH_PATTERNS.search(full_path)) or (
            parsed.hostname and ("apply" in parsed.hostname.lower() or "beneficiary" in parsed.hostname.lower() or "register" in parsed.hostname.lower())
        )
    except Exception:
        return False


def verify_source(url: str, source_type: str = None) -> dict:
    """
    Classify source provenance and link type.
    Returns:
    - verification_status: human readable status string
    - source_authority: Registered government portal / Official government / Secondary / Unknown
    - is_official_domain: bool
    - is_application_portal: bool
    - link_type: "Direct Application Portal" | "Official Scheme Information Page" | "Secondary Source" | "Unverified"
    """
    if not url:
        return {
            "verification_status": "Source URL missing",
            "source_authority": "Unknown",
            "is_official_domain": False,
            "is_application_portal": False,
            "link_type": "Unverified",
        }

    is_official = is_indian_government_domain(url) or is_registered_domain(url)
    is_app_link = is_direct_application_link(url) and is_official

    if is_secondary_domain(url) or source_type == "secondary":
        return {
            "verification_status": "Secondary informational source",
            "source_authority": "Secondary",
            "is_official_domain": False,
            "is_application_portal": False,
            "link_type": "Secondary Source",
        }

    if is_app_link:
        return {
            "verification_status": "Verified Official Application / Registration Portal",
            "source_authority": "Official Government Portal",
            "is_official_domain": True,
            "is_application_portal": True,
            "link_type": "Direct Application Portal",
        }

    if is_official:
        return {
            "verification_status": "Verified Official Scheme Information Page",
            "source_authority": "Official Government Portal",
            "is_official_domain": True,
            "is_application_portal": False,
            "link_type": "Official Scheme Information Page",
        }

    return {
        "verification_status": "Unverified external source",
        "source_authority": "Unknown",
        "is_official_domain": False,
        "is_application_portal": False,
        "link_type": "Unverified",
    }


def verify_document(document: dict) -> dict:
    """Add provenance information to one collected document."""
    result = dict(document)
    verification = verify_source(
        result.get("url"),
        result.get("source_type"),
    )
    result.update(verification)
    result["scheme_details_verified"] = verification["is_official_domain"]
    return result


def verify_documents(documents: list[dict]) -> list[dict]:
    """Verify source provenance for a list of documents."""
    return [verify_document(doc) for doc in documents]
