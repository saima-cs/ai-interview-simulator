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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

/* ---------- MAIN APP ---------- */

.stApp {
    background: #f7f9fc;
}

.main .block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: #101828;
}

section[data-testid="stSidebar"] * {
    color: #ffffff;
}

.sidebar-logo {
    text-align: center;
    padding: 15px 0 25px 0;
}

.sidebar-logo-icon {
    font-size: 48px;
}

.sidebar-logo-title {
    font-size: 23px;
    font-weight: 800;
    color: white;
}

.sidebar-logo-subtitle {
    color: #98a2b3;
    font-size: 13px;
    margin-top: 4px;
}


/* ---------- SIDEBAR BUTTONS ---------- */

section[data-testid="stSidebar"] .stButton button {
    width: 100%;
    background: #1d2939 !important;
    color: #ffffff !important;
    border: 1px solid #344054 !important;
    border-radius: 12px !important;
    min-height: 45px !important;
    font-weight: 600 !important;
    margin-bottom: 7px !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: #344054 !important;
    border-color: #667085 !important;
}


/* ---------- HERO ---------- */

.hero {
    background:
        radial-gradient(
            circle at top right,
            rgba(255,255,255,0.18),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #2563eb,
            #4f46e5 55%,
            #7c3aed
        );

    border-radius: 28px;
    padding: 55px 50px;
    color: white;
    box-shadow: 0 20px 50px rgba(79,70,229,0.20);
    margin-bottom: 28px;
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 8px 15px;
    border-radius: 30px;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 18px;
}

.hero h1 {
    color: white !important;
    font-size: 48px !important;
    line-height: 1.08 !important;
    margin: 0 !important;
    font-weight: 800 !important;
}

.hero h2 {
    color: #e0e7ff !important;
    font-size: 22px !important;
    margin-top: 15px !important;
    font-weight: 600 !important;
}

.hero p {
    color: #eef2ff !important;
    font-size: 16px !important;
    line-height: 1.7 !important;
    max-width: 700px;
}


/* ---------- SECTION TITLE ---------- */

.section-title {
    font-size: 27px;
    font-weight: 800;
    color: #101828;
    margin-top: 35px;
    margin-bottom: 8px;
}

.section-subtitle {
    color: #667085;
    margin-bottom: 22px;
}


/* ---------- FEATURE CARDS ---------- */

.feature-card {
    background: white;
    border: 1px solid #eaecf0;
    border-radius: 18px;
    padding: 25px;
    min-height: 175px;
    box-shadow: 0 8px 25px rgba(16,24,40,0.05);
}

.feature-icon {
    font-size: 32px;
    margin-bottom: 10px;
}

.feature-title {
    color: #101828;
    font-size: 18px;
    font-weight: 750;
    margin-bottom: 8px;
}

.feature-text {
    color: #667085;
    line-height: 1.55;
    font-size: 14px;
}


/* ---------- STAT CARDS ---------- */

.stat-card {
    background: white;
    border: 1px solid #eaecf0;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 5px 20px rgba(16,24,40,0.04);
}

.stat-number {
    color: #4f46e5;
    font-size: 30px;
    font-weight: 800;
}

.stat-label {
    color: #667085;
    font-size: 13px;
    font-weight: 600;
    margin-top: 4px;
}


/* ---------- SETUP CARD ---------- */

.setup-card {
    background: white;
    border: 1px solid #eaecf0;
    border-radius: 20px;
    padding: 28px;
    box-shadow: 0 8px 25px rgba(16,24,40,0.05);
}


/* ---------- INPUTS ---------- */

div[data-baseweb="select"] > div {
    background: white !important;
    color: #101828 !important;
    border-color: #d0d5dd !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] span {
    color: #101828 !important;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    background: white !important;
    color: #101828 !important;
    border-color: #d0d5dd !important;
    border-radius: 10px !important;
}

div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: #98a2b3 !important;
}


/* ---------- BUTTONS ---------- */

.stButton > button {
    border-radius: 11px !important;
    min-height: 45px !important;
    font-weight: 700 !important;
    border: 1px solid #d0d5dd !important;
    background: white !important;
    color: #101828 !important;
}

.stButton > button:hover {
    border-color: #6366f1 !important;
    color: #4338ca !important;
    background: #f5f3ff !important;
}


/* ---------- PRIMARY CTA ---------- */

.primary-btn button {
    background: linear-gradient(
        135deg,
        #4f46e5,
        #7c3aed
    ) !important;

    color: white !important;
    border: none !important;
    font-size: 16px !important;
    min-height: 52px !important;
}

.primary-btn button:hover {
    color: white !important;
    background: linear-gradient(
        135deg,
        #4338ca,
        #6d28d9
    ) !important;
}


/* ---------- INTERVIEW CARD ---------- */

.interview-card {
    background: white;
    border: 1px solid #eaecf0;
    border-radius: 20px;
    padding: 30px;
    box-shadow: 0 10px 30px rgba(16,24,40,0.06);
}

.ai-badge {
    display: inline-block;
    background: #eef2ff;
    color: #4f46e5;
    padding: 7px 13px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 800;
}

.question {
    background: #f8fafc;
    border-left: 5px solid #6366f1;
    border-radius: 12px;
    padding: 20px;
    margin-top: 15px;
    color: #101828;
    font-size: 18px;
    line-height: 1.65;
}


/* ---------- FOOTER ---------- */

.footer {
    text-align: center;
    color: #98a2b3;
    font-size: 13px;
    padding: 35px 0 10px 0;
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
        st.error("Groq package is not installed.")
        return None

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
        st.error(f"Could not initialize Groq: {e}")
        return None


# ============================================================
# RESUME EXTRACTION
# ============================================================

def extract_resume_text(uploaded_file):

    if PdfReader is None:
        st.error("PyPDF2 is not installed.")
        return ""

    if uploaded_file is None:
        return ""

    try:

        reader = PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"

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
You are a professional technical interviewer.

Generate ONE interview question.

Job Role: {role}
Interview Type: {interview_type}
Difficulty: {difficulty}
Experience: {experience}

Previous questions:
{previous if previous else "None"}

Resume:
{resume if resume else "No resume provided"}

Rules:
- Generate exactly ONE question.
- Do not repeat previous questions.
- Match the selected role.
- Match the selected interview type.
- Match the difficulty.
- Make it realistic.
- Keep it concise.
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
                        "Return exactly one question."
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

        result = (
            response.choices[0]
            .message.content
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
                ""
            )
            result = result.replace(
                "```",
                ""
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
                            0
                        )
                    )
                )

                evaluation[field] = max(
                    0,
                    min(10, value)
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

    evaluations = st.session_state.evaluations

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
        e.get("score", 0)
        for e in evaluations
    )

    technical = mean(
        e.get("technical_knowledge", 0)
        for e in evaluations
    )

    communication = mean(
        e.get("communication", 0)
        for e in evaluations
    )

    relevance = mean(
        e.get("relevance", 0)
        for e in evaluations
    )

    confidence = mean(
        e.get("confidence", 0)
        for e in evaluations
    )

    problem_solving = mean(
        e.get("correctness", 0)
        for e in evaluations
    )

    return {
        "overall_score": round(overall * 10),
        "technical": round(technical, 1),
        "communication": round(communication, 1),
        "problem_solving": round(
            problem_solving,
            1
        ),
        "relevance": round(
            relevance,
            1
        ),
        "confidence": round(
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
            <div class="sidebar-logo">

                <div class="sidebar-logo-icon">
                    🤖
                </div>

                <div class="sidebar-logo-title">
                    AI Interview
                </div>

                <div class="sidebar-logo-subtitle">
                    Simulator
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        if st.button(
            "🏠  Home",
            use_container_width=True
        ):
            st.session_state.page = "Home"
            st.rerun()

        if st.button(
            "⚙️  Interview Setup",
            use_container_width=True
        ):
            st.session_state.page = "Interview Setup"
            st.rerun()

        if st.button(
            "🎤  Mock Interview",
            use_container_width=True
        ):

            if st.session_state.interview_started:
                st.session_state.page = "Mock Interview"
            else:
                st.session_state.page = "Interview Setup"

            st.rerun()

        if st.button(
            "📊  Results",
            use_container_width=True
        ):
            st.session_state.page = "Results"
            st.rerun()

        if st.button(
            "📚  History",
            use_container_width=True
        ):
            st.session_state.page = "History"
            st.rerun()

        if st.button(
            "ℹ️  About",
            use_container_width=True
        ):
            st.session_state.page = "About"
            st.rerun()

        st.divider()

        st.caption(
            "🚀 Practice smarter with AI"
        )


# ============================================================
# HOME / FRONT PAGE
# ============================================================

def show_home():

    # HERO
    st.markdown(
        """
        <div class="hero">

            <div class="hero-badge">
                ✨ AI-POWERED INTERVIEW PRACTICE
            </div>

            <h1>
                Ace Your Next<br>
                Interview with AI 🤖
            </h1>

            <h2>
                Practice. Improve. Get Interview-Ready.
            </h2>

            <p>
                Simulate realistic technical, HR and behavioral
                interviews with an AI interviewer. Get instant
                feedback, detailed scoring and personalized
                improvement suggestions.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # CTA
    col1, col2, col3 = st.columns([1, 1.3, 1])

    with col2:

        st.markdown(
            '<div class="primary-btn">',
            unsafe_allow_html=True
        )

        if st.button(
            "🚀 Start Your Free Interview",
            use_container_width=True
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # STATS
    st.markdown(
        '<div class="section-title">Your Progress</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Track your interview preparation journey.</div>',
        unsafe_allow_html=True
    )

    completed = st.session_state.interview_count

    total_questions = sum(
        len(item.get("questions", []))
        for item in st.session_state.history
    )

    if st.session_state.scores:

        average = round(
            mean(st.session_state.scores) * 10
        )

    else:

        average = 0

    cols = st.columns(4)

    stats = [
        ("🎯", completed, "Interviews Completed"),
        ("📝", total_questions, "Questions Practiced"),
        ("⭐", f"{average}%", "Average Score"),
        ("🚀", "∞", "Room to Improve"),
    ]

    for col, data in zip(cols, stats):

        with col:

            icon, number, label = data

            st.markdown(
                f"""
                <div class="stat-card">

                    <div style="font-size:25px;">
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
        '<div class="section-title">Everything You Need to Improve</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">A complete AI-powered interview preparation experience.</div>',
        unsafe_allow_html=True
    )

    features = [
        (
            "🤖",
            "AI Interviewer",
            "Get realistic questions generated specifically for your target role."
        ),
        (
            "🧠",
            "Smart Evaluation",
            "Receive detailed AI feedback on every answer you provide."
        ),
        (
            "📊",
            "Performance Analytics",
            "Understand your technical knowledge, communication and confidence."
        ),
        (
            "📄",
            "Resume-Based Questions",
            "Upload your resume and practice questions related to your profile."
        ),
        (
            "🎯",
            "Multiple Interview Types",
            "Practice Technical, HR, Behavioral or Mixed interviews."
        ),
        (
            "📈",
            "Personalized Improvement",
            "Discover weak areas and get concepts to review."
        ),
    ]

    for row in range(0, len(features), 3):

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
        '<div class="section-title">How It Works</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Start practicing in three simple steps.</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(3)

    steps = [
        (
            "01",
            "Configure",
            "Choose your role, interview type, difficulty and experience."
        ),
        (
            "02",
            "Practice",
            "Answer AI-generated interview questions like a real interview."
        ),
        (
            "03",
            "Improve",
            "Review your score, strengths and personalized feedback."
        ),
    ]

    for col, step in zip(cols, steps):

        with col:

            number, title, text = step

            st.markdown(
                f"""
                <div class="feature-card">

                    <div style="
                        color:#4f46e5;
                        font-size:14px;
                        font-weight:800;
                    ">
                        STEP {number}
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

    # FINAL CTA
    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero" style="text-align:center; padding:40px;">

            <h1 style="font-size:32px !important;">
                Ready to Practice? 🎤
            </h1>

            <p style="
                margin-left:auto;
                margin-right:auto;
            ">
                Turn interview anxiety into interview confidence.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 1.3, 1])

    with col2:

        st.markdown(
            '<div class="primary-btn">',
            unsafe_allow_html=True
        )

        if st.button(
            "🎤 Begin Interview Practice",
            use_container_width=True
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================
# INTERVIEW SETUP
# ============================================================

def show_interview_setup():

    st.title("⚙️ Interview Setup")

    st.caption(
        "Customize your AI interview before you begin."
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.markdown(
            '<div class="setup-card">',
            unsafe_allow_html=True
        )

        st.subheader("🎯 Interview Preferences")

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
                "Enter your role",
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

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    with right:

        st.markdown(
            '<div class="setup-card">',
            unsafe_allow_html=True
        )

        st.subheader("👨‍💻 Candidate Profile")

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
            "### 📄 Optional Resume"
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
                    "Reading resume..."
                ):

                    text = extract_resume_text(
                        resume_file
                    )

                st.session_state.resume_text = text
                st.session_state.resume_name = resume_file.name

            if st.session_state.resume_text:

                st.success(
                    "✅ Resume loaded successfully."
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown(
            '<div class="primary-btn">',
            unsafe_allow_html=True
        )

        if st.button(
            "🚀 Start AI Interview",
            use_container_width=True
        ):

            if not job_role.strip():

                st.warning(
                    "Please enter a job role."
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
            "⚙️ Go to Setup",
            use_container_width=True
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        return

    config = st.session_state.interview_config

    total = config.get(
        "number_questions",
        5
    )

    current = st.session_state.current_question

    if current >= total:

        st.session_state.interview_finished = True

        if not st.session_state.result_counted:

            st.session_state.interview_count += 1
            st.session_state.result_counted = True

            report = generate_final_report()

            st.session_state.history.append(
                {
                    "role": config.get(
                        "job_role",
                        "Unknown"
                    ),
                    "type": config.get(
                        "interview_type",
                        "Unknown"
                    ),
                    "difficulty": config.get(
                        "difficulty",
                        "Unknown"
                    ),
                    "score": report["overall_score"],
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

    st.title("🎤 Mock Interview")

    st.caption(
        f"{config.get('job_role')} • "
        f"{config.get('interview_type')} • "
        f"{config.get('difficulty')}"
    )

    st.progress(
        (current + 1) / total,
        text=f"Question {current + 1} of {total}"
    )

    if len(st.session_state.questions) <= current:

        with st.spinner(
            "🤖 AI interviewer is preparing your question..."
        ):

            question = generate_question()

        if not question:
            return

        st.session_state.questions.append(
            question
        )

    question = st.session_state.questions[current]

    st.markdown(
        f"""
        <div class="interview-card">

            <div class="ai-badge">
                🤖 AI INTERVIEWER
            </div>

            <div style="
                margin-top:15px;
                font-size:14px;
                color:#667085;
                font-weight:600;
            ">
                QUESTION {current + 1}
            </div>

            <div class="question">
                {question}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 📝 Your Answer")

    answer = st.text_area(
        "Answer",
        height=220,
        placeholder=(
            "Write your answer as if you are speaking "
            "to a real interviewer..."
        ),
        label_visibility="collapsed",
        key=f"answer_{current}"
    )

    col1, col2 = st.columns(2)

    with col1:

        submit = st.button(
            "✅ Submit Answer",
            use_container_width=True
        )

    with col2:

        skip = st.button(
            "⏭️ Skip Question",
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

    st.title("🎯 Interview Complete!")

    if not st.session_state.evaluations:

        st.info(
            "Complete an interview to see your results."
        )

        if st.button(
            "🚀 Start Interview",
            use_container_width=True
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        return

    report = generate_final_report()

    score = report["overall_score"]

    if score >= 90:
        level = "Excellent 🏆"
        message = "Outstanding interview performance!"

    elif score >= 80:
        level = "Very Good 🌟"
        message = "Great job! Keep polishing your skills."

    elif score >= 70:
        level = "Good 👍"
        message = "Good foundation. Keep practicing."

    else:
        level = "Needs Improvement 📈"
        message = "Keep practicing and focus on your weak areas."

    st.markdown(
        f"""
        <div class="hero" style="text-align:center;">

            <div style="
                font-size:64px;
                font-weight:900;
                color:white;
            ">
                {score}/100
            </div>

            <div style="
                font-size:25px;
                font-weight:800;
                color:white;
            ">
                {level}
            </div>

            <div style="
                color:#e0e7ff;
                margin-top:10px;
            ">
                {message}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("📊 Performance Breakdown")

    cols = st.columns(5)

    metrics = [
        (
            "Technical",
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

    for col, (label, value) in zip(
        cols,
        metrics
    ):

        with col:

            st.metric(
                label,
                f"{value}/10"
            )

    strengths = []
    improvements = []
    concepts = []

    for evaluation in st.session_state.evaluations:

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

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("💪 Strengths")

        unique = list(
            dict.fromkeys(strengths)
        )

        if unique:

            for item in unique[:8]:
                st.success(item)

        else:
            st.info(
                "Keep practicing to identify your strengths."
            )

    with col2:

        st.subheader("📈 Improvement Areas")

        unique = list(
            dict.fromkeys(improvements)
        )

        if unique:

            for item in unique[:8]:
                st.warning(item)

        else:

            st.info(
                "No major improvement areas found."
            )

    if concepts:

        st.subheader("📚 Concepts to Review")

        for concept in list(
            dict.fromkeys(concepts)
        )[:12]:

            st.markdown(
                f"• {concept}"
            )

    st.subheader(
        "📝 Question-by-Question Review"
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
            f"Question {i + 1} — "
            f"{evaluation.get('score', 0)}/10"
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
                    "**✨ Better Answer:**"
                )

                st.write(better)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🔄 Start New Interview",
            use_container_width=True
        ):

            reset_interview()

            st.session_state.page = "Interview Setup"

            st.rerun()

    with col2:

        if st.button(
            "🏠 Back Home",
            use_container_width=True
        ):

            st.session_state.page = "Home"
            st.rerun()


# ============================================================
# HISTORY
# ============================================================

def show_history():

    st.title("📚 Interview History")

    if not st.session_state.history:

        st.info(
            "No completed interviews yet."
        )

        if st.button(
            "🚀 Start Your First Interview",
            use_container_width=True
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        return

    for i, interview in enumerate(
        reversed(
            st.session_state.history
        ),
        1
    ):

        with st.expander(
            f"Interview {i} • "
            f"{interview.get('role')} • "
            f"{interview.get('score')}/100"
        ):

            st.write(
                "**Role:**",
                interview.get("role")
            )

            st.write(
                "**Type:**",
                interview.get("type")
            )

            st.write(
                "**Difficulty:**",
                interview.get("difficulty")
            )

            st.progress(
                interview.get(
                    "score",
                    0
                ) / 100
            )


# ============================================================
# ABOUT
# ============================================================

def show_about():

    st.title("ℹ️ About")

    st.markdown(
        """
        ### 🤖 AI Interview Simulator

        AI Interview Simulator is a portfolio-ready
        AI application designed to help students and
        job seekers practice interviews.

        ### 🛠️ Technology

        - Python
        - Streamlit
        - Groq API
        - PyPDF2
        - GitHub
        - Streamlit Cloud

        ### ✨ Features

        - AI-generated interview questions
        - Technical interviews
        - HR interviews
        - Behavioral interviews
        - Multiple difficulty levels
        - AI answer evaluation
        - Performance scoring
        - Resume-based interview questions
        - Strength analysis
        - Improvement suggestions
        - Interview history

        ### 🚀 Future Features

        - Voice interview
        - Video interview
        - Downloadable reports
        - Performance charts
        - More AI models
        - Multi-language support
        """
    )


# ============================================================
# PAGE ROUTER
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

        🤖 AI Interview Simulator
        <br>
        Built with Python • Streamlit • Groq AI
        <br>
        Practice. Improve. Get Interview-Ready. 🚀

    </div>
    """,
    unsafe_allow_html=True
)
