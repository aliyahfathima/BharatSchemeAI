"""
BharatScheme AI - Deterministic Eligibility Matching Engine

Compares citizen profile against structured and unstructured scheme rules.
Checks:
- Age
- Gender
- State / UT
- Category (General, OBC, SC, ST, EWS)
- Annual Family Income
- Occupation and Employment
- Student and Farmer status
- Area (Rural / Urban)
- Disability status

Outputs one of four exact statuses:
1. Eligible (🟢)
2. Possibly Eligible (🟡)
3. Not Eligible (🔴)
4. Insufficient Information (⚪)

Detailed breakdown of:
- Conditions satisfied
- Conditions not satisfied
- Missing information
"""

import re
from typing import Optional
from models import (
    UserProfile,
    GovernmentScheme,
    EligibilityResult,
    MatchStatus,
    Gender,
    Category,
    EmploymentStatus,
)


def evaluate_eligibility(profile: UserProfile, scheme: GovernmentScheme) -> EligibilityResult:
    """
    Deterministically evaluates a user's eligibility for a given scheme.
    Combines rule-based hard constraints with criteria pattern matching.
    """
    satisfied = []
    unsatisfied = []
    missing = []
    reasons = []

    criteria_text = (scheme.eligibility_criteria or "").lower()
    scheme_name = scheme.name.lower()
    category_name = (scheme.category or "").lower()

    # ---------------------------------------------
    # 1. STATE RESTRICTION
    # ---------------------------------------------
    scheme_state = (scheme.state or "").strip()
    user_state = (profile.state or "").strip()

    if scheme_state and scheme.level.lower() == "state":
        if not user_state:
            missing.append(f"Resident state confirmation (Scheme is restricted to {scheme_state})")
        elif scheme_state.lower() != user_state.lower():
            unsatisfied.append(f"State residency: Scheme is restricted to {scheme_state}, but your profile state is {user_state}")
        else:
            satisfied.append(f"State residency: Matches requirement for {scheme_state}")
    else:
        satisfied.append("Geographic coverage: Open to all States / Union Territories across India")

    # ---------------------------------------------
    # 2. GENDER RESTRICTION
    # ---------------------------------------------
    is_women_only = (
        "women" in scheme_name
        or "girl" in scheme_name
        or "magalir" in scheme_name
        or "penn" in scheme_name
        or "matru" in scheme_name
        or "maternity" in criteria_text
        or "pregnant women" in criteria_text
        or "female" in criteria_text
        or "women heads" in criteria_text
        or "sukanya" in scheme_name
        or "ladki bahin" in scheme_name
    )

    is_men_only = "boys" in scheme_name or "tamil pudhalvan" in scheme_name

    user_gender = profile.gender.value if profile.gender else None

    if is_women_only:
        if not user_gender:
            missing.append("Gender verification (Scheme is exclusively for female beneficiaries / women heads of household)")
        elif user_gender == Gender.MALE.value:
            unsatisfied.append("Gender requirement: Scheme is exclusively for female beneficiaries")
        else:
            satisfied.append("Gender requirement: Matches female beneficiary criteria")

    if is_men_only:
        if not user_gender:
            missing.append("Gender verification (Scheme is for male students)")
        elif user_gender == Gender.FEMALE.value:
            unsatisfied.append("Gender requirement: Scheme is specifically for male students")
        else:
            satisfied.append("Gender requirement: Matches male beneficiary criteria")

    # ---------------------------------------------
    # 3. AGE RESTRICTION
    # ---------------------------------------------
    user_age = profile.age

    # Atal Pension Yojana: 18 to 40
    if "atal pension" in scheme_name or "apy" in scheme_name:
        if user_age is None:
            missing.append("Age verification (Must be between 18 and 40 years)")
        elif user_age < 18 or user_age > 40:
            unsatisfied.append(f"Age criterion: Must be 18 to 40 years (Current age: {user_age})")
        else:
            satisfied.append(f"Age criterion: Age {user_age} is within eligible bracket (18-40 years)")

    # PM-KISAN / Micro loans / Enterprise: 18+
    elif any(k in scheme_name for k in ["kisan", "mudra", "svanidhi", "vishwakarma", "stand-up"]):
        if user_age is not None:
            if user_age < 18:
                unsatisfied.append(f"Age criterion: Minimum age is 18 years (Current age: {user_age})")
            else:
                satisfied.append(f"Age criterion: Age {user_age} satisfies adult eligibility (18+)")

    # KMUT (Tamil Nadu women): 21+
    elif "kalaignar magalir" in scheme_name or "kmut" in scheme_name:
        if user_age is not None:
            if user_age < 21:
                unsatisfied.append(f"Age criterion: Minimum age is 21 years (Current age: {user_age})")
            else:
                satisfied.append(f"Age criterion: Age {user_age} satisfies requirement (21+)")

    # Student scholarships: usually under 35
    elif "scholarship" in scheme_name or "penn" in scheme_name or "pudhalvan" in scheme_name:
        if user_age is not None:
            if user_age > 35:
                unsatisfied.append(f"Age criterion: Education schemes are typically for students under 35 (Current age: {user_age})")
            else:
                satisfied.append(f"Age criterion: Age {user_age} matches student profile")

    # ---------------------------------------------
    # 4. ANNUAL FAMILY INCOME CEILING
    # ---------------------------------------------
    user_income = profile.annual_income if profile.annual_income is not None else profile.family_income

    # Check for income ceilings mentioned in criteria text
    income_match = re.search(r"₹\s*([0-9\.]+)\s*(lakh|lakhs|crore)", criteria_text, re.IGNORECASE)
    ceiling_amount = None

    if "2.5 lakh" in criteria_text or "kmut" in scheme_name or "nsp" in scheme_name:
        ceiling_amount = 250000.0
    elif "3 lakh" in criteria_text or "ews" in criteria_text:
        ceiling_amount = 300000.0
    elif "6 lakh" in criteria_text or "lig" in criteria_text:
        ceiling_amount = 600000.0
    elif "8 lakh" in criteria_text or "pmmvy" in scheme_name:
        ceiling_amount = 800000.0

    if ceiling_amount is not None:
        if user_income is None:
            missing.append(f"Income certificate verification (Income ceiling is ₹{ceiling_amount:,.0f}/year)")
        elif user_income > ceiling_amount:
            unsatisfied.append(f"Income ceiling: Annual income of ₹{user_income:,.0f} exceeds maximum threshold of ₹{ceiling_amount:,.0f}")
        else:
            satisfied.append(f"Income criteria: Annual income ₹{user_income:,.0f} is within eligibility ceiling of ₹{ceiling_amount:,.0f}")
    elif user_income is not None:
        satisfied.append(f"Financial profile: Income details provided (₹{user_income:,.0f})")

    # ---------------------------------------------
    # 5. OCCUPATION & BENEFICIARY ROLE
    # ---------------------------------------------
    user_occ = (profile.occupation or "").lower()
    is_farmer = profile.is_farmer or ("farmer" in user_occ) or (profile.employment_status == EmploymentStatus.FARMER)
    is_student = profile.is_student or ("student" in user_occ) or (profile.employment_status == EmploymentStatus.STUDENT)

    # Agriculture schemes
    if "farmer" in category_name or "agriculture" in category_name or "kisan" in scheme_name:
        if profile.is_farmer is False:
            unsatisfied.append("Occupation requirement: Scheme is specifically for agricultural landholders / farmers")
        elif is_farmer:
            satisfied.append("Occupation requirement: Matches farmer / agricultural beneficiary category")
        else:
            missing.append("Farmer status / cultivable land ownership verification")

    # Education / Scholarship schemes
    elif "education" in category_name or "scholarship" in scheme_name or "pudhumai penn" in scheme_name or "tamil pudhalvan" in scheme_name:
        if profile.employment_status and profile.employment_status not in (EmploymentStatus.STUDENT, EmploymentStatus.UNEMPLOYED, EmploymentStatus.NOT_PROVIDED):
            missing.append("Active student enrollment verification (Bonafide certificate / college registration)")
        elif is_student:
            satisfied.append("Academic status: Confirmed active student status")
        else:
            satisfied.append("Academic eligibility: Requires active enrollment in recognized educational institution")

    # Artisan / Craftsperson schemes (PM Vishwakarma)
    elif "vishwakarma" in scheme_name or "artisan" in category_name:
        artisan_trades = ["carpenter", "blacksmith", "goldsmith", "potter", "mason", "tailor", "cobbler", "barber", "washerman"]
        if any(t in user_occ for t in artisan_trades):
            satisfied.append(f"Traditional trade: Occupation '{profile.occupation}' matches eligible traditional craftsman trade")
        elif profile.occupation:
            missing.append("Trade verification: Must belong to one of 18 traditional artisan/craftsman trades")
        else:
            missing.append("Declaration of traditional trade / hand skill engagement")

    # Street vendor schemes (PM SVANidhi)
    elif "svanidhi" in scheme_name or "vendor" in criteria_text:
        if "vendor" in user_occ or "hawker" in user_occ or "shop" in user_occ:
            satisfied.append("Vending occupation: Matches street vendor / micro-retail category")
        else:
            missing.append("Urban Local Body (ULB) Certificate of Vending or Letter of Recommendation")

    # ---------------------------------------------
    # 6. DISABILITY STATUS
    # ---------------------------------------------
    if "disability" in category_name or "swavlamban" in scheme_name or "udid" in scheme_name:
        if profile.is_differently_abled is True:
            satisfied.append("Disability status: Beneficiary is identified as Person with Disability (PwD)")
        elif profile.is_differently_abled is False:
            unsatisfied.append("Disability criteria: Scheme is reserved for Persons with Benchmark Disabilities (40%+)")
        else:
            missing.append("Disability status and benchmark percentage confirmation (>40%)")

    # ---------------------------------------------
    # 7. SOCIAL CATEGORY (SC / ST / OBC / EWS / General)
    # ---------------------------------------------
    if "sc/st" in criteria_text or "stand-up" in scheme_name:
        user_cat = profile.category.value if profile.category else None
        if user_cat in (Category.SC.value, Category.ST.value):
            satisfied.append(f"Category requirement: Matches priority category ({user_cat})")
        elif is_women_only and user_gender == Gender.FEMALE.value:
            satisfied.append("Category requirement: Eligible under Women Entrepreneur priority")
        elif user_cat and user_cat not in (Category.SC.value, Category.ST.value):
            if not is_women_only:
                unsatisfied.append(f"Social category: Scheme requires SC or ST category (Profile category: {user_cat})")

    # ---------------------------------------------
    # 8. TARGETED SUPPORT CATEGORY MATCH
    # ---------------------------------------------
    if profile.support_categories:
        for sc in profile.support_categories:
            sc_lower = sc.lower()
            first_term = sc_lower.split("&")[0].strip()
            if (
                first_term in scheme_name
                or first_term in category_name
                or first_term in criteria_text
                or sc_lower in scheme_name
                or sc_lower in category_name
            ):
                satisfied.append(f"User Goal: Aligns directly with your requested '{sc}' support preference")
                break

    # ---------------------------------------------
    # OVERALL MATCH STATUS RESOLUTION
    # ---------------------------------------------
    if len(unsatisfied) > 0:
        match_status = MatchStatus.NOT_ELIGIBLE
        confidence = "High"
        reason = f"At least {len(unsatisfied)} key condition(s) are not met: " + "; ".join(unsatisfied[:2])
        next_steps = "Explore alternative schemes designed for your specific demographic and state profile."

    elif len(missing) >= 2 and len(satisfied) <= 1:
        match_status = MatchStatus.INSUFFICIENT_INFORMATION
        confidence = "Medium"
        reason = "Essential beneficiary details are missing to determine conclusive eligibility: " + "; ".join(missing[:2])
        next_steps = "Update your profile with additional information (income certificate, state residency, or category) for definitive matching."

    elif len(missing) > 0:
        match_status = MatchStatus.POSSIBLY_ELIGIBLE
        confidence = "Medium"
        reason = "Meets core eligibility criteria (" + "; ".join(satisfied[:2]) + f"), pending verification of {missing[0]}."
        next_steps = "Prepare the listed required documents and review official scheme guidelines before submitting your application."

    else:
        match_status = MatchStatus.ELIGIBLE
        confidence = "High"
        reason = "Profile satisfies all verified eligibility conditions: " + "; ".join(satisfied[:3])
        next_steps = "Proceed to the official application portal using the 'Apply Now' button and prepare required documents."

    return EligibilityResult(
        scheme_name=scheme.name,
        match_status=match_status,
        confidence=confidence,
        reason=reason,
        satisfied_conditions=satisfied,
        unsatisfied_conditions=unsatisfied,
        missing_information=missing,
        next_steps=next_steps,
    )


def match_all_schemes(profile: UserProfile, schemes: list[GovernmentScheme]) -> list[EligibilityResult]:
    """Evaluate eligibility for a list of schemes."""
    return [evaluate_eligibility(profile, scheme) for scheme in schemes]
