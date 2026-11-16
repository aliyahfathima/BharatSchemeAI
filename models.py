
"""
BharatScheme AI - Pydantic Data Models
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl


# ---------------- ENUMS ----------------

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


class EmploymentStatus(str, Enum):
    EMPLOYED = "Employed"
    UNEMPLOYED = "Unemployed"
    SELF_EMPLOYED = "Self-Employed"
    STUDENT = "Student"
    RETIRED = "Retired"


class AreaType(str, Enum):
    URBAN = "Urban"
    RURAL = "Rural"
    SEMI_URBAN = "Semi-Urban"


class MatchStatus(str, Enum):
    POTENTIAL_MATCH = "Potential Match"
    POSSIBLE_MISMATCH = "Possible Mismatch"
    INSUFFICIENT_INFORMATION = "Insufficient Information"


# ---------------- USER PROFILE ----------------

class UserProfile(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=150)
    gender: Gender
    state: str = Field(min_length=1)
    category: Category
    annual_income: float = Field(ge=0)
    employment_status: EmploymentStatus
    area_type: AreaType

    is_differently_abled: bool = False
    education: Optional[str] = None
    occupation: Optional[str] = None


# ---------------- GOVERNMENT SCHEME ----------------

class GovernmentScheme(BaseModel):
    name: str
    ministry: str = "Not specified"
    description: str
    benefits: str
    eligibility_criteria: str
    how_to_apply: str

    official_link: Optional[str] = None
    source: Optional[str] = None


# ---------------- ELIGIBILITY RESULT ----------------

class EligibilityResult(BaseModel):
    scheme_name: str

    match_status: MatchStatus

    confidence: str = Field(
        description="High, Medium, or Low"
    )

    reason: str

    missing_information: list[str] = Field(
        default_factory=list
    )

    next_steps: Optional[str] = None


# ---------------- COMPLETE RESPONSE ----------------

class SchemeDiscoveryResponse(BaseModel):
    user_summary: str

    schemes: list[GovernmentScheme] = Field(
        default_factory=list
    )

    eligibility: list[EligibilityResult] = Field(
        default_factory=list
    )

    additional_tips: Optional[str] = None
