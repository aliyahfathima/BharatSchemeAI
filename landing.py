import streamlit as st

def show_landing_page():
    st.markdown("""
    <style>
    [data-testid="stDeployButton"] {display:none !important;}
    [data-testid="stToolbar"] {background:transparent;}
    .block-container {
        max-width: 1250px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    .landing-nav {
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding:12px 4px 22px;
        border-bottom:1px solid rgba(120,140,160,.2);
    }
    .brand {
        font-size:24px;
        font-weight:800;
        color:var(--text-color);
    }
    .brand span {color:#159b83;}
    .nav-tag {
        color:var(--text-color);
        font-size:14px;
    }
    .hero {
        margin-top:28px;
        padding:55px 48px;
        border-radius:24px;
        background:linear-gradient(110deg,rgba(8,35,57,.96),rgba(10,91,91,.83)),
        url('https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&w=1600&q=85');
        background-size:cover;
        background-position:center;
        color:white;
        min-height:350px;
    }
    .hero-tag {
        display:inline-block;
        background:rgba(255,255,255,.15);
        border:1px solid rgba(255,255,255,.25);
        padding:7px 13px;
        border-radius:30px;
        font-size:13px;
        margin-bottom:18px;
    }
    .hero h1 {
        color:white !important;
        font-size:clamp(34px,5vw,55px);
        line-height:1.12;
        max-width:650px;
        margin:0 0 18px 0;
    }
    .hero p {
        color:#e4f1f2 !important;
        font-size:17px;
        line-height:1.7;
        max-width:590px;
    }
    .section-title {
        font-size:27px;
        font-weight:750;
        color:var(--text-color);
        margin:38px 0 8px;
    }
    .section-sub {
        color:var(--text-color);
        opacity:.72;
        margin-bottom:20px;
    }
    .category-card {
        background:var(--secondary-background-color);
        border:1px solid rgba(130,150,170,.22);
        border-radius:16px;
        padding:20px 16px;
        min-height:130px;
    }
    .category-icon {font-size:30px;margin-bottom:12px;}
    .category-name {
        font-size:16px;
        font-weight:700;
        color:var(--text-color);
    }
    .category-desc {
        font-size:13px;
        color:var(--text-color);
        opacity:.7;
        margin-top:5px;
    }
    .step-card {
        padding:20px;
        border-radius:15px;
        border:1px solid rgba(130,150,170,.22);
        background:var(--secondary-background-color);
        min-height:135px;
    }
    .step-number {
        color:#159b83;
        font-weight:800;
        font-size:14px;
    }
    .step-card h4 {color:var(--text-color);margin:10px 0 6px;}
    .step-card p {color:var(--text-color);opacity:.72;font-size:14px;}
    .trust {
        margin-top:30px;
        padding:22px;
        border-radius:16px;
        background:rgba(21,155,131,.09);
        border:1px solid rgba(21,155,131,.2);
        color:var(--text-color);
    }
    .footer-text {
        text-align:center;
        color:var(--text-color);
        opacity:.65;
        font-size:13px;
        padding:28px 0 5px;
    }
    </style>

    <div class="landing-nav">
      <div class="brand">Bharat<span>Scheme</span> AI</div>
      <div class="nav-tag">Government Scheme Discovery Assistant</div>
    </div>

    <section class="hero">
      <div class="hero-tag">🇮🇳 AI-powered citizen assistance</div>
      <h1>Find Government Schemes You Deserve.</h1>
      <p>
        Discover Central and State Government welfare schemes that may
        match your profile. Understand eligibility, benefits and how to apply
        — all in one place.
      </p>
    </section>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    left, right = st.columns([1, 1])

    with left:
        st.markdown("### Start your scheme discovery")
        st.write("Answer a few simple questions. Our AI assistant will analyse your profile and find relevant schemes.")

        if st.button("Discover My Schemes  →", type="primary", use_container_width=True):
            return True

    with right:
        st.markdown("""
        <div class="trust">
          <h3>Discover benefits with clarity</h3>
          <p>✓ Personalised scheme discovery</p>
          <p>✓ Eligibility explained in simple language</p>
          <p>✓ Benefits and required documents</p>
          <p>✓ Links to official government sources</p>
          <p style="font-size:12px;opacity:.75">
          BharatScheme AI is an independent prototype, not an official government website.
          </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Explore scheme categories</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-sub'>Discover support across important areas of everyday life.</div>", unsafe_allow_html=True)

    categories = [
        ("🌾", "Agriculture", "Support for farmers"),
        ("🎓", "Education", "Scholarships and learning"),
        ("🏥", "Healthcare", "Health and family welfare"),
        ("💼", "Employment", "Jobs and skill development"),
        ("👩", "Women & Child", "Women and child welfare"),
    ]

    cols = st.columns(5)
    for col, item in zip(cols, categories):
        with col:
            st.markdown(f"""
            <div class="category-card">
              <div class="category-icon">{item[0]}</div>
              <div class="category-name">{item[1]}</div>
              <div class="category-desc">{item[2]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>How it works</div>", unsafe_allow_html=True)
    steps = [
        ("01", "Share your profile", "Enter basic details such as age, state and occupation."),
        ("02", "AI analyses schemes", "Relevant scheme information is checked against your profile."),
        ("03", "Understand and apply", "Review possible matches, documents and official application links."),
    ]

    cols = st.columns(3)
    for col, item in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div class="step-card">
              <div class="step-number">STEP {item[0]}</div>
              <h4>{item[1]}</h4>
              <p>{item[2]}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""
    <div class="footer-text">
      BharatScheme AI · Discover. Understand. Apply.<br>
      Independent AI prototype · Always verify eligibility on official government portals.
    </div>
    """, unsafe_allow_html=True)

    return False
