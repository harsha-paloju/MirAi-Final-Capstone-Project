import streamlit as st
import pandas as pd
import json
import re
import os
import time
import base64
import random
from datetime import datetime
from io import BytesIO
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import pypdf

# Import Google GenAI SDK (modern SDK) with fallback to legacy
try:
    from google import genai
    from google.genai import types
    HAS_GOOGLE_GENAI = True
except Exception:
    HAS_GOOGLE_GENAI = False
    import google.generativeai as legacy_genai

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="EchoStudy · Voice, YouTube & PDF to StudyPack",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  PROFESSIONAL LIGHT DESIGN SYSTEM
#  - Soft light button styling with Semi-Bold text
#  - Generous sidebar placeholder & input sizing
#  - Clean Quick Demos typography
#  - Zero black bars & pure light theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Mono:wght@400;500;600&display=swap');

:root {
    --bg-base:      #f8fafc;
    --bg-card:      #ffffff;
    --bg-panel:     #f1f5f9;
    --bg-subtle:    #f8fafc;
    --bg-hover:     #e2e8f0;
    --accent:       #6366f1;
    --accent-light: #eef2ff;
    --accent-hover: #4f46e5;
    --accent-glow:  rgba(99, 102, 241, 0.16);
    --accent-dim:   #e0e7ff;
    --amber:        #d97706;
    --amber-dim:    #fef3c7;
    --success:      #059669;
    --success-dim:  #ecfdf5;
    --danger:       #dc2626;
    --danger-dim:   #fef2f2;
    --text-main:    #0f172a;
    --text-soft:    #334155;
    --text-muted:   #64748b;
    --border:       #e2e8f0;
    --border-lit:   #cbd5e1;
    --shadow-sm:    0 1px 3px rgba(0, 0, 0, 0.05);
    --shadow-md:    0 4px 14px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.03);
    --shadow-lg:    0 10px 25px rgba(99, 102, 241, 0.1), 0 4px 10px rgba(0, 0, 0, 0.03);
}

/* ── Global App & Header Reset ── */
header[data-testid="stHeader"], [data-testid="stHeader"], .stAppHeader {
    background-color: var(--bg-base) !important;
    color: var(--text-main) !important;
}
[data-testid="stToolbar"] {
    color: var(--text-muted) !important;
}

html, body, [data-testid="stAppViewContainer"], .stApp, .main {
    background-color: var(--bg-base) !important;
    color: var(--text-main) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

/* ── Sidebar Styling ── */
section[data-testid="stSidebar"], [data-testid="stSidebar"], [data-testid="stSidebar"] > div {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
    color: var(--text-main) !important;
}

/* Sidebar Inputs & Placeholder Sizing */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] [data-baseweb="input"] input {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    height: 44px !important;
    color: #0f172a !important;
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
}

[data-testid="stSidebar"] input::placeholder {
    font-size: 0.88rem !important;
    font-weight: 400 !important;
    color: #94a3b8 !important;
    opacity: 1 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    min-height: 44px !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    border-color: #cbd5e1 !important;
    display: flex !important;
    align-items: center !important;
}

/* Sidebar Quick Demos Button Typography */
[data-testid="stSidebar"] .stButton > button {
    background: #f8fafc !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
    text-align: center !important;
    line-height: 1.4 !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #eef2ff !important;
    color: #4338ca !important;
    border-color: #c7d2fe !important;
    transform: translateY(-1px) !important;
}

/* ── Typography ── */
h1 {
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    color: var(--text-main) !important;
    letter-spacing: -0.6px !important;
    line-height: 1.2 !important;
}
h2 {
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    color: var(--text-main) !important;
    letter-spacing: -0.3px !important;
}
h3 {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: var(--text-main) !important;
}
h4 {
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: var(--accent) !important;
}
p, span, label, div {
    color: var(--text-soft);
    font-weight: 400;
}

/* ── Section Labels ── */
.sec-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
}

/* ── Input Source 5 Buttons (Light soft colors with Semi-Bold text) ── */
.mode-btn-active > div > button,
.stButton > button[kind="primary"] {
    background: #eef2ff !important;
    color: #4338ca !important;
    border: 2px solid #6366f1 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
    box-shadow: 0 2px 10px rgba(99, 102, 241, 0.12) !important;
    transition: all 0.2s ease !important;
}
.mode-btn-active > div > button:hover,
.stButton > button[kind="primary"]:hover {
    background: #e0e7ff !important;
    color: #3730a3 !important;
    border-color: #4f46e5 !important;
}

.mode-btn-inactive > div > button,
.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #475569 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 10px 14px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
}
.mode-btn-inactive > div > button:hover,
.stButton > button[kind="secondary"]:hover {
    background: #f8fafc !important;
    color: #1e293b !important;
    border-color: #cbd5e1 !important;
}

/* Main Generate Action Button */
.main-generate-btn .stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px 24px !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.25) !important;
    transition: all 0.2s ease !important;
}
.main-generate-btn .stButton > button:hover {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
}

/* ── Inputs & Textareas ── */
.stTextInput > div > div, .stTextArea > div > div,
.stTextInput input, .stTextArea textarea {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 10px !important;
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    box-shadow: var(--shadow-sm) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
}
[data-baseweb="input"] button, [data-testid="stTextInput"] button {
    background-color: transparent !important;
    color: var(--text-muted) !important;
    border: none !important;
    box-shadow: none !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-lit) !important;
    box-shadow: var(--shadow-md) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    font-weight: 600 !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stMetricValue"] {
    color: var(--text-main) !important;
    font-size: 1.95rem !important;
    font-weight: 800 !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    margin-bottom: 12px !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.94rem !important;
    font-weight: 600 !important;
    color: var(--text-main) !important;
}
[data-testid="stExpander"] summary:hover {
    color: var(--accent) !important;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 6px !important;
}
[data-baseweb="tab"] {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: var(--accent) !important;
    font-weight: 700 !important;
    background: var(--bg-card) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* ── Hero Header ── */
.echo-hero {
    background: linear-gradient(135deg, #ffffff 0%, #f4f6ff 100%);
    border: 1px solid #e0e7ff;
    border-top: 4px solid var(--accent);
    border-radius: 16px;
    padding: 26px 30px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-md);
}
.echo-hero h1 { margin: 0 0 6px !important; color: #1e1b4b !important; }
.echo-hero p  { color: var(--text-soft) !important; font-size: 0.95rem !important; margin: 0 !important; line-height: 1.6 !important; font-weight: 400 !important; }

/* ── Flashcard ── */
.flashcard {
    width: 100%;
    min-height: 220px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 26px 28px;
    transition: all 0.25s ease;
    position: relative;
    box-shadow: var(--shadow-md);
}
.flashcard:hover {
    border-color: var(--border-lit);
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
.flashcard .fc-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 8px;
}
.flashcard .fc-q {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1.5;
    margin-bottom: 14px;
}
.flashcard .fc-a {
    font-size: 0.95rem;
    font-weight: 400;
    color: var(--text-soft);
    line-height: 1.7;
    border-top: 1px solid var(--border);
    padding-top: 14px;
    margin-top: 6px;
}
.flashcard .fc-num {
    position: absolute;
    top: 18px; right: 22px;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted);
}
.fc-difficulty {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.diff-easy   { background: var(--success-dim); color: var(--success); border: 1px solid #a7f3d0; }
.diff-medium { background: var(--amber-dim);   color: var(--amber);   border: 1px solid #fde68a; }
.diff-hard   { background: var(--danger-dim);  color: var(--danger);  border: 1px solid #fecaca; }

/* ── Study Guide Blocks ── */
.guide-block {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 0 12px 12px 0;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-sm);
}
.guide-block h4 {
    font-size: 0.98rem !important;
    font-weight: 700 !important;
    color: var(--accent) !important;
    margin: 0 0 8px !important;
}
.guide-block p {
    font-size: 0.92rem !important;
    font-weight: 400 !important;
    color: var(--text-soft) !important;
    margin: 0 !important;
    line-height: 1.75 !important;
}

/* ── Waveform Animation ── */
@keyframes wave-pulse {
    0%, 100% { transform: scaleY(0.35); }
    50%       { transform: scaleY(1.0); }
}
.waveform {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 5px;
    height: 36px;
    margin: 12px 0;
}
.wave-bar {
    width: 4px;
    background: var(--accent);
    border-radius: 2px;
    animation: wave-pulse 1.2s ease-in-out infinite;
    opacity: 0.85;
}
.wave-bar:nth-child(1)  { animation-delay: 0.0s; height: 26px; }
.wave-bar:nth-child(2)  { animation-delay: 0.1s; height: 34px; }
.wave-bar:nth-child(3)  { animation-delay: 0.2s; height: 20px; }
.wave-bar:nth-child(4)  { animation-delay: 0.3s; height: 38px; }
.wave-bar:nth-child(5)  { animation-delay: 0.4s; height: 28px; }
.wave-bar:nth-child(6)  { animation-delay: 0.5s; height: 36px; }
.wave-bar:nth-child(7)  { animation-delay: 0.6s; height: 18px; }
.wave-bar:nth-child(8)  { animation-delay: 0.7s; height: 32px; }
.wave-bar:nth-child(9)  { animation-delay: 0.8s; height: 24px; }
.wave-bar:nth-child(10) { animation-delay: 0.9s; height: 36px; }
.wave-bar:nth-child(11) { animation-delay: 1.0s; height: 16px; }
.wave-bar:nth-child(12) { animation-delay: 1.1s; height: 30px; }

/* ── Sidebar Stat Pill ── */
.stat-pill {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: var(--shadow-sm);
}
.stat-pill .sp-label { font-family: 'DM Mono', monospace; font-size: 0.68rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
.stat-pill .sp-value { font-size: 1.18rem; font-weight: 800; color: var(--accent); }

/* ── Cards ── */
.yt-card, .pdf-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-sm);
}
.yt-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: #fef2f2;
    border: 1px solid #fee2e2;
    border-radius: 6px;
    color: #dc2626;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    font-weight: 600;
}
.pdf-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    background: #f0fdf4;
    border: 1px solid #dcfce7;
    border-radius: 6px;
    color: #16a34a;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    font-weight: 600;
}

hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    env_api_key = os.environ.get("GEMINI_API_KEY", "")
    try:
        if not env_api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            env_api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    defaults = {
        "api_key":           env_api_key,
        "api_key_set":       bool(env_api_key),
        "selected_model":    "gemini-2.5-flash",
        "discovered_models": [],
        "transcript_text":   "",
        "subject":           "",
        "yt_url":            "",
        "yt_video_id":       "",
        "yt_video_title":    "",
        "pdf_name":          "",
        "pdf_pages":         0,
        "pdf_words":         0,
        "study_guide":       None,
        "flashcards":        [],
        "quiz_questions":    [],
        "analysis_done":     False,
        "run_count":         0,
        "last_run_ts":       None,
        # quiz state
        "quiz_active":       False,
        "quiz_index":        0,
        "quiz_score":        0,
        "quiz_answers":      {},
        "quiz_finished":     False,
        # flashcard state
        "fc_index":          0,
        "fc_show_answer":    False,
        # input mode: 'youtube' | 'pdf' | 'audio' | 'text' | 'file'
        "input_mode":        "youtube",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """You are EchoStudy, an elite academic intelligence engine specialising in converting raw lecture notes, spoken summaries, PDF notes, or video transcripts into world-class study materials.

Your output is always a single, valid JSON object. No markdown fences, no preamble, no prose outside the JSON.

JSON Schema:
{
  "subject_title": "string — inferred or provided subject name",
  "topic_count": int,
  "estimated_read_time_mins": int,
  "difficulty_level": "Beginner | Intermediate | Advanced",
  "study_guide": {
    "overview": "2-3 sentence paragraph summarising the entire lecture/content",
    "key_concepts": [
      { "term": "string", "definition": "clear 1-2 sentence definition", "example": "concrete real-world example" }
    ],
    "important_formulas": ["string — only if applicable, else empty list"],
    "common_mistakes": ["string — common misconceptions students make"],
    "exam_tips": ["string — specific exam strategy tips based on the content"]
  },
  "flashcards": [
    {
      "id": int,
      "question": "string — concise, exam-style question",
      "answer": "string — clear, complete answer (2-4 sentences)",
      "difficulty": "Easy | Medium | Hard",
      "topic_tag": "string — sub-topic this card belongs to"
    }
  ],
  "quiz": [
    {
      "id": int,
      "question": "string — MCQ question",
      "options": {
        "A": "string",
        "B": "string",
        "C": "string",
        "D": "string"
      },
      "correct": "A | B | C | D",
      "explanation": "string — why the correct answer is right (1-2 sentences)"
    }
  ]
}

Rules:
- Generate EXACTLY 8 flashcards and EXACTLY 5 quiz questions.
- Flashcard questions must be high-yield, exam-style conceptual checks.
- Quiz distractors must be realistic and plausible.
- Return ONLY the JSON object.
"""


# ─────────────────────────────────────────────
#  HELPERS & API INTEGRATION
# ─────────────────────────────────────────────
def extract_youtube_video_id(url: str) -> str:
    """Extract 11-char YouTube video ID from various URL formats."""
    if not url:
        return ""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/|v\/|shorts\/|live\/)([0-9A-Za-z_-]{11})',
        r'youtu\.be\/([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def get_youtube_video_title(video_id: str) -> str:
    """Fetch video title using YouTube oEmbed without requiring an API key."""
    if not video_id:
        return ""
    try:
        url = f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={video_id}"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("title", "")
    except Exception:
        pass
    return ""


def fetch_youtube_transcript(video_id: str) -> tuple[str, list[dict]]:
    """Fetch full transcript and timestamped snippets for a YouTube video.
    Compatible with both old (<= 0.6.x) and new (>= 0.7.x) youtube-transcript-api versions.
    """
    if not video_id:
        raise ValueError("Invalid YouTube Video ID.")

    raw_snippets = None

    # ── Strategy 1: direct get_transcript (works in all versions) ──
    try:
        raw_snippets = YouTubeTranscriptApi.get_transcript(
            video_id, languages=['en', 'en-US', 'en-GB', 'en-IN']
        )
    except Exception:
        pass

    # ── Strategy 2: list_transcripts fallback (new API >= 0.7) ──
    if raw_snippets is None:
        try:
            ytt_api = YouTubeTranscriptApi()          # new versions are instantiated
            transcript_list = ytt_api.list(video_id)  # new API: .list()
            try:
                t = transcript_list.find_transcript(['en', 'en-US', 'en-GB', 'en-IN'])
            except Exception:
                try:
                    t = transcript_list.find_manually_created_transcript(
                        ['en', 'en-US', 'en-GB', 'en-IN']
                    )
                except Exception:
                    available = list(transcript_list)
                    if available:
                        try:
                            t = available[0].translate('en')
                        except Exception:
                            t = available[0]
                    else:
                        raise Exception("No captions found for this video.")
            fetched = t.fetch()
            # new API returns FetchedTranscript object; convert to list of dicts
            raw_snippets = list(fetched)
        except Exception:
            pass

    # ── Strategy 3: old list_transcripts API (<= 0.6) ──
    if raw_snippets is None:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                t = transcript_list.find_transcript(['en', 'en-US', 'en-GB', 'en-IN'])
            except Exception:
                try:
                    t = transcript_list.find_manually_created_transcript(
                        ['en', 'en-US', 'en-GB', 'en-IN']
                    )
                except Exception:
                    available = list(transcript_list)
                    if available:
                        try:
                            t = available[0].translate('en')
                        except Exception:
                            t = available[0]
                    else:
                        raise Exception("No captions found for this video.")
            raw_snippets = t.fetch()
        except Exception as e:
            raise Exception(f"Could not retrieve captions for YouTube video ({str(e)}).")

    if raw_snippets is None:
        raise Exception("Could not retrieve captions for this YouTube video.")

    formatted_snippets = []
    text_chunks = []

    for s in raw_snippets:
        if isinstance(s, dict):
            text     = s.get('text', '')
            start    = s.get('start', 0)
            duration = s.get('duration', 0)
        else:
            text     = getattr(s, 'text', '')
            start    = getattr(s, 'start', 0)
            duration = getattr(s, 'duration', 0)

        text = text.replace('\n', ' ').strip()
        if text:
            text_chunks.append(text)
            formatted_snippets.append({"start": start, "duration": duration, "text": text})

    full_transcript = " ".join(text_chunks)
    if not full_transcript.strip():
        raise Exception("YouTube transcript was empty or contains no spoken words.")
    return full_transcript, formatted_snippets


def extract_text_from_pdf(pdf_file) -> tuple[str, int, int]:
    """Extract text, page count, and word count from an uploaded PDF file."""
    reader = pypdf.PdfReader(pdf_file)
    page_count = len(reader.pages)
    text_chunks = []
    
    for i, page in enumerate(reader.pages, 1):
        page_text = page.extract_text() or ""
        page_text_clean = page_text.strip()
        if page_text_clean:
            text_chunks.append(f"--- [Page {i}] ---\n" + page_text_clean)
            
    full_text = "\n\n".join(text_chunks)
    word_count = len(full_text.split())
    if not full_text.strip():
        raise Exception("No readable text found in PDF. Scanned images or password-protected PDFs are not supported.")
    return full_text, page_count, word_count


def clean_and_parse_json(raw_text: str) -> dict:
    """Robust JSON parser that sanitizes model output and normalizes schema."""
    if not raw_text or not str(raw_text).strip():
        raise ValueError("Empty response received from AI model.")
    
    cleaned = str(raw_text).strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE).strip()
    
    data = None
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r'(\{.*\})', cleaned, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError:
                fixed = re.sub(r',\s*([\}\]])', r'\1', json_str)
                try:
                    data = json.loads(fixed)
                except json.JSONDecodeError:
                    pass
        if data is None:
            raise ValueError("Could not extract valid JSON structure from AI output. Please try again.")
            
    normalized = {
        "subject_title": data.get("subject_title", "General Study Pack"),
        "topic_count": int(data.get("topic_count", 0) or 0),
        "estimated_read_time_mins": int(data.get("estimated_read_time_mins", 5) or 5),
        "difficulty_level": data.get("difficulty_level", "Intermediate"),
        "study_guide": data.get("study_guide", {}) or {},
        "flashcards": data.get("flashcards", []) or [],
        "quiz": data.get("quiz", []) or []
    }
    
    sg = normalized["study_guide"]
    if not isinstance(sg, dict):
        sg = {}
    sg["overview"] = sg.get("overview", "Overview not generated.")
    sg["key_concepts"] = sg.get("key_concepts", []) or []
    sg["important_formulas"] = sg.get("important_formulas", []) or []
    sg["common_mistakes"] = sg.get("common_mistakes", []) or []
    sg["exam_tips"] = sg.get("exam_tips", []) or []
    normalized["study_guide"] = sg
    
    norm_cards = []
    for i, c in enumerate(normalized["flashcards"], 1):
        if isinstance(c, dict):
            norm_cards.append({
                "id": c.get("id", i),
                "question": c.get("question", "No question text"),
                "answer": c.get("answer", "No answer text"),
                "difficulty": c.get("difficulty", "Medium") if c.get("difficulty") in ["Easy", "Medium", "Hard"] else "Medium",
                "topic_tag": c.get("topic_tag", "Core Concept") or "Core Concept"
            })
    normalized["flashcards"] = norm_cards
    
    norm_quiz = []
    for i, q in enumerate(normalized["quiz"], 1):
        if isinstance(q, dict):
            opts = q.get("options", {}) or {}
            norm_quiz.append({
                "id": q.get("id", i),
                "question": q.get("question", "Question text missing"),
                "options": {
                    "A": opts.get("A", "Option A"),
                    "B": opts.get("B", "Option B"),
                    "C": opts.get("C", "Option C"),
                    "D": opts.get("D", "Option D"),
                },
                "correct": q.get("correct", "A") if q.get("correct") in ["A", "B", "C", "D"] else "A",
                "explanation": q.get("explanation", "No explanation provided.")
            })
    normalized["quiz"] = norm_quiz
    return normalized


def discover_active_models(api_key: str) -> list[str]:
    """Query live Google API for models that support generateContent."""
    if not api_key:
        return ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]
    
    found = []
    try:
        if HAS_GOOGLE_GENAI:
            client = genai.Client(api_key=api_key)
            for m in client.models.list():
                m_name = getattr(m, "name", "").replace("models/", "")
                if "gemini" in m_name and "embedding" not in m_name and "aqa" not in m_name:
                    found.append(m_name)
    except Exception:
        pass

    preferred_order = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-2.5-pro",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    ordered = [p for p in preferred_order if p in found]
    for f in found:
        if f not in ordered:
            ordered.append(f)
            
    return ordered or preferred_order


def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/wav", model_name: str = "gemini-2.5-flash") -> str:
    """Send audio bytes to Gemini for multimodal transcription with auto model fallback."""
    api_key = st.session_state.api_key.strip()
    
    live_models = discover_active_models(api_key)
    candidate_models = [model_name] + [m for m in live_models if m != model_name]
    
    prompt_text = f"""Transcribe this lecture recording or voice note accurately.
Subject context: {st.session_state.subject if st.session_state.subject else 'Not specified'}.
Output ONLY the clean transcription text — no labels, no timestamps, no preamble."""

    if HAS_GOOGLE_GENAI:
        client = genai.Client(api_key=api_key)
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        last_err = None
        for m in candidate_models:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=[audio_part, prompt_text]
                )
                return response.text.strip()
            except Exception as e:
                last_err = e
                if any(x in str(e).lower() for x in ["404", "not found", "is not supported"]):
                    continue
                else:
                    raise e
        raise last_err
    else:
        legacy_genai.configure(api_key=api_key)
        audio_part = {"mime_type": mime_type, "data": audio_bytes}
        last_err = None
        for m in candidate_models:
            try:
                model = legacy_genai.GenerativeModel(model_name=m)
                response = model.generate_content([audio_part, prompt_text])
                return response.text.strip()
            except Exception as e:
                last_err = e
                if any(x in str(e).lower() for x in ["404", "not found", "is not supported"]):
                    continue
                else:
                    raise e
        raise last_err


def generate_study_materials(transcript: str, subject: str, model_name: str = "gemini-2.5-flash") -> dict:
    """Generate structured study package with Gemini using live discovery and model fallback."""
    api_key = st.session_state.api_key.strip()
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""Today: {today}
Subject (if specified): {subject if subject.strip() else "Infer subject from content"}

--- CONTENT / TRANSCRIPT ---
{transcript}
--- END ---

Generate the complete study package according to the strict JSON schema."""

    live_models = discover_active_models(api_key)
    candidate_models = [model_name] + [m for m in live_models if m != model_name]

    if HAS_GOOGLE_GENAI:
        client = genai.Client(api_key=api_key)
        last_err = None
        for m in candidate_models:
            try:
                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.2,
                )
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=config
                )
                return clean_and_parse_json(response.text)
            except Exception as e:
                last_err = e
                if any(x in str(e).lower() for x in ["404", "not found", "is not supported", "not_found"]):
                    continue
                try:
                    config_fallback = types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,
                    )
                    response = client.models.generate_content(
                        model=m,
                        contents=prompt,
                        config=config_fallback
                    )
                    return clean_and_parse_json(response.text)
                except Exception as e2:
                    last_err = e2
                    continue
        raise last_err
    else:
        legacy_genai.configure(api_key=api_key)
        last_err = None
        for m in candidate_models:
            try:
                model = legacy_genai.GenerativeModel(
                    model_name=m,
                    system_instruction=SYSTEM_PROMPT
                )
                response = model.generate_content(prompt)
                return clean_and_parse_json(response.text)
            except Exception as e:
                last_err = e
                if any(x in str(e).lower() for x in ["404", "not found", "is not supported"]):
                    continue
                else:
                    raise e
        raise last_err


def reset_quiz():
    st.session_state.quiz_active   = True
    st.session_state.quiz_index    = 0
    st.session_state.quiz_score    = 0
    st.session_state.quiz_answers  = {}
    st.session_state.quiz_finished = False


def difficulty_badge(diff: str) -> str:
    cls_map = {"Easy": "diff-easy", "Medium": "diff-medium", "Hard": "diff-hard"}
    cls = cls_map.get(diff, "diff-medium")
    return f'<span class="fc-difficulty {cls}">{diff}</span>'


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sec-label">⚙ Configuration</div>', unsafe_allow_html=True)

    api_input = st.text_input(
        "Gemini API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="Enter your Gemini API key (AIza...)",
        help="Get your free API key at aistudio.google.com",
    )
    if api_input != st.session_state.api_key:
        st.session_state.api_key = api_input
        st.session_state.api_key_set = bool(api_input.strip())
        st.session_state.discovered_models = []

    # Model discovery
    if st.session_state.api_key_set and not st.session_state.discovered_models:
        st.session_state.discovered_models = discover_active_models(st.session_state.api_key)

    available_models = st.session_state.discovered_models or ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]
    
    def format_model_label(m_id: str) -> str:
        if "2.5-flash" in m_id:
            return "⚡ Gemini 2.5 Flash (Recommended)"
        elif "2.0-flash" in m_id:
            return "⚡ Gemini 2.0 Flash"
        elif "1.5-flash" in m_id:
            return "⚡ Gemini 1.5 Flash"
        elif "2.5-pro" in m_id:
            return "🧠 Gemini 2.5 Pro (Deep Analysis)"
        elif "1.5-pro" in m_id:
            return "🧠 Gemini 1.5 Pro"
        return f"✨ {m_id}"

    curr_idx = 0
    if st.session_state.selected_model in available_models:
        curr_idx = available_models.index(st.session_state.selected_model)

    selected_m = st.selectbox(
        "AI Model",
        options=available_models,
        format_func=format_model_label,
        index=curr_idx,
        help="Select your preferred model. If any model is unavailable, EchoStudy automatically routes to an active fallback."
    )
    st.session_state.selected_model = selected_m

    subject_input = st.text_input(
        "Subject / Topic",
        value=st.session_state.subject,
        placeholder="e.g. Operating Systems, Deep Learning",
        help="Optional: provides context to enhance AI accuracy",
    )
    st.session_state.subject = subject_input

    st.markdown("---")
    st.markdown('<div class="sec-label">📊 Session Stats</div>', unsafe_allow_html=True)

    fc_count = len(st.session_state.flashcards)
    qz_count = len(st.session_state.quiz_questions)
    score    = st.session_state.quiz_score

    st.markdown(f"""
    <div class="stat-pill"><span class="sp-label">Flashcards</span><span class="sp-value">{fc_count}</span></div>
    <div class="stat-pill"><span class="sp-label">Quiz Qs</span><span class="sp-value">{qz_count}</span></div>
    <div class="stat-pill"><span class="sp-label">Generations</span><span class="sp-value">{st.session_state.run_count}</span></div>
    """, unsafe_allow_html=True)

    if st.session_state.quiz_finished:
        pct = int(score / qz_count * 100) if qz_count else 0
        clr = '#059669' if pct>=60 else '#d97706' if pct>=40 else '#dc2626'
        st.markdown(f"""
        <div class="stat-pill"><span class="sp-label">Quiz Score</span>
        <span class="sp-value" style="color:{clr}">{score}/{qz_count}</span></div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Quick Demos with clean typography
    st.markdown('<div class="sec-label">🧪 Quick Demos</div>', unsafe_allow_html=True)
    if st.button("⚡ Load Sample Notes (OS)", use_container_width=True):
        st.session_state.input_mode = "text"
        st.session_state.subject = "Operating Systems - Process Scheduling"
        st.session_state.transcript_text = """
Okay so today we're covering process scheduling in operating systems. Basically the CPU can only run one process at a time, but we have hundreds of processes wanting CPU time. The OS uses a scheduler to decide which process gets CPU time.

First algorithm is FCFS, First Come First Serve - processes are executed in arrival order. Very simple, but suffers from the convoy effect where short processes wait behind long CPU bursts.

Second is SJF, Shortest Job First. It picks the process with the smallest CPU burst time next. It is mathematically optimal for minimizing average waiting time, but suffers from starvation for long processes.

Third is Round Robin (RR). Each process gets a fixed time slice or quantum (e.g. 20ms). Once expired, it is preempted. If quantum is too small, context switching overhead dominates; if too large, it degrades into FCFS.

Fourth is Priority Scheduling. Highest priority runs first. Starvation is solved using aging (gradually boosting priority of waiting processes).

Multilevel Queue divides ready queues by type (foreground vs background) with individual algorithms. For the exam, know how to calculate average waiting time and turnaround time using Gantt charts.
        """.strip()
        st.rerun()

    if st.button("📄 Load Sample PDF (DBMS ACID)", use_container_width=True):
        st.session_state.input_mode = "pdf"
        st.session_state.pdf_name = "DBMS_Transactions_and_ACID_Properties.pdf"
        st.session_state.pdf_pages = 3
        sample_pdf_text = """--- [Page 1] ---
DATABASE MANAGEMENT SYSTEMS (CS301)
Lecture 14: Transaction Processing & ACID Properties

1. What is a Transaction?
A transaction is a single logical unit of work that accesses and possibly modifies the contents of a database. Transactions are initiated by user programs written in high-level data manipulation language (SQL) or programming languages embedded with SQL.

2. The ACID Properties
To ensure data integrity and database consistency in multi-user concurrent environments, every DBMS enforces four fundamental properties known as ACID:

- Atomicity ("All or Nothing"): Either all operations of the transaction are reflected properly in the database, or none are. If a crash occurs halfway, rollback occurs via the recovery manager.
- Consistency: Execution of a transaction in isolation preserves database consistency and validity constraints (e.g. sum of account balances before and after transfer must remain identical).
- Isolation: Even though multiple transactions execute concurrently, the system guarantees that for every pair of transactions Ti and Tj, Ti does not see the intermediate uncommitted state of Tj.
- Durability: Once a transaction commits successfully, its changes persist permanently in non-volatile storage, surviving subsequent system crashes or power failures.

--- [Page 2] ---
3. Concurrency Control & Serializability
When transactions execute concurrently without proper isolation, several anomalies can arise:
- Dirty Read (Read Uncommitted): Reading data modified by an uncommitted transaction that later aborts.
- Non-Repeatable Read: Re-reading the same row within a transaction and getting different values because another committed transaction updated it.
- Phantom Read: A query executing twice within a transaction retrieves different sets of rows due to concurrent inserts.

Serializability is the gold standard criterion for database correctness. A concurrent schedule is serializable if its outcome is equivalent to some serial execution of the same transactions:
- Conflict Serializability: Checked using Precedence Graphs (Serialization Graph). If the graph contains a cycle, the schedule is NOT conflict serializable.
- View Serializability: A strictly broader condition than conflict serializability, but NP-complete to test in general.

--- [Page 3] ---
4. Lock-Based Protocols & Two-Phase Locking (2PL)
- Shared Lock (S-Lock): Allows read access. Multiple transactions can hold S-locks concurrently.
- Exclusive Lock (X-Lock): Allows read and write access. Only one transaction can hold an X-lock.

Two-Phase Locking (2PL) Protocol guarantees Conflict Serializability:
1. Growing Phase: A transaction may obtain locks, but cannot release any lock.
2. Shrinking Phase: A transaction may release locks, but cannot acquire any new locks.

Strict 2PL: Releases all exclusive locks only at commit/abort time. This avoids cascading aborts and ensures recoverable schedules.

5. Write-Ahead Logging (WAL)
WAL rule states: The log record representing a change must be flushed to stable disk before the corresponding dirty database page is written to disk. This ensures Atomicity and Durability using the ARIES recovery algorithm (Analysis, Redo, Undo)."""
        st.session_state.transcript_text = sample_pdf_text.strip()
        st.session_state.pdf_words = len(st.session_state.transcript_text.split())
        st.session_state.subject = "Database Management Systems - Transactions & ACID"
        st.rerun()

    if st.button("🎥 Load Sample YouTube (Neural Nets)", use_container_width=True):
        st.session_state.input_mode = "youtube"
        st.session_state.yt_url = "https://www.youtube.com/watch?v=aircAruvnKk"
        st.session_state.subject = "Neural Networks & Deep Learning"
        st.rerun()

    st.markdown("---")
    with st.expander("ℹ️ About EchoStudy"):
        st.markdown("""
        <div style="font-family:'DM Mono',monospace; font-size:0.75rem; color:#64748b; line-height:1.8;">
        <b style="color:#6366f1; font-weight:700;">EchoStudy v2.0</b><br>
        Powered by Google Gemini AI<br><br>
        <span style="font-weight:600; color:#334155;">Features:</span><br>
        ✅ 🎥 YouTube Video to StudyPack<br>
        ✅ 📄 PDF Notes Document Ingestion<br>
        ✅ 🎙️ Mic Voice Recording<br>
        ✅ 📁 Audio File Upload<br>
        ✅ 📖 Structured Study Guide<br>
        ✅ 🃏 8 Exam Flashcards<br>
        ✅ 🧠 5-Question MCQ Quiz<br>
        ✅ 📤 CSV / JSON / MD Export
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="echo-hero">
    <h1>🎙️ EchoStudy</h1>
    <p>Convert lecture voice notes, typed notes, <b>PDF documents</b>, or <b>YouTube video links</b> into an interactive study pack.<br>
    Flashcards, Study Guide, and Practice Quiz — generated in seconds by Gemini AI.</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.api_key_set:
    st.info("🔑 Please enter your **Gemini API Key** in the sidebar to get started. Free at [aistudio.google.com](https://aistudio.google.com)", icon="ℹ️")
    st.stop()


# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
tab_input, tab_guide, tab_flash, tab_quiz, tab_export = st.tabs([
    "📥  Input & Generation",
    "📖  Study Guide",
    "🃏  Flashcards",
    "🧠  Quiz",
    "📤  Export",
])


# ══════════════════════════════════════════════
#  TAB 1 — INPUT & GENERATION
# ══════════════════════════════════════════════
with tab_input:
    st.markdown('<div class="sec-label">1. Choose Input Source</div>', unsafe_allow_html=True)

    mode_c1, mode_c2, mode_c3, mode_c4, mode_c5 = st.columns(5)
    with mode_c1:
        yt_cls = "mode-btn-active" if st.session_state.input_mode == "youtube" else "mode-btn-inactive"
        st.markdown(f'<div class="{yt_cls}">', unsafe_allow_html=True)
        if st.button("🎥  YouTube Link", use_container_width=True, key="btn_mode_yt"):
            st.session_state.input_mode = "youtube"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with mode_c2:
        pdf_cls = "mode-btn-active" if st.session_state.input_mode == "pdf" else "mode-btn-inactive"
        st.markdown(f'<div class="{pdf_cls}">', unsafe_allow_html=True)
        if st.button("📄  PDF Notes", use_container_width=True, key="btn_mode_pdf"):
            st.session_state.input_mode = "pdf"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with mode_c3:
        mic_cls = "mode-btn-active" if st.session_state.input_mode == "audio" else "mode-btn-inactive"
        st.markdown(f'<div class="{mic_cls}">', unsafe_allow_html=True)
        if st.button("🎙️  Voice Recording", use_container_width=True, key="btn_mode_mic"):
            st.session_state.input_mode = "audio"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with mode_c4:
        txt_cls = "mode-btn-active" if st.session_state.input_mode == "text" else "mode-btn-inactive"
        st.markdown(f'<div class="{txt_cls}">', unsafe_allow_html=True)
        if st.button("✏️  Type / Paste Notes", use_container_width=True, key="btn_mode_txt"):
            st.session_state.input_mode = "text"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with mode_c5:
        file_cls = "mode-btn-active" if st.session_state.input_mode == "file" else "mode-btn-inactive"
        st.markdown(f'<div class="{file_cls}">', unsafe_allow_html=True)
        if st.button("📁  Audio File", use_container_width=True, key="btn_mode_file"):
            st.session_state.input_mode = "file"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    final_content_to_process = ""

    # ─────────────────────────────────────────
    # MODE A: YOUTUBE LINK
    # ─────────────────────────────────────────
    if st.session_state.input_mode == "youtube":
        st.markdown("""
        <div style="font-size:1.15rem; font-weight:700; color:#0f172a; margin-bottom:4px;">
            🎥 YouTube Video to StudyPack
        </div>
        <div style="font-size:0.9rem; font-weight:400; color:#475569; margin-bottom:14px;">
            Paste any educational YouTube lecture, tutorial, or video link. EchoStudy will extract the transcript and generate complete study materials.
        </div>
        """, unsafe_allow_html=True)

        col_url, col_fetch = st.columns([3.5, 1.2])
        with col_url:
            yt_input = st.text_input(
                "YouTube Video URL",
                value=st.session_state.yt_url,
                placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/...",
                label_visibility="collapsed",
            )
            st.session_state.yt_url = yt_input

        video_id = extract_youtube_video_id(yt_input)

        if video_id:
            st.session_state.yt_video_id = video_id
            
            if not st.session_state.yt_video_title or st.session_state.yt_video_id != video_id:
                title = get_youtube_video_title(video_id)
                if title:
                    st.session_state.yt_video_title = title
                    if not st.session_state.subject:
                        st.session_state.subject = title

            col_vid, col_info = st.columns([1.5, 2])
            with col_vid:
                st.video(f"https://www.youtube.com/watch?v={video_id}")
            with col_info:
                st.markdown(f"""
                <div class="yt-card">
                    <span class="yt-badge">▶ YouTube Video</span>
                    <h3 style="margin: 10px 0 4px; font-weight:700; color:#0f172a;">{st.session_state.yt_video_title or 'YouTube Lecture'}</h3>
                    <p style="font-size:0.82rem; font-weight:500; color:#64748b; font-family:'DM Mono',monospace; margin-bottom:0;">Video ID: {video_id}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.button("📥 Fetch Video Transcript", use_container_width=True):
                    with st.spinner("Extracting captions and transcript from YouTube..."):
                        try:
                            transcript_text, snippets = fetch_youtube_transcript(video_id)
                            st.session_state.transcript_text = transcript_text
                            st.success(f"✅ Extracted transcript ({len(transcript_text.split())} words, {len(snippets)} snippets)!")
                        except Exception as e:
                            st.error(f"❌ Failed to extract transcript: {str(e)}")

        if st.session_state.transcript_text:
            with st.expander("📝 Extracted YouTube Transcript Preview", expanded=False):
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:14px;
                            font-size:0.88rem; font-weight:400; color:#334155; line-height:1.7; max-height:260px; overflow-y:auto;">
                    {st.session_state.transcript_text}
                </div>
                """, unsafe_allow_html=True)

        final_content_to_process = st.session_state.transcript_text

    # ─────────────────────────────────────────
    # MODE B: PDF NOTES UPLOAD
    # ─────────────────────────────────────────
    elif st.session_state.input_mode == "pdf":
        st.markdown("""
        <div style="font-size:1.15rem; font-weight:700; color:#0f172a; margin-bottom:4px;">
            📄 PDF Notes & Lecture Slide Ingestion
        </div>
        <div style="font-size:0.9rem; font-weight:400; color:#475569; margin-bottom:14px;">
            Upload lecture notes, textbooks, slides, or research papers (.pdf). EchoStudy extracts the text and builds high-yield flashcards and quizzes.
        </div>
        """, unsafe_allow_html=True)

        uploaded_pdf = st.file_uploader(
            "Upload Notes PDF",
            type=["pdf"],
            help="Upload any PDF notes or slide decks",
            label_visibility="collapsed"
        )

        if uploaded_pdf is not None:
            if st.session_state.pdf_name != uploaded_pdf.name:
                with st.spinner(f"Extracting text from {uploaded_pdf.name}..."):
                    try:
                        pdf_text, pages, words = extract_text_from_pdf(uploaded_pdf)
                        st.session_state.transcript_text = pdf_text
                        st.session_state.pdf_name = uploaded_pdf.name
                        st.session_state.pdf_pages = pages
                        st.session_state.pdf_words = words

                        if not st.session_state.subject:
                            clean_subj = re.sub(r'\.pdf$', '', uploaded_pdf.name, flags=re.IGNORECASE)
                            clean_subj = clean_subj.replace('_', ' ').replace('-', ' ').title()
                            st.session_state.subject = clean_subj
                        st.success(f"✅ Extracted {words:,} words from {pages} PDF pages!")
                    except Exception as e:
                        st.error(f"❌ Failed to extract PDF text: {str(e)}")

        if st.session_state.pdf_name and st.session_state.transcript_text:
            st.markdown(f"""
            <div class="pdf-card">
                <span class="pdf-badge">📄 PDF Document</span>
                <h3 style="margin: 10px 0 4px; font-weight:700; color:#0f172a;">{st.session_state.pdf_name}</h3>
                <p style="font-size:0.84rem; font-weight:500; color:#64748b; font-family:'DM Mono',monospace; margin-bottom:0;">
                    {st.session_state.pdf_pages} Pages · {st.session_state.pdf_words:,} Words
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("📝 Extracted PDF Text Preview", expanded=False):
                st.markdown(f"""
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:14px;
                            font-size:0.88rem; font-weight:400; color:#334155; line-height:1.7; max-height:260px; overflow-y:auto;">
                    {st.session_state.transcript_text}
                </div>
                """, unsafe_allow_html=True)

        final_content_to_process = st.session_state.transcript_text

    # ─────────────────────────────────────────
    # MODE C: LIVE AUDIO RECORDING
    # ─────────────────────────────────────────
    elif st.session_state.input_mode == "audio":
        st.markdown("""
        <div style="text-align:center; padding: 6px 0;">
            <div style="font-size:1.15rem; font-weight:700; color:#0f172a;">
                🎙️ Record Your Lecture Notes
            </div>
            <div style="font-size:0.88rem; font-weight:400; color:#64748b; margin-top:4px;">
                Speak naturally into your microphone. Gemini multimodal AI will transcribe and clean it up.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="waveform">
            <div class="wave-bar"></div><div class="wave-bar"></div>
            <div class="wave-bar"></div><div class="wave-bar"></div>
            <div class="wave-bar"></div><div class="wave-bar"></div>
            <div class="wave-bar"></div><div class="wave-bar"></div>
            <div class="wave-bar"></div><div class="wave-bar"></div>
            <div class="wave-bar"></div><div class="wave-bar"></div>
        </div>
        """, unsafe_allow_html=True)

        audio_mic = st.audio_input("Record audio", label_visibility="collapsed")
        if audio_mic is not None:
            if st.button("📡 Transcribe Recording", use_container_width=True):
                with st.spinner("Gemini is transcribing your voice recording..."):
                    try:
                        audio_bytes = audio_mic.read()
                        mime_type = getattr(audio_mic, "type", "audio/wav") or "audio/wav"
                        st.session_state.transcript_text = transcribe_audio(
                            audio_bytes,
                            mime_type=mime_type,
                            model_name=st.session_state.selected_model
                        )
                        st.success("✅ Voice transcription successful!")
                    except Exception as e:
                        st.error(f"❌ Transcription failed: {str(e)}")

        final_content_to_process = st.session_state.transcript_text

    # ─────────────────────────────────────────
    # MODE D: TYPE / PASTE NOTES
    # ─────────────────────────────────────────
    elif st.session_state.input_mode == "text":
        st.markdown("""
        <div style="font-size:1.15rem; font-weight:700; color:#0f172a; margin-bottom:6px;">
            ✏️ Paste or Type Lecture Notes
        </div>
        <div style="font-size:0.88rem; font-weight:400; color:#64748b; margin-bottom:12px;">
            Input your lecture notes, summaries, or syllabus topics.
        </div>
        """, unsafe_allow_html=True)

        text_val = st.text_area(
            "Notes Text",
            height=280,
            value=st.session_state.transcript_text,
            placeholder="Paste raw lecture notes, article text, or bullet points here...",
            label_visibility="collapsed",
        )
        st.session_state.transcript_text = text_val
        final_content_to_process = text_val

    # ─────────────────────────────────────────
    # MODE E: AUDIO FILE UPLOAD
    # ─────────────────────────────────────────
    elif st.session_state.input_mode == "file":
        st.markdown("""
        <div style="font-size:1.15rem; font-weight:700; color:#0f172a; margin-bottom:6px;">
            📁 Upload Audio Lecture File
        </div>
        <div style="font-size:0.88rem; font-weight:400; color:#64748b; margin-bottom:12px;">
            Upload pre-recorded audio lectures (.mp3, .wav, .m4a, .ogg, .webm).
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload Audio",
            type=["wav", "mp3", "m4a", "ogg", "webm"],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            st.audio(uploaded_file)
            if st.button("📡 Transcribe Uploaded Audio", use_container_width=True):
                with st.spinner("Gemini is transcribing your uploaded audio file..."):
                    try:
                        audio_bytes = uploaded_file.read()
                        mime_type = uploaded_file.type or "audio/wav"
                        st.session_state.transcript_text = transcribe_audio(
                            audio_bytes,
                            mime_type=mime_type,
                            model_name=st.session_state.selected_model
                        )
                        st.success("✅ File transcription successful!")
                    except Exception as e:
                        st.error(f"❌ Transcription failed: {str(e)}")

        final_content_to_process = st.session_state.transcript_text

    st.markdown("---")

    # ─────────────────────────────────────────
    # GENERATION ACTION BAR
    # ─────────────────────────────────────────
    st.markdown('<div class="sec-label">2. Generate Complete Study Pack</div>', unsafe_allow_html=True)

    btn_col1, btn_col2, _ = st.columns([2.2, 1, 2.5])
    with btn_col1:
        st.markdown('<div class="main-generate-btn">', unsafe_allow_html=True)
        generate_clicked = st.button("⚡ Generate Study Pack", use_container_width=True, key="main_gen_btn")
        st.markdown('</div>', unsafe_allow_html=True)
    with btn_col2:
        clear_clicked = st.button("🗑️ Clear All", use_container_width=True)

    if clear_clicked:
        for k in ["transcript_text", "study_guide", "flashcards", "quiz_questions",
                  "analysis_done", "quiz_active", "quiz_index", "quiz_score",
                  "quiz_answers", "quiz_finished", "fc_index", "fc_show_answer",
                  "yt_url", "yt_video_id", "yt_video_title", "pdf_name", "pdf_pages", "pdf_words", "subject"]:
            if k in ["flashcards", "quiz_questions"]:
                st.session_state[k] = []
            elif k == "quiz_answers":
                st.session_state[k] = {}
            elif k in ["analysis_done", "quiz_active", "quiz_finished", "fc_show_answer"]:
                st.session_state[k] = False
            elif k in ["quiz_index", "quiz_score", "fc_index", "pdf_pages", "pdf_words"]:
                st.session_state[k] = 0
            elif k == "study_guide":
                st.session_state[k] = None
            else:
                st.session_state[k] = ""
        st.success("Cleared all inputs and generated data.")
        st.rerun()

    if generate_clicked:
        if st.session_state.input_mode == "youtube" and not final_content_to_process.strip():
            vid = extract_youtube_video_id(st.session_state.yt_url)
            if vid:
                with st.spinner("Fetching YouTube transcript..."):
                    try:
                        t_text, _ = fetch_youtube_transcript(vid)
                        st.session_state.transcript_text = t_text
                        final_content_to_process = t_text
                    except Exception as e:
                        st.error(f"❌ Could not fetch YouTube transcript: {str(e)}")
                        st.stop()
            else:
                st.error("⚠️ Please provide a valid YouTube video URL.", icon="🚫")
                st.stop()

        if not final_content_to_process or len(final_content_to_process.strip().split()) < 10:
            st.error("⚠️ Please provide lecture notes, upload a PDF, record voice, or load a YouTube video first.", icon="🚫")
            st.stop()

        prog = st.progress(0, text="🧠 Analyzing content with Gemini...")
        try:
            prog.progress(35, text=f"⚡ Processing with {st.session_state.selected_model}...")
            result = generate_study_materials(
                final_content_to_process,
                st.session_state.subject,
                model_name=st.session_state.selected_model
            )

            prog.progress(75, text="🃏 Assembling flashcards, study guide, and quiz...")
            time.sleep(0.3)

            st.session_state.study_guide    = result.get("study_guide", {})
            st.session_state.flashcards     = result.get("flashcards", [])
            st.session_state.quiz_questions = result.get("quiz", [])
            st.session_state.analysis_done  = True
            st.session_state.run_count     += 1
            st.session_state.last_run_ts    = datetime.now().strftime("%H:%M:%S")
            st.session_state.fc_index       = 0
            st.session_state.fc_show_answer = False

            if not st.session_state.subject and result.get("subject_title"):
                st.session_state.subject = result.get("subject_title")

            reset_quiz()

            prog.progress(100, text="✅ Study Pack Ready!")
            time.sleep(0.4)
            prog.empty()

            st.success("🎉 Your Study Pack has been generated! Explore the tabs above.", icon="✨")

            r = result
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Flashcards", len(st.session_state.flashcards), delta="8 cards")
            with m2: st.metric("Quiz Questions", len(st.session_state.quiz_questions), delta="5 practice Qs")
            with m3: st.metric("Key Concepts", len(r.get("study_guide", {}).get("key_concepts", [])), delta="defined")
            with m4: st.metric("Difficulty", r.get("difficulty_level", "Intermediate"), delta=f"~{r.get('estimated_read_time_mins', 5)} min read")

        except Exception as e:
            prog.empty()
            st.error(f"❌ Generation failed: {str(e)}", icon="🚫")


# ══════════════════════════════════════════════
#  TAB 2 — STUDY GUIDE
# ══════════════════════════════════════════════
with tab_guide:
    if not st.session_state.analysis_done or not st.session_state.study_guide:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#64748b;">
            <div style="font-size:3rem">📖</div>
            <div style="margin-top:12px; font-size:1.15rem; color:#0f172a; font-weight:700;">No Study Guide Generated Yet</div>
            <div style="font-size:0.88rem; margin-top:6px; font-weight:400; color:#64748b;">Go to the <b>Input</b> tab to record audio, paste notes, upload a PDF, or provide a YouTube link.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        sg = st.session_state.study_guide
        concepts = sg.get("key_concepts", [])
        mistakes = sg.get("common_mistakes", [])
        tips     = sg.get("exam_tips", [])
        formulas = sg.get("important_formulas", [])

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Key Concepts", len(concepts), delta="with examples")
        with c2: st.metric("Common Mistakes", len(mistakes), delta="to avoid")
        with c3: st.metric("Exam Tips", len(tips), delta="strategy points")

        st.markdown("---")

        st.markdown('<div class="sec-label">Overview</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="guide-block">
            <p>{sg.get("overview", "No overview available.")}</p>
        </div>
        """, unsafe_allow_html=True)

        if concepts:
            st.markdown('<div class="sec-label" style="margin-top:24px">Key Concepts & Terminology</div>', unsafe_allow_html=True)
            for c in concepts:
                with st.expander(f"📌 {c.get('term', 'Concept')}", expanded=False):
                    col_d, col_e = st.columns([1, 1])
                    with col_d:
                        st.markdown(f"""
                        <div style="font-size:0.92rem; font-weight:400; color:#334155; line-height:1.7;">
                            <b style="color:#6366f1; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Definition</b><br>
                            {c.get('definition', '')}
                        </div>
                        """, unsafe_allow_html=True)
                    with col_e:
                        st.markdown(f"""
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px;
                                    font-size:0.92rem; font-weight:400; color:#334155; line-height:1.7;">
                            <b style="color:#d97706; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Real-World Example</b><br>
                            {c.get('example', '')}
                        </div>
                        """, unsafe_allow_html=True)

        if formulas:
            st.markdown('<div class="sec-label" style="margin-top:24px">Important Formulas & Relationships</div>', unsafe_allow_html=True)
            for f in formulas:
                st.markdown(f"""
                <div style="background:#f5f3ff; border:1px solid #c7d2fe; border-radius:8px;
                            padding:12px 18px; margin-bottom:8px; font-family:'DM Mono',monospace;
                            font-size:0.92rem; font-weight:500; color:#312e81;">
                    {f}
                </div>
                """, unsafe_allow_html=True)

        if mistakes:
            st.markdown('<div class="sec-label" style="margin-top:24px">⚠️ Common Misconceptions to Avoid</div>', unsafe_allow_html=True)
            with st.expander("Click to review common student mistakes", expanded=True):
                for m in mistakes:
                    st.markdown(f"""
                    <div style="display:flex; gap:10px; padding:10px 0; border-bottom:1px solid #e2e8f0;
                                font-size:0.92rem; font-weight:400; color:#334155;">
                        <span style="color:#dc2626; font-weight:700;">✕</span>
                        <span>{m}</span>
                    </div>
                    """, unsafe_allow_html=True)

        if tips:
            st.markdown('<div class="sec-label" style="margin-top:24px">🎯 High-Yield Exam Tips</div>', unsafe_allow_html=True)
            for i, tip in enumerate(tips, 1):
                st.markdown(f"""
                <div class="guide-block">
                    <h4>Exam Strategy {i}</h4>
                    <p>{tip}</p>
                </div>
                """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  TAB 3 — FLASHCARDS
# ══════════════════════════════════════════════
with tab_flash:
    if not st.session_state.analysis_done or not st.session_state.flashcards:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#64748b;">
            <div style="font-size:3rem">🃏</div>
            <div style="margin-top:12px; font-size:1.15rem; color:#0f172a; font-weight:700;">No Flashcards Available</div>
            <div style="font-size:0.88rem; margin-top:6px; font-weight:400; color:#64748b;">Generate your study pack to build an active recall deck.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        cards = st.session_state.flashcards
        total = len(cards)
        idx   = min(st.session_state.fc_index, max(0, total - 1))

        easy   = sum(1 for c in cards if c.get("difficulty") == "Easy")
        medium = sum(1 for c in cards if c.get("difficulty") == "Medium")
        hard   = sum(1 for c in cards if c.get("difficulty") == "Hard")

        k1, k2, k3, k4 = st.columns(4)
        with k1: st.metric("Total Cards", total, delta="in this deck")
        with k2: st.metric("🟢 Easy", easy, delta=f"{round(easy/total*100) if total else 0}%")
        with k3: st.metric("🟡 Medium", medium, delta=f"{round(medium/total*100) if total else 0}%")
        with k4: st.metric("🔴 Hard", hard, delta=f"{round(hard/total*100) if total else 0}%")

        st.markdown("---")

        view_mode = st.radio(
            "Flashcard View Mode",
            ["🎴 One at a Time", "📋 All Cards", "📊 Card Table Editor"],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.markdown("---")

        if view_mode == "🎴 One at a Time":
            card = cards[idx]
            nav1, nav2, nav3, nav4 = st.columns([1, 1, 2, 1])
            with nav1:
                if st.button("◀ Previous", use_container_width=True, disabled=(idx == 0)):
                    st.session_state.fc_index = max(0, idx - 1)
                    st.session_state.fc_show_answer = False
                    st.rerun()
            with nav2:
                if st.button("Next ▶", use_container_width=True, disabled=(idx == total - 1)):
                    st.session_state.fc_index = min(total - 1, idx + 1)
                    st.session_state.fc_show_answer = False
                    st.rerun()
            with nav3:
                st.markdown(f"""
                <div style="text-align:center; font-family:'DM Mono',monospace; font-size:0.84rem; font-weight:600; color:#64748b; padding-top:10px;">
                    Card {idx + 1} of {total} · {card.get('topic_tag', 'General')}
                </div>
                """, unsafe_allow_html=True)
            with nav4:
                if st.button("🔀 Shuffle", use_container_width=True):
                    st.session_state.fc_index = random.randint(0, total - 1)
                    st.session_state.fc_show_answer = False
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            show_ans = st.session_state.fc_show_answer
            ans_html = f"<div class='fc-a'><b style='color:#6366f1; font-size:0.78rem; font-weight:700; text-transform:uppercase; letter-spacing:1px;'>Answer</b><br>{card.get('answer','')}</div>" if show_ans else "<div style='color:#64748b; font-size:0.86rem; font-style:italic; margin-top:14px;'>Click below to reveal answer →</div>"

            st.markdown(f"""
            <div class="flashcard">
                <span class="fc-num">#{card.get('id', idx+1):02d}</span>
                <div class="fc-tag">Topic: {card.get('topic_tag', 'General')}</div>
                {difficulty_badge(card.get('difficulty', 'Medium'))}
                <div class="fc-q">{card.get('question', '')}</div>
                {ans_html}
            </div>
            """, unsafe_allow_html=True)

            col_rev, _ = st.columns([1.5, 3])
            with col_rev:
                if not show_ans:
                    if st.button("👁️ Reveal Answer", use_container_width=True):
                        st.session_state.fc_show_answer = True
                        st.rerun()
                else:
                    if st.button("🙈 Hide Answer", use_container_width=True):
                        st.session_state.fc_show_answer = False
                        st.rerun()

        elif view_mode == "📋 All Cards":
            diff_filter = st.selectbox("Filter by difficulty", ["All", "Easy", "Medium", "Hard"])
            filtered = [c for c in cards if diff_filter == "All" or c.get("difficulty") == diff_filter]
            st.caption(f"Showing {len(filtered)} of {total} flashcards")

            for c in filtered:
                with st.expander(f"#{c.get('id', 0):02d} · {c.get('question', '')[:90]}..."):
                    cq, ca = st.columns([1, 1])
                    with cq:
                        st.markdown(f"""
                        <div style="font-size:0.92rem; font-weight:400; color:#0f172a; line-height:1.65;">
                            <b style="color:#6366f1; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Question</b><br>
                            {c.get('question', '')}
                        </div>
                        """, unsafe_allow_html=True)
                    with ca:
                        st.markdown(f"""
                        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; font-size:0.92rem; font-weight:400; color:#334155; line-height:1.65;">
                            <b style="color:#059669; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Answer</b><br>
                            {c.get('answer', '')}
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown(f"{difficulty_badge(c.get('difficulty', 'Medium'))} &nbsp; <span style='font-size:0.78rem; font-weight:500; color:#64748b;'>Topic: {c.get('topic_tag','')}</span>", unsafe_allow_html=True)

        else:
            df_cards = pd.DataFrame(cards)[["id", "question", "answer", "difficulty", "topic_tag"]]
            df_cards.columns = ["#", "Question", "Answer", "Difficulty", "Topic"]
            st.data_editor(
                df_cards,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                column_config={
                    "#":          st.column_config.NumberColumn(width="small"),
                    "Question":   st.column_config.TextColumn(width="large"),
                    "Answer":     st.column_config.TextColumn(width="large"),
                    "Difficulty": st.column_config.SelectboxColumn(options=["Easy", "Medium", "Hard"], width="small"),
                    "Topic":      st.column_config.TextColumn(width="medium"),
                },
            )


# ══════════════════════════════════════════════
#  TAB 4 — QUIZ
# ══════════════════════════════════════════════
with tab_quiz:
    if not st.session_state.analysis_done or not st.session_state.quiz_questions:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#64748b;">
            <div style="font-size:3rem">🧠</div>
            <div style="margin-top:12px; font-size:1.15rem; color:#0f172a; font-weight:700;">Quiz Not Ready</div>
            <div style="font-size:0.88rem; margin-top:6px; font-weight:400; color:#64748b;">Generate your study pack to unlock an interactive 5-question quiz.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        questions = st.session_state.quiz_questions
        total_q   = len(questions)

        if not st.session_state.quiz_active and not st.session_state.quiz_finished:
            st.markdown(f"""
            <div style="text-align:center; padding:40px 20px;">
                <div style="font-size:3.5rem; margin-bottom:12px">🧠</div>
                <div style="font-size:1.5rem; font-weight:800; color:#0f172a;">
                    Ready for a Knowledge Check?
                </div>
                <div style="font-size:0.92rem; font-weight:400; color:#64748b; margin-top:8px;">
                    {total_q} Multiple Choice Questions · Instant Evaluation · Detailed Explanations
                </div>
            </div>
            """, unsafe_allow_html=True)
            c_start, _, _ = st.columns([1.5, 2, 1])
            with c_start:
                if st.button("🚀 Start Interactive Quiz", use_container_width=True):
                    reset_quiz()
                    st.rerun()

        elif st.session_state.quiz_active and not st.session_state.quiz_finished:
            q_idx = st.session_state.quiz_index
            q     = questions[q_idx]

            progress_pct = (q_idx) / total_q
            st.progress(progress_pct, text=f"Question {q_idx + 1} of {total_q}")

            sc1, sc2, sc3 = st.columns(3)
            with sc1: st.metric("Current Question", f"{q_idx + 1}/{total_q}")
            with sc2: st.metric("Score", f"{st.session_state.quiz_score}")
            with sc3: st.metric("Remaining", f"{total_q - q_idx - 1}")

            st.markdown("---")

            st.markdown(f"""
            <div style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid #6366f1;
                        border-radius:12px; padding:22px 26px; margin-bottom:18px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                <div style="font-family:'DM Mono',monospace; font-size:0.72rem; font-weight:600; color:#64748b;
                            text-transform:uppercase; letter-spacing:2px; margin-bottom:8px;">
                    Question {q_idx + 1}
                </div>
                <div style="font-size:1.15rem; font-weight:700; color:#0f172a; line-height:1.5;">
                    {q.get('question', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            already_answered = q_idx in st.session_state.quiz_answers
            correct_opt      = q.get("correct", "A")
            opts             = q.get("options", {})

            for opt_key in ["A", "B", "C", "D"]:
                opt_val = opts.get(opt_key, "")
                if not opt_val:
                    continue

                if already_answered:
                    chosen = st.session_state.quiz_answers.get(q_idx)
                    if opt_key == correct_opt:
                        bg_style = "background:#ecfdf5; border:1px solid #10b981; color:#065f46;"
                    elif opt_key == chosen and chosen != correct_opt:
                        bg_style = "background:#fef2f2; border:1px solid #ef4444; color:#991b1b;"
                    else:
                        bg_style = "background:#ffffff; border:1px solid #e2e8f0; color:#64748b;"

                    badge = "  ✓ Correct" if opt_key == correct_opt else ("  ✗ Your choice" if opt_key == chosen else "")
                    st.markdown(f"""
                    <div style="{bg_style} border-radius:10px; padding:14px 18px; margin-bottom:8px;
                                font-size:0.92rem; font-weight:500;">
                        <b>{opt_key}.</b> {opt_val} <b>{badge}</b>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(f"{opt_key}.  {opt_val}", key=f"q{q_idx}_opt_{opt_key}", use_container_width=True):
                        st.session_state.quiz_answers[q_idx] = opt_key
                        if opt_key == correct_opt:
                            st.session_state.quiz_score += 1
                        st.rerun()

            if already_answered:
                st.markdown(f"""
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;
                            padding:14px 18px; margin-top:12px;">
                    <div style="font-size:0.75rem; color:#6366f1; text-transform:uppercase;
                                letter-spacing:1px; margin-bottom:6px; font-weight:700;">💡 Explanation</div>
                    <div style="font-size:0.92rem; font-weight:400; color:#334155; line-height:1.65;">
                        {q.get('explanation', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                btn_label = "🏁 Finish Quiz & View Results" if q_idx == total_q - 1 else "Next Question ▶"
                if st.button(btn_label, use_container_width=False):
                    if q_idx < total_q - 1:
                        st.session_state.quiz_index += 1
                    else:
                        st.session_state.quiz_finished = True
                        st.session_state.quiz_active   = False
                    st.rerun()

        elif st.session_state.quiz_finished:
            score = st.session_state.quiz_score
            pct   = int(score / total_q * 100) if total_q else 0
            grade = "A+" if pct>=90 else "A" if pct>=80 else "B" if pct>=70 else "C" if pct>=60 else "D" if pct>=50 else "F"
            clr   = "#059669" if pct>=70 else "#d97706" if pct>=50 else "#dc2626"
            feedback = ("🔥 Outstanding mastery! You have a solid grasp of this lecture." if pct>=80
                        else "👍 Great effort! Review the flashcards for any concepts you missed." if pct>=60
                        else "📚 Keep practicing! Read through the study guide and take the quiz again.")

            st.markdown(f"""
            <div style="text-align:center; padding:30px 20px; background:#ffffff; border:1px solid #e2e8f0; border-radius:16px; margin-bottom:20px; box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                <div style="font-size:0.75rem; font-family:'DM Mono',monospace; font-weight:600; color:#64748b;
                            text-transform:uppercase; letter-spacing:2px; margin-bottom:8px;">Quiz Results</div>
                <div style="font-size:4rem; font-weight:800; color:{clr}; line-height:1;">{grade}</div>
                <div style="font-size:1.2rem; font-weight:700; color:#0f172a; margin-top:8px;"><b>{score} / {total_q}</b> correct ({pct}%)</div>
                <div style="font-size:0.92rem; font-weight:400; color:#475569; margin-top:10px;">{feedback}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            with st.expander("📋 Review All Questions & Answers", expanded=True):
                for i, q in enumerate(questions):
                    chosen  = st.session_state.quiz_answers.get(i, "—")
                    correct = q.get("correct", "A")
                    right   = (chosen == correct)
                    st.markdown(f"""
                    <div style="padding:12px 0; border-bottom:1px solid #e2e8f0;">
                        <div style="font-size:0.92rem; font-weight:600; color:#0f172a; margin-bottom:6px;">
                            <b>Q{i+1}.</b> {q.get('question', '')}
                        </div>
                        <div style="font-size:0.86rem;">
                            <span style="color:{'#059669' if right else '#dc2626'}; font-weight:700;">
                                {'✓ Correct (Option ' + correct + ')' if right else f'✗ Your Answer: {chosen} · Correct: {correct}'}
                            </span>
                        </div>
                        <div style="font-size:0.85rem; font-weight:400; color:#64748b; margin-top:4px;">
                            {q.get('explanation', '')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            col_ret, _ = st.columns([1.5, 3])
            with col_ret:
                if st.button("🔄 Retake Quiz", use_container_width=True):
                    reset_quiz()
                    st.rerun()


# ══════════════════════════════════════════════
#  TAB 5 — EXPORT
# ══════════════════════════════════════════════
with tab_export:
    if not st.session_state.analysis_done:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#64748b;">
            <div style="font-size:3rem">📤</div>
            <div style="margin-top:12px; font-size:1.15rem; color:#0f172a; font-weight:700;">Nothing to Export Yet</div>
            <div style="font-size:0.88rem; margin-top:6px; font-weight:400; color:#64748b;">Generate your study pack first to export in CSV, JSON, and Markdown formats.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        now   = datetime.now().strftime("%Y%m%d_%H%M")
        subj  = st.session_state.subject or "study_pack"
        safe_subj = re.sub(r'[^a-zA-Z0-9_-]', '_', subj).strip('_')
        cards = st.session_state.flashcards
        guide = st.session_state.study_guide or {}

        st.markdown('<div class="sec-label">Export Formats</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        # CSV Export
        with col1:
            st.markdown("<b style='font-size:0.95rem; font-weight:700; color:#0f172a;'>🃏 Flashcards CSV</b>", unsafe_allow_html=True)
            st.caption("Direct import into Anki, Quizlet, or Excel")
            df_export = pd.DataFrame(cards)
            csv_bytes = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ Download CSV",
                csv_bytes,
                file_name=f"echostudy_{safe_subj}_{now}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # JSON Export
        with col2:
            st.markdown("<b style='font-size:0.95rem; font-weight:700; color:#0f172a;'>🗂️ Complete StudyPack JSON</b>", unsafe_allow_html=True)
            st.caption("Full pack with study guide, flashcards, and quiz")
            export_obj = {
                "exported_at":  datetime.now().isoformat(),
                "subject":      subj,
                "source_type":  st.session_state.input_mode,
                "source_text":  st.session_state.transcript_text,
                "youtube_url":  st.session_state.yt_url if st.session_state.input_mode == "youtube" else None,
                "pdf_name":     st.session_state.pdf_name if st.session_state.input_mode == "pdf" else None,
                "pdf_pages":    st.session_state.pdf_pages if st.session_state.input_mode == "pdf" else None,
                "study_guide":  guide,
                "flashcards":   cards,
                "quiz":         st.session_state.quiz_questions,
                "quiz_score":   f"{st.session_state.quiz_score}/{len(st.session_state.quiz_questions)}" if st.session_state.quiz_finished else "not_taken",
            }
            json_bytes = json.dumps(export_obj, indent=2).encode("utf-8")
            st.download_button(
                "⬇ Download JSON",
                json_bytes,
                file_name=f"echostudy_{safe_subj}_{now}.json",
                mime="application/json",
                use_container_width=True
            )

        # Markdown Export
        with col3:
            st.markdown("<b style='font-size:0.95rem; font-weight:700; color:#0f172a;'>📋 Study Guide Markdown</b>", unsafe_allow_html=True)
            st.caption("Clean format for Notion, Obsidian, and Notes")
            md = [
                f"# 📖 Study Guide: {subj}",
                f"> Generated by EchoStudy AI · {datetime.now().strftime('%d %b %Y')}",
                "",
                "## Overview",
                guide.get("overview", ""),
                "",
                "## Key Concepts",
            ]
            for c in guide.get("key_concepts", []):
                md += [
                    f"### {c.get('term','')}",
                    f"- **Definition:** {c.get('definition','')}",
                    f"- **Example:** {c.get('example','')}",
                    ""
                ]
            if guide.get("important_formulas"):
                md += ["## Important Formulas", ""]
                for f in guide.get("important_formulas", []):
                    md.append(f"- `{f}`")
                md.append("")
            if guide.get("common_mistakes"):
                md += ["## Common Mistakes to Avoid", ""]
                for m in guide.get("common_mistakes", []):
                    md.append(f"- ✕ {m}")
                md.append("")
            if guide.get("exam_tips"):
                md += ["## High-Yield Exam Tips", ""]
                for t in guide.get("exam_tips", []):
                    md.append(f"- 🎯 {t}")
                md.append("")

            md += [
                "## Flashcards",
                "",
                "| # | Question | Answer | Difficulty | Topic |",
                "|---|----------|--------|------------|-------|"
            ]
            for c in cards:
                md.append(f"| {c.get('id','')} | {c.get('question','')} | {c.get('answer','')} | {c.get('difficulty','')} | {c.get('topic_tag','')} |")

            md_bytes = "\n".join(md).encode("utf-8")
            st.download_button(
                "⬇ Download Markdown",
                md_bytes,
                file_name=f"echostudy_{safe_subj}_{now}.md",
                mime="text/markdown",
                use_container_width=True
            )

        st.markdown("---")

        with st.expander("📊 Flashcards Table Preview", expanded=False):
            if cards:
                st.data_editor(
                    pd.DataFrame(cards),
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                )

        with st.expander("🗂️ Full JSON Preview", expanded=False):
            st.json(export_obj)