"""
BharatScheme AI - SQLite Scheme Catalogue

Stores extracted government scheme documents and structured verified schemes
for instant search, reuse, and offline resiliency.
Preserves existing database records while adding full structured scheme support.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

from models import GovernmentScheme, DocumentRequirement, ApplicationProcedure, ApplicationStep

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "bharatscheme.db"


def get_connection():
    """Create a database connection."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create tables and indexes if they do not exist."""
    with get_connection() as connection:
        # 1. Existing scheme documents table (preserved)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scheme_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                parent_url TEXT,
                source_name TEXT,
                source_type TEXT DEFAULT 'unknown',
                level TEXT,
                state TEXT,
                content_type TEXT,
                content TEXT,
                extraction_status TEXT,
                discovery_status TEXT,
                first_collected TEXT,
                last_collected TEXT
            )
        """)

        connection.execute("CREATE INDEX IF NOT EXISTS idx_scheme_state ON scheme_documents(state)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_scheme_source_type ON scheme_documents(source_type)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_scheme_title ON scheme_documents(title)")

        # 2. Enhanced verified schemes table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS verified_schemes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                aliases_json TEXT,
                ministry TEXT,
                department TEXT,
                description TEXT,
                benefits TEXT,
                eligibility_criteria TEXT,
                category TEXT,
                level TEXT,
                state TEXT,
                district TEXT,
                documents_required_json TEXT,
                required_documents_json TEXT,
                application_steps_json TEXT,
                how_to_apply TEXT,
                application_procedure_json TEXT,
                official_link TEXT,
                application_link TEXT,
                has_direct_form INTEGER DEFAULT 0,
                link_type TEXT,
                is_application_link_verified INTEGER DEFAULT 0,
                source TEXT,
                source_urls_json TEXT,
                verification_status TEXT,
                last_checked TEXT
            )
        """)

        connection.execute("CREATE INDEX IF NOT EXISTS idx_verified_name ON verified_schemes(name)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_verified_category ON verified_schemes(category)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_verified_state ON verified_schemes(state)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_verified_level ON verified_schemes(level)")

        connection.commit()

    # Seed verified schemes if empty
    seed_verified_schemes_if_needed()


def seed_verified_schemes_if_needed():
    """Populate verified schemes from curated_data if table is empty."""
    try:
        from curated_data import VERIFIED_SCHEMES_LIST
        with get_connection() as connection:
            count = connection.execute("SELECT COUNT(*) FROM verified_schemes").fetchone()[0]
            if count == 0:
                for scheme in VERIFIED_SCHEMES_LIST:
                    save_verified_scheme(scheme, connection=connection)
                connection.commit()
    except Exception as error:
        print(f"Verified schemes seeding notice: {error}")


def scheme_to_db_dict(scheme: GovernmentScheme) -> dict:
    """Serialize a GovernmentScheme object for SQLite storage."""
    req_docs_json = json.dumps([d.model_dump() for d in scheme.required_documents], ensure_ascii=False) if scheme.required_documents else "[]"
    app_proc_json = json.dumps(scheme.application_procedure.model_dump(), ensure_ascii=False) if scheme.application_procedure else "{}"
    return {
        "name": scheme.name,
        "aliases_json": json.dumps(scheme.aliases, ensure_ascii=False),
        "ministry": scheme.ministry,
        "department": scheme.department,
        "description": scheme.description,
        "benefits": scheme.benefits,
        "eligibility_criteria": scheme.eligibility_criteria,
        "category": scheme.category or "General",
        "level": scheme.level or "Central",
        "state": scheme.state,
        "district": scheme.district,
        "documents_required_json": json.dumps(scheme.documents_required, ensure_ascii=False),
        "required_documents_json": req_docs_json,
        "application_steps_json": json.dumps(scheme.application_steps, ensure_ascii=False),
        "how_to_apply": scheme.how_to_apply,
        "application_procedure_json": app_proc_json,
        "official_link": scheme.official_link,
        "application_link": scheme.application_link,
        "has_direct_form": 1 if scheme.has_direct_form else 0,
        "link_type": scheme.link_type,
        "is_application_link_verified": 1 if scheme.is_application_link_verified else 0,
        "source": scheme.source,
        "source_urls_json": json.dumps(scheme.source_urls, ensure_ascii=False),
        "verification_status": scheme.verification_status,
        "last_checked": scheme.last_checked or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def row_to_government_scheme(row) -> GovernmentScheme:
    """Deserialize a SQLite Row to GovernmentScheme."""
    r = dict(row)

    # Documents required
    documents_required = []
    if r.get("documents_required_json"):
        try:
            documents_required = json.loads(r["documents_required_json"])
        except Exception:
            pass

    # Structured documents
    required_documents = []
    if r.get("required_documents_json"):
        try:
            raw_docs = json.loads(r["required_documents_json"])
            required_documents = [DocumentRequirement(**d) for d in raw_docs]
        except Exception:
            pass

    # Application steps
    application_steps = []
    if r.get("application_steps_json"):
        try:
            application_steps = json.loads(r["application_steps_json"])
        except Exception:
            pass

    # Application procedure
    application_procedure = None
    if r.get("application_procedure_json"):
        try:
            raw_proc = json.loads(r["application_procedure_json"])
            if raw_proc and raw_proc.get("steps"):
                steps = [ApplicationStep(**s) for s in raw_proc.get("steps", [])]
                raw_proc["steps"] = steps
                application_procedure = ApplicationProcedure(**raw_proc)
        except Exception:
            pass

    # Aliases
    aliases = []
    if r.get("aliases_json"):
        try:
            aliases = json.loads(r["aliases_json"])
        except Exception:
            pass

    # Source URLs
    source_urls = []
    if r.get("source_urls_json"):
        try:
            source_urls = json.loads(r["source_urls_json"])
        except Exception:
            pass

    return GovernmentScheme(
        name=r.get("name") or "Unnamed Scheme",
        aliases=aliases,
        ministry=r.get("ministry") or "Not specified",
        department=r.get("department") or "Not specified",
        description=r.get("description") or "",
        benefits=r.get("benefits") or "",
        eligibility_criteria=r.get("eligibility_criteria") or "",
        category=r.get("category") or "General",
        documents_required=documents_required,
        required_documents=required_documents,
        application_steps=application_steps,
        how_to_apply=r.get("how_to_apply") or "",
        application_procedure=application_procedure,
        level=r.get("level") or "Central",
        state=r.get("state"),
        district=r.get("district"),
        official_link=r.get("official_link"),
        application_link=r.get("application_link"),
        has_direct_form=bool(r.get("has_direct_form")),
        link_type=r.get("link_type") or "Official Information Page",
        is_application_link_verified=bool(r.get("is_application_link_verified")),
        source=r.get("source"),
        source_urls=source_urls,
        verification_status=r.get("verification_status") or "Verified Official",
        last_checked=r.get("last_checked"),
    )


def save_verified_scheme(scheme: GovernmentScheme, connection=None):
    """Save or update a verified scheme in the database."""
    data = scheme_to_db_dict(scheme)
    query = """
        INSERT INTO verified_schemes (
            name, aliases_json, ministry, department, description, benefits,
            eligibility_criteria, category, level, state, district,
            documents_required_json, required_documents_json, application_steps_json,
            how_to_apply, application_procedure_json, official_link, application_link,
            has_direct_form, link_type, is_application_link_verified,
            source, source_urls_json, verification_status, last_checked
        )
        VALUES (
            :name, :aliases_json, :ministry, :department, :description, :benefits,
            :eligibility_criteria, :category, :level, :state, :district,
            :documents_required_json, :required_documents_json, :application_steps_json,
            :how_to_apply, :application_procedure_json, :official_link, :application_link,
            :has_direct_form, :link_type, :is_application_link_verified,
            :source, :source_urls_json, :verification_status, :last_checked
        )
        ON CONFLICT(name) DO UPDATE SET
            aliases_json = excluded.aliases_json,
            ministry = excluded.ministry,
            department = excluded.department,
            description = excluded.description,
            benefits = excluded.benefits,
            eligibility_criteria = excluded.eligibility_criteria,
            category = excluded.category,
            level = excluded.level,
            state = excluded.state,
            district = excluded.district,
            documents_required_json = excluded.documents_required_json,
            required_documents_json = excluded.required_documents_json,
            application_steps_json = excluded.application_steps_json,
            how_to_apply = excluded.how_to_apply,
            application_procedure_json = excluded.application_procedure_json,
            official_link = excluded.official_link,
            application_link = excluded.application_link,
            has_direct_form = excluded.has_direct_form,
            link_type = excluded.link_type,
            is_application_link_verified = excluded.is_application_link_verified,
            source = excluded.source,
            source_urls_json = excluded.source_urls_json,
            verification_status = excluded.verification_status,
            last_checked = excluded.last_checked
    """
    if connection:
        connection.execute(query, data)
    else:
        with get_connection() as conn:
            conn.execute(query, data)
            conn.commit()


def search_verified_schemes(keyword=None, state=None, category=None, limit=20) -> list[GovernmentScheme]:
    """Search verified structured schemes by keyword, state, and category."""
    initialize_database()

    query = "SELECT * FROM verified_schemes WHERE 1=1"
    params = []

    if state:
        # Match central schemes (state is null or empty) OR schemes for this specific state
        query += " AND (state IS NULL OR state = '' OR state = ?)"
        params.append(state)

    if category:
        query += " AND (category LIKE ?)"
        params.append(f"%{category.strip()}%")

    if keyword and keyword.strip():
        kw = f"%{keyword.strip()}%"
        query += " AND (name LIKE ? OR aliases_json LIKE ? OR description LIKE ? OR benefits LIKE ? OR eligibility_criteria LIKE ?)"
        params.extend([kw, kw, kw, kw, kw])

    query += " ORDER BY level ASC, name ASC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [row_to_government_scheme(row) for row in rows]


def get_all_verified_schemes(limit=100) -> list[GovernmentScheme]:
    """Retrieve all verified schemes."""
    initialize_database()
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM verified_schemes ORDER BY level ASC, name ASC LIMIT ?", (limit,)).fetchall()
    return [row_to_government_scheme(row) for row in rows]


# ---------------------------------------------
# RAW DOCUMENT STORAGE (PRESERVED FOR BACKWARD COMPATIBILITY)
# ---------------------------------------------

def save_documents(documents):
    """
    Save extracted documents to raw scheme_documents table.
    Preserves existing functionality without breaking callers.
    """
    if not documents:
        return 0

    now = datetime.now(timezone.utc).isoformat()
    saved_count = 0
    initialize_database()

    with get_connection() as connection:
        for document in documents:
            url = document.get("url", "").strip()
            if not url:
                continue

            connection.execute("""
                INSERT INTO scheme_documents (
                    title, url, parent_url, source_name, source_type,
                    level, state, content_type, content, extraction_status,
                    discovery_status, first_collected, last_collected
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    parent_url = excluded.parent_url,
                    source_name = excluded.source_name,
                    source_type = excluded.source_type,
                    level = excluded.level,
                    state = excluded.state,
                    content_type = excluded.content_type,
                    content = excluded.content,
                    extraction_status = excluded.extraction_status,
                    discovery_status = excluded.discovery_status,
                    last_collected = excluded.last_collected
            """, (
                document.get("title", "Untitled"),
                url,
                document.get("parent_url"),
                document.get("source_name"),
                document.get("source_type", "unknown"),
                document.get("level"),
                document.get("state"),
                document.get("content_type"),
                document.get("content", ""),
                document.get("extraction_status", "Unknown"),
                document.get("discovery_status", "Candidate - not yet verified"),
                now,
                now,
            ))
            saved_count += 1
        connection.commit()

    return saved_count


def search_documents(keyword, state=None, limit=50):
    """Search saved raw documents by title or extracted content."""
    initialize_database()
    keyword = f"%{keyword.strip()}%"

    query = """
        SELECT *
        FROM scheme_documents
        WHERE (title LIKE ? OR content LIKE ?)
    """
    parameters = [keyword, keyword]

    if state:
        query += " AND (state = ? OR state IS NULL)"
        parameters.append(state)

    query += " ORDER BY last_collected DESC LIMIT ?"
    parameters.append(limit)

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


def get_all_documents(limit=500):
    """Return recently collected raw documents."""
    initialize_database()
    with get_connection() as connection:
        rows = connection.execute("""
            SELECT *
            FROM scheme_documents
            ORDER BY last_collected DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [dict(row) for row in rows]


def get_catalogue_stats():
    """Return combined catalogue statistics."""
    initialize_database()
    with get_connection() as connection:
        total_docs = connection.execute("SELECT COUNT(*) FROM scheme_documents").fetchone()[0]
        official_docs = connection.execute("SELECT COUNT(*) FROM scheme_documents WHERE source_type = 'official'").fetchone()[0]
        states_covered = connection.execute("SELECT COUNT(DISTINCT state) FROM scheme_documents WHERE state IS NOT NULL AND state != ''").fetchone()[0]
        pdfs = connection.execute("SELECT COUNT(*) FROM scheme_documents WHERE content_type = 'PDF'").fetchone()[0]

        total_verified = connection.execute("SELECT COUNT(*) FROM verified_schemes").fetchone()[0]
        verified_with_direct_links = connection.execute("SELECT COUNT(*) FROM verified_schemes WHERE has_direct_form = 1").fetchone()[0]

    return {
        "total_documents": total_docs,
        "official_documents": official_docs,
        "states_covered": states_covered,
        "pdf_documents": pdfs,
        "total_verified_schemes": total_verified,
        "verified_with_direct_links": verified_with_direct_links,
    }


# Initialize when imported
initialize_database()
