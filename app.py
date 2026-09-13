import json
import os
from statistics import mean

import streamlit as st
from groq import Groq

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
# PROFESSIONAL UI / CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

.stApp {
    background: #f5f7fb !important;
    color: #172033 !important;
}

.main .block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: #172033 !important;
    font-weight: 700 !important;
}

p {
    color: #475569 !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background: #111827 !important;
    border-right: 1px solid #1f2937 !important;
}

section[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: #1f2937 !important;
    color: #ffffff !important;
    border: 1px solid #374151 !important;
    border-radius: 12px !important;
    min-height: 45px !important;
    font-weight: 600 !important;
    margin-bottom: 5px !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: #2563eb !important;
    border-color: #3b82f6 !important;
    color: #ffffff !important;
}


/* ============================================================
   HERO
   ============================================================ */

.hero-card {
    background: linear-gradient(
        135deg,
        #2563eb 0%,
        #4f46e5 50%,
        #7c3aed 100%
    ) !important;

    padding: 2.3rem;
    border-radius: 22px;
    margin-bottom: 1.5rem;

    box-shadow:
        0 12px 35px rgba(37, 99, 235, 0.18);
}

.hero-title {
    color: #ffffff !important;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
}

.hero-subtitle {
    color: #e0e7ff !important;
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.7rem;
}

.hero-description {
    color: #eef2ff !important;
    font-size: 1rem;
    line-height: 1.65;
}


/* ============================================================
   CARDS
   ============================================================ */

.custom-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 18px;
    padding: 1.4rem;
    margin: 0.7rem 0;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.06);
}

.card-title {
    color: #172033 !important;
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 0.6rem;
}

.card-text {
    color: #64748b !important;
    line-height: 1.6;
}


/* ============================================================
   STAT CARDS
   ============================================================ */

.stat-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 17px;
    padding: 1.3rem;
    text-align: center;

    box-shadow:
        0 5px 18px rgba(15, 23, 42, 0.05);
}

.stat-number {
    color: #2563eb !important;
    font-size: 2rem;
    font-weight: 800;
}

.stat-label {
    color: #64748b !important;
    font-size: 0.9rem;
    font-weight: 600;
}


/* ============================================================
   LABELS
   ============================================================ */

label,
[data-testid="stWidgetLabel"] p {
    color: #334155 !important;
    font-weight: 600 !important;
}


/* ============================================================
   SELECTBOX
   ============================================================ */

/* Main selectbox */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #172033 !important;

    border: 1px solid #cbd5e1 !important;
    border-radius: 11px !important;

    min-height: 48px !important;
}

/* Selected text */
div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
    color: #172033 !important;
}

/* Input text */
div[data-testid="stSelectbox"] div[data-baseweb="select"] input {
    color: #172033 !important;
}

/* Dropdown arrow */
div[data-testid="stSelectbox"] svg {
    fill: #475569 !important;
}


/* ============================================================
   DROPDOWN POPUP
   ============================================================ */

div[data-baseweb="popover"] {
    background: #ffffff !important;
}

div[data-baseweb="popover"] * {
    color: #172033 !important;
}

div[role="listbox"] {
    background: #ffffff !important;
}

div[role="option"] {
    background: #ffffff !important;
    color: #172033 !important;
}

div[role="option"]:hover {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
}


/* ============================================================
   TEXT INPUT
   ============================================================ */

div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    color: #172033 !important;

    border: 1px solid #cbd5e1 !important;
    border-radius: 11px !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #94a3b8 !important;
}


/* ============================================================
   TEXT AREA
   ============================================================ */

div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #172033 !important;

    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;
}

div[data-testid="stTextArea"] textarea::placeholder {
    color: #94a3b8 !important;
}


/* ============================================================
   FILE UPLOADER
   ============================================================ */

section[data-testid="stFileUploaderDropzone"] {
    background: #ffffff !important;
    border: 1px dashed #94a3b8 !important;
    border-radius: 14px !important;
}

section[data-testid="stFileUploaderDropzone"] * {
    color: #475569 !important;
}

section[data-testid="stFileUploaderDropzone"] button {
    background: #eff6ff !important;
    color: #2563eb !important;

    border: 1px solid #bfdbfe !important;
    border-radius: 9px !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {
    background: #ffffff !important;
    color: #172033 !important;

    border: 1px solid #cbd5e1 !important;
    border-radius: 12px !important;

    min-height: 46px !important;
    font-weight: 600 !important;

    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    border-color: #3b82f6 !important;

    transform: translateY(-1px);
}


/* ============================================================
   METRICS
   ============================================================ */

div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 1rem !important;

    box-shadow:
        0 4px 15px rgba(15, 23, 42, 0.05);
}

div[data-testid="stMetricLabel"] {
    color: #64748b !important;
}

div[data-testid="stMetricValue"] {
    color: #2563eb !important;
}


/* ============================================================
   INTERVIEWER CARD
   ============================================================ */

.interviewer-card {
    background: #ffffff !important;

    border: 1px solid #dbe4f0 !important;
    border-radius: 20px;

    padding: 1.8rem;
    margin: 1rem 0;

    box-shadow:
        0 8px 25px rgba(15, 23, 42, 0.07);
}

.ai-badge {
    display: inline-block;

    background: #eef2ff !important;
    color: #4f46e5 !important;

    padding: 0.45rem 0.85rem;
    border-radius: 999px;

    font-size: 0.82rem;
    font-weight: 700;

    margin-bottom: 0.9rem;
}

.question-box {
    background: #f8fafc !important;

    border-left: 4px solid #4f46e5;

    padding: 1.25rem;
    border-radius: 12px;

    color: #172033 !important;

    font-size: 1.08rem;
    line-height: 1.7;

    margin-top: 0.7rem;
}


/* ============================================================
   PROGRESS
   ============================================================ */

div[data-testid="stProgress"] > div > div {
    background: linear-gradient(
        90deg,
        #2563eb,
        #7c3aed
    ) !important;
}


/* ============================================================
   EXPANDERS
   ============================================================ */

div[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
}


/* ============================================================
   ALERTS
   ============================================================ */

div[data-testid="stAlert"] {
    border-radius: 12px !important;
}


/* ============================================================
   FOOTER
   ============================================================ */

.footer {
    text-align: center;
    color: #94a3b8 !important;
    font-size: 0.85rem;
    padding: 2rem 0 1rem;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "page": "Dashboard",
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
    """Get Groq client from Streamlit Secrets or environment."""

    api_key = None

    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass

    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return None

    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"⚠️ Could not initialize Groq: {e}")
        return None


# ============================================================
# RESUME TEXT EXTRACTION
# ============================================================

def extract_resume_text(uploaded_file):
    """Extract readable text from uploaded PDF."""

    if PdfReader is None:
        st.error("PyPDF2 is not installed.")
        return ""

    if uploaded_file is None:
        return ""

    try:
        reader = PdfReader(uploaded_file)

        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        text = "\n".join(pages).strip()

        if not text:
            st.warning(
                "⚠️ No readable text was found in this PDF."
            )
            return ""

        return text

    except Exception as e:
        st.error(
            f"⚠️ Could not read the resume PDF: {e}"
        )
        return ""


# ============================================================
# GENERATE QUESTION
# ============================================================

def generate_question():
    """Generate one personalized interview question."""

    client = get_groq_client()

    if client is None:
        st.error(
            "⚠️ Groq API key is missing. "
            "Add GROQ_API_KEY in Streamlit Cloud Secrets."
        )
        return None

    config = st.session_state.interview_config

    role = config.get(
        "job_role",
        "Software Engineer",
    )

    interview_type = config.get(
        "interview_type",
        "Technical Interview",
    )

    difficulty = config.get(
        "difficulty",
        "Intermediate",
    )

    experience = config.get(
        "experience",
        "Fresher",
    )

    previous_questions = st.session_state.questions

    previous_text = "\n".join(
        previous_questions[-5:]
    )

    resume_context = st.session_state.get(
        "resume_text",
        "",
    )

    resume_context = resume_context[:5000]

    prompt = f"""
You are a professional AI interviewer.

Generate ONE interview question.

Candidate profile:
Job Role: {role}
Interview Type: {interview_type}
Difficulty: {difficulty}
Experience: {experience}

Previous questions:
{previous_text if previous_text else "None"}

Resume information:
{resume_context if resume_context else "No resume provided."}

Rules:
- Generate exactly ONE question.
- Match the job role.
- Match the interview type.
- Match the difficulty.
- Do not repeat previous questions.
- Technical interviews should test practical technical knowledge.
- HR interviews should test professional communication.
- Behavioral interviews should use realistic scenarios.
- Mixed interviews should vary appropriately.
- Keep it clear and interview-ready.
- Return ONLY the question.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert interviewer. "
                        "Return only one interview question."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
            max_tokens=300,
        )

        question = (
            response.choices[0]
            .message.content
            .strip()
        )

        if not question:
            st.error(
                "⚠️ AI returned an empty question."
            )
            return None

        return question

    except Exception as e:

        st.error(
            f"⚠️ Error generating question: {e}"
        )

        return None


# ============================================================
# EVALUATE ANSWER
# ============================================================

def evaluate_answer(question, answer):
    """Evaluate an interview answer with AI."""

    client = get_groq_client()

    if client is None:
        st.error(
            "⚠️ Groq API key is missing."
        )
        return None

    config = st.session_state.interview_config

    role = config.get(
        "job_role",
        "Software Engineer",
    )

    interview_type = config.get(
        "interview_type",
        "Technical Interview",
    )

    difficulty = config.get(
        "difficulty",
        "Intermediate",
    )

    experience = config.get(
        "experience",
        "Fresher",
    )

    prompt = f"""
Evaluate this interview answer fairly.

Candidate:
Role: {role}
Interview Type: {interview_type}
Difficulty: {difficulty}
Experience: {experience}

Question:
{question}

Candidate Answer:
{answer}

Give scores from 0 to 10.

Return ONLY valid JSON:

{{
    "score": 8,
    "correctness": 8,
    "relevance": 9,
    "technical_knowledge": 7,
    "communication": 8,
    "confidence": 8,
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "improvements": [
        "Improvement 1",
        "Improvement 2"
    ],
    "better_answer": "Example of a stronger answer.",
    "concepts_to_review": [
        "Concept 1",
        "Concept 2"
    ]
}}

Rules:
- All numeric scores must be 0-10.
- Strengths must be a list.
- Improvements must be a list.
- Concepts must be a list.
- Better answer must be a string.
- Be fair to a fresher.
- Do not invent achievements.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert interview evaluator. "
                        "Return only valid JSON."
                    ),
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
            response.choices[0]
            .message.content
            .strip()
        )

        if result.startswith("```"):
            result = result.replace(
                "```json",
                "",
            )
            result = result.replace(
                "```",
                "",
            )
            result = result.strip()

        evaluation = json.loads(result)

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
                            0,
                        )
                    )
                )

                evaluation[field] = max(
                    0,
                    min(10, value),
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
                list,
            ):
                evaluation[field] = []

        if not isinstance(
            evaluation.get("better_answer"),
            str,
        ):
            evaluation["better_answer"] = ""

        return evaluation

    except json.JSONDecodeError:

        st.error(
            "⚠️ AI returned an invalid evaluation format."
        )

        return None

    except Exception as e:

        st.error(
            f"⚠️ Error evaluating answer: {e}"
        )

        return None


# ============================================================
# FINAL REPORT
# ============================================================

def generate_final_report():

    evaluations = st.session_state.evaluations

    if not evaluations:

        return {
            "overall_score": 0,
            "technical_knowledge": 0,
            "communication": 0,
            "problem_solving": 0,
            "relevance": 0,
            "confidence": 0,
        }

    technical = mean(
        [
            e.get(
                "technical_knowledge",
                0,
            )
            for e in evaluations
        ]
    )

    communication = mean(
        [
            e.get(
                "communication",
                0,
            )
            for e in evaluations
        ]
    )

    relevance = mean(
        [
            e.get(
                "relevance",
                0,
            )
            for e in evaluations
        ]
    )

    confidence = mean(
        [
            e.get(
                "confidence",
                0,
            )
            for e in evaluations
        ]
    )

    correctness = mean(
        [
            e.get(
                "correctness",
                0,
            )
            for e in evaluations
        ]
    )

    overall = mean(
        [
            e.get(
                "score",
                0,
            )
            for e in evaluations
        ]
    )

    return {
        "overall_score": round(
            overall * 10
        ),
        "technical_knowledge": round(
            technical,
            1,
        ),
        "communication": round(
            communication,
            1,
        ),
        "problem_solving": round(
            correctness,
            1,
        ),
        "relevance": round(
            relevance,
            1,
        ),
        "confidence": round(
            confidence,
            1,
        ),
    }


# ============================================================
# RESET INTERVIEW
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
            <div style="
                text-align:center;
                padding:10px 0 20px 0;
            ">

                <div style="
                    font-size:48px;
                ">
                    🤖
                </div>

                <div style="
                    font-size:22px;
                    font-weight:800;
                    color:white;
                ">
                    AI Interview
                </div>

                <div style="
                    font-size:14px;
                    color:#9ca3af;
                    margin-top:4px;
                ">
                    Simulator
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        st.markdown(
            "### 🧭 Navigation"
        )

        if st.button(
            "🏠 Dashboard",
            use_container_width=True,
        ):

            st.session_state.page = "Dashboard"
            st.rerun()

        if st.button(
            "⚙️ Interview Setup",
            use_container_width=True,
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        if st.button(
            "🎤 Mock Interview",
            use_container_width=True,
        ):

            if st.session_state.interview_started:
                st.session_state.page = "Mock Interview"
            else:
                st.session_state.page = "Interview Setup"

            st.rerun()

        if st.button(
            "📊 Results",
            use_container_width=True,
        ):

            st.session_state.page = "Results"
            st.rerun()

        if st.button(
            "📚 Interview History",
            use_container_width=True,
        ):

            st.session_state.page = "Interview History"
            st.rerun()

        if st.button(
            "ℹ️ About",
            use_container_width=True,
        ):

            st.session_state.page = "About"
            st.rerun()

        st.markdown("---")

        st.markdown(
            """
            <div style="
                background:#1f2937;
                padding:14px;
                border-radius:12px;
            ">

                <div style="
                    font-weight:700;
                    color:white;
                ">
                    🚀 AI Practice
                </div>

                <div style="
                    font-size:13px;
                    color:#9ca3af;
                    margin-top:5px;
                    line-height:1.5;
                ">
                    Practice interviews, receive AI feedback,
                    and improve your confidence.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    st.markdown(
        """
        <div class="hero-card">

            <div class="hero-title">
                🤖 AI Interview Simulator
            </div>

            <div class="hero-subtitle">
                Practice. Improve. Get Interview-Ready.
            </div>

            <div class="hero-description">
                Practice realistic interviews with an AI interviewer,
                receive detailed feedback, discover weak areas,
                and improve your interview performance.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    total_questions = sum(
        len(item.get("questions", []))
        for item in st.session_state.history
    )

    if st.session_state.scores:

        avg_score = round(
            mean(
                st.session_state.scores
            ) * 10
        )

    else:

        avg_score = 0

    improvement_count = 0

    for evaluation in st.session_state.evaluations:

        improvement_count += len(
            evaluation.get(
                "improvements",
                [],
            )
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {total_questions}
                </div>
                <div class="stat-label">
                    Interview Questions
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {avg_score}%
                </div>
                <div class="stat-label">
                    Average Score
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {st.session_state.interview_count}
                </div>
                <div class="stat-label">
                    Interviews Completed
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col4:

        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">
                    {improvement_count}
                </div>
                <div class="stat-label">
                    Improvement Areas
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    col1, col2 = st.columns([1.3, 1])

    with col1:

        st.markdown(
            """
            <div class="custom-card">

                <div class="card-title">
                    🎯 Prepare for Your Next Interview
                </div>

                <div class="card-text">
                    Choose your job role, interview type,
                    difficulty level, experience, and number
                    of questions. The AI interviewer will
                    generate personalized questions for you.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🚀 Start Your First Interview",
            use_container_width=True,
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

    with col2:

        st.markdown(
            """
            <div class="custom-card">

                <div class="card-title">
                    ✨ What You Get
                </div>

                <div class="card-text">
                    • AI-generated interview questions<br>
                    • Detailed answer evaluation<br>
                    • Technical and communication scores<br>
                    • Strengths and improvement areas<br>
                    • Better answer suggestions<br>
                    • Interview performance report
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# INTERVIEW SETUP
# ============================================================

def show_interview_setup():

    st.title("⚙️ Interview Setup")

    st.markdown(
        "Customize your interview before you begin."
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        job_roles = [
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

        job_role = st.selectbox(
            "💼 Job Role",
            job_roles,
        )

        if job_role == "Custom Role":

            job_role = st.text_input(
                "Enter your custom job role",
                placeholder=(
                    "e.g. Generative AI Engineer"
                ),
            )

        interview_type = st.selectbox(
            "🎤 Interview Type",
            [
                "Technical Interview",
                "HR Interview",
                "Behavioral Interview",
                "Mixed Interview",
            ],
        )

        difficulty = st.selectbox(
            "📈 Difficulty",
            [
                "Beginner",
                "Intermediate",
                "Advanced",
                "Expert",
            ],
        )

    with col2:

        number_questions = st.selectbox(
            "🔢 Number of Questions",
            [5, 10, 15],
        )

        experience = st.selectbox(
            "👨‍💻 Experience Level",
            [
                "Fresher",
                "0–1 Years",
                "1–3 Years",
                "3+ Years",
            ],
        )

        st.markdown(
            "### 📄 Optional Resume"
        )

        resume_file = st.file_uploader(
            "Upload your resume PDF",
            type=["pdf"],
        )

        if resume_file is not None:

            if (
                st.session_state.resume_name
                != resume_file.name
            ):

                with st.spinner(
                    "Reading your resume..."
                ):

                    resume_text = (
                        extract_resume_text(
                            resume_file
                        )
                    )

                st.session_state.resume_text = (
                    resume_text
                )

                st.session_state.resume_name = (
                    resume_file.name
                )

                if resume_text:

                    st.success(
                        "✅ Resume successfully loaded."
                    )

    st.markdown("---")

    st.markdown(
        """
        <div class="custom-card">

            <div class="card-title">
                💡 Interview Configuration
            </div>

            <div class="card-text">
                Your AI interviewer will generate questions
                based on your selected role, interview type,
                difficulty level, experience level, and
                optional resume.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "🚀 Start Interview",
        use_container_width=True,
    ):

        if not job_role.strip():

            st.warning(
                "⚠️ Please enter a job role."
            )

            return

        reset_interview()

        st.session_state.interview_config = {
            "job_role": job_role,
            "interview_type": interview_type,
            "difficulty": difficulty,
            "number_questions": number_questions,
            "experience": experience,
        }

        st.session_state.interview_started = True

        st.session_state.page = "Mock Interview"

        st.rerun()


# ============================================================
# AI EVALUATION DISPLAY
# ============================================================

def show_evaluation(evaluation):

    st.markdown("### 🧠 AI Evaluation")

    score = evaluation.get(
        "score",
        0,
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "Score",
            f"{score}/10",
        )

    with col2:
        st.metric(
            "Correctness",
            f"{evaluation.get('correctness', 0)}/10",
        )

    with col3:
        st.metric(
            "Relevance",
            f"{evaluation.get('relevance', 0)}/10",
        )

    with col4:
        st.metric(
            "Technical",
            f"{evaluation.get('technical_knowledge', 0)}/10",
        )

    with col5:
        st.metric(
            "Communication",
            f"{evaluation.get('communication', 0)}/10",
        )

    with col6:
        st.metric(
            "Confidence",
            f"{evaluation.get('confidence', 0)}/10",
        )

    strengths = evaluation.get(
        "strengths",
        [],
    )

    improvements = evaluation.get(
        "improvements",
        [],
    )

    concepts = evaluation.get(
        "concepts_to_review",
        [],
    )

    better_answer = evaluation.get(
        "better_answer",
        "",
    )

    if strengths:

        with st.expander(
            "💪 Strengths",
            expanded=True,
        ):

            for item in strengths:
                st.markdown(
                    f"• {item}"
                )

    if improvements:

        with st.expander(
            "📈 Areas to Improve",
            expanded=True,
        ):

            for item in improvements:
                st.markdown(
                    f"• {item}"
                )

    if better_answer:

        with st.expander(
            "✨ Better Answer",
            expanded=False,
        ):

            st.write(
                better_answer
            )

    if concepts:

        with st.expander(
            "📚 Concepts to Review",
            expanded=False,
        ):

            for item in concepts:
                st.markdown(
                    f"• {item}"
                )


# ============================================================
# MOCK INTERVIEW
# ============================================================

def show_mock_interview():

    if not st.session_state.interview_started:

        st.warning(
            "Please configure your interview first."
        )

        if st.button(
            "⚙️ Go to Interview Setup",
            use_container_width=True,
        ):

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

        return

    config = st.session_state.interview_config

    total_questions = config.get(
        "number_questions",
        5,
    )

    current_index = (
        st.session_state.current_question
    )

    if current_index >= total_questions:

        st.session_state.interview_finished = True

        if not st.session_state.result_counted:

            st.session_state.interview_count += 1

            st.session_state.result_counted = True

            report = generate_final_report()

            st.session_state.history.append(
                {
                    "role": config.get(
                        "job_role",
                        "Unknown",
                    ),
                    "type": config.get(
                        "interview_type",
                        "Unknown",
                    ),
                    "difficulty": config.get(
                        "difficulty",
                        "Unknown",
                    ),
                    "score": report.get(
                        "overall_score",
                        0,
                    ),
                    "questions": list(
                        st.session_state.questions
                    ),
                    "answers": list(
                        st.session_state.answers
                    ),
                    "evaluations": list(
                        st.session_state.evaluations
                    ),
                }
            )

        st.session_state.page = "Results"

        st.rerun()

        return

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.title("🎤 Mock Interview")

    st.markdown(
        f"""
        **{config.get('job_role', 'Software Engineer')}**
        &nbsp; • &nbsp;
        {config.get('interview_type', 'Technical Interview')}
        &nbsp; • &nbsp;
        {config.get('difficulty', 'Intermediate')}
        """
    )

    progress_value = (
        (current_index + 1)
        / total_questions
    )

    st.progress(
        progress_value,
        text=(
            f"Question {current_index + 1} "
            f"of {total_questions}"
        ),
    )

    # --------------------------------------------------------
    # GENERATE QUESTION
    # --------------------------------------------------------

    if (
        len(st.session_state.questions)
        <= current_index
    ):

        with st.spinner(
            "🤖 AI interviewer is preparing your question..."
        ):

            question = generate_question()

        if question:

            st.session_state.questions.append(
                question
            )

        else:

            return

    question = st.session_state.questions[
        current_index
    ]

    # --------------------------------------------------------
    # QUESTION CARD
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="interviewer-card">

            <div class="ai-badge">
                🤖 AI INTERVIEWER
            </div>

            <div class="card-title">
                Question {current_index + 1}
            </div>

            <div class="question-box">
                {question}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # ANSWER
    # --------------------------------------------------------

    st.markdown(
        "### 📝 Your Answer"
    )

    answer = st.text_area(
        "Write your answer below",
        height=220,
        placeholder=(
            "Type your answer as if you were "
            "speaking to a real interviewer..."
        ),
        key=f"answer_{current_index}",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns(2)

    with col1:

        submit = st.button(
            "✅ Submit Answer",
            use_container_width=True,
        )

    with col2:

        skip = st.button(
            "⏭️ Skip Question",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # SUBMIT ANSWER
    # --------------------------------------------------------

    if submit:

        if not answer.strip():

            st.warning(
                "⚠️ Please write an answer before submitting."
            )

        else:

            with st.spinner(
                "🧠 AI is evaluating your answer..."
            ):

                evaluation = evaluate_answer(
                    question,
                    answer,
                )

            if evaluation:

                score = evaluation.get(
                    "score",
                    0,
                )

                st.session_state.answers.append(
                    answer
                )

                st.session_state.evaluations.append(
                    evaluation
                )

                st.session_state.scores.append(
                    score
                )

                st.session_state.current_question += 1

                st.rerun()

    # --------------------------------------------------------
    # SKIP QUESTION
    # --------------------------------------------------------

    if skip:

        st.session_state.answers.append(
            "[Question skipped]"
        )

        skipped_evaluation = {
            "score": 0,
            "correctness": 0,
            "relevance": 0,
            "technical_knowledge": 0,
            "communication": 0,
            "confidence": 0,
            "strengths": [],
            "improvements": [
                "Try to answer every interview question."
            ],
            "better_answer": "",
            "concepts_to_review": [],
        }

        st.session_state.evaluations.append(
            skipped_evaluation
        )

        st.session_state.scores.append(0)

        st.session_state.current_question += 1

        st.rerun()


# ============================================================
# RESULTS
# ============================================================

def show_results():

    st.title(
        "🎯 Interview Complete!"
    )

    if not st.session_state.evaluations:

        st.info(
            "No interview results are available yet."
        )

        if st.button(
            "🚀 Start an Interview",
            use_container_width=True,
        ):

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

        return

    report = generate_final_report()

    overall = report["overall_score"]

    if overall >= 90:

        level = "Excellent 🏆"

        message = (
            "Outstanding performance! "
            "You are showing strong interview readiness."
        )

    elif overall >= 80:

        level = "Very Good 🌟"

        message = (
            "Great performance! "
            "A little more practice can make you even stronger."
        )

    elif overall >= 70:

        level = "Good 👍"

        message = (
            "Good foundation. "
            "Focus on your improvement areas."
        )

    else:

        level = "Needs Improvement 📈"

        message = (
            "Keep practicing. "
            "Every interview is an opportunity to improve."
        )

    # --------------------------------------------------------
    # SCORE HERO
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="hero-card" style="text-align:center;">

            <div style="
                font-size:4rem;
                font-weight:800;
                color:white;
            ">
                {overall}/100
            </div>

            <div style="
                font-size:1.5rem;
                font-weight:700;
                color:white;
            ">
                {level}
            </div>

            <div style="
                color:#e0e7ff;
                margin-top:8px;
            ">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # PERFORMANCE
    # --------------------------------------------------------

    st.subheader(
        "📊 Performance Breakdown"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Technical Knowledge",
            f"{report['technical_knowledge']}/10",
        )

    with col2:

        st.metric(
            "Communication",
            f"{report['communication']}/10",
        )

    with col3:

        st.metric(
            "Problem Solving",
            f"{report['problem_solving']}/10",
        )

    with col4:

        st.metric(
            "Relevance",
            f"{report['relevance']}/10",
        )

    with col5:

        st.metric(
            "Confidence",
            f"{report['confidence']}/10",
        )

    # --------------------------------------------------------
    # FEEDBACK
    # --------------------------------------------------------

    strengths = []
    improvements = []
    concepts = []

    for evaluation in (
        st.session_state.evaluations
    ):

        strengths.extend(
            evaluation.get(
                "strengths",
                [],
            )
        )

        improvements.extend(
            evaluation.get(
                "improvements",
                [],
            )
        )

        concepts.extend(
            evaluation.get(
                "concepts_to_review",
                [],
            )
        )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="custom-card">

                <div class="card-title">
                    💪 Your Strengths
                </div>
            """,
            unsafe_allow_html=True,
        )

        unique_strengths = list(
            dict.fromkeys(strengths)
        )

        if unique_strengths:

            for item in unique_strengths[:8]:

                st.markdown(
                    f"✅ {item}"
                )

        else:

            st.write(
                "Complete more answers to identify your strengths."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="custom-card">

                <div class="card-title">
                    📈 Areas to Improve
                </div>
            """,
            unsafe_allow_html=True,
        )

        unique_improvements = list(
            dict.fromkeys(improvements)
        )

        if unique_improvements:

            for item in unique_improvements[:8]:

                st.markdown(
                    f"🔹 {item}"
                )

        else:

            st.write(
                "No major improvement areas identified."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # CONCEPTS
    # --------------------------------------------------------

    if concepts:

        st.subheader(
            "📚 Concepts to Review"
        )

        unique_concepts = list(
            dict.fromkeys(concepts)
        )

        for concept in unique_concepts[:12]:

            st.markdown(
                f"• {concept}"
            )

    # --------------------------------------------------------
    # QUESTION REVIEW
    # --------------------------------------------------------

    st.subheader(
        "📝 Question-by-Question Review"
    )

    for index, question in enumerate(
        st.session_state.questions
    ):

        evaluation = (
            st.session_state.evaluations[index]
            if index
            < len(
                st.session_state.evaluations
            )
            else {}
        )

        answer = (
            st.session_state.answers[index]
            if index
            < len(
                st.session_state.answers
            )
            else "[No answer]"
        )

        score = evaluation.get(
            "score",
            0,
        )

        with st.expander(
            f"Question {index + 1} — Score: {score}/10"
        ):

            st.markdown(
                "**Question:**"
            )

            st.write(question)

            st.markdown(
                "**Your Answer:**"
            )

            st.write(answer)

            st.markdown(
                "**AI Feedback:**"
            )

            st.write(
                "Correctness:",
                f"{evaluation.get('correctness', 0)}/10",
            )

            st.write(
                "Relevance:",
                f"{evaluation.get('relevance', 0)}/10",
            )

            st.write(
                "Technical Knowledge:",
                f"{evaluation.get('technical_knowledge', 0)}/10",
            )

            st.write(
                "Communication:",
                f"{evaluation.get('communication', 0)}/10",
            )

            st.write(
                "Confidence:",
                f"{evaluation.get('confidence', 0)}/10",
            )

            better_answer = evaluation.get(
                "better_answer",
                "",
            )

            if better_answer:

                st.markdown(
                    "**✨ Better Answer:**"
                )

                st.write(
                    better_answer
                )

    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🔄 Start New Interview",
            use_container_width=True,
        ):

            reset_interview()

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

    with col2:

        if st.button(
            "🏠 Back to Dashboard",
            use_container_width=True,
        ):

            st.session_state.page = (
                "Dashboard"
            )

            st.rerun()


# ============================================================
# HISTORY
# ============================================================

def show_history():

    st.title(
        "📚 Interview History"
    )

    history = st.session_state.history

    if not history:

        st.info(
            "You have not completed any interviews yet."
        )

        if st.button(
            "🚀 Start Your First Interview",
            use_container_width=True,
        ):

            st.session_state.page = (
                "Interview Setup"
            )

            st.rerun()

        return

    for index, item in enumerate(
        reversed(history),
        start=1,
    ):

        with st.expander(
            f"Interview {index} — "
            f"{item.get('role', 'Unknown Role')} — "
            f"{item.get('score', 0)}/100"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write(
                    "**Role:**",
                    item.get(
                        "role",
                        "Unknown",
                    ),
                )

            with col2:

                st.write(
                    "**Type:**",
                    item.get(
                        "type",
                        "Unknown",
                    ),
                )

            with col3:

                st.write(
                    "**Difficulty:**",
                    item.get(
                        "difficulty",
                        "Unknown",
                    ),
                )

            st.progress(
                item.get(
                    "score",
                    0,
                ) / 100
            )


# ============================================================
# ABOUT
# ============================================================

def show_about():

    st.title(
        "ℹ️ About AI Interview Simulator"
    )

    st.markdown(
        """
        <div class="custom-card">

            <div class="card-title">
                🤖 AI Interview Simulator
            </div>

            <div class="card-text">

                AI Interview Simulator is an AI-powered
                mock interview platform designed to help
                students and job seekers practice interviews.

                <br><br>

                <b>Technology Stack</b>

                <br><br>

                🐍 Python<br>
                🎨 Streamlit<br>
                🧠 Groq API<br>
                📄 PyPDF2<br>
                ☁️ Streamlit Cloud<br>
                🐙 GitHub

                <br><br>

                <b>Core Features</b>

                <br><br>

                • Personalized AI interview questions<br>
                • Technical, HR and behavioral interviews<br>
                • Multiple difficulty levels<br>
                • AI answer evaluation<br>
                • Performance scoring<br>
                • Strength and weakness analysis<br>
                • Better answer suggestions<br>
                • Resume-based questions<br>
                • Interview history

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "### 🚀 Future Improvements"
    )

    future_items = [
        "🎤 Voice-based interviews",
        "📹 Video interview simulation",
        "📄 Advanced resume analysis",
        "📊 Performance charts",
        "🏆 Interview leaderboard",
        "💬 Follow-up interview questions",
        "📥 Downloadable interview reports",
        "🌍 Multi-language interviews",
    ]

    for item in future_items:

        st.markdown(
            f"• {item}"
        )


# ============================================================
# PAGE ROUTING
# ============================================================

show_sidebar()

if st.session_state.page == "Dashboard":

    show_dashboard()

elif st.session_state.page == "Interview Setup":

    show_interview_setup()

elif st.session_state.page == "Mock Interview":

    show_mock_interview()

elif st.session_state.page == "Results":

    show_results()

elif st.session_state.page == "Interview History":

    show_history()

elif st.session_state.page == "About":

    show_about()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        🤖 AI Interview Simulator
        &nbsp; • &nbsp;
        Built with Python, Streamlit & Groq

        <br>

        Practice. Improve. Get Interview-Ready. 🚀

    </div>
    """,
    unsafe_allow_html=True,
)
