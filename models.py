"""
BharatScheme AI - Data Models

Flexible beneficiary profiles and structured government scheme records.
Includes document checklists, step-by-step application guidance,
and direct official application portal models.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# -----------------------------
# ENUMS
# -----------------------------

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class Category(str, Enum):
    GENERAL = "General"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"
    NOT_APPLICABLE = "Not Applicable"
    NOT_PROVIDED = "Not Provided"


class EmploymentStatus(str, Enum):
    EMPLOYED = "Employed"
    UNEMPLOYED = "Unemployed"
    SELF_EMPLOYED = "Self-Employed"
    STUDENT = "Student"
    FARMER = "Farmer"
    RETIRED = "Retired"
    NOT_APPLICABLE = "Not Applicable"
    NOT_PROVIDED = "Not Provided"


class AreaType(str, Enum):
    URBAN = "Urban"
    RURAL = "Rural"
    SEMI_URBAN = "Semi-Urban"
    NOT_PROVIDED = "Not Provided"


class BeneficiaryType(str, Enum):
    CHILD = "Child"
    STUDENT = "Student"
    WOMAN = "Woman"
    FARMER = "Farmer"
    FAMILY = "Family"
    INDIVIDUAL = "Individual"
    SENIOR_CITIZEN = "Senior Citizen"
    ENTREPRENEUR = "Entrepreneur"
    PERSON_WITH_DISABILITY = "Person with Disability"
    OTHER = "Other"


class MatchStatus(str, Enum):
    ELIGIBLE = "Eligible"
    POSSIBLY_ELIGIBLE = "Possibly Eligible"
    NOT_ELIGIBLE = "Not Eligible"
    INSUFFICIENT_INFORMATION = "Insufficient Information"
    # Backward compatibility aliases
    POTENTIAL_MATCH = "Eligible"
    POSSIBLE_MISMATCH = "Not Eligible"

    @classmethod
    def from_str(cls, val: str) -> "MatchStatus":
        if not val:
            return cls.INSUFFICIENT_INFORMATION
        normalized = str(val).strip().lower()
        if "potential" in normalized or normalized == "eligible":
            return cls.ELIGIBLE
        if "possibly" in normalized or "partial" in normalized or "likely" in normalized:
            return cls.POSSIBLY_ELIGIBLE
        if "not" in normalized or "mismatch" in normalized or "ineligible" in normalized:
            return cls.NOT_ELIGIBLE
        return cls.INSUFFICIENT_INFORMATION


class SchemeLevel(str, Enum):
    CENTRAL = "Central"
    STATE = "State"
    CENTRAL_SPONSORED = "Centrally Sponsored"
    LOCAL = "Local"


# -----------------------------
# REQUIRED DOCUMENTS MODEL
# -----------------------------

class DocumentRequirement(BaseModel):
    """Specific document required to apply for a scheme."""
    name: str
    is_mandatory: bool = True
    purpose: str = ""
    description: str = ""


# -----------------------------
# APPLICATION PROCEDURE MODEL
# -----------------------------

class ApplicationStep(BaseModel):
    """Single step in the scheme application procedure."""
    step_number: int
    title: str
    description: str = ""


class ApplicationProcedure(BaseModel):
    """Structured step-by-step application instructions."""
    mode: str = "Online"  # "Online", "Offline", "Hybrid"
    portal_name: str = ""
    official_portal_url: Optional[str] = None
    direct_form_url: Optional[str] = None
    steps: list[ApplicationStep] = Field(default_factory=list)
    offline_authority: Optional[str] = None
    form_download_url: Optional[str] = None
    tracking_method: Optional[str] = None
    acknowledgement_info: Optional[str] = None


# -----------------------------
# BENEFICIARY PROFILE
# -----------------------------

class UserProfile(BaseModel):
    """
    Beneficiary profile for personalized scheme discovery.
    Missing information is never automatically treated as ineligible.
    Sensitive data (Aadhaar, bank numbers, OTPs) is NEVER collected.
    """
    name: Optional[str] = "Citizen"
    beneficiary_type: Optional[BeneficiaryType] = None

    # Section A: Basic Details
    age: Optional[int] = Field(default=None, ge=0, le=150)
    gender: Optional[Gender] = None
    state: Optional[str] = None
    district: Optional[str] = None

    # Section B: Social and Financial Details
    category: Optional[Category] = None
    annual_income: Optional[float] = Field(default=None, ge=0)
    family_income: Optional[float] = Field(default=None, ge=0)
    area_type: Optional[AreaType] = None
    is_differently_abled: Optional[bool] = None

    # Section C: Education and Employment
    education: Optional[str] = None
    occupation: Optional[str] = None
    employment_status: Optional[EmploymentStatus] = None
    is_student: Optional[bool] = None
    is_farmer: Optional[bool] = None

    # Section D: Support Needs
    support_categories: list[str] = Field(default_factory=list)
    support_description: Optional[str] = None

    # Section E: Additional Details (only if relevant)
    marital_status: Optional[str] = None
    minority_status: Optional[str] = None
    family_size: Optional[int] = Field(default=None, ge=1)
    land_ownership: Optional[str] = None
    additional_information: Optional[str] = None


# -----------------------------
# GOVERNMENT SCHEME
# -----------------------------

class GovernmentScheme(BaseModel):
    """Complete, verified government scheme representation."""
    name: str
    aliases: list[str] = Field(default_factory=list)
    ministry: str = "Not specified"
    department: str = "Not specified"

    description: str = ""
    benefits: str = ""
    eligibility_criteria: str = ""
    category: str = "General"  # Agriculture, Education, Health, Women, Social, etc.

    # Documents
    documents_required: list[str] = Field(default_factory=list)
    required_documents: list[DocumentRequirement] = Field(default_factory=list)

    # Application steps
    application_steps: list[str] = Field(default_factory=list)
    how_to_apply: str = ""
    application_procedure: Optional[ApplicationProcedure] = None

    # Geographic level
    level: str = "Central"  # Central or State
    state: Optional[str] = None
    district: Optional[str] = None

    # Verified Links
    official_link: Optional[str] = None
    application_link: Optional[str] = None
    has_direct_form: bool = False
    link_type: str = "Official Information Page"  # "Direct Application Portal", "Registration Form", "Official Information Page", "Unverified"
    is_application_link_verified: bool = False

    # Provenance
    source: Optional[str] = None
    source_urls: list[str] = Field(default_factory=list)
    verification_status: str = "Not verified"
    last_checked: Optional[str] = None


# -----------------------------
# ELIGIBILITY RESULT
# -----------------------------

class EligibilityResult(BaseModel):
    scheme_name: str
    match_status: MatchStatus
    confidence: str = "Medium"  # High, Medium, Low
    reason: str = ""
    satisfied_conditions: list[str] = Field(default_factory=list)
    unsatisfied_conditions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    next_steps: Optional[str] = None


# -----------------------------
# GEMINI RESPONSE
# -----------------------------

class SchemeDiscoveryResponse(BaseModel):
    user_summary: str = ""
    schemes: list[GovernmentScheme] = Field(default_factory=list)
    eligibility: list[EligibilityResult] = Field(default_factory=list)
    additional_tips: Optional[str] = None
