import re
import streamlit as st
from PyPDF2 import PdfReader
from google import genai

st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Playfair+Display:wght@700;800&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background: #f4f6fb;
    color: #1a1d2e;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 50%, #f0f9ff 100%);
    min-height: 100vh;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Navbar ── */
.navbar {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(99,102,241,0.12);
    padding: 0 48px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 2px 24px rgba(99,102,241,0.06);
}
.navbar-brand {
    font-family: 'Playfair Display', serif;
    font-size: 1.45rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}
.navbar-tagline {
    font-size: 0.82rem;
    color: #6b7280;
    font-weight: 400;
    letter-spacing: 0.3px;
}
.navbar-pill {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 6px 16px;
    border-radius: 100px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 72px 24px 56px;
    position: relative;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    color: #6366f1;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 6px 16px;
    border-radius: 100px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 24px;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 5vw, 3.8rem);
    font-weight: 800;
    line-height: 1.12;
    letter-spacing: -1.5px;
    color: #0f172a;
    margin-bottom: 18px;
}
.hero h1 span {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.08rem;
    color: #64748b;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
    font-weight: 400;
}

/* ── Main card wrapper ── */
.main-wrapper {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 24px 80px;
}

/* ── Card ── */
.card {
    background: #ffffff;
    border-radius: 20px;
    padding: 32px;
    box-shadow: 0 4px 24px rgba(15,23,42,0.06), 0 1px 4px rgba(15,23,42,0.04);
    border: 1px solid rgba(99,102,241,0.08);
    margin-bottom: 24px;
    transition: box-shadow 0.2s ease;
}
.card:hover {
    box-shadow: 0 8px 40px rgba(99,102,241,0.10), 0 2px 8px rgba(15,23,42,0.06);
}
.card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.card-desc {
    font-size: 0.88rem;
    color: #94a3b8;
    margin-bottom: 20px;
    font-weight: 400;
}

/* ── Metric cards ── */
.metric-row {
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.metric-card {
    flex: 1;
    min-width: 160px;
    background: #ffffff;
    border-radius: 16px;
    padding: 24px 20px;
    box-shadow: 0 4px 20px rgba(15,23,42,0.06);
    border: 1px solid rgba(99,102,241,0.08);
    text-align: center;
}
.metric-card.highlight {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    border: none;
    box-shadow: 0 8px 32px rgba(99,102,241,0.28);
}
.metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 800;
    line-height: 1;
    color: #6366f1;
    margin-bottom: 6px;
}
.metric-card.highlight .metric-value { color: #ffffff; }
.metric-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.metric-card.highlight .metric-label { color: rgba(255,255,255,0.75); }

/* ── Keyword chips ── */
.chip-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
.chip {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 100px;
    font-size: 0.80rem;
    font-weight: 600;
    letter-spacing: 0.2px;
}
.chip-green {
    background: #dcfce7;
    color: #15803d;
    border: 1px solid #bbf7d0;
}
.chip-red {
    background: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fecaca;
}

/* ── Section label ── */
.section-label {
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 14px;
}

/* ── Suggestion list ── */
.suggestion-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.92rem;
    color: #334155;
    line-height: 1.6;
}
.suggestion-item:last-child { border-bottom: none; }
.suggestion-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    flex-shrink: 0;
    margin-top: 7px;
}

/* ── AI review list ── */
.ai-review-item {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 14px 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.93rem;
    color: #1e293b;
    line-height: 1.65;
}
.ai-review-item:last-child { border-bottom: none; }
.ai-num {
    width: 24px;
    height: 24px;
    border-radius: 8px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, rgba(99,102,241,0.03), rgba(139,92,246,0.04));
    border: 2px dashed rgba(99,102,241,0.25) !important;
    border-radius: 16px !important;
    padding: 8px !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(99,102,241,0.5) !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}

/* ── Text inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border-radius: 12px !important;
    border: 1.5px solid #e2e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.93rem !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    background: #fafbff !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
    outline: none !important;
}

/* ── Button ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 14px 36px !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.30) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    width: 100% !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.38) !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0) !important;
}

/* ── Alert / info boxes ── */
[data-testid="stAlert"] {
    border-radius: 14px !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { font-family: 'DM Sans', sans-serif !important; }

/* ── Divider ── */
hr { border-color: #e2e8f0 !important; margin: 8px 0 !important; }

/* ── Success banner ── */
.success-banner {
    background: linear-gradient(135deg, #dcfce7, #d1fae5);
    border: 1px solid #86efac;
    border-radius: 14px;
    padding: 16px 22px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 24px;
    font-size: 0.93rem;
    font-weight: 600;
    color: #15803d;
}

/* ── Steps strip ── */
.steps-strip {
    display: flex;
    justify-content: center;
    gap: 40px;
    flex-wrap: wrap;
    margin-bottom: 48px;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.88rem;
    color: #64748b;
    font-weight: 500;
}
.step-num {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    font-size: 0.75rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
</style>
""", unsafe_allow_html=True)

# ── Navbar ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="navbar">
    <div>
        <div class="navbar-brand">ResumeIQ</div>
        <div class="navbar-tagline">Powered by Gemini AI</div>
    </div>
    <div class="navbar-pill">✦ Free to use</div>
</div>
""", unsafe_allow_html=True)

# ── Hero ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">✦ AI-Powered ATS Analyzer</div>
    <h1>Get Your Resume <span>Interview-Ready</span></h1>
    <p class="hero-sub">
        Upload your resume, paste a job description, and get instant ATS score,
        keyword analysis, and AI-powered suggestions — all in seconds.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Steps ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="steps-strip">
    <div class="step-item"><div class="step-num">1</div> Upload Resume PDF</div>
    <div class="step-item"><div class="step-num">2</div> Enter Job Role & JD</div>
    <div class="step-item"><div class="step-num">3</div> Get Instant Analysis</div>
</div>
""", unsafe_allow_html=True)

# ── API key ─────────────────────────────────────────────────────────────────────
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ GEMINI_API_KEY not found. Add it in .streamlit/secrets.toml")
    st.stop()

client = genai.Client(api_key=api_key)

# ── Main content ─────────────────────────────────────────────────────────────────
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("""
    <div class="card">
        <div class="card-title">📄 Upload Your Resume</div>
        <div class="card-desc">PDF format only · Max 10MB</div>
    </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your resume here or click to browse",
        type=["pdf"],
        label_visibility="collapsed"
    )

with col_right:
    st.markdown("""
    <div class="card">
        <div class="card-title">🎯 Target Job Details</div>
        <div class="card-desc">Help us match your resume precisely</div>
    </div>
    """, unsafe_allow_html=True)
    job_role = st.text_input(
        "Target Job Role",
        placeholder="e.g. AI Intern, Data Analyst, ML Engineer",
        label_visibility="visible"
    )
    job_description = st.text_area(
        "Job Description",
        height=180,
        placeholder="Paste the full job description here…",
        label_visibility="visible"
    )

# ── Analyze button ──────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
btn_col = st.columns([1, 2, 1])[1]
with btn_col:
    analyze_btn = st.button("🔍  Analyze My Resume", use_container_width=True)

# ── Backend logic (unchanged) ────────────────────────────────────────────────────
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9+#.\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


IMPORTANT_KEYWORDS = [
    "python", "java", "c", "c++", "javascript", "typescript", "sql",
    "machine learning", "deep learning", "artificial intelligence",
    "cnn", "rnn", "lstm", "nlp", "computer vision",
    "classification", "regression", "prediction",
    "numpy", "pandas", "matplotlib", "scikit-learn",
    "tensorflow", "keras", "pytorch", "opencv",
    "html", "css", "react", "node", "flask", "fastapi",
    "rest api", "api",
    "mysql", "mongodb", "postgresql",
    "git", "github", "vs code", "jupyter notebook",
    "streamlit", "power bi", "excel",
    "aws", "ec2", "docker", "deployment", "netlify",
    "data preprocessing", "data cleaning", "data analysis",
    "model training", "model evaluation", "accuracy",
    "performance", "optimization", "visualization",
    "dataset", "datasets", "projects"
]


def extract_keywords(text):
    text = clean_text(text)
    found_keywords = set()
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in text:
            found_keywords.add(keyword)
    return found_keywords


def compare_resume_with_jd(resume_text, jd_text):
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)
    matched_keywords = sorted(resume_keywords.intersection(jd_keywords))
    missing_keywords = sorted(jd_keywords - resume_keywords)
    if len(jd_keywords) == 0:
        ats_score = 0
    else:
        ats_score = round((len(matched_keywords) / len(jd_keywords)) * 100, 2)
    return matched_keywords, missing_keywords, ats_score


def generate_suggestions(missing_keywords):
    suggestions = []
    for keyword in missing_keywords:
        if keyword in ["tensorflow", "keras", "pytorch"]:
            suggestions.append(f"Add a deep learning project using {keyword}.")
        elif keyword in ["numpy", "pandas"]:
            suggestions.append(f"Mention data preprocessing or data analysis using {keyword}.")
        elif keyword == "opencv":
            suggestions.append("Add a computer vision project using OpenCV.")
        elif keyword in ["flask", "fastapi"]:
            suggestions.append(f"Add an API/backend project using {keyword}.")
        elif keyword == "react":
            suggestions.append("Mention a frontend or UI project using React.")
        elif keyword in ["aws", "ec2", "docker", "deployment"]:
            suggestions.append(f"Add deployment experience using {keyword}.")
        elif keyword in ["machine learning", "deep learning"]:
            suggestions.append(f"Highlight {keyword} projects with model performance.")
        elif keyword in ["accuracy", "performance", "optimization"]:
            suggestions.append("Add accuracy, performance score, or optimization details.")
        elif keyword in ["dataset", "datasets"]:
            suggestions.append("Mention datasets used in your projects.")
        else:
            suggestions.append(f"Add {keyword} naturally in your skills or project section.")
    if not suggestions:
        suggestions.append("Your resume already matches the important technical JD keywords well.")
    return suggestions


def ai_resume_review(resume_text, job_role, job_description):
    prompt = f"""
You are an ATS resume analyzer.

Analyze this resume for the role: {job_role}

Job Description:
{job_description}

Resume:
{resume_text}

Give the review in exactly 6 bullet points only line by line.

Rules:
- Keep each bullet point short and simple.
- Focus only on programming languages, tools, libraries, frameworks, projects, datasets, performance, and deployment.
- Do not write long paragraphs.
- Do not use sections like Strengths, Weaknesses, Final Suggestions.
- Do not suggest random words like ability, good, months, candidate, location, hybrid.
- Make it comfortable for website users to read.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


# ── Results ──────────────────────────────────────────────────────────────────────
if uploaded_file and job_role and job_description:
    if analyze_btn:
        with st.spinner("Analyzing your resume with AI…"):
            try:
                resume_text = extract_text_from_pdf(uploaded_file)
                matched, missing, score = compare_resume_with_jd(resume_text, job_description)
                suggestions = generate_suggestions(missing)

                # ── Success banner ──
                st.markdown("""
                <div class="success-banner">
                    ✅ &nbsp; Analysis complete! Here's how your resume stacks up.
                </div>
                """, unsafe_allow_html=True)

                # ── Metric cards ──
                score_color = "#15803d" if score >= 70 else ("#d97706" if score >= 40 else "#b91c1c")
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-card highlight">
                        <div class="metric-value">{score}%</div>
                        <div class="metric-label">ATS Match Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color:#16a34a">{len(matched)}</div>
                        <div class="metric-label">Matched Keywords</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color:#dc2626">{len(missing)}</div>
                        <div class="metric-label">Missing Keywords</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Keywords section ──
                kw_col1, kw_col2 = st.columns(2, gap="large")

                with kw_col1:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-title">✅ Matched Keywords</div>', unsafe_allow_html=True)
                    if matched:
                        chips = "".join(
                            [f'<span class="chip chip-green">{kw}</span>' for kw in matched]
                        )
                        st.markdown(f'<div class="chip-wrap">{chips}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p style="color:#94a3b8;font-size:0.88rem;margin-top:8px;">No important technical keywords matched.</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with kw_col2:
                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-title">❌ Missing Keywords</div>', unsafe_allow_html=True)
                    if missing:
                        chips = "".join(
                            [f'<span class="chip chip-red">{kw}</span>' for kw in missing]
                        )
                        st.markdown(f'<div class="chip-wrap">{chips}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p style="color:#15803d;font-size:0.88rem;margin-top:8px;">🎉 No important technical keywords missing!</p>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                # ── Smart suggestions ──
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">💡 Smart Suggestions</div>', unsafe_allow_html=True)
                st.markdown('<div class="card-desc">Actionable tips to boost your ATS score</div>', unsafe_allow_html=True)
                items_html = "".join([
                    f'<div class="suggestion-item"><div class="suggestion-dot"></div><span>{s}</span></div>'
                    for s in suggestions
                ])
                st.markdown(items_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # ── AI Review ──
                review = ai_resume_review(resume_text, job_role, job_description)
                points = [p.strip() for p in review.split("*") if p.strip()]

                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title">🤖 AI Resume Review</div>', unsafe_allow_html=True)
                st.markdown('<div class="card-desc">Gemini AI deep analysis of your resume vs the job description</div>', unsafe_allow_html=True)

                review_items = "".join([
                    f'<div class="ai-review-item"><div class="ai-num">{i+1}</div><span>{p}</span></div>'
                    for i, p in enumerate(points)
                ])
                st.markdown(review_items, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Something went wrong: {e}")

else:
    st.markdown("""
    <div style="text-align:center; padding: 40px 0; color:#94a3b8; font-size:0.92rem;">
        ☝️ Fill in all three fields above and click <strong style="color:#6366f1">Analyze My Resume</strong> to get started.
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close main-wrapper

# ── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 32px 24px 48px; color:#cbd5e1; font-size:0.80rem; border-top: 1px solid #e2e8f0; margin-top: 16px;">
    ResumeIQ &nbsp;·&nbsp; Powered by Gemini AI &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)