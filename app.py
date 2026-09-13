import streamlit as st
import os
import json
import re
import html
from typing import Dict, Any, List

# Optional PDF support
try:
    from PyPDF2 import PdfReader
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

# Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CONFIG
# =========================================================

MODEL_NAME = "openai/gpt-oss-20b"


# =========================================================
# CUSTOM CSS
# =========================================================

st.html("""
<style>

    /* ---------- MAIN APP ---------- */

    .stApp {
        background: #f6f8fc;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1250px;
    }

    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #263044;
    }

    section[data-testid="stSidebar"] * {
        color: #f9fafb !important;
    }

    .sidebar-logo {
        text-align: center;
        padding: 10px 5px 25px 5px;
    }

    .sidebar-logo-icon {
        font-size: 42px;
    }

    .sidebar-logo-title {
        font-size: 20px;
        font-weight: 800;
        margin-top: 5px;
    }

    .sidebar-logo-subtitle {
        font-size: 12px;
        color: #9ca3af !important;
        margin-top: 4px;
    }

    .sidebar-section {
        color: #9ca3af !important;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 20px 0 10px 0;
    }

    /* ---------- HERO ---------- */

    .hero {
        background: linear-gradient(
            135deg,
            #111827 0%,
            #1e1b4b 50%,
            #312e81 100%
        );
        border-radius: 24px;
        padding: 35px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 15px 40px rgba(49, 46, 129, 0.18);
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.18);
        padding: 7px 14px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 14px;
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        margin: 0;
        line-height: 1.15;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #c7d2fe !important;
        margin-top: 12px;
    }

    .hero-description {
        font-size: 14px;
        color: #d1d5db !important;
        max-width: 760px;
        line-height: 1.7;
        margin-top: 12px;
    }

    /* ---------- CARDS ---------- */

    .card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 18px;
        box-shadow: 0 5px 20px rgba(15,23,42,0.05);
    }

    .card-title {
        color: #111827 !important;
        font-size: 20px;
        font-weight: 800;
        margin-bottom: 6px;
    }

    .card-subtitle {
        color: #6b7280 !important;
        font-size: 13px;
        margin-bottom: 20px;
    }

    /* ---------- STAT CARDS ---------- */

    .stat-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 22px;
        min-height: 125px;
        box-shadow: 0 5px 20px rgba(15,23,42,0.05);
    }

    .stat-icon {
        font-size: 25px;
        margin-bottom: 8px;
    }

    .stat-value {
        font-size: 28px;
        font-weight: 800;
        color: #111827 !important;
    }

    .stat-label {
        font-size: 13px;
        color: #6b7280 !important;
        margin-top: 3px;
    }

    /* ---------- INTERVIEW ---------- */

    .interview-header {
        margin-bottom: 18px;
    }

    .interview-title {
        color: #111827 !important;
        font-size: 32px;
        font-weight: 800;
        margin: 0;
    }

    .interview-subtitle {
        color: #6b7280 !important;
        margin-top: 5px;
    }

    .question-panel {
        background: #191c24;
        border-radius: 18px;
        padding: 28px;
        margin-top: 20px;
        color: white !important;
        box-shadow: 0 12px 30px rgba(15,23,42,0.15);
    }

    .ai-badge {
        display: inline-block;
        background: #312e81;
        color: #c7d2fe !important;
        padding: 7px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.5px;
        margin-bottom: 15px;
    }

    .question-number {
        color: #a5b4fc !important;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .question-text {
        color: white !important;
        font-size: 21px;
        font-weight: 650;
        line-height: 1.6;
    }

    /* ---------- RESULT ---------- */

    .score-card {
        background: linear-gradient(
            135deg,
            #111827,
            #312e81
        );
        border-radius: 22px;
        padding: 35px;
        color: white !important;
        text-align: center;
        margin-bottom: 25px;
    }

    .score-number {
        font-size: 62px;
        font-weight: 900;
        line-height: 1;
    }

    .score-label {
        color: #c7d2fe !important;
        font-size: 14px;
        margin-top: 8px;
    }

    .result-badge {
        display: inline-block;
        margin-top: 15px;
        padding: 8px 18px;
        background: rgba(255,255,255,0.12);
        border-radius: 30px;
        font-weight: 700;
    }

    .result-section {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 18px;
    }

    .result-heading {
        color: #111827 !important;
        font-size: 18px;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .list-item {
        color: #374151 !important;
        font-size: 14px;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;
    }

    /* ---------- INFO ---------- */

    .info-box {
        background: #eef2ff;
        border: 1px solid #c7d2fe;
        border-radius: 15px;
        padding: 16px;
        color: #312e81 !important;
        font-size: 13px;
        line-height: 1.6;
        margin-bottom: 18px;
    }

    .success-box {
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 15px;
        padding: 16px;
        color: #065f46 !important;
        font-size: 13px;
        margin-bottom: 18px;
    }

    .warning-box {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-radius: 15px;
        padding: 16px;
        color: #92400e !important;
        font-size: 13px;
        margin-bottom: 18px;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #9ca3af !important;
        font-size: 12px;
        padding: 30px 0 10px 0;
    }

</style>
""")


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "page": "Dashboard",
    "interview_started": False,
    "questions": [],
    "current_question": 0,
    "answers": [],
    "evaluations": [],
    "final_report": None,
    "history": [],
    "job_role": "Software Engineer",
    "interview_type": "Technical",
    "difficulty": "Intermediate",
    "num_questions": 5,
    "experience": "Fresher",
    "resume_text": "",
    "resume_name": "",
    "resume_mode": False,
    "last_error": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# GROQ CLIENT
# =========================================================

def get_api_key():
    """Get Groq API key from Streamlit Secrets or environment."""

    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    return os.environ.get("GROQ_API_KEY", "")


def get_client():
    if not GROQ_AVAILABLE:
        return None

    api_key = get_api_key()

    if not api_key:
        return None

    try:
        return Groq(api_key=api_key)
    except Exception:
        return None


# =========================================================
# AI HELPER
# =========================================================

def call_groq(prompt: str, temperature: float = 0.5) -> str:

    client = get_client()

    if client is None:
        return ""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional AI interview assistant. "
                        "Give accurate, concise, practical responses."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=temperature,
            max_tokens=1200
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        st.session_state.last_error = str(e)
        return ""


# =========================================================
# QUESTION GENERATION
# =========================================================

def generate_question(
    role: str,
    interview_type: str,
    difficulty: str,
    experience: str,
    previous_questions: List[str] = None
) -> str:

    previous_questions = previous_questions or []

    previous_text = "\n".join(
        f"- {q}" for q in previous_questions[-5:]
    )

    prompt = f"""
Create ONE interview question.

Job Role: {role}
Interview Type: {interview_type}
Difficulty: {difficulty}
Experience Level: {experience}

Previous questions:
{previous_text}

Requirements:
- Ask only ONE question.
- Make it relevant to the selected role.
- Do not repeat previous questions.
- Make it suitable for a real interview.
- Return ONLY the question.
- Do NOT add labels such as "Question:".
- Do NOT add explanations.
- Do NOT use Markdown.
- Do NOT use code fences.
- Do NOT return Python, SQL, JavaScript, HTML, CSS, or any code snippet.
- Plain text only.
"""

    result = call_groq(prompt, temperature=0.7)

    if result:
        result = re.sub(r"```[a-zA-Z0-9_+-]*", "", result)
        result = result.replace("```", "")
        result = result.replace("Question:", "").strip()

        return result

    # Fallback questions
    fallback = {
        "Software Engineer":
            "What is the difference between a process and a thread?",
        "Python Developer":
            "What are the main advantages of using Python for software development?",
        "AI Engineer":
            "What is the difference between machine learning and deep learning?",
        "Machine Learning Engineer":
            "What is overfitting, and how can you reduce it?",
        "Data Scientist":
            "How would you handle missing values in a dataset?",
        "Data Analyst":
            "What is the difference between correlation and causation?",
        "Web Developer":
            "What is the difference between frontend and backend development?",
        "Frontend Developer":
            "What is the purpose of responsive web design?",
        "Backend Developer":
            "What is an API and why is it useful?",
        "Cybersecurity Analyst":
            "What is phishing and how can organizations reduce the risk?",
        "Computer Science Student":
            "What programming language are you most comfortable with and why?"
    }

    return fallback.get(
        role,
        "Tell me about yourself and your technical background."
    )


# =========================================================
# ANSWER EVALUATION
# =========================================================

def evaluate_answer(question: str, answer: str) -> Dict[str, Any]:

    prompt = f"""
Evaluate this interview answer.

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

Return ONLY valid JSON.

Use exactly this structure:

{{
  "score": 8,
  "correctness": 8,
  "relevance": 9,
  "technical_knowledge": 7,
  "communication": 8,
  "confidence": 8,
  "completeness": 7,
  "strengths": [
    "strength 1",
    "strength 2"
  ],
  "improvements": [
    "improvement 1",
    "improvement 2"
  ],
  "better_answer": "A concise improved answer",
  "concepts_to_review": [
    "concept 1",
    "concept 2"
  ]
}}

Scoring:
0 = very poor
10 = excellent

Do not use Markdown.
Do not put JSON inside a code block.
"""

    result = call_groq(prompt, temperature=0.2)

    if result:

        try:
            result = re.sub(r"```json", "", result, flags=re.IGNORECASE)
            result = result.replace("```", "").strip()

            match = re.search(r"\{.*\}", result, re.DOTALL)

            if match:
                data = json.loads(match.group())

                return {
                    "score": int(data.get("score", 5)),
                    "correctness": int(data.get("correctness", 5)),
                    "relevance": int(data.get("relevance", 5)),
                    "technical_knowledge": int(
                        data.get("technical_knowledge", 5)
                    ),
                    "communication": int(
                        data.get("communication", 5)
                    ),
                    "confidence": int(
                        data.get("confidence", 5)
                    ),
                    "completeness": int(
                        data.get("completeness", 5)
                    ),
                    "strengths": data.get("strengths", []),
                    "improvements": data.get("improvements", []),
                    "better_answer": data.get(
                        "better_answer",
                        "Try to provide a more structured and specific answer."
                    ),
                    "concepts_to_review": data.get(
                        "concepts_to_review",
                        []
                    )
                }

        except Exception:
            pass

    # Fallback evaluation
    length_score = min(10, max(3, len(answer.split()) // 8))

    return {
        "score": length_score,
        "correctness": length_score,
        "relevance": min(10, length_score + 1),
        "technical_knowledge": length_score,
        "communication": length_score,
        "confidence": length_score,
        "completeness": length_score,
        "strengths": [
            "You attempted the question.",
            "Your answer communicates your basic understanding."
        ],
        "improvements": [
            "Add more specific examples.",
            "Structure your answer more clearly."
        ],
        "better_answer":
            "Give a clear explanation, include a practical example, "
            "and explain why your approach works.",
        "concepts_to_review": [
            "Core concepts related to this question"
        ]
    }


# =========================================================
# FINAL REPORT
# =========================================================

def generate_final_report(
    evaluations: List[Dict[str, Any]],
    role: str
) -> Dict[str, Any]:

    if not evaluations:
        return {}

    average = sum(
        float(e.get("score", 0))
        for e in evaluations
    ) / len(evaluations)

    overall = round(average * 10)

    if overall >= 90:
        level = "Excellent"
    elif overall >= 80:
        level = "Very Good"
    elif overall >= 70:
        level = "Good"
    elif overall >= 50:
        level = "Needs Improvement"
    else:
        level = "Beginner"

    all_strengths = []
    all_improvements = []
    all_concepts = []

    for evaluation in evaluations:
        all_strengths.extend(
            evaluation.get("strengths", [])
        )
        all_improvements.extend(
            evaluation.get("improvements", [])
        )
        all_concepts.extend(
            evaluation.get("concepts_to_review", [])
        )

    prompt = f"""
Create a short final interview report.

Role: {role}
Overall score: {overall}/100
Performance level: {level}

Evaluation data:
{json.dumps(evaluations, indent=2)}

Return ONLY valid JSON:

{{
  "summary": "short interview summary",
  "recommendations": [
    "recommendation 1",
    "recommendation 2",
    "recommendation 3"
  ]
}}
"""

    ai_result = call_groq(prompt, temperature=0.3)

    summary = (
        f"You completed the interview for the {role} role "
        f"with an overall score of {overall}/100."
    )

    recommendations = [
        "Practice explaining technical concepts clearly.",
        "Use specific examples when answering interview questions.",
        "Review the concepts identified in your weak areas."
    ]

    if ai_result:
        try:
            ai_result = re.sub(
                r"```json",
                "",
                ai_result,
                flags=re.IGNORECASE
            )
            ai_result = ai_result.replace("```", "").strip()

            match = re.search(
                r"\{.*\}",
                ai_result,
                re.DOTALL
            )

            if match:
                parsed = json.loads(match.group())

                summary = parsed.get(
                    "summary",
                    summary
                )

                recommendations = parsed.get(
                    "recommendations",
                    recommendations
                )

        except Exception:
            pass

    return {
        "overall_score": overall,
        "performance_level": level,
        "summary": summary,
        "recommendations": recommendations,
        "strengths": list(dict.fromkeys(all_strengths))[:6],
        "improvements": list(dict.fromkeys(all_improvements))[:6],
        "concepts_to_review": list(dict.fromkeys(all_concepts))[:6]
    }


# =========================================================
# RESUME EXTRACTION
# =========================================================

def extract_resume_text(uploaded_file):

    if not PDF_AVAILABLE:
        return ""

    try:
        reader = PdfReader(uploaded_file)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

        return text.strip()

    except Exception as e:
        st.session_state.last_error = str(e)
        return ""


# =========================================================
# RESET
# =========================================================

def reset_interview():

    st.session_state.interview_started = False
    st.session_state.questions = []
    st.session_state.current_question = 0
    st.session_state.answers = []
    st.session_state.evaluations = []
    st.session_state.final_report = None
    st.session_state.last_error = ""


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.html("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🎤</div>
        <div class="sidebar-logo-title">
            AI Interview Simulator
        </div>
        <div class="sidebar-logo-subtitle">
            Practice • Improve • Succeed
        </div>
    </div>
    """)

    st.html("""
    <div class="sidebar-section">
        Navigation
    </div>
    """)

    if st.button(
        "🏠  Dashboard",
        use_container_width=True
    ):
        st.session_state.page = "Dashboard"
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
        st.session_state.page = "Mock Interview"
        st.rerun()

    if st.button(
        "📊  Results",
        use_container_width=True
    ):
        st.session_state.page = "Results"
        st.rerun()

    if st.button(
        "📚  Interview History",
        use_container_width=True
    ):
        st.session_state.page = "Interview History"
        st.rerun()

    st.html("""
    <div class="sidebar-section">
        Current Session
    </div>
    """)

    st.write(
        f"**Role:** {st.session_state.job_role}"
    )

    st.write(
        f"**Difficulty:** {st.session_state.difficulty}"
    )

    st.write(
        f"**Questions:** {st.session_state.num_questions}"
    )

    if st.button(
        "🔄 Reset Interview",
        use_container_width=True
    ):
        reset_interview()
        st.session_state.page = "Dashboard"
        st.rerun()


# =========================================================
# DASHBOARD
# =========================================================

def show_dashboard():

    st.html("""
    <div class="hero">

        <div class="hero-badge">
            🤖 AI-POWERED INTERVIEW PRACTICE
        </div>

        <div class="hero-title">
            AI Interview Simulator
        </div>

        <div class="hero-subtitle">
            Practice. Improve. Get Interview-Ready.
        </div>

        <div class="hero-description">
            Practice realistic interviews with an AI interviewer,
            receive instant feedback, discover your weak areas,
            and improve your confidence before the real interview.
        </div>

    </div>
    """)

    completed = len(st.session_state.history)

    if st.session_state.evaluations:
        avg_score = round(
            sum(
                e.get("score", 0)
                for e in st.session_state.evaluations
            ) / len(st.session_state.evaluations),
            1
        )
    else:
        avg_score = 0

    improvement_areas = 0

    for evaluation in st.session_state.evaluations:
        improvement_areas += len(
            evaluation.get("improvements", [])
        )

    cols = st.columns(4)

    stats = [
        ("❓", st.session_state.num_questions, "Interview Questions"),
        ("⭐", f"{avg_score}/10", "Average Score"),
        ("🎯", completed, "Interviews Completed"),
        ("📈", improvement_areas, "Improvement Areas")
    ]

    for col, stat in zip(cols, stats):

        icon, value, label = stat

        with col:
            st.html(
                f"""
                <div class="stat-card">

                    <div class="stat-icon">
                        {icon}
                    </div>

                    <div class="stat-value">
                        {html.escape(str(value))}
                    </div>

                    <div class="stat-label">
                        {html.escape(label)}
                    </div>

                </div>
                """
            )

    st.write("")

    col1, col2 = st.columns([1.5, 1])

    with col1:

        st.html("""
        <div class="card">

            <div class="card-title">
                🚀 Start Your Interview
            </div>

            <div class="card-subtitle">
                Configure your interview and start practicing
                with your AI interviewer.
            </div>

        </div>
        """)

        if st.button(
            "⚙️ Configure Interview",
            type="primary",
            use_container_width=True
        ):
            st.session_state.page = "Interview Setup"
            st.rerun()

    with col2:

        st.html("""
        <div class="info-box">

            <strong>💡 Pro Tip</strong><br><br>

            Keep your answers structured:
            <br>
            <b>Situation → Action → Result</b>

            <br><br>

            For technical questions, explain your
            reasoning instead of only giving the final answer.

        </div>
        """)


# =========================================================
# INTERVIEW SETUP
# =========================================================

def show_interview_setup():

    st.title("⚙️ Interview Setup")

    st.caption(
        "Customize your AI-powered mock interview."
    )

    st.html("""
    <div class="info-box">

        🎯 <b>Choose your role, interview type,
        difficulty and experience level.</b>

        The AI will generate questions based on
        your selections.

    </div>
    """)

    col1, col2 = st.columns(2)

    with col1:

        roles = [
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
            "Custom Role"
        ]

        role = st.selectbox(
            "💼 Job Role",
            roles,
            index=roles.index(
                st.session_state.job_role
            ) if st.session_state.job_role in roles else 0
        )

        if role == "Custom Role":

            role = st.text_input(
                "Enter your custom role",
                placeholder="e.g. Generative AI Engineer"
            )

        interview_types = [
            "Technical",
            "HR",
            "Behavioral",
            "Mixed"
        ]

        interview_type = st.selectbox(
            "🎯 Interview Type",
            interview_types,
            index=interview_types.index(
                st.session_state.interview_type
            )
        )

        experience_levels = [
            "Fresher",
            "0–1 Years",
            "1–3 Years",
            "3+ Years"
        ]

        experience = st.selectbox(
            "👤 Experience Level",
            experience_levels,
            index=experience_levels.index(
                st.session_state.experience
            )
        )

    with col2:

        difficulties = [
            "Beginner",
            "Intermediate",
            "Advanced",
            "Expert"
        ]

        difficulty = st.selectbox(
            "🔥 Difficulty",
            difficulties,
            index=difficulties.index(
                st.session_state.difficulty
            )
        )

        num_questions = st.selectbox(
            "❓ Number of Questions",
            [5, 10, 15],
            index=[5, 10, 15].index(
                st.session_state.num_questions
            )
        )

        st.write("")

        st.html("""
        <div class="card">

            <div class="card-title">
                📄 Resume-Based Interview
            </div>

            <div class="card-subtitle">
                Upload your resume and let the AI
                generate personalized questions.
            </div>

        </div>
        """)

        uploaded_resume = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"]
        )

        if uploaded_resume:

            if not PDF_AVAILABLE:

                st.warning(
                    "PyPDF2 is not installed."
                )

            else:

                resume_text = extract_resume_text(
                    uploaded_resume
                )

                if resume_text:

                    st.session_state.resume_text = resume_text
                    st.session_state.resume_name = (
                        uploaded_resume.name
                    )
                    st.session_state.resume_mode = True

                    st.success(
                        "Resume uploaded successfully!"
                    )

    st.write("")

    if st.button(
        "🚀 START INTERVIEW",
        type="primary",
        use_container_width=True
    ):

        if not role or not role.strip():

            st.error(
                "Please enter a job role."
            )

        else:

            st.session_state.job_role = role
            st.session_state.interview_type = interview_type
            st.session_state.difficulty = difficulty
            st.session_state.num_questions = num_questions
            st.session_state.experience = experience

            reset_interview()

            st.session_state.job_role = role
            st.session_state.interview_type = interview_type
            st.session_state.difficulty = difficulty
            st.session_state.num_questions = num_questions
            st.session_state.experience = experience

            with st.spinner(
                "🤖 AI is preparing your first question..."
            ):

                first_question = generate_question(
                    role,
                    interview_type,
                    difficulty,
                    experience
                )

            st.session_state.questions = [
                first_question
            ]

            st.session_state.interview_started = True
            st.session_state.current_question = 0
            st.session_state.page = "Mock Interview"

            st.rerun()


# =========================================================
# MOCK INTERVIEW
# =========================================================

def show_mock_interview():

    if not st.session_state.interview_started:

        st.html("""
        <div class="warning-box">

            ⚠️ <b>No active interview.</b><br><br>

            Please configure your interview first.

        </div>
        """)

        if st.button(
            "⚙️ Go to Interview Setup",
            type="primary"
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        return

    current = st.session_state.current_question
    total = st.session_state.num_questions

    questions = st.session_state.questions

    if current >= len(questions):

        st.session_state.page = "Results"
        st.rerun()

        return

    question = questions[current]

    st.html(
        f"""
        <div class="interview-header">

            <div class="interview-title">
                🎤 Mock Interview
            </div>

            <div class="interview-subtitle">
                {html.escape(st.session_state.job_role)}
                •
                {html.escape(st.session_state.interview_type)}
                •
                {html.escape(st.session_state.difficulty)}
            </div>

        </div>
        """
    )

    progress_value = (
        current / total
        if total > 0
        else 0
    )

    st.progress(
        progress_value,
        text=f"Question {current + 1} of {total}"
    )

    # IMPORTANT:
    # st.html() prevents raw HTML code from appearing.
    safe_question = html.escape(question)

    st.html(
        f"""
        <div class="question-panel">

            <div class="ai-badge">
                🤖 AI INTERVIEWER
            </div>

            <div class="question-number">
                QUESTION {current + 1}
            </div>

            <div class="question-text">
                {safe_question}
            </div>

        </div>
        """
    )

    st.write("")

    answer = st.text_area(
        "📝 Your Answer",
        placeholder=(
            "Type your answer here...\n\n"
            "Try to explain your reasoning clearly "
            "and give practical examples."
        ),
        height=220,
        key=f"answer_{current}"
    )

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:

        submit = st.button(
            "✅ Submit Answer",
            type="primary",
            use_container_width=True
        )

    with col2:

        skip = st.button(
            "⏭️ Skip",
            use_container_width=True
        )

    if submit:

        if not answer.strip():

            st.warning(
                "Please write an answer before submitting."
            )

        else:

            with st.spinner(
                "🤖 AI is evaluating your answer..."
            ):

                evaluation = evaluate_answer(
                    question,
                    answer
                )

            st.session_state.answers.append(answer)
            st.session_state.evaluations.append(
                evaluation
            )

            if current + 1 >= total:

                with st.spinner(
                    "📊 Generating your final report..."
                ):

                    report = generate_final_report(
                        st.session_state.evaluations,
                        st.session_state.job_role
                    )

                st.session_state.final_report = report

                st.session_state.history.append({
                    "role": st.session_state.job_role,
                    "type": st.session_state.interview_type,
                    "difficulty": st.session_state.difficulty,
                    "score": report.get(
                        "overall_score",
                        0
                    ),
                    "level": report.get(
                        "performance_level",
                        "Unknown"
                    ),
                    "questions": total
                })

                st.session_state.interview_started = False
                st.session_state.page = "Results"

                st.rerun()

            else:

                next_question = generate_question(
                    st.session_state.job_role,
                    st.session_state.interview_type,
                    st.session_state.difficulty,
                    st.session_state.experience,
                    st.session_state.questions
                )

                st.session_state.questions.append(
                    next_question
                )

                st.session_state.current_question += 1

                st.rerun()

    if skip:

        st.session_state.answers.append(
            "[Skipped]"
        )

        st.session_state.evaluations.append({
            "score": 0,
            "correctness": 0,
            "relevance": 0,
            "technical_knowledge": 0,
            "communication": 0,
            "confidence": 0,
            "completeness": 0,
            "strengths": [],
            "improvements": [
                "This question was skipped."
            ],
            "better_answer": "",
            "concepts_to_review": []
        })

        if current + 1 >= total:

            report = generate_final_report(
                st.session_state.evaluations,
                st.session_state.job_role
            )

            st.session_state.final_report = report

            st.session_state.history.append({
                "role": st.session_state.job_role,
                "type": st.session_state.interview_type,
                "difficulty": st.session_state.difficulty,
                "score": report.get(
                    "overall_score",
                    0
                ),
                "level": report.get(
                    "performance_level",
                    "Unknown"
                ),
                "questions": total
            })

            st.session_state.interview_started = False
            st.session_state.page = "Results"

            st.rerun()

        else:

            next_question = generate_question(
                st.session_state.job_role,
                st.session_state.interview_type,
                st.session_state.difficulty,
                st.session_state.experience,
                st.session_state.questions
            )

            st.session_state.questions.append(
                next_question
            )

            st.session_state.current_question += 1

            st.rerun()


# =========================================================
# RESULTS
# =========================================================

def show_results():

    report = st.session_state.final_report

    if not report:

        st.html("""
        <div class="warning-box">

            📊 No interview results are available yet.

        </div>
        """)

        if st.button(
            "🚀 Start an Interview",
            type="primary"
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        return

    score = report.get(
        "overall_score",
        0
    )

    level = report.get(
        "performance_level",
        "Good"
    )

    st.html("""
    <div style="margin-bottom:20px;">
        <h1 style="color:#111827;">
            🎯 Interview Complete!
        </h1>

        <p style="color:#6b7280;">
            Here is your AI-powered performance report.
        </p>
    </div>
    """)

    st.html(
        f"""
        <div class="score-card">

            <div style="font-size:15px;">
                OVERALL SCORE
            </div>

            <div class="score-number">
                {score}/100
            </div>

            <div class="score-label">
                Your interview performance
            </div>

            <div class="result-badge">
                {html.escape(level)}
            </div>

        </div>
        """
    )

    evaluations = st.session_state.evaluations

    if evaluations:

        metrics = {
            "Technical Knowledge": round(
                sum(
                    e.get(
                        "technical_knowledge",
                        0
                    )
                    for e in evaluations
                ) / len(evaluations) * 10
            ),
            "Communication": round(
                sum(
                    e.get(
                        "communication",
                        0
                    )
                    for e in evaluations
                ) / len(evaluations) * 10
            ),
            "Relevance": round(
                sum(
                    e.get(
                        "relevance",
                        0
                    )
                    for e in evaluations
                ) / len(evaluations) * 10
            ),
            "Confidence": round(
                sum(
                    e.get(
                        "confidence",
                        0
                    )
                    for e in evaluations
                ) / len(evaluations) * 10
            )
        }

        st.subheader(
            "📈 Performance Breakdown"
        )

        cols = st.columns(4)

        for col, (label, value) in zip(
            cols,
            metrics.items()
        ):

            with col:

                st.metric(
                    label,
                    f"{value}/100"
                )

                st.progress(
                    min(value / 100, 1.0)
                )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        strengths = report.get(
            "strengths",
            []
        )

        st.html("""
        <div class="result-section">

            <div class="result-heading">
                💪 Strengths
            </div>

        </div>
        """)

        if strengths:

            for item in strengths:

                st.markdown(
                    f"✓ {item}"
                )

        else:

            st.write(
                "No strengths recorded."
            )

    with col2:

        improvements = report.get(
            "improvements",
            []
        )

        st.html("""
        <div class="result-section">

            <div class="result-heading">
                📈 Improvement Areas
            </div>

        </div>
        """)

        if improvements:

            for item in improvements:

                st.markdown(
                    f"• {item}"
                )

        else:

            st.write(
                "No improvement areas recorded."
            )

    st.html("""
    <div class="result-section">

        <div class="result-heading">
            🤖 AI Recommendations
        </div>

    </div>
    """)

    recommendations = report.get(
        "recommendations",
        []
    )

    for recommendation in recommendations:

        st.markdown(
            f"💡 {recommendation}"
        )

    st.html("""
    <div class="result-section">

        <div class="result-heading">
            📚 Concepts to Review
        </div>

    </div>
    """)

    concepts = report.get(
        "concepts_to_review",
        []
    )

    if concepts:

        for concept in concepts:

            st.markdown(
                f"📌 {concept}"
            )

    else:

        st.write(
            "No specific concepts were identified."
        )

    st.html(
        f"""
        <div class="success-box">

            <b>📝 Interview Summary</b><br><br>

            {html.escape(
                str(
                    report.get(
                        "summary",
                        ""
                    )
                )
            )}

        </div>
        """
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🔄 Start New Interview",
            type="primary",
            use_container_width=True
        ):

            reset_interview()
            st.session_state.page = "Interview Setup"
            st.rerun()

    with col2:

        if st.button(
            "🏠 Back to Dashboard",
            use_container_width=True
        ):

            st.session_state.page = "Dashboard"
            st.rerun()


# =========================================================
# HISTORY
# =========================================================

def show_history():

    st.title("📚 Interview History")

    history = st.session_state.history

    if not history:

        st.html("""
        <div class="info-box">

            📚 No interviews completed in this session yet.

            <br><br>

            Complete your first mock interview
            and your results will appear here.

        </div>
        """)

        return

    for index, interview in enumerate(
        reversed(history),
        start=1
    ):

        st.html(
            f"""
            <div class="card">

                <div class="card-title">
                    🎤 Interview #{index}
                </div>

                <div style="
                    color:#6b7280;
                    font-size:14px;
                    line-height:2;
                ">

                    <b>Role:</b>
                    {html.escape(
                        str(
                            interview.get(
                                "role",
                                "Unknown"
                            )
                        )
                    )}
                    <br>

                    <b>Type:</b>
                    {html.escape(
                        str(
                            interview.get(
                                "type",
                                "Unknown"
                            )
                        )
                    )}
                    <br>

                    <b>Difficulty:</b>
                    {html.escape(
                        str(
                            interview.get(
                                "difficulty",
                                "Unknown"
                            )
                        )
                    )}
                    <br>

                    <b>Questions:</b>
                    {interview.get("questions", 0)}
                    <br>

                    <b>Score:</b>
                    {interview.get("score", 0)}/100
                    <br>

                    <b>Performance:</b>
                    {html.escape(
                        str(
                            interview.get(
                                "level",
                                "Unknown"
                            )
                        )
                    )}

                </div>

            </div>
            """
        )


# =========================================================
# PAGE ROUTER
# =========================================================

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


# =========================================================
# FOOTER
# =========================================================

st.html("""
<div class="footer">

    🤖 AI Interview Simulator
    • Built with Python + Streamlit + Groq

</div>
""")
st.html("""
<style>

/* =========================================
   FIX: SELECTBOX / INPUT TEXT VISIBILITY
   ========================================= */

/* Labels */
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stFileUploader"] label {
    color: #111827 !important;
    font-weight: 700 !important;
    font-size: 14px !important;
}

/* Selected value inside selectbox */
div[data-baseweb="select"] {
    background-color: #ffffff !important;
    border-radius: 10px !important;
}

div[data-baseweb="select"] * {
    color: #111827 !important;
}

/* Selectbox selected text */
div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
div[data-baseweb="select"] input {
    color: #111827 !important;
}

/* Text input */
div[data-baseweb="input"] {
    background-color: #ffffff !important;
}

div[data-baseweb="input"] input {
    color: #111827 !important;
    background-color: #ffffff !important;
}

/* Placeholder */
input::placeholder,
textarea::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

/* Textarea */
textarea {
    color: #111827 !important;
    background-color: #ffffff !important;
}

/* Dropdown menu */
ul[role="listbox"] {
    background-color: #ffffff !important;
}

ul[role="listbox"] li {
    color: #111827 !important;
    background-color: #ffffff !important;
}

ul[role="listbox"] li:hover {
    background-color: #eef2ff !important;
    color: #111827 !important;
}

/* Radio buttons */
div[data-testid="stRadio"] label {
    color: #111827 !important;
}

/* File uploader text */
section[data-testid="stFileUploaderDropzone"] * {
    color: #111827 !important;
}

</style>
""")
