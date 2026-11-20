
import streamlit as st
from textwrap import dedent


def render_html(content):
    """Render HTML directly without Markdown parsing."""
    st.html(dedent(content))


def show_landing_page():

    # =====================================
    # HEADER AND HERO SECTION
    # =====================================

    render_html("""
    <div class="landing-shell">

        <nav class="landing-nav">
            <div class="landing-brand">
                <span class="brand-icon">🇮🇳</span>
                <span>Bharat<span class="brand-orange">Scheme</span> AI</span>
            </div>

            <div class="nav-tag">
                GOVERNMENT SCHEME DISCOVERY ASSISTANT
            </div>
        </nav>

        <section class="hero-section">

            <div class="hero-content">

                <div class="hero-tag">
                    <span class="hero-dot"></span>
                    AI-POWERED CITIZEN ASSISTANCE
                </div>

                <h1>
                    Discover Government Schemes.
                    <span>Unlock Your Benefits.</span>
                </h1>

                <p class="hero-description">
                    Find Central and State Government schemes that may
                    match your profile. Understand benefits, eligibility
                    and application procedures — all in one place.
                </p>

                <div class="hero-highlights">
                    <span>✓ Personalised Discovery</span>
                    <span>✓ Eligibility Guidance</span>
                    <span>✓ Official Sources</span>
                </div>

                <div class="hero-note">
                    One intelligent guide for every citizen.
                </div>

            </div>

            <div class="hero-visual">

                <div class="visual-card">

                    <div class="visual-top">
                        <span class="visual-icon">🇮🇳</span>
                        <span class="visual-status">SMART DISCOVERY</span>
                    </div>

                    <div class="visual-title">
                        Your Benefits,
                        <span>Within Reach.</span>
                    </div>

                    <div class="visual-description">
                        Explore opportunities designed for your needs.
                    </div>

                    <div class="visual-divider"></div>

                    <div class="visual-feature">
                        <span class="feature-symbol">✦</span>
                        <div>
                            <strong>AI-Powered Search</strong>
                            <small>Discover relevant schemes</small>
                        </div>
                    </div>

                    <div class="visual-feature">
                        <span class="feature-symbol">✓</span>
                        <div>
                            <strong>Eligibility Guidance</strong>
                            <small>Understand who can apply</small>
                        </div>
                    </div>

                    <div class="visual-feature">
                        <span class="feature-symbol">↗</span>
                        <div>
                            <strong>Source-Based Results</strong>
                            <small>Explore supporting information</small>
                        </div>
                    </div>

                </div>

                <div class="floating-card">
                    <span>✦</span>
                    Making scheme discovery simpler
                </div>

            </div>

        </section>

    </div>
    """)

    render_html('<div class="landing-spacer"></div>')

    # =====================================
    # GET STARTED SECTION
    # =====================================

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:

        render_html("""
        <div class="start-content">

            <div class="section-eyebrow">GET STARTED</div>

            <h2>Start your scheme discovery</h2>

            <p>
                Share a few basic details about yourself.
                Our AI assistant will help identify government
                schemes that may be relevant to you.
            </p>

            <div class="start-points">
                <span>✓ Simple profile-based search</span>
                <span>✓ Central and State scheme discovery</span>
                <span>✓ Easy-to-understand information</span>
            </div>

        </div>
        """)

        clicked = st.button(
            "Discover My Schemes  →",
            type="primary",
            use_container_width=True,
            key="landing_discover_button"
        )

        render_html("""
        <div class="privacy-note">
            🔒 No Aadhaar number, bank details or OTP required.
        </div>
        """)

    with right:

        render_html("""
        <div class="trust-card">

            <div class="trust-icon">✦</div>

            <h3>Discover benefits with clarity</h3>

            <p>Your journey towards informed access.</p>

            <div class="trust-item">
                <span>01</span>
                <div>
                    <strong>Personalised Discovery</strong>
                    <small>Find schemes based on your profile.</small>
                </div>
            </div>

            <div class="trust-item">
                <span>02</span>
                <div>
                    <strong>Simple Eligibility</strong>
                    <small>Understand eligibility conditions.</small>
                </div>
            </div>

            <div class="trust-item">
                <span>03</span>
                <div>
                    <strong>Benefits &amp; Documents</strong>
                    <small>Learn about benefits and required documents.</small>
                </div>
            </div>

            <div class="trust-item">
                <span>04</span>
                <div>
                    <strong>Source Information</strong>
                    <small>Review available official source links.</small>
                </div>
            </div>

        </div>
        """)

    render_html('<div class="landing-section-gap"></div>')

    # =====================================
    # CATEGORIES SECTION
    # =====================================

    render_html("""
    <div class="section-heading">

        <div class="section-eyebrow">EXPLORE OPPORTUNITIES</div>

        <h2>Government support for every stage of life</h2>

        <p>
            Explore major areas where government schemes provide support.
        </p>

    </div>
    """)

    categories = [
        (
            "🌾",
            "Agriculture",
            "Support for farmers and rural communities",
            "cat-green"
        ),
        (
            "🎓",
            "Education",
            "Scholarships and student assistance",
            "cat-orange"
        ),
        (
            "🏥",
            "Healthcare",
            "Health protection and medical support",
            "cat-blue"
        ),
        (
            "💼",
            "Employment",
            "Skills, jobs and livelihood opportunities",
            "cat-purple"
        ),
        (
            "👩‍👧",
            "Women &amp; Child",
            "Women empowerment and child welfare",
            "cat-pink"
        ),
    ]

    def show_category(item):

        icon, title, description, color_class = item

        render_html(f"""
        <div class="category-card {color_class}">

            <div class="category-icon">{icon}</div>

            <h3>{title}</h3>

            <p>{description}</p>

        </div>
        """)

    # First row: 3 categories
    row_one = st.columns(3, gap="medium")

    for col, item in zip(row_one, categories[:3]):
        with col:
            show_category(item)

    # Second row: 2 centered categories
    row_two = st.columns([0.5, 1, 1, 0.5], gap="medium")

    for col, item in zip(
        [row_two[1], row_two[2]],
        categories[3:]
    ):
        with col:
            show_category(item)

    render_html('<div class="landing-section-gap"></div>')

    # =====================================
    # HOW IT WORKS SECTION
    # =====================================

    render_html("""
    <div class="section-heading">

        <div class="section-eyebrow">HOW IT WORKS</div>

        <h2>Three simple steps to get started</h2>

        <p>
            From your profile to relevant government scheme information.
        </p>

    </div>
    """)

    steps = [
        (
            "01",
            "Share Your Profile",
            "Enter basic details such as your state, age, occupation and other relevant information."
        ),
        (
            "02",
            "AI Analyses Schemes",
            "The system searches available scheme information and analyses potential matches."
        ),
        (
            "03",
            "Understand &amp; Apply",
            "Review scheme benefits, eligibility details and available application sources."
        ),
    ]

    step_cols = st.columns(3, gap="medium")

    for col, (number, title, description) in zip(step_cols, steps):

        with col:

            render_html(f"""
            <div class="step-card">

                <div class="step-number">{number}</div>

                <h3>{title}</h3>

                <p>{description}</p>

            </div>
            """)

    # =====================================
    # BOTTOM BANNER AND FOOTER
    # =====================================

    render_html("""
    <div class="bottom-banner">

        <div>
            <div class="banner-eyebrow">BHARATSCHEME AI</div>

            <h2>Every Citizen. Every Opportunity.</h2>

            <p>Discover. Understand. Apply.</p>
        </div>

        <div class="banner-symbol">🇮🇳</div>

    </div>

    <footer class="landing-footer">

        <div class="footer-brand">
            Bharat<span>Scheme</span> AI
        </div>

        <p>
            Built with Python, Streamlit, Google Gemini and Tavily
        </p>

        <small>
            An independent prototype for government scheme discovery.
            Always verify scheme details with the relevant official authority.
        </small>

    </footer>
    """)

    return clicked
