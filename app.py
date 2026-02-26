import streamlit as st
import pdfplumber
import time
import re
import math
from datetime import datetime
from transformers import pipeline

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuMind AI · Smart Document Summarizer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# CUSTOM CSS  — sleek dark theme with amber accents
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Instrument+Sans:wght@300;400;500&family=JetBrains+Mono:wght@300;400&display=swap');

/* ── root ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0f0f11 !important;
    color: #e8e4dc !important;
    font-family: 'Instrument Sans', sans-serif !important;
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #17171a !important;
    border-right: 1px solid #2a2a30 !important;
}
[data-testid="stSidebar"] * { color: #e8e4dc !important; }

/* ── block container ── */
.block-container { padding: 2.5rem 3rem 4rem 3rem !important; max-width: 1400px; }

/* ── headings ── */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: clamp(1.8rem, 3.5vw, 2.8rem) !important;
    font-weight: 800 !important;
    letter-spacing: -.02em !important;
    color: #f0ebe0 !important;
    margin-bottom: .2rem !important;
}
h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: #d4a853 !important;
}

/* ── amber accent span ── */
.accent { color: #d4a853; }

/* ── divider ── */
hr { border-color: #2a2a30 !important; margin: 1.5rem 0 !important; }

/* ── cards ── */
.card {
    background: #1a1a1f;
    border: 1px solid #2a2a30;
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.4rem;
}
.card-accent { border-left: 3px solid #d4a853; }

/* ── stat row ── */
.stat-row { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1rem 0; }
.stat-box {
    flex: 1; min-width: 110px;
    background: #111114;
    border: 1px solid #2a2a30;
    border-radius: 10px;
    padding: .9rem 1rem;
    text-align: center;
}
.stat-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 400;
    color: #d4a853;
    display: block;
}
.stat-lbl {
    font-size: .65rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #5a5a6a;
    display: block;
    margin-top: .2rem;
}

/* ── readability pill ── */
.pill {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: .7rem;
    padding: .25rem .8rem;
    border-radius: 20px;
    font-weight: 400;
    margin: .2rem .2rem 0 0;
}
.pill-green  { background: #14291a; color: #4ade80; border: 1px solid #1f4a28; }
.pill-yellow { background: #2a2510; color: #facc15; border: 1px solid #4a3d10; }
.pill-orange { background: #2a1c10; color: #fb923c; border: 1px solid #4a2c10; }
.pill-red    { background: #2a1010; color: #f87171; border: 1px solid #4a1818; }

/* ── model badge ── */
.model-badge {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: .65rem;
    padding: .2rem .7rem;
    background: #1e1e28;
    border: 1px dashed #3a3a4a;
    border-radius: 4px;
    color: #7a7a9a;
    letter-spacing: .06em;
}

/* ── textarea & inputs ── */
textarea, input[type="text"] {
    background: #111114 !important;
    color: #e8e4dc !important;
    border: 1px solid #2a2a30 !important;
    border-radius: 8px !important;
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: .92rem !important;
}
textarea:focus, input:focus {
    border-color: #d4a853 !important;
    box-shadow: 0 0 0 2px rgba(212,168,83,.15) !important;
}

/* ── selectbox ── */
div[data-baseweb="select"] > div {
    background: #111114 !important;
    border: 1px solid #2a2a30 !important;
    border-radius: 8px !important;
    color: #e8e4dc !important;
}
div[data-baseweb="select"] svg { fill: #d4a853 !important; }

/* ── radio ── */
div[role="radiogroup"] label { color: #c0bab0 !important; }
div[role="radiogroup"] [data-testid="stMarkdownContainer"] p { color: #c0bab0 !important; }

/* ── slider ── */
[data-testid="stSlider"] { accent-color: #d4a853; }
[data-testid="stSlider"] div[data-testid="stThumbValue"] {
    color: #d4a853 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── buttons ── */
.stButton > button {
    background: #d4a853 !important;
    color: #0f0f11 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: .9rem !important;
    letter-spacing: .05em !important;
    padding: .65rem 1.8rem !important;
    transition: all .2s !important;
    height: auto !important;
}
.stButton > button:hover {
    background: #e8bf6a !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(212,168,83,.3) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* secondary button style */
.sec-btn .stButton > button {
    background: transparent !important;
    color: #7a7a8a !important;
    border: 1px solid #2a2a30 !important;
}
.sec-btn .stButton > button:hover {
    border-color: #d4a853 !important;
    color: #d4a853 !important;
    box-shadow: none !important;
}

/* ── file uploader ── */
[data-testid="stFileUploader"] {
    background: #111114 !important;
    border: 1.5px dashed #2a2a30 !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"]:hover { border-color: #d4a853 !important; }

/* ── success / warning / info ── */
[data-testid="stAlert"] {
    background: #1a1a1f !important;
    border-radius: 8px !important;
}

/* ── progress bar ── */
[data-testid="stProgressBar"] > div { background-color: #d4a853 !important; }

/* ── metrics ── */
[data-testid="metric-container"] {
    background: #1a1a1f;
    border: 1px solid #2a2a30;
    border-radius: 10px;
    padding: .8rem 1rem;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    color: #d4a853 !important;
}
[data-testid="stMetricLabel"] { color: #7a7a8a !important; }

/* ── caption ── */
[data-testid="stCaptionContainer"] { color: #5a5a6a !important; }

/* ── download button ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #d4a853 !important;
    border: 1px solid #d4a853 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(212,168,83,.1) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── spinner text ── */
.stSpinner > div { border-top-color: #d4a853 !important; }

/* ── tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: #7a7a8a !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #d4a853 !important;
    border-bottom-color: #d4a853 !important;
}

/* ── history item ── */
.hist-item {
    background: #111114;
    border: 1px solid #2a2a30;
    border-left: 3px solid #d4a853;
    border-radius: 8px;
    padding: .9rem 1.1rem;
    margin-bottom: .8rem;
    cursor: default;
}
.hist-item:hover { border-color: #d4a853; }
.hist-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: .63rem;
    color: #5a5a6a;
    margin-bottom: .3rem;
    letter-spacing: .06em;
}
.hist-snippet { font-size: .83rem; color: #a0a0b0; line-height: 1.5; }

/* ── chunk warn ── */
.chunk-warn {
    background: #1e1a10;
    border: 1px solid #3a3010;
    border-radius: 6px;
    padding: .5rem .9rem;
    font-size: .78rem;
    color: #b8a060;
    margin: .5rem 0;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────

def word_count(text: str) -> int:
    return len(text.split())


def sentence_count(text: str) -> int:
    return max(1, len(re.split(r'[.!?]+', text.strip())))


def syllable_count(word: str) -> int:
    word = word.lower().strip(".,!?;:")
    if len(word) <= 3:
        return 1
    n = len(re.findall(r'[aeiouy]+', word))
    if word.endswith('e'):
        n -= 1
    return max(1, n)


def flesch_kincaid(text: str) -> float:
    words = text.split()
    wc = max(1, len(words))
    sc = sentence_count(text)
    syl = sum(syllable_count(w) for w in words)
    return round(0.39 * (wc / sc) + 11.8 * (syl / wc) - 15.59, 1)


def readability_info(grade: float):
    if grade < 6:
        return "Very Easy", "pill-green"
    elif grade < 9:
        return "Easy", "pill-green"
    elif grade < 12:
        return "Moderate", "pill-yellow"
    elif grade < 15:
        return "Difficult", "pill-orange"
    else:
        return "Very Difficult", "pill-red"


def chunk_text(text: str, max_tokens: int = 900) -> list[str]:
    """Split text into chunks of ≤ max_tokens words."""
    words = text.split()
    return [" ".join(words[i:i+max_tokens]) for i in range(0, len(words), max_tokens)]


def extract_pdf(uploaded_file) -> str:
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text.strip()


def to_bullets(text: str) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return "\n".join(f"• {s.strip()}" for s in sentences if s.strip())


def stat_html(value, label):
    return f"""
    <div class="stat-box">
        <span class="stat-num">{value}</span>
        <span class="stat-lbl">{label}</span>
    </div>"""


# ─────────────────────────────────────────────────────────
# MODEL REGISTRY
# ─────────────────────────────────────────────────────────
MODELS = {
    "⚡ Fast  —  DistilBART":  "sshleifer/distilbart-cnn-12-6",
    "🎯 Balanced  —  T5 Small":  "t5-small",
    "✨ Best Quality  —  BART Large": "facebook/bart-large-cnn",
}

@st.cache_resource(show_spinner=False)
def load_model(model_name: str):
    return pipeline("summarization", model=model_name)

# ─────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []   # list of dicts
if "last_summary" not in st.session_state:
    st.session_state.last_summary = None


# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 DocuMind AI")
    st.caption("Smart Document Summarizer · v2.0")
    st.divider()

    st.markdown("### Model")
    model_choice = st.selectbox(
        "Select AI Model",
        list(MODELS.keys()),
        label_visibility="collapsed"
    )

    st.markdown("### Summary Size")
    size_label = st.radio(
        "Size", ["Short", "Medium", "Long"],
        label_visibility="collapsed",
        horizontal=True
    )

    size_map = {
        "Short":  (60,  120),
        "Medium": (100, 220),
        "Long":   (180, 350),
    }
    min_len, max_len = size_map[size_label]

    st.markdown("### Output Format")
    fmt = st.radio(
        "Format", ["Paragraph", "Bullet Points"],
        label_visibility="collapsed",
        horizontal=True
    )

    st.divider()
    st.markdown("### About")
    st.caption(
        "DocuMind AI — an intelligent document summarization tool built for AI/ML internship. "
        "Powered by HuggingFace Transformers (BART, T5). Supports long documents via automatic chunking."
    )


# ─────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────
st.markdown("""
<h1>DocuMind <span class="accent">AI</span></h1>
<p style="color:#5a5a6a;font-size:.92rem;margin-bottom:1.5rem;">
    Intelligent Document Summarization — paste text or upload a PDF and get a precise, AI-generated summary instantly.
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────
tab_main, tab_history = st.tabs(["📝  Summarize", "🕒  History"])

# ╔══════════════════════════════════════════════════════╗
# ║  TAB 1 — MAIN                                        ║
# ╚══════════════════════════════════════════════════════╝
with tab_main:

    col_in, col_out = st.columns(2, gap="large")

    # ── INPUT ─────────────────────────────────────────────
    with col_in:
        st.markdown("#### 📥 Input")

        uploaded = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            help="Text will be extracted automatically from all pages."
        )

        input_text = st.text_area(
            "Or paste your text",
            height=260,
            placeholder="Paste any article, report, essay, or research paper…",
            label_visibility="collapsed",
        )

        # PDF overrides pasted text
        pdf_text = ""
        if uploaded:
            with st.spinner("Extracting PDF…"):
                pdf_text = extract_pdf(uploaded)
            if pdf_text:
                st.success(f"✓ Extracted {word_count(pdf_text):,} words from PDF")
                with st.expander("Preview extracted text"):
                    st.text(pdf_text[:1500] + ("…" if len(pdf_text) > 1500 else ""))

        active_text = pdf_text if pdf_text else input_text.strip()

        # Live word count
        wc_in = word_count(active_text) if active_text else 0
        chunks_needed = max(1, math.ceil(wc_in / 900))

        c1, c2 = st.columns(2)
        c1.metric("Words", f"{wc_in:,}")
        c2.metric("Chunks", chunks_needed, help="Long texts are split into chunks for the model")

        if chunks_needed > 1:
            st.markdown(f'<div class="chunk-warn">⚠ Text will be split into {chunks_needed} chunks (model token limit). Results merged automatically.</div>', unsafe_allow_html=True)

        btn_col, clr_col = st.columns([3, 1])
        run = btn_col.button("🧠 Analyse & Summarise", use_container_width=True)
        with clr_col:
            st.markdown('<div class="sec-btn">', unsafe_allow_html=True)
            if st.button("Clear", use_container_width=True):
                st.session_state.last_summary = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # ── OUTPUT ────────────────────────────────────────────
    with col_out:
        st.markdown("#### 📄 Summary")

        if run:
            if not active_text:
                st.warning("Please paste text or upload a PDF first.")
            else:
                model_key = MODELS[model_choice]
                progress = st.progress(0, text="Loading model…")

                with st.spinner(""):
                    summarizer = load_model(model_key)
                    progress.progress(25, text="Model ready — summarizing…")

                    chunks = chunk_text(active_text)
                    summaries = []
                    for i, chunk in enumerate(chunks):
                        result = summarizer(
                            chunk,
                            max_length=max_len,
                            min_length=min_len,
                            do_sample=False,
                        )
                        summaries.append(result[0]["summary_text"])
                        progress.progress(25 + int(75 * (i + 1) / len(chunks)),
                                          text=f"Chunk {i+1}/{len(chunks)} done…")

                    combined = " ".join(summaries)

                    # Second-pass merge if multiple chunks
                    if len(summaries) > 1 and word_count(combined) > max_len:
                        merge_result = summarizer(
                            combined,
                            max_length=max_len,
                            min_length=min_len,
                            do_sample=False,
                        )
                        combined = merge_result[0]["summary_text"]

                    final = to_bullets(combined) if fmt == "Bullet Points" else combined
                    progress.empty()

                # grade metrics
                grade_in  = flesch_kincaid(active_text)
                grade_out = flesch_kincaid(final)
                lbl_in,  cls_in  = readability_info(grade_in)
                lbl_out, cls_out = readability_info(grade_out)
                wc_out = word_count(final)
                compression = round((1 - wc_out / max(1, wc_in)) * 100, 1)

                # persist
                st.session_state.last_summary = {
                    "summary": final,
                    "model": model_key,
                    "wc_in": wc_in,
                    "wc_out": wc_out,
                    "compression": compression,
                    "grade_in": grade_in,
                    "lbl_in": lbl_in,
                    "cls_in": cls_in,
                    "grade_out": grade_out,
                    "lbl_out": lbl_out,
                    "cls_out": cls_out,
                    "ts": datetime.now().strftime("%b %d · %H:%M"),
                    "snippet": active_text[:100] + "…",
                    "fmt": fmt,
                    "size": size_label,
                }
                st.session_state.history.insert(0, st.session_state.last_summary)
                if len(st.session_state.history) > 15:
                    st.session_state.history = st.session_state.history[:15]

        # render result
        s = st.session_state.last_summary
        if s:
            st.success("Summary generated successfully!")

            # stat row
            st.markdown(
                '<div class="stat-row">'
                + stat_html(f"{s['wc_in']:,}", "Input Words")
                + stat_html(f"{s['wc_out']:,}", "Summary Words")
                + stat_html(f"{s['compression']}%", "Compression")
                + '</div>',
                unsafe_allow_html=True
            )

            # readability
            st.markdown(
                f"Readability: "
                f"<span class='pill {s['cls_in']}'>{s['lbl_in']} ({s['grade_in']})</span> → "
                f"<span class='pill {s['cls_out']}'>{s['lbl_out']} ({s['grade_out']})</span>",
                unsafe_allow_html=True
            )
            st.caption(" ")

            st.text_area("", s["summary"], height=280, label_visibility="collapsed")

            # model badge + download
            st.markdown(f'<span class="model-badge">Model: {s["model"]}</span>', unsafe_allow_html=True)
            st.download_button(
                "⬇ Download Summary (.txt)",
                data=s["summary"],
                file_name=f"documind_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.markdown("""
            <div style="height:260px;display:flex;align-items:center;justify-content:center;
                        border:1px dashed #2a2a30;border-radius:10px;color:#3a3a4a;
                        font-family:'JetBrains Mono',monospace;font-size:.8rem;letter-spacing:.08em;">
                AWAITING INPUT
            </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════╗
# ║  TAB 2 — HISTORY                                     ║
# ╚══════════════════════════════════════════════════════╝
with tab_history:
    st.markdown("#### 🕒 Recent Summaries")
    st.caption("Session history (up to 15 entries) — resets on page refresh.")

    if not st.session_state.history:
        st.info("No summaries yet. Generate one in the Summarize tab.")
    else:
        if st.button("🗑 Clear History"):
            st.session_state.history = []
            st.rerun()

        for i, item in enumerate(st.session_state.history):
            st.markdown(f"""
            <div class="hist-item">
                <div class="hist-meta">#{i+1} &nbsp;|&nbsp; {item['ts']} &nbsp;|&nbsp;
                    {item['wc_in']:,} → {item['wc_out']:,} words &nbsp;|&nbsp;
                    -{item['compression']}% &nbsp;|&nbsp; {item['size']} · {item['fmt']}
                </div>
                <div class="hist-snippet">{item['snippet']}</div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander(f"View full summary #{i+1}"):
                st.text_area("", item["summary"], height=180, key=f"h_{i}", label_visibility="collapsed")
                st.download_button(
                    "⬇ Download",
                    data=item["summary"],
                    file_name=f"documind_summary_{i+1}.txt",
                    mime="text/plain",
                    key=f"dl_{i}"
                )

# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("---")
st.caption("DocuMind AI v2.0 · Built with Python, Streamlit & HuggingFace Transformers · AI/ML Internship Project")
