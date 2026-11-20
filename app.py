
from __future__ import annotations

import streamlit as st
from pathlib import Path

import config
from models import (
    UserProfile,
    Gender,
    Category,
    EmploymentStatus,
    AreaType,
    MatchStatus,
)
from search_service import search_schemes
from gemini_service import discover_and_analyse
from translations import LANGUAGES
from landing import show_landing_page
from scheme_browser import show_scheme_browser


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="BharatScheme AI",
    page_icon="🇮🇳",
    layout="wide",
)

# Load custom CSS
css_path = Path(__file__).parent / "assets" / "style.css"

if css_path.exists():
    st.markdown(
        f"<style>{css_path.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )


# ---------------- SESSION STATE ----------------

if "page" not in st.session_state:
    st.session_state.page = "home"

if "language" not in st.session_state:
    st.session_state.language = "English"


# ---------------- LANDING PAGE ----------------

if st.session_state.page == "home":

    if show_landing_page():
        st.session_state.page = "form"
        st.rerun()

    st.stop()


# ---------------- LANGUAGE SELECTION ----------------

language = st.selectbox(
    "🌐 Language / மொழி",
    list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(
        st.session_state.language
    ),
    key="language_selector",
)

st.session_state.language = language
t = LANGUAGES[language]


# ---------------- MAIN NAVIGATION ----------------

page_option = st.radio(
    "Choose Your Service",
    [
        "Find My Schemes",
        "Explore All Schemes",
    ],
    horizontal=True,
    key="main_navigation",
)

if page_option == "Explore All Schemes":

    show_scheme_browser(language)

    st.stop()


# ---------------- HEADER ----------------

st.title("BharatScheme AI")

st.subheader(
    "Discover Government Schemes Made for You"
)

st.caption(
    "An AI-powered guide to Central and State Government welfare schemes."
)

st.divider()


# ---------------- SIDEBAR ----------------

st.sidebar.markdown(
    """
    <div style="text-align:center;padding:15px 5px;">
        <div style="font-size:40px;">🇮🇳</div>
        <h2 style="color:white;">BharatScheme AI</h2>
        <p style="color:#dbe5f0;">
            Government Scheme Discovery Assistant
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")

st.sidebar.markdown(
    f"### 📌 {t['how_it_works']}"
)

st.sidebar.markdown(
    """
    1. Enter your citizen profile.
    2. Search government scheme information.
    3. Analyse eligibility using Gemini AI.
    4. Review benefits and application guidance.
    """
)

missing_keys = config.validate_keys()

if missing_keys:
    st.sidebar.error(
        "Missing API configuration: "
        + ", ".join(missing_keys)
    )
else:
    st.sidebar.success(
        "API configuration detected"
    )

st.sidebar.markdown("---")

st.sidebar.caption(
    "This prototype provides preliminary guidance. "
    "Always verify information through official government portals."
)


# ---------------- STATES AND UT ----------------

STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
]


# ---------------- PROFILE FORM ----------------

st.markdown(
    '<div class="feature-card">'
    '<h3>👤 Citizen Information</h3>'
    '<p>Provide your details to discover potentially relevant schemes.</p>'
    '</div>',
    unsafe_allow_html=True,
)

st.write("")

with st.form("profile_form"):

    st.header(f"📝 {t['profile']}")

    st.info(
        "Enter accurate details. Your name, Aadhaar number, OTP "
        "and bank details are not required."
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        age = st.number_input(
            t["age"],
            min_value=0,
            max_value=150,
            value=21,
            step=1,
        )

        gender = st.selectbox(
            t["gender"],
            [item.value for item in Gender],
        )

        state = st.selectbox(
            t["state"],
            STATES,
        )

    with col2:

        category = st.selectbox(
            t["category"],
            [item.value for item in Category],
        )

        annual_income = st.number_input(
            t["income"] + " (₹)",
            min_value=0,
            value=200000,
            step=10000,
        )

        employment = st.selectbox(
            t["employment"],
            [item.value for item in EmploymentStatus],
        )

    with col3:

        area = st.selectbox(
            t["area"],
            [item.value for item in AreaType],
        )

        differently_abled = st.checkbox(
            t["disability"]
        )

        education = st.text_input(
            t["education"],
            placeholder="Example: Graduate",
        )

        occupation = st.text_input(
            t["occupation"],
            placeholder="Example: Farmer",
        )

    # ---------------- SECTION: WHAT SUPPORT DO YOU NEED? ----------------
    st.markdown("---")
    st.markdown(
        """
        <div class="support-section-header">
            <h3>🎯 What Support Do You Need?</h3>
            <p>Select the benefit categories you want to explore. You can select multiple areas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    SUPPORT_CATEGORIES_DATA = [
        ("Education & Scholarships", "🎓"),
        ("Employment & Job Opportunities", "💼"),
        ("Self Employment & Business Loans", "🚀"),
        ("Women Empowerment", "👩‍👧"),
        ("Agriculture & Farmers Support", "🌾"),
        ("Housing & Home Loans", "🏠"),
        ("Healthcare & Medical Assistance", "🏥"),
        ("Pension & Old Age Support", "👵"),
        ("Disability Support", "♿"),
        ("Skill Development & Training", "🛠️"),
        ("Financial Assistance", "💰"),
        ("Food & Ration Benefits", "🍲"),
        ("Marriage Assistance", "💍"),
        ("Child & Family Welfare", "👨‍👩‍👧‍👦"),
        ("Other Government Benefits", "🏛️"),
    ]

    support_options = [cat[0] for cat in SUPPORT_CATEGORIES_DATA]
    support_icons = {cat[0]: cat[1] for cat in SUPPORT_CATEGORIES_DATA}

    selected_support_categories = st.pills(
        "Choose Support Categories:",
        options=support_options,
        format_func=lambda x: f"{support_icons.get(x, '📌')}  {x}",
        selection_mode="multi",
        default=[],
        key="support_category_pills",
        label_visibility="collapsed",
    )

    if selected_support_categories:
        st.markdown(
            f"""
            <div class="selection-summary-box">
                <strong>✓ Selected Support Categories ({len(selected_support_categories)}):</strong> {", ".join([f"{support_icons.get(c, '')} {c}" for c in selected_support_categories])}
            </div>
            """,
            unsafe_allow_html=True,
        )

    support_description = st.text_area(
        "Tell us more about the support you need (optional):",
        placeholder="Example: Looking for an engineering scholarship, or loan and subsidy to start a dairy farm.",
        max_chars=300,
        help="Optional: Share specific details so our AI can prioritize the most relevant schemes.",
        key="support_desc_input",
    )

    submitted = st.form_submit_button(
        "🔍 " + t["find"],
        use_container_width=True,
    )


# ---------------- PROCESSING ----------------

if submitted:

    if missing_keys:

        st.error(
            "Please configure your Gemini and Tavily API keys "
            "inside the .env file."
        )

        st.stop()

    try:

        profile = UserProfile(
            name="Citizen",
            age=int(age),
            gender=Gender(gender),
            state=state,
            category=Category(category),
            annual_income=float(annual_income),
            employment_status=EmploymentStatus(employment),
            area_type=AreaType(area),
            is_differently_abled=differently_abled,
            education=education.strip() or None,
            occupation=occupation.strip() or None,
            support_categories=list(selected_support_categories or []),
            support_description=support_description.strip() or None,
            is_farmer=True if ("farmer" in (occupation or "").lower() or "Agriculture & Farmers Support" in (selected_support_categories or [])) else None,
            is_student=True if ("student" in (occupation or "").lower() or "Education & Scholarships" in (selected_support_categories or [])) else None,
        )

    except Exception as exc:

        st.error(
            f"Profile validation failed: {exc}"
        )

        st.stop()

    # STEP 1: LIVE WEB SEARCH

    st.markdown("---")

    st.header("🌐 " + t["searching"])

    try:

        with st.status(
            t["searching"],
            expanded=True,
        ) as search_status:

            st.write(
                "Connecting to government scheme search..."
            )

            search_results = search_schemes(profile)

            if not search_results:

                search_status.update(
                    label="No relevant search results found.",
                    state="error",
                )

                st.warning(
                    "Try again with different profile details."
                )

                st.stop()

            search_status.update(
                label=f"Retrieved {len(search_results)} web sources.",
                state="complete",
                expanded=False,
            )

        st.success(
            f"Successfully retrieved {len(search_results)} web sources."
        )

    except Exception as exc:

        st.error(
            "Web search failed. Check your Tavily API key, "
            "internet connection and usage limits."
        )

        st.caption(str(exc))

        st.stop()

    # STEP 2: GEMINI AI ANALYSIS

    st.markdown("---")

    st.header("🤖 " + t["analysing"])

    try:

        with st.status(
            t["analysing"],
            expanded=True,
        ) as ai_status:

            st.write(
                "Comparing your profile with retrieved scheme information..."
            )

            result = discover_and_analyse(
                profile,
                search_results,
                language=language,
            )

            ai_status.update(
                label="AI analysis completed.",
                state="complete",
                expanded=False,
            )

    except Exception as exc:

        st.error(
            "AI analysis failed. Check your Gemini API key, "
            "model availability and API usage limits."
        )

        st.caption(str(exc))

        st.stop()

    # STEP 3: PROFILE SUMMARY

    st.markdown("---")

    st.header("📋 Profile Summary")

    st.write(result.user_summary)

    col1, col2, col3 = st.columns(3)

    col1.metric(t["age"], age)

    col2.metric(t["state"], state)

    col3.metric(
        t["income"],
        f"₹{annual_income:,.0f}",
    )

    if profile.support_categories:
        st.markdown(
            "**Targeted Support Categories:** "
            + " • ".join([f"`{c}`" for c in profile.support_categories])
        )

    if profile.support_description:
        st.caption(f"**Specific Need Mentioned:** *\"{profile.support_description}\"*")

    # STEP 4: SCHEME RESULTS

    st.markdown("---")

    st.header(
        f"🏛️ {t['results']} ({len(result.schemes)})"
    )

    if not result.schemes:

        st.warning(
            "No sufficiently supported scheme recommendations "
            "were found in the available search results."
        )

    status_icons = {
        MatchStatus.ELIGIBLE: "🟢",
        MatchStatus.POSSIBLY_ELIGIBLE: "🟡",
        MatchStatus.NOT_ELIGIBLE: "🔴",
        MatchStatus.INSUFFICIENT_INFORMATION: "⚪",
        # Backward compatibility
        MatchStatus.POTENTIAL_MATCH: "🟢",
        MatchStatus.POSSIBLE_MISMATCH: "🔴",
    }

    status_descriptions = {
        MatchStatus.ELIGIBLE:
            "Citizen profile satisfies verified eligibility conditions.",

        MatchStatus.POSSIBLY_ELIGIBLE:
            "Citizen likely meets primary criteria; specific document verification required.",

        MatchStatus.NOT_ELIGIBLE:
            "At least one condition (age, gender, state residency, or income) does not match.",

        MatchStatus.INSUFFICIENT_INFORMATION:
            "More information is needed to confirm eligibility.",

        MatchStatus.POTENTIAL_MATCH:
            "Citizen profile satisfies verified eligibility conditions.",

        MatchStatus.POSSIBLE_MISMATCH:
            "At least one known condition may not match.",
    }

    for index, scheme in enumerate(
        result.schemes,
        start=1,
    ):

        eligibility = next(
            (
                item for item in result.eligibility
                if item.scheme_name.strip().lower()
                == scheme.name.strip().lower()
            ),
            None,
        )

        match_status_enum = eligibility.match_status if eligibility else MatchStatus.INSUFFICIENT_INFORMATION
        icon = status_icons.get(match_status_enum, "ℹ️")
        level_tag = f"[{scheme.level.upper()}]" if scheme.level else ""
        category_tag = f"[{scheme.category}]" if scheme.category else ""
        heading = f"{icon} {index}. {scheme.name}  {level_tag} {category_tag}"

        with st.expander(
            heading,
            expanded=(index == 1),
        ):
            # Header info badges
            top_col1, top_col2 = st.columns([2, 1])
            with top_col1:
                st.markdown(f"**Ministry / Department:** {scheme.ministry}")
                if scheme.state:
                    st.caption(f"📍 State: **{scheme.state}**")
            with top_col2:
                if eligibility:
                    st.markdown(f"**Eligibility Status:** {icon} `{eligibility.match_status.value}`")

            # 1. Overview & Benefits
            st.markdown("### 📌 " + t["about"])
            st.write(scheme.description)

            st.markdown("### 🎁 " + t["benefits"])
            st.write(scheme.benefits)

            # 2. Eligibility Breakdown
            st.markdown("### ⚖️ " + t["eligibility"])
            st.write(scheme.eligibility_criteria)

            if eligibility:
                st.markdown("#### Citizen Eligibility Evaluation")
                st.info(f"**Assessment:** {status_descriptions.get(eligibility.match_status, '')}\n\n**Reason:** {eligibility.reason}")

                if eligibility.satisfied_conditions:
                    st.markdown("**✓ Conditions Satisfied:**")
                    for cond in eligibility.satisfied_conditions:
                        st.markdown(f"- 🟢 {cond}")

                if eligibility.unsatisfied_conditions:
                    st.markdown("**✗ Conditions Not Met:**")
                    for cond in eligibility.unsatisfied_conditions:
                        st.markdown(f"- 🔴 {cond}")

                if eligibility.missing_information:
                    st.markdown("**ℹ️ Information / Documents Still Required:**")
                    for item in eligibility.missing_information:
                        st.markdown(f"- ⚪ {item}")

                if eligibility.next_steps:
                    st.caption(f"👉 **Next Step:** {eligibility.next_steps}")

            # 3. Required Documents Checklist
            st.divider()
            st.markdown("### 📑 Required Documents Checklist")
            st.caption("Keep these genuine documents ready before starting your application:")

            if scheme.required_documents:
                for doc in scheme.required_documents:
                    badge = "🔴 Mandatory" if doc.is_mandatory else "🟡 Optional"
                    desc = f" — *{doc.purpose}*" if doc.purpose else ""
                    st.checkbox(f"**{doc.name}** ({badge}){desc}", value=False, key=f"doc_{index}_{doc.name[:20]}")
            elif scheme.documents_required:
                for doc_name in scheme.documents_required:
                    st.checkbox(f"**{doc_name}** (Mandatory / Verification proof)", value=False, key=f"doc_legacy_{index}_{doc_name[:20]}")
            else:
                st.info("Specific document list could not be verified from available evidence. Refer to the official portal.")

            # 4. How to Apply
            st.divider()
            st.markdown("### 🚀 " + t["apply"])

            if scheme.application_procedure and scheme.application_procedure.steps:
                st.markdown(f"**Application Mode:** `{scheme.application_procedure.mode}`")
                for s in scheme.application_procedure.steps:
                    st.markdown(f"**Step {s.step_number}: {s.title}**")
                    if s.description:
                        st.write(s.description)

                if scheme.application_procedure.tracking_method:
                    st.caption(f"🔍 **Tracking:** {scheme.application_procedure.tracking_method}")
            elif scheme.application_steps:
                for step_txt in scheme.application_steps:
                    st.markdown(f"- {step_txt}")
            elif scheme.how_to_apply:
                st.write(scheme.how_to_apply)
            else:
                st.write("Application procedure could not be confirmed from the collected evidence.")

            # 5. Direct Official Portal Link
            st.divider()
            st.markdown("### 🌐 Official Application Portal")

            btn_col1, btn_col2 = st.columns([1.5, 1])
            with btn_col1:
                if scheme.application_link:
                    st.link_button(
                        "🔗 APPLY NOW – OFFICIAL PORTAL",
                        scheme.application_link,
                        type="primary",
                        use_container_width=True,
                    )
                    st.caption(f"Verified Link: `{scheme.application_link}`")
                elif scheme.official_link:
                    st.link_button(
                        "🏛️ VISIT OFFICIAL SCHEME PORTAL",
                        scheme.official_link,
                        use_container_width=True,
                    )
                    st.caption("Direct registration form not verified. General official portal link provided.")
                else:
                    st.warning("Direct application form not verified from official sources.")

            with btn_col2:
                st.caption(f"**Link Classification:** {scheme.link_type}")
                st.caption(f"**Source Provenance:** {scheme.verification_status}")
                if scheme.source:
                    st.caption(f"[View Reference Source]({scheme.source})")

    # STEP 5: ADDITIONAL GUIDANCE

    if result.additional_tips:

        st.markdown("---")

        st.header("💡 Additional Guidance")

        st.info(result.additional_tips)

    # STEP 6: IMPORTANT REMINDER

    st.markdown("---")

    st.warning(
        "Important: BharatScheme AI provides preliminary information "
        "based on available web sources. Scheme rules can change. "
        "Verify eligibility, benefits, documents and application "
        "availability with the relevant official government department."
    )


# ---------------- FOOTER ----------------

st.markdown(
    """
    <div class="india-accent"></div>
    <div class="footer">
        <h3>🇮🇳 BharatScheme AI</h3>
        <p>Discover. Understand. Apply.</p>
        <p>Built with Python · Streamlit · Google Gemini · Tavily</p>
        <p>Independent prototype. Not an official Government of India portal.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
