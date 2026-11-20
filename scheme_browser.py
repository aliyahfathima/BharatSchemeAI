
"""
BharatScheme AI - Scheme Browser

Provides:
1. Explore collected schemes
2. Search by scheme name or abbreviation
3. Browse by State / UT
"""

import streamlit as st

from scheme_catalogue import (
    get_all_documents,
    search_documents,
    get_catalogue_stats,
)

from search_service import search_schemes
from gemini_service import discover_and_analyse


def show_document_card(document):
    """Display a collected document with its source details."""

    with st.container(border=True):

        st.subheader(document.get("title", "Untitled scheme"))

        state = document.get("state") or "Central / Not specified"
        source = document.get("source_name") or "Unknown source"

        st.caption(f"{state}  |  {source}")

        content = document.get("content", "")

        if content:
            st.write(content[:700] + ("..." if len(content) > 700 else ""))

        url = document.get("url")

        if url:
            st.markdown(f"[View original source]({url})")

        st.caption(
            "Source status: Candidate document - scheme details "
            "not independently verified"
        )


def show_catalogue_statistics():
    """Display database collection statistics."""

    stats = get_catalogue_stats()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Collected documents",
        stats["total_documents"],
    )

    col2.metric(
        "Official-source documents",
        stats["official_documents"],
    )

    col3.metric(
        "States represented",
        stats["states_covered"],
    )


def show_explore_schemes():
    """Browse documents already collected."""

    st.subheader("Explore Government Schemes")

    st.write(
        "Browse information collected from registered government "
        "portals. You do not need to enter personal details."
    )

    show_catalogue_statistics()

    keyword = st.text_input(
        "Filter by scheme name or keyword",
        placeholder="Example: scholarship, pension, PM-KISAN",
        key="explore_keyword",
    )

    documents = (
        search_documents(keyword, limit=100)
        if keyword.strip()
        else get_all_documents(limit=100)
    )

    if not documents:
        st.info(
            "No collected documents found yet. Run the collection "
            "pipeline to populate the catalogue."
        )
        return

    st.write(f"Showing {len(documents)} collected documents.")

    for document in documents:
        show_document_card(document)


def show_scheme_name_search(language="English"):
    """Search for a specific scheme by name or abbreviation."""

    st.subheader("Search by Scheme Name")

    st.write(
        "Search for a scheme using its full name or abbreviation."
    )

    scheme_name = st.text_input(
        "Enter scheme name",
        placeholder="Example: PM-KISAN, SSY, PMAY, NSP",
        key="scheme_name_search",
    )

    if st.button(
        "Search Scheme",
        type="primary",
        key="search_scheme_button",
    ):

        if not scheme_name.strip():
            st.warning("Please enter a scheme name.")
            return

        with st.spinner("Searching official government sources..."):

            try:
                results = search_schemes(
                    profile=None,
                    scheme_name=scheme_name.strip(),
                )

                if not results:
                    st.warning(
                        "No matching source information was found. "
                        "Try another scheme name or abbreviation."
                    )
                    return

                st.success(
                    f"Found {len(results)} source results."
                )

                analysis = discover_and_analyse(
                    profile=None,
                    search_results=results,
                    language=language,
                    scheme_name=scheme_name.strip(),
                )

                st.subheader("AI Analysis")

                st.write(analysis.user_summary)

                for scheme in analysis.schemes:

                    with st.container(border=True):
                        st.subheader(scheme.name)

                        st.write(scheme.description)

                        st.markdown("**Benefits**")
                        st.write(scheme.benefits)

                        st.markdown("**Eligibility**")
                        st.write(scheme.eligibility_criteria)

                        st.markdown("**How to apply**")
                        st.write(scheme.how_to_apply)

                        st.caption(
                            f"Source verification: "
                            f"{scheme.verification_status}"
                        )

                        if scheme.official_link:
                            st.markdown(
                                f"[Official scheme source]"
                                f"({scheme.official_link})"
                            )

                if analysis.additional_tips:
                    st.info(analysis.additional_tips)

            except Exception as error:
                st.error(
                    f"Search failed: {error}"
                )


def show_state_explorer():
    """Browse the catalogue by State or Union Territory."""

    st.subheader("State / UT Explorer")

    states = [
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

    selected_state = st.selectbox(
        "Select State / Union Territory",
        states,
    )

    documents = search_documents(
        keyword="",
        state=selected_state,
        limit=100,
    )

    st.write(f"Collected documents for {selected_state}: {len(documents)}")

    if not documents:
        st.info(
            "No documents for this location have been collected yet. "
            "This does not mean that the State has no government schemes."
        )
        return

    for document in documents:
        show_document_card(document)


def show_scheme_browser(language="English"):
    """Main scheme browsing interface."""

    st.title("Government Scheme Explorer")

    st.write(
        "Discover government scheme information from collected "
        "official sources."
    )

    explore_tab, search_tab, state_tab = st.tabs([
        "Explore Schemes",
        "Search by Name",
        "State / UT Explorer",
    ])

    with explore_tab:
        show_explore_schemes()

    with search_tab:
        show_scheme_name_search(language)

    with state_tab:
        show_state_explorer()
