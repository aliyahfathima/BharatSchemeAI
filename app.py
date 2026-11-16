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


# ---------------- PAGE NAVIGATION ----------------

if "page" not in st.session_state:
    st.session_state.page = "home"

if "language" not in st.session_state:
    st.session_state.language = "English"

if st.session_state.page == "home":
    language = st.session_state.language
    t = LANGUAGES[language]

    if show_landing_page():
        st.session_state.page = "form"
        st.rerun()

    st.stop()

# ---------------- LANGUAGE SELECTION ----------------

if "language" not in st.session_state:
    st.session_state.language = "English"

language = st.selectbox(
    "🌐 Language / மொழி",
    list(LANGUAGES.keys()),
    index=list(LANGUAGES.keys()).index(st.session_state.language),
    key="language_selector",
)

st.session_state.language = language
t = LANGUAGES[language]


# ---------------- HEADER ----------------

st.title("BharatScheme AI")
st.subheader("Discover Government Schemes Made for You")
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
        <p style="color:#dbe5f0;">Government Scheme Discovery Assistant</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"### 📌 {t['how_it_works']}")
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
    st.sidebar.error("Missing API configuration: " + ", ".join(missing_keys))
else:
    st.sidebar.success("API configuration detected")

st.sidebar.markdown("---")
st.sidebar.caption(
    "This prototype provides preliminary guidance. "
    "Always verify information through official government portals."
)


# ---------------- STATES AND UT ----------------

STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
    "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]


# ---------------- PROFILE FORM ----------------

st.markdown(
    '<div class="feature-card"><h3>👤 Citizen Information</h3>'
    '<p>Provide your details to discover potentially relevant schemes.</p></div>',
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
            t["age"], min_value=0, max_value=150, value=21, step=1
        )

        gender = st.selectbox(
            t["gender"], [item.value for item in Gender]
        )

        state = st.selectbox(
            t["state"], STATES
        )

    with col2:
        category = st.selectbox(
            t["category"], [item.value for item in Category]
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
            t["area"], [item.value for item in AreaType]
        )

        differently_abled = st.checkbox(t["disability"])

        education = st.text_input(
            t["education"],
            placeholder="Example: Graduate",
        )

        occupation = st.text_input(
            t["occupation"],
            placeholder="Example: Farmer",
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
        )

    except Exception as exc:
        st.error(f"Profile validation failed: {exc}")
        st.stop()

    # STEP 1: LIVE WEB SEARCH

    st.markdown("---")
    st.header("🌐 " + t["searching"])

    try:
        with st.status(
            t["searching"],
            expanded=True,
        ) as search_status:

            st.write("Connecting to government scheme search...")
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

            st.write("Comparing your profile with retrieved scheme information...")
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
    col3.metric(t["income"], f"₹{annual_income:,.0f}")

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
        MatchStatus.POTENTIAL_MATCH: "🟢",
        MatchStatus.POSSIBLE_MISMATCH: "🔴",
        MatchStatus.INSUFFICIENT_INFORMATION: "🟡",
    }

    status_descriptions = {
        MatchStatus.POTENTIAL_MATCH:
            "Available evidence suggests a potential match.",
        MatchStatus.POSSIBLE_MISMATCH:
            "At least one known condition may not match.",
        MatchStatus.INSUFFICIENT_INFORMATION:
            "More information is needed to assess eligibility.",
    }

    for index, scheme in enumerate(result.schemes, start=1):

        eligibility = next(
            (
                item for item in result.eligibility
                if item.scheme_name.strip().lower()
                == scheme.name.strip().lower()
            ),
            None,
        )

        if eligibility:
            icon = status_icons.get(
                eligibility.match_status, "ℹ️"
            )
            heading = f"{icon} {index}. {scheme.name}"
        else:
            heading = f"ℹ️ {index}. {scheme.name}"

        with st.expander(heading, expanded=False):

            st.markdown(
                f"**Ministry / Department:** {scheme.ministry}"
            )

            st.markdown("### " + t["about"])
            st.write(scheme.description)

            st.markdown("### " + t["benefits"])
            st.write(scheme.benefits)

            st.markdown("### " + t["eligibility"])
            st.write(scheme.eligibility_criteria)

            st.markdown("### " + t["apply"])
            st.write(scheme.how_to_apply)

            if scheme.official_link:
                st.markdown("### Official Government Link")
                st.markdown(
                    f"[Visit Official Portal]({scheme.official_link})"
                )

            if scheme.source:
                st.markdown("### Source")
                st.markdown(f"[View Source]({scheme.source})")

            if eligibility:
                st.divider()
                st.markdown("### Your Eligibility Assessment")

                st.subheader(
                    f"{status_icons.get(eligibility.match_status, 'ℹ️')} "
                    f"{eligibility.match_status.value}"
                )

                st.write(
                    status_descriptions.get(
                        eligibility.match_status, ""
                    )
                )

                st.markdown(
                    f"**Confidence:** {eligibility.confidence}"
                )

                st.markdown("**Reason:**")
                st.write(eligibility.reason)

                if eligibility.missing_information:
                    st.markdown("**Information still required:**")
                    for item in eligibility.missing_information:
                        st.write(f"- {item}")

                if eligibility.next_steps:
                    st.markdown("**Recommended Next Steps:**")
                    st.write(eligibility.next_steps)

            else:
                st.info(
                    "An individual eligibility assessment "
                    "was not returned for this scheme."
                )

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

