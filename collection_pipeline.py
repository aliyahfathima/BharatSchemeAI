
"""
BharatScheme AI - Collection Pipeline

Runs source discovery, document extraction and database storage.
"""

from source_registry import get_official_sources
from source_discovery import discover_scheme_links
from scheme_collector import collect_scheme_content
from scheme_catalogue import save_documents, get_catalogue_stats


def run_collection(
    selected_state=None,
    max_links_per_source=20,
    max_documents=50,
):
    """Collect and save documents from registered official sources."""

    sources = get_official_sources()

    if selected_state:
        sources = [
            source for source in sources
            if source.get("level") == "Central"
            or source.get("state", "").lower() == selected_state.lower()
        ]

    print("=" * 55)
    print("BHARATSCHEME AI - COLLECTION STARTED")
    print("=" * 55)
    print("Sources selected:", len(sources))

    all_links = []
    seen_urls = set()

    # Stage 1: Discover candidate scheme pages.
    for source in sources:
        print("\nDiscovering:", source["name"])

        links = discover_scheme_links(
            source,
            max_links=max_links_per_source,
        )

        for link in links:
            if link["url"] not in seen_urls:
                seen_urls.add(link["url"])
                all_links.append(link)

        print("Candidate links found:", len(links))

    print("\nTotal unique candidate links:", len(all_links))

    # Stage 2: Extract document content.
    print("\nExtracting document content...")

    documents = collect_scheme_content(
        all_links,
        max_documents=max_documents,
    )

    print("Documents extracted:", len(documents))

    # Stage 3: Save documents into SQLite.
    print("\nSaving documents to database...")

    saved = save_documents(documents)

    # Stage 4: Display catalogue statistics.
    stats = get_catalogue_stats()

    print("\n" + "=" * 55)
    print("COLLECTION COMPLETED")
    print("=" * 55)
    print("Documents processed:", len(documents))
    print("Records saved or updated:", saved)
    print("Total catalogue documents:", stats["total_documents"])
    print("Official-source documents:", stats["official_documents"])
    print("States represented:", stats["states_covered"])
    print("PDF documents:", stats["pdf_documents"])

    return {
        "sources_selected": len(sources),
        "candidate_links": len(all_links),
        "documents_extracted": len(documents),
        "records_saved": saved,
        "statistics": stats,
    }


if __name__ == "__main__":
    run_collection(
        selected_state="Tamil Nadu",
        max_links_per_source=10,
        max_documents=15,
    )
