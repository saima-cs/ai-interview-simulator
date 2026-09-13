import json
import os
from statistics import mean

import streamlit as st

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# PREMIUM UI CSS
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   GLOBAL
========================================================= */

.stApp {
    background:
        radial-gradient(
            circle at 85% 5%,
            rgba(124, 58, 237, 0.10),
            transparent 25%
        ),
        radial-gradient(
            circle at 10% 25%,
            rgba(37, 99, 235, 0.07),
            transparent 25%
        ),
        #080b14;
    color: #f8fafc;
}

.main .block-container {
    max-width: 1350px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}


/* =========================================================
   REMOVE DEFAULT STREAMLIT DECORATION
========================================================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* =========================================================
   SIDEBAR
========================================================= */

section[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #0b1020 0%,
            #090d18 100%
        ) !important;

    border-right: 1px solid #1e293b;
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

.sidebar-brand {
    padding: 15px 5px 25px;
    text-align: center;
}

.sidebar-logo {
    width: 62px;
    height: 62px;
    margin: auto;
    border-radius: 18px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 31px;

    background:
        linear-gradient(
            135deg,
            #6366f1,
            #8b5cf6
        );

    box-shadow:
        0 12px 35px rgba(99,102,241,0.35);
}

.sidebar-title {
    margin-top: 13px;
    font-size: 20px;
    font-weight: 800;
    color: #ffffff;
}

.sidebar-subtitle {
    margin-top: 4px;
    color: #94a3b8;
    font-size: 12px;
}

.sidebar-section {
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.2px;
    margin: 22px 4px 9px;
    text-transform: uppercase;
}


/* Sidebar buttons */

section[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;

    background: transparent !important;
    color: #cbd5e1 !important;

    border: 1px solid transparent !important;
    border-radius: 12px !important;

    min-height: 43px !important;

    text-align: left !important;

    padding-left: 15px !important;

    font-size: 14px !important;
    font-weight: 650 !important;

    transition: 0.2s ease;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #151c2e !important;
    border-color: #26334d !important;
    color: #ffffff !important;
    transform: translateX(2px);
}


/* =========================================================
   TOP NAV
========================================================= */

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;

    padding: 4px 2px 25px;
}

.topbar-title {
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;

    padding: 7px 12px;

    border-radius: 30px;

    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.18);

    color: #6ee7b7;
    font-size: 12px;
    font-weight: 700;
}


/* =========================================================
   HERO
========================================================= */

.hero-container {
    position: relative;
    overflow: hidden;

    min-height: 480px;

    border-radius: 30px;

    padding: 60px;

    background:
        radial-gradient(
            circle at 78% 35%,
            rgba(139,92,246,0.38),
            transparent 28%
        ),
        radial-gradient(
            circle at 100% 100%,
            rgba(37,99,235,0.25),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #111936 0%,
            #10152c 48%,
            #0c1123 100%
        );

    border: 1px solid #283451;

    box-shadow:
        0 25px 80px rgba(0,0,0,0.35);
}

.hero-container::before {
    content: "";
    position: absolute;

    width: 330px;
    height: 330px;

    right: -110px;
    top: -110px;

    border-radius: 50%;

    border: 1px solid rgba(139,92,246,0.18);
}

.hero-container::after {
    content: "";
    position: absolute;

    width: 230px;
    height: 230px;

    right: -60px;
    top: -60px;

    border-radius: 50%;

    border: 1px solid rgba(96,165,250,0.14);
}

.hero-content {
    position: relative;
    z-index: 2;
    max-width: 700px;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;

    padding: 8px 14px;

    border-radius: 30px;

    background: rgba(99,102,241,0.12);
    border: 1px solid rgba(129,140,248,0.28);

    color: #c4b5fd;

    font-size: 11px;
    font-weight: 800;

    letter-spacing: 0.7px;
}

.hero-title {
    margin-top: 24px;

    font-size: 56px;
    line-height: 1.02;

    font-weight: 900;

    letter-spacing: -2.5px;

    color: #ffffff;
}

.gradient-text {
    background:
        linear-gradient(
            90deg,
            #60a5fa,
            #a78bfa,
            #c084fc
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    margin-top: 20px;

    font-size: 21px;
    font-weight: 650;

    color: #cbd5e1;
}

.hero-description {
    margin-top: 14px;

    max-width: 620px;

    color: #94a3b8;

    font-size: 15px;
    line-height: 1.75;
}


/* =========================================================
   HERO AI VISUAL
========================================================= */

.ai-orb {
    position: absolute;

    right: 80px;
    top: 100px;

    width: 190px;
    height: 190px;

    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 75px;

    background:
        radial-gradient(
            circle,
            rgba(139,92,246,0.35),
            rgba(37,99,235,0.08) 55%,
            transparent 70%
        );

    border: 1px solid rgba(139,92,246,0.35);

    box-shadow:
        0 0 70px rgba(124,58,237,0.25),
        inset 0 0 45px rgba(99,102,241,0.10);
}

.ai-orb-ring {
    position: absolute;

    width: 250px;
    height: 250px;

    border-radius: 50%;

    border: 1px dashed rgba(129,140,248,0.20);
}


/* =========================================================
   CTA
========================================================= */

.cta-wrap .stButton > button {
    min-height: 55px !important;

    border: 0 !important;

    border-radius: 14px !important;

    background:
        linear-gradient(
            135deg,
            #6366f1,
            #8b5cf6
        ) !important;

    color: white !important;

    font-size: 15px !important;
    font-weight: 800 !important;

    box-shadow:
        0 12px 35px rgba(99,102,241,0.28);

    transition: 0.2s ease;
}

.cta-wrap .stButton > button:hover {
    background:
        linear-gradient(
            135deg,
            #818cf8,
            #a78bfa
        ) !important;

    transform: translateY(-2px);

    box-shadow:
        0 16px 45px rgba(99,102,241,0.38);
}


/* =========================================================
   SECTION TITLES
========================================================= */

.section-heading {
    margin-top: 42px;

    color: #ffffff;

    font-size: 25px;
    font-weight: 850;

    letter-spacing: -0.5px;
}

.section-description {
    color: #64748b;

    font-size: 14px;

    margin-top: 5px;
    margin-bottom: 22px;
}


/* =========================================================
   STAT CARDS
========================================================= */

.stat-card {
    min-height: 145px;

    padding: 22px;

    border-radius: 18px;

    background:
        linear-gradient(
            145deg,
            rgba(20,27,46,0.98),
            rgba(12,17,31,0.98)
        );

    border: 1px solid #202c45;

    box-shadow:
        0 12px 35px rgba(0,0,0,0.20);

    transition: 0.2s ease;
}

.stat-card:hover {
    border-color: #394b72;
    transform: translateY(-3px);
}

.stat-icon {
    font-size: 22px;
}

.stat-number {
    margin-top: 12px;

    color: #ffffff;

    font-size: 30px;
    font-weight: 850;
}

.stat-label {
    margin-top: 4px;

    color: #64748b;

    font-size: 12px;
    font-weight: 700;
}


/* =========================================================
   FEATURE CARDS
========================================================= */

.feature-card {
    min-height: 205px;

    padding: 25px;

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            #111827,
            #0d1321
        );

    border: 1px solid #202c45;

    box-shadow:
        0 12px 35px rgba(0,0,0,0.16);

    transition: 0.25s ease;
}

.feature-card:hover {
    transform: translateY(-5px);

    border-color: #4c5f8d;

    box-shadow:
        0 20px 45px rgba(0,0,0,0.28);
}

.feature-icon {
    width: 50px;
    height: 50px;

    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 14px;

    background:
        rgba(99,102,241,0.12);

    border: 1px solid rgba(99,102,241,0.20);

    font-size: 23px;
}

.feature-title {
    margin-top: 17px;

    color: #f8fafc;

    font-size: 17px;
    font-weight: 800;
}

.feature-text {
    margin-top: 8px;

    color: #718096;

    font-size: 13px;

    line-height: 1.65;
}


/* =========================================================
   STEP CARDS
========================================================= */

.step-card {
    padding: 24px;

    min-height: 160px;

    border-radius: 18px;

    background: #0d1321;

    border: 1px solid #202c45;
}

.step-number {
    color: #818cf8;

    font-size: 12px;

    font-weight: 900;

    letter-spacing: 1px;
}

.step-title {
    color: #ffffff;

    margin-top: 12px;

    font-size: 18px;

    font-weight: 800;
}

.step-text {
    color: #64748b;

    margin-top: 7px;

    font-size: 13px;

    line-height: 1.6;
}


/* =========================================================
   SETUP / INTERVIEW PANELS
========================================================= */

.dark-panel {
    padding: 28px;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            #111827,
            #0c1220
        );

    border: 1px solid #202c45;

    box-shadow:
        0 15px 40px rgba(0,0,0,0.18);
}

.panel-title {
    color: #ffffff;

    font-size: 19px;

    font-weight: 800;
}

.panel-subtitle {
    color: #64748b;

    font-size: 13px;

    margin-top: 4px;
}


/* =========================================================
   INPUTS
========================================================= */

div[data-baseweb="select"] > div {
    background: #111827 !important;

    color: #f8fafc !important;

    border: 1px solid #26334d !important;

    border-radius: 11px !important;
}

div[data-baseweb="select"] span {
    color: #e2e8f0 !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #111827 !important;

    color: #f8fafc !important;

    border: 1px solid #26334d !important;

    border-radius: 11px !important;
}

div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #6366f1 !important;
}

div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: #475569 !important;
}


/* Labels */

.stSelectbox label,
.stTextInput label,
.stTextArea label,
.stFileUploader label {
    color: #cbd5e1 !important;

    font-size: 13px !important;

    font-weight: 700 !important;
}


/* =========================================================
   NORMAL BUTTONS
========================================================= */

.stButton > button {
    min-height: 46px !important;

    border-radius: 11px !important;

    background: #111827 !important;

    color: #cbd5e1 !important;

    border: 1px solid #26334d !important;

    font-weight: 700 !important;

    transition: 0.2s ease;
}

.stButton > button:hover {
    background: #172033 !important;

    border-color: #6366f1 !important;

    color: #ffffff !important;
}


/* =========================================================
   PROGRESS
========================================================= */

div[data-testid="stProgress"] > div {
    background: #1e293b !important;
}

div[data-testid="stProgress"] > div > div {
    background:
        linear-gradient(
            90deg,
            #6366f1,
            #8b5cf6
        ) !important;
}


/* =========================================================
   INTERVIEW QUESTION
========================================================= */

.question-panel {
    padding: 30px;

    margin-top: 20px;

    border-radius: 22px;

    background:
        radial-gradient(
            circle at 90% 10%,
            rgba(99,102,241,0.10),
            transparent 30%
        ),
        #0d1321;

    border: 1px solid #26334d;

    box-shadow:
        0 15px 45px rgba(0,0,0,0.22);
}

.ai-label {
    display: inline-block;

    padding: 7px 12px;

    border-radius: 30px;

    background: rgba(99,102,241,0.12);

    border: 1px solid rgba(99,102,241,0.25);

    color: #a5b4fc;

    font-size: 11px;

    font-weight: 850;

    letter-spacing: 0.5px;
}

.question-number {
    margin-top: 20px;

    color: #64748b;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1px;
}

.question-text {
    margin-top: 10px;

    color: #f8fafc;

    font-size: 23px;

    line-height: 1.55;

    font-weight: 700;
}


/* =========================================================
   RESULTS
========================================================= */

.score-panel {
    text-align: center;

    padding: 48px 25px;

    border-radius: 26px;

    background:
        radial-gradient(
            circle at center,
            rgba(99,102,241,0.20),
            transparent 55%
        ),
        #0d1321;

    border: 1px solid #293755;

    box-shadow:
        0 20px 60px rgba(0,0,0,0.25);
}

.big-score {
    color: #ffffff;

    font-size: 72px;

    line-height: 1;

    font-weight: 900;

    letter-spacing: -3px;
}

.performance {
    margin-top: 12px;

    color: #a5b4fc;

    font-size: 22px;

    font-weight: 850;
}

.performance-text {
    margin-top: 8px;

    color: #64748b;

    font-size: 14px;
}


/* =========================================================
   RESULT METRICS
========================================================= */

.result-metric {
    padding: 20px;

    border-radius: 16px;

    background: #111827;

    border: 1px solid #202c45;

    text-align: center;
}

.result-value {
    color: #ffffff;

    font-size: 25px;

    font-weight: 850;
}

.result-label {
    margin-top: 5px;

    color: #64748b;

    font-size: 11px;

    font-weight: 750;
}


/* =========================================================
   EXPANDERS
========================================================= */

.streamlit-expanderHeader {
    background: #111827 !important;

    color: #e2e8f0 !important;

    border-radius: 12px !important;
}


/* =========================================================
   ALERTS
========================================================= */

div[data-testid="stAlert"] {
    border-radius: 12px !important;
}


/* =========================================================
   FOOTER
========================================================= */

.footer {
    margin-top: 60px;

    padding: 25px;

    text-align: center;

    color: #475569;

    font-size: 12px;

    border-top: 1px solid #172033;
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 900px) {

    .hero-container {
        padding: 35px 25px;
        min-height: auto;
    }

    .hero-title {
        font-size: 39px;
    }

    .ai-orb {
        display: none;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "Home",
    "questions": [],
    "answers": [],
    "evaluations": [],
    "scores": [],
    "current_question": 0,
    "interview_started": False,
    "interview_finished": False,
    "interview_config": {},
    "interview_count": 0,
    "result_counted": False,
    "resume_text": "",
    "resume_name": "",
    "history": [],
}

for key, value in defaults.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# GROQ CLIENT
# ============================================================

def get_groq_client():

    if Groq is None:

        st.error(
            "Groq package is not installed."
        )

        return None

    api_key = None

    try:

        api_key = st.secrets.get(
            "GROQ_API_KEY"
        )

    except Exception:

        pass

    if not api_key:

        api_key = os.environ.get(
            "GROQ_API_KEY"
        )

    if not api_key:

        return None

    try:

        return Groq(
            api_key=api_key
        )

    except Exception as e:

        st.error(
            f"Could not initialize Groq: {e}"
        )

        return None


# ============================================================
# RESUME EXTRACTION
# ============================================================

def extract_resume_text(uploaded_file):

    if PdfReader is None:

        st.error(
            "PyPDF2 is not installed."
        )

        return ""

    if uploaded_file is None:

        return ""

    try:

        reader = PdfReader(
            uploaded_file
        )

        text = ""

        for page in reader.pages:

            text += (
                page.extract_text() or ""
            ) + "\n"

        text = text.strip()

        if not text:

            st.warning(
                "No readable text was found in this PDF."
            )

            return ""

        return text

    except Exception as e:

        st.error(
            f"Could not read resume: {e}"
        )

        return ""


# ============================================================
# GENERATE QUESTION
# ============================================================

def generate_question():

    client = get_groq_client()

    if client is None:

        st.error(
            "⚠️ Groq API key is missing. "
            "Please configure GROQ_API_KEY."
        )

        return None

    config = st.session_state.interview_config

    role = config.get(
        "job_role",
        "Software Engineer"
    )

    interview_type = config.get(
        "interview_type",
        "Technical Interview"
    )

    difficulty = config.get(
        "difficulty",
        "Intermediate"
    )

    experience = config.get(
        "experience",
        "Fresher"
    )

    previous = "\n".join(
        st.session_state.questions[-5:]
    )

    resume = st.session_state.get(
        "resume_text",
        ""
    )[:5000]

    prompt = f"""
You are a professional interviewer.

Generate ONE realistic interview question.

Job Role: {role}
Interview Type: {interview_type}
Difficulty: {difficulty}
Experience: {experience}

Previous Questions:
{previous if previous else "None"}

Resume:
{resume if resume else "No resume provided"}

Rules:
- Generate exactly ONE question.
- Do not repeat previous questions.
- Match the selected role.
- Match the interview type.
- Match the difficulty.
- Be realistic.
- Be appropriate for the candidate experience.
- Keep the question concise.
- Return ONLY the question.
"""

    try:

        response = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content":
                        "You are an expert interviewer. "
                        "Return exactly one question.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0.7,

            max_tokens=300,
        )

        result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return result if result else None

    except Exception as e:

        st.error(
            f"⚠️ Error generating question: {e}"
        )

        return None


# ============================================================
# EVALUATE ANSWER
# ============================================================

def evaluate_answer(question, answer):

    client = get_groq_client()

    if client is None:

        st.error(
            "⚠️ Groq API key is missing."
        )

        return None

    config = st.session_state.interview_config

    role = config.get(
        "job_role",
        "Software Engineer"
    )

    interview_type = config.get(
        "interview_type",
        "Technical Interview"
    )

    difficulty = config.get(
        "difficulty",
        "Intermediate"
    )

    prompt = f"""
Evaluate the candidate's interview answer.

Role: {role}
Interview Type: {interview_type}
Difficulty: {difficulty}

Question:
{question}

Candidate Answer:
{answer}

Return ONLY valid JSON using exactly this structure:

{{
    "score": 8,
    "correctness": 8,
    "relevance": 9,
    "technical_knowledge": 7,
    "communication": 8,
    "confidence": 8,
    "strengths": [
        "Strength"
    ],
    "improvements": [
        "Improvement"
    ],
    "better_answer": "A stronger example answer.",
    "concepts_to_review": [
        "Concept"
    ]
}}

Scores must be between 0 and 10.

Be fair to a fresher.
"""

    try:

        response = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content":
                        "You are an expert interview evaluator. "
                        "Return only valid JSON.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],

            temperature=0.2,

            max_tokens=1200,
        )

        result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        if result.startswith("```"):

            result = result.replace(
                "```json",
                ""
            )

            result = result.replace(
                "```",
                ""
            )

            result = result.strip()

        evaluation = json.loads(
            result
        )

        numeric_fields = [
            "score",
            "correctness",
            "relevance",
            "technical_knowledge",
            "communication",
            "confidence",
        ]

        for field in numeric_fields:

            try:

                value = int(
                    float(
                        evaluation.get(
                            field,
                            0
                        )
                    )
                )

                evaluation[field] = max(
                    0,
                    min(
                        10,
                        value
                    )
                )

            except Exception:

                evaluation[field] = 0

        for field in [
            "strengths",
            "improvements",
            "concepts_to_review",
        ]:

            if not isinstance(
                evaluation.get(field),
                list
            ):

                evaluation[field] = []

        return evaluation

    except json.JSONDecodeError:

        st.error(
            "⚠️ AI returned invalid JSON."
        )

        return None

    except Exception as e:

        st.error(
            f"⚠️ Evaluation error: {e}"
        )

        return None


# ============================================================
# FINAL REPORT
# ============================================================

def generate_final_report():

    evaluations = (
        st.session_state.evaluations
    )

    if not evaluations:

        return {
            "overall_score": 0,
            "technical": 0,
            "communication": 0,
            "problem_solving": 0,
            "relevance": 0,
            "confidence": 0,
        }

    overall = mean(
        e.get(
            "score",
            0
        )
        for e in evaluations
    )

    technical = mean(
        e.get(
            "technical_knowledge",
            0
        )
        for e in evaluations
    )

    communication = mean(
        e.get(
            "communication",
            0
        )
        for e in evaluations
    )

    relevance = mean(
        e.get(
            "relevance",
            0
        )
        for e in evaluations
    )

    confidence = mean(
        e.get(
            "confidence",
            0
        )
        for e in evaluations
    )

    problem_solving = mean(
        e.get(
            "correctness",
            0
        )
        for e in evaluations
    )

    return {
        "overall_score":
            round(
                overall * 10
            ),

        "technical":
            round(
                technical,
                1
            ),

        "communication":
            round(
                communication,
                1
            ),

        "problem_solving":
            round(
                problem_solving,
                1
            ),

        "relevance":
            round(
                relevance,
                1
            ),

        "confidence":
            round(
                confidence,
                1
            ),
    }


# ============================================================
# RESET
# ============================================================

def reset_interview():

    st.session_state.questions = []

    st.session_state.answers = []

    st.session_state.evaluations = []

    st.session_state.scores = []

    st.session_state.current_question = 0

    st.session_state.interview_started = False

    st.session_state.interview_finished = False

    st.session_state.result_counted = False


# ============================================================
# SIDEBAR
# ============================================================

def show_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-brand">

                <div class="sidebar-logo">
                    🤖
                </div>

                <div class="sidebar-title">
                    AI Interview
                </div>

                <div class="sidebar-subtitle">
                    Smart Interview Preparation
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="sidebar-section">Workspace</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "🏠   Home",
            use_container_width=True
        ):

            st.session_state.page = "Home"

            st.rerun()

        if st.button(
            "⚙️   Interview Setup",
            use_container_width=True
        ):

            st.session_state.page = "Interview Setup"

            st.rerun()

        if st.button(
            "🎤   Mock Interview",
            use_container_width=True
        ):

            if st.session_state.interview_started:

                st.session_state.page = (
                    "Mock Interview"
                )

            else:

                st.session_state.page = (
                    "Interview Setup"
                )

            st.rerun()

        if st.button(
            "📊   Results",
            use_container_width=True
        ):

            st.session_state.page = "Results"

            st.rerun()

        if st.button(
            "📚   History",
            use_container_width=True
        ):

            st.session_state.page = "History"

            st.rerun()

        st.markdown(
            '<div class="sidebar-section">Information</div>',
            unsafe_allow_html=True
        )

        if st.button(
            "ℹ️   About",
            use_container_width=True
        ):

            st.session_state.page = "About"

            st.rerun()

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="
                padding:15px;
                border-radius:14px;
                background:#101827;
                border:1px solid #202c45;
            ">

                <div style="
                    color:#a5b4fc;
                    font-size:12px;
                    font-weight:800;
                ">
                    AI ENGINE
                </div>

                <div style="
                    color:#64748b;
                    font-size:11px;
                    margin-top:5px;
                    line-height:1.5;
                ">
                    Powered by Groq AI
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# HOME
# ============================================================

def show_home():

    st.markdown(
        """
        <div class="topbar">

            <div class="topbar-title">
                AI Interview Simulator
            </div>

            <div class="status-pill">
                ● AI SYSTEM ONLINE
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    # HERO

    st.markdown(
        """
        <div class="hero-container">

            <div class="hero-content">

                <div class="hero-badge">
                    ✦ AI-POWERED INTERVIEW PRACTICE
                </div>

                <div class="hero-title">
                    Master Your Next
                    <br>
                    <span class="gradient-text">
                        Interview with AI.
                    </span>
                </div>

                <div class="hero-subtitle">
                    Practice. Improve. Get Interview-Ready.
                </div>

                <div class="hero-description">
                    Experience realistic technical, HR and
                    behavioral interviews with an AI interviewer.
                    Get intelligent scoring, detailed feedback,
                    resume-based questions and personalized
                    recommendations.
                </div>

            </div>

            <div class="ai-orb-ring"></div>

            <div class="ai-orb">
                🤖
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # HERO CTA

    col1, col2, col3 = st.columns(
        [1, 1.4, 1]
    )

    with col2:

        st.markdown(
            '<div class="cta-wrap">',
            unsafe_allow_html=True
        )

        if st.button(
            "🚀  Start Your AI Interview",
            use_container_width=True
        ):

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # STATS

    st.markdown(
        """
        <div class="section-heading">
            Your Interview Dashboard
        </div>

        <div class="section-description">
            Track your preparation and improve with every interview.
        </div>
        """,
        unsafe_allow_html=True
    )

    completed = (
        st.session_state.interview_count
    )

    total_questions = sum(
        len(
            item.get(
                "questions",
                []
            )
        )
        for item in st.session_state.history
    )

    if st.session_state.scores:

        average = round(
            mean(
                st.session_state.scores
            ) * 10
        )

    else:

        average = 0

    stats = [
        (
            "🎯",
            completed,
            "Interviews Completed"
        ),
        (
            "📝",
            total_questions,
            "Questions Practiced"
        ),
        (
            "⭐",
            f"{average}%",
            "Average Score"
        ),
        (
            "🚀",
            "∞",
            "Potential to Improve"
        ),
    ]

    cols = st.columns(4)

    for col, item in zip(
        cols,
        stats
    ):

        with col:

            icon, number, label = item

            st.markdown(
                f"""
                <div class="stat-card">

                    <div class="stat-icon">
                        {icon}
                    </div>

                    <div class="stat-number">
                        {number}
                    </div>

                    <div class="stat-label">
                        {label}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # FEATURES

    st.markdown(
        """
        <div class="section-heading">
            Everything You Need to Improve
        </div>

        <div class="section-description">
            A complete AI-powered interview preparation workspace.
        </div>
        """,
        unsafe_allow_html=True
    )

    features = [

        (
            "🤖",
            "AI Interviewer",
            "Get realistic questions generated dynamically for your target role, experience and difficulty."
        ),

        (
            "🧠",
            "Smart Evaluation",
            "AI analyzes your answers for correctness, relevance, communication and technical knowledge."
        ),

        (
            "📊",
            "Performance Analytics",
            "Understand your strengths, weaknesses, confidence and overall interview performance."
        ),

        (
            "📄",
            "Resume-Based Practice",
            "Upload your resume and generate interview questions based on your own experience."
        ),

        (
            "🎯",
            "Multiple Interview Modes",
            "Practice Technical, HR, Behavioral or Mixed interview sessions."
        ),

        (
            "📈",
            "Personalized Feedback",
            "Get better-answer examples and concepts you should review before your next interview."
        ),
    ]

    for row in range(
        0,
        len(features),
        3
    ):

        cols = st.columns(3)

        for col, feature in zip(
            cols,
            features[row:row + 3]
        ):

            icon, title, text = feature

            with col:

                st.markdown(
                    f"""
                    <div class="feature-card">

                        <div class="feature-icon">
                            {icon}
                        </div>

                        <div class="feature-title">
                            {title}
                        </div>

                        <div class="feature-text">
                            {text}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # HOW IT WORKS

    st.markdown(
        """
        <div class="section-heading">
            How It Works
        </div>

        <div class="section-description">
            Start practicing in three simple steps.
        </div>
        """,
        unsafe_allow_html=True
    )

    steps = [

        (
            "01",
            "Configure",
            "Choose your target role, interview type, difficulty and experience level."
        ),

        (
            "02",
            "Practice",
            "Answer AI-generated questions exactly as you would in a real interview."
        ),

        (
            "03",
            "Improve",
            "Review your score, feedback, strengths and concepts to study."
        ),
    ]

    cols = st.columns(3)

    for col, step in zip(
        cols,
        steps
    ):

        with col:

            number, title, text = step

            st.markdown(
                f"""
                <div class="step-card">

                    <div class="step-number">
                        STEP {number}
                    </div>

                    <div class="step-title">
                        {title}
                    </div>

                    <div class="step-text">
                        {text}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    # FINAL CTA

    st.markdown(
        "<br><br>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:42px 20px;
            border-radius:22px;
            background:
                linear-gradient(
                    135deg,
                    rgba(99,102,241,0.12),
                    rgba(139,92,246,0.06)
                );
            border:1px solid #253252;
        ">

            <div style="
                color:#ffffff;
                font-size:27px;
                font-weight:850;
            ">
                Ready to level up your interview skills?
            </div>

            <div style="
                color:#64748b;
                font-size:14px;
                margin-top:8px;
            ">
                Your next interview practice session starts here.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(
        [1, 1.2, 1]
    )

    with col2:

        st.markdown(
            '<div class="cta-wrap">',
            unsafe_allow_html=True
        )

        if st.button(
            "🎤  Begin Interview Practice",
            use_container_width=True
        ):

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# INTERVIEW SETUP
# ============================================================

def show_interview_setup():

    st.markdown(
        """
        <div class="topbar">

            <div class="topbar-title">
                Interview Configuration
            </div>

            <div class="status-pill">
                ● READY
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-heading">
            ⚙️ Build Your Interview
        </div>

        <div class="section-description">
            Configure your AI interviewer before you begin.
        </div>
        """,
        unsafe_allow_html=True
    )

    left, right = st.columns(
        2,
        gap="large"
    )

    # LEFT

    with left:

        st.markdown(
            """
            <div class="dark-panel">

                <div class="panel-title">
                    🎯 Interview Preferences
                </div>

                <div class="panel-subtitle">
                    Tell the AI what kind of interview you want.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        job_role = st.selectbox(
            "💼 Job Role",

            [
                "Software Engineer",
                "Python Developer",
                "AI Engineer",
                "Machine Learning Engineer",
                "Data Scientist",
                "Data Analyst",
                "Web Developer",
                "Frontend Developer",
                "Backend Developer",
                "Cybersecurity Analyst",
                "Computer Science Student",
                "Custom Role",
            ]
        )

        if job_role == "Custom Role":

            job_role = st.text_input(
                "Custom Job Role",
                placeholder="e.g. Generative AI Engineer"
            )

        interview_type = st.selectbox(
            "🎤 Interview Type",

            [
                "Technical Interview",
                "HR Interview",
                "Behavioral Interview",
                "Mixed Interview",
            ]
        )

        difficulty = st.selectbox(
            "📈 Difficulty",

            [
                "Beginner",
                "Intermediate",
                "Advanced",
                "Expert",
            ]
        )

    # RIGHT

    with right:

        st.markdown(
            """
            <div class="dark-panel">

                <div class="panel-title">
                    👨‍💻 Candidate Profile
                </div>

                <div class="panel-subtitle">
                    Customize the interview for your experience.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        number_questions = st.selectbox(
            "🔢 Number of Questions",
            [5, 10, 15]
        )

        experience = st.selectbox(
            "💼 Experience Level",

            [
                "Fresher",
                "0–1 Years",
                "1–3 Years",
                "3+ Years",
            ]
        )

        st.markdown(
            "#### 📄 Optional Resume"
        )

        resume_file = st.file_uploader(
            "Upload your resume PDF",
            type=["pdf"]
        )

        if resume_file:

            if (
                st.session_state.resume_name
                != resume_file.name
            ):

                with st.spinner(
                    "Reading your resume..."
                ):

                    text = extract_resume_text(
                        resume_file
                    )

                st.session_state.resume_text = text

                st.session_state.resume_name = (
                    resume_file.name
                )

            if st.session_state.resume_text:

                st.success(
                    "✅ Resume loaded successfully."
                )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(
        [1, 1.4, 1]
    )

    with col2:

        st.markdown(
            '<div class="cta-wrap">',
            unsafe_allow_html=True
        )

        if st.button(
            "🚀  Start AI Interview",
            use_container_width=True
        ):

            if not job_role.strip():

                st.warning(
                    "Please enter a job role."
                )

                return

            reset_interview()

            st.session_state.interview_config = {

                "job_role":
                    job_role,

                "interview_type":
                    interview_type,

                "difficulty":
                    difficulty,

                "number_questions":
                    number_questions,

                "experience":
                    experience,
            }

            st.session_state.interview_started = True

            st.session_state.page = (
                "Mock Interview"
            )

            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# MOCK INTERVIEW
# ============================================================

def show_mock_interview():

    if not st.session_state.interview_started:

        st.warning(
            "Please start an interview first."
        )

        if st.button(
            "⚙️ Go to Interview Setup",
            use_container_width=True
        ):

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

        return

    config = st.session_state.interview_config

    total = config.get(
        "number_questions",
        5
    )

    current = (
        st.session_state.current_question
    )

    if current >= total:

        st.session_state.interview_finished = True

        if not st.session_state.result_counted:

            st.session_state.interview_count += 1

            st.session_state.result_counted = True

            report = generate_final_report()

            st.session_state.history.append(
                {
                    "role":
                        config.get(
                            "job_role",
                            "Unknown"
                        ),

                    "type":
                        config.get(
                            "interview_type",
                            "Unknown"
                        ),

                    "difficulty":
                        config.get(
                            "difficulty",
                            "Unknown"
                        ),

                    "score":
                        report[
                            "overall_score"
                        ],

                    "questions":
                        list(
                            st.session_state.questions
                        ),

                    "answers":
                        list(
                            st.session_state.answers
                        ),

                    "evaluations":
                        list(
                            st.session_state.evaluations
                        ),
                }
            )

        st.session_state.page = "Results"

        st.rerun()

        return

    # HEADER

    st.markdown(
        """
        <div class="topbar">

            <div class="topbar-title">
                🎤 Live AI Interview
            </div>

            <div class="status-pill">
                ● INTERVIEW ACTIVE
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div style="
            color:#64748b;
            font-size:13px;
            margin-bottom:12px;
        ">
            {config.get('job_role')}
            &nbsp; • &nbsp;
            {config.get('interview_type')}
            &nbsp; • &nbsp;
            {config.get('difficulty')}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.progress(
        (current + 1) / total,

        text=(
            f"Question {current + 1} "
            f"of {total}"
        )
    )

    if len(
        st.session_state.questions
    ) <= current:

        with st.spinner(
            "🤖 AI interviewer is preparing your question..."
        ):

            question = generate_question()

        if not question:

            return

        st.session_state.questions.append(
            question
        )

    question = (
        st.session_state.questions[current]
    )

    st.markdown(
        f"""
        <div class="question-panel">

            <div class="ai-label">
                🤖 AI INTERVIEWER
            </div>

            <div class="question-number">
                QUESTION {current + 1}
            </div>

            <div class="question-text">
                {question}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="panel-title">
            📝 Your Answer
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Answer as if you are speaking directly to the interviewer."
    )

    answer = st.text_area(
        "Your Answer",

        height=220,

        placeholder=(
            "Type your answer here..."
        ),

        label_visibility="collapsed",

        key=f"answer_{current}",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        submit = st.button(
            "✅  Submit Answer",
            use_container_width=True
        )

    with col2:

        skip = st.button(
            "⏭️  Skip Question",
            use_container_width=True
        )

    if submit:

        if not answer.strip():

            st.warning(
                "Please write an answer first."
            )

        else:

            with st.spinner(
                "🧠 AI is evaluating your answer..."
            ):

                evaluation = evaluate_answer(
                    question,
                    answer
                )

            if evaluation:

                st.session_state.answers.append(
                    answer
                )

                st.session_state.evaluations.append(
                    evaluation
                )

                st.session_state.scores.append(
                    evaluation.get(
                        "score",
                        0
                    )
                )

                st.session_state.current_question += 1

                st.rerun()

    if skip:

        st.session_state.answers.append(
            "[Question skipped]"
        )

        evaluation = {

            "score": 0,

            "correctness": 0,

            "relevance": 0,

            "technical_knowledge": 0,

            "communication": 0,

            "confidence": 0,

            "strengths": [],

            "improvements": [
                "Try to answer every question."
            ],

            "better_answer": "",

            "concepts_to_review": [],
        }

        st.session_state.evaluations.append(
            evaluation
        )

        st.session_state.scores.append(0)

        st.session_state.current_question += 1

        st.rerun()


# ============================================================
# RESULTS
# ============================================================

def show_results():

    st.markdown(
        """
        <div class="topbar">

            <div class="topbar-title">
                Interview Performance
            </div>

            <div class="status-pill">
                ✓ COMPLETED
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.evaluations:

        st.markdown(
            """
            <div class="dark-panel">

                <div class="panel-title">
                    🎯 No Interview Results Yet
                </div>

                <div class="panel-subtitle">
                    Complete an interview to unlock your performance report.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "🚀 Start Interview",
            use_container_width=True
        ):

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

        return

    report = generate_final_report()

    score = report[
        "overall_score"
    ]

    if score >= 90:

        level = "Excellent 🏆"

        message = (
            "Outstanding interview performance!"
        )

    elif score >= 80:

        level = "Very Good 🌟"

        message = (
            "Great job! Keep polishing your skills."
        )

    elif score >= 70:

        level = "Good 👍"

        message = (
            "Good foundation. Keep practicing."
        )

    else:

        level = "Needs Improvement 📈"

        message = (
            "Keep practicing and focus on your weak areas."
        )

    st.markdown(
        f"""
        <div class="score-panel">

            <div class="big-score">
                {score}/100
            </div>

            <div class="performance">
                {level}
            </div>

            <div class="performance-text">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="section-heading">
            📊 Performance Breakdown
        </div>

        <div class="section-description">
            Here's how you performed across the key interview skills.
        </div>
        """,
        unsafe_allow_html=True
    )

    metrics = [

        (
            "Technical Knowledge",
            report["technical"]
        ),

        (
            "Communication",
            report["communication"]
        ),

        (
            "Problem Solving",
            report["problem_solving"]
        ),

        (
            "Relevance",
            report["relevance"]
        ),

        (
            "Confidence",
            report["confidence"]
        ),
    ]

    cols = st.columns(5)

    for col, item in zip(
        cols,
        metrics
    ):

        with col:

            label, value = item

            st.markdown(
                f"""
                <div class="result-metric">

                    <div class="result-value">
                        {value}/10
                    </div>

                    <div class="result-label">
                        {label}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    strengths = []

    improvements = []

    concepts = []

    for evaluation in (
        st.session_state.evaluations
    ):

        strengths.extend(
            evaluation.get(
                "strengths",
                []
            )
        )

        improvements.extend(
            evaluation.get(
                "improvements",
                []
            )
        )

        concepts.extend(
            evaluation.get(
                "concepts_to_review",
                []
            )
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="panel-title">
                💪 Your Strengths
            </div>
            """,
            unsafe_allow_html=True
        )

        unique_strengths = list(
            dict.fromkeys(
                strengths
            )
        )

        if unique_strengths:

            for item in unique_strengths[:8]:

                st.success(
                    item
                )

        else:

            st.info(
                "Keep practicing to identify your strongest areas."
            )

    with col2:

        st.markdown(
            """
            <div class="panel-title">
                📈 Improvement Areas
            </div>
            """,
            unsafe_allow_html=True
        )

        unique_improvements = list(
            dict.fromkeys(
                improvements
            )
        )

        if unique_improvements:

            for item in unique_improvements[:8]:

                st.warning(
                    item
                )

        else:

            st.info(
                "No major improvement areas found."
            )

    unique_concepts = list(
        dict.fromkeys(
            concepts
        )
    )

    if unique_concepts:

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="panel-title">
                📚 Concepts to Review
            </div>
            """,
            unsafe_allow_html=True
        )

        for concept in unique_concepts[:12]:

            st.markdown(
                f"""
                <div style="
                    padding:11px 14px;
                    margin-top:8px;
                    border-radius:10px;
                    background:#111827;
                    border:1px solid #202c45;
                    color:#cbd5e1;
                    font-size:13px;
                ">
                    📌 {concept}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        """
        <div class="section-heading">
            📝 Question-by-Question Review
        </div>

        <div class="section-description">
            Review your answers and see how the AI evaluated them.
        </div>
        """,
        unsafe_allow_html=True
    )

    for i, question in enumerate(
        st.session_state.questions
    ):

        evaluation = (

            st.session_state.evaluations[i]

            if i < len(
                st.session_state.evaluations
            )

            else {}
        )

        answer = (

            st.session_state.answers[i]

            if i < len(
                st.session_state.answers
            )

            else ""
        )

        with st.expander(
            f"Question {i + 1}  •  "
            f"{evaluation.get('score', 0)}/10"
        ):

            st.markdown(
                "**Question**"
            )

            st.write(
                question
            )

            st.markdown(
                "**Your Answer**"
            )

            st.write(
                answer
            )

            st.markdown(
                "**AI Feedback**"
            )

            st.write(
                f"Correctness: "
                f"{evaluation.get('correctness', 0)}/10"
            )

            st.write(
                f"Technical Knowledge: "
                f"{evaluation.get('technical_knowledge', 0)}/10"
            )

            st.write(
                f"Communication: "
                f"{evaluation.get('communication', 0)}/10"
            )

            better = evaluation.get(
                "better_answer",
                ""
            )

            if better:

                st.markdown(
                    "**✨ Better Answer**"
                )

                st.write(
                    better
                )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🔄  Start New Interview",
            use_container_width=True
        ):

            reset_interview()

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

    with col2:

        if st.button(
            "🏠  Back to Home",
            use_container_width=True
        ):

            st.session_state.page = "Home"

            st.rerun()


# ============================================================
# HISTORY
# ============================================================

def show_history():

    st.markdown(
        """
        <div class="section-heading">
            📚 Interview History
        </div>

        <div class="section-description">
            Review your completed interview sessions.
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.history:

        st.markdown(
            """
            <div class="dark-panel">

                <div class="panel-title">
                    No interviews yet
                </div>

                <div class="panel-subtitle">
                    Complete your first AI interview to build your history.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(
            "🚀 Start Your First Interview",
            use_container_width=True
        ):

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

        return

    for i, interview in enumerate(
        reversed(
            st.session_state.history
        ),
        1
    ):

        score = interview.get(
            "score",
            0
        )

        with st.expander(
            f"Interview {i}  •  "
            f"{interview.get('role')}  •  "
            f"{score}/100"
        ):

            st.write(
                "**Role:**",
                interview.get(
                    "role"
                )
            )

            st.write(
                "**Type:**",
                interview.get(
                    "type"
                )
            )

            st.write(
                "**Difficulty:**",
                interview.get(
                    "difficulty"
                )
            )

            st.progress(
                score / 100
            )


# ============================================================
# ABOUT
# ============================================================

def show_about():

    st.markdown(
        """
        <div class="section-heading">
            ℹ️ About AI Interview Simulator
        </div>

        <div class="section-description">
            A portfolio-ready AI interview preparation platform.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="dark-panel">

            <div class="panel-title">
                🤖 What is AI Interview Simulator?
            </div>

            <div style="
                color:#94a3b8;
                margin-top:14px;
                line-height:1.8;
                font-size:14px;
            ">
                AI Interview Simulator is an AI-powered application
                designed to help students and job seekers practice
                realistic interviews, receive instant feedback and
                identify areas for improvement.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🛠️
                </div>

                <div class="feature-title">
                    Technology Stack
                </div>

                <div class="feature-text">
                    Python<br>
                    Streamlit<br>
                    Groq API<br>
                    PyPDF2<br>
                    GitHub<br>
                    Streamlit Cloud
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            """
            <div class="feature-card">

                <div class="feature-icon">
                    🚀
                </div>

                <div class="feature-title">
                    Future Improvements
                </div>

                <div class="feature-text">
                    Voice interviews<br>
                    Video interviews<br>
                    Downloadable reports<br>
                    Performance charts<br>
                    Multi-language support<br>
                    Advanced AI models
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# ROUTER
# ============================================================

show_sidebar()

page = st.session_state.page

if page == "Home":

    show_home()

elif page == "Interview Setup":

    show_interview_setup()

elif page == "Mock Interview":

    show_mock_interview()

elif page == "Results":

    show_results()

elif page == "History":

    show_history()

elif page == "About":

    show_about()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <b style="color:#64748b;">
            🤖 AI Interview Simulator
        </b>

        <br><br>

        Built with Python • Streamlit • Groq AI

        <br>

        Practice. Improve. Get Interview-Ready. 🚀

    </div>
    """,
    unsafe_allow_html=True
)
