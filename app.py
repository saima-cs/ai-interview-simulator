
import json
import os

import streamlit as st
from groq import Groq


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Interview Simulator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #f8fafc;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

section[data-testid="stSidebar"] {
    background: #111827;
}

section[data-testid="stSidebar"] * {
    color: white;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1400px;
}

.hero {
    background: linear-gradient(
        135deg,
        #111827 0%,
        #1e3a8a 50%,
        #312e81 100%
    );
    padding: 40px;
    border-radius: 24px;
    margin-bottom: 30px;
    color: white;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    margin-bottom: 10px;
}

.hero-subtitle {
    font-size: 20px;
    opacity: 0.9;
    margin-bottom: 12px;
}

.hero-description {
    font-size: 16px;
    opacity: 0.8;
    max-width: 750px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 5px 20px rgba(15, 23, 42, 0.06);
    margin-bottom: 20px;
}

.card-title {
    font-size: 20px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 8px;
}

.card-text {
    color: #6b7280;
    font-size: 15px;
    line-height: 1.6;
}

.feature-card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    min-height: 160px;
    box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
}

.feature-icon {
    font-size: 32px;
    margin-bottom: 10px;
}

.feature-title {
    font-size: 17px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 8px;
}

.feature-description {
    color: #6b7280;
    font-size: 14px;
    line-height: 1.5;
}

.section-title {
    font-size: 28px;
    font-weight: 800;
    color: #111827;
    margin-top: 20px;
    margin-bottom: 18px;
}

.section-subtitle {
    color: #6b7280;
    font-size: 15px;
    margin-bottom: 25px;
}

.ai-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 30px;
    background: #eef2ff;
    color: #4338ca;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 15px;
}

.feedback-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
}

.score-big {
    font-size: 45px;
    font-weight: 800;
    color: #312e81;
}

.custom-footer {
    text-align: center;
    padding: 30px 10px;
    color: #6b7280;
    font-size: 13px;
}

.stButton > button {
    border-radius: 12px;
    border: none;
    padding: 12px 22px;
    font-weight: 700;
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
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# GROQ CLIENT
# ============================================================

def get_groq_client():

    api_key = None

    # Streamlit Cloud / local secrets
    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass

    # Google Colab fallback
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        return None

    return Groq(api_key=api_key)


# ============================================================
# GENERATE INTERVIEW QUESTION
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

    previous_questions = st.session_state.questions

    previous_text = "\n".join(
        previous_questions[-5:]
    )

    prompt = f"""
You are a professional interviewer conducting
a realistic job interview.

Candidate information:

Job Role: {role}
Interview Type: {interview_type}
Difficulty: {difficulty}
Experience: {experience}

Previous questions:
{previous_text if previous_text else "None"}

Generate ONE new interview question.

Requirements:

1. Make it relevant to the selected job role.
2. Match the selected interview type.
3. Match the difficulty level.
4. Match the candidate's experience.
5. Do not repeat previous questions.
6. Make the question realistic.
7. Return ONLY the interview question.
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert interviewer "
                        "who creates realistic interview questions."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=300,
        )

        question = response.choices[0].message.content.strip()

        return question

    except Exception as e:

        st.error(
            f"⚠️ Error generating interview question: {e}"
        )

        return None


# ============================================================
# EVALUATE ANSWER
# ============================================================

def evaluate_answer(question, answer):

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

    prompt = f"""
You are an expert professional interview evaluator.

Evaluate the candidate's answer fairly.

Job Role:
{role}

Interview Type:
{interview_type}

Difficulty:
{difficulty}

Experience:
{experience}

Interview Question:
{question}

Candidate Answer:
{answer}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "score": 0,
    "correctness": 0,
    "relevance": 0,
    "technical_knowledge": 0,
    "communication": 0,
    "confidence": 0,
    "strengths": [],
    "improvements": [],
    "better_answer": "",
    "concepts_to_review": []
}}

Rules:

- Every score must be an integer from 0 to 10.
- score is the overall score.
- Evaluate according to the candidate's experience.
- Give 2 or 3 strengths.
- Give 2 or 3 improvements.
- Give a concise improved answer.
- Give useful concepts to review.
- Do not include markdown.
- Do not include any text outside the JSON.
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
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=1200
        )

        result = response.choices[0].message.content.strip()

        # Remove markdown code fences
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


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:20px 5px 30px;
        ">

            <div style="font-size:45px;">
                🤖
            </div>

            <h2 style="margin:5px 0;">
                AI Interview
            </h2>

            <p style="color:#9ca3af !important;">
                Simulator
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown("### Navigation")

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

    if st.button(
        "ℹ️  About",
        use_container_width=True
    ):

        st.session_state.page = "About"
        st.rerun()

    st.markdown("---")

    st.markdown(
        """
        <div style="text-align:center;padding:15px;">

            <p style="color:#9ca3af !important;font-size:13px;">
                Powered by
            </p>

            <p style="color:white !important;font-weight:700;">
                Groq + Streamlit
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DASHBOARD
# ============================================================

def show_dashboard():

    st.markdown(
        """
        <div class="hero">

            <div class="ai-badge">
                🤖 AI-POWERED INTERVIEW COACH
            </div>

            <div class="hero-title">
                AI Interview Simulator
            </div>

            <div class="hero-subtitle">
                Practice. Improve. Get Interview-Ready.
            </div>

            <div class="hero-description">
                Practice realistic interviews with an AI interviewer
                and receive instant personalized feedback.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">'
        '👋 Welcome to your AI-powered interview coach'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">

            <div class="card-title">
                Your personal AI interview practice platform
            </div>

            <div class="card-text">
                Prepare for technical, HR, behavioral, and mixed
                interviews through realistic AI-powered sessions.
                Choose your target role, difficulty level, and
                experience, then practice answering questions
                like a real interview.
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    completed_questions = len(
        st.session_state.scores
    )

    if completed_questions:

        average_score = (
            sum(st.session_state.scores)
            / completed_questions
        )

    else:

        average_score = 0

    improvement_areas = 0

    if st.session_state.evaluations:

        improvement_areas = len(
            set(
                item
                for evaluation
                in st.session_state.evaluations
                for item
                in evaluation.get(
                    "improvements",
                    []
                )
            )
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Interview Questions",
            completed_questions
        )

    with col2:

        st.metric(
            "Average Score",
            f"{average_score:.1f}/10"
        )

    with col3:

        st.metric(
            "Interviews Completed",
            st.session_state.interview_count
        )

    with col4:

        st.metric(
            "Improvement Areas",
            improvement_areas
        )

    st.markdown(
        '<div class="section-title">'
        '✨ What You Can Practice'
        '</div>',
        unsafe_allow_html=True
    )

    features = [
        (
            "🎯",
            "Realistic Questions",
            "AI-generated questions tailored to your target role."
        ),
        (
            "🧠",
            "AI Evaluation",
            "Receive detailed feedback after answering questions."
        ),
        (
            "📊",
            "Performance Analytics",
            "Understand your strengths and improvement areas."
        ),
        (
            "💼",
            "Multiple Job Roles",
            "Practice Software Engineering, AI, Data Science and more."
        ),
        (
            "📄",
            "Resume Interviews",
            "Generate questions based on your actual resume."
        ),
        (
            "🚀",
            "Improve Faster",
            "Get personalized recommendations after your interview."
        )
    ]

    for start in range(0, len(features), 3):

        cols = st.columns(3)

        for index, feature in enumerate(
            features[start:start + 3]
        ):

            with cols[index]:

                st.markdown(
                    f"""
                    <div class="feature-card">

                        <div class="feature-icon">
                            {feature[0]}
                        </div>

                        <div class="feature-title">
                            {feature[1]}
                        </div>

                        <div class="feature-description">
                            {feature[2]}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.write("")

    if st.button(
        "🚀 Start Your First Interview",
        use_container_width=True
    ):

        st.session_state.page = "Interview Setup"
        st.rerun()


# ============================================================
# INTERVIEW SETUP
# ============================================================

def show_interview_setup():

    st.markdown(
        '<div class="section-title">'
        '⚙️ Interview Setup'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">'
        'Customize your interview experience before you begin.'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

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
                "Custom Role"
            ]
        )

        interview_type = st.selectbox(
            "🎤 Interview Type",
            [
                "Technical Interview",
                "HR Interview",
                "Behavioral Interview",
                "Mixed Interview"
            ]
        )

        difficulty = st.selectbox(
            "🔥 Difficulty",
            [
                "Beginner",
                "Intermediate",
                "Advanced",
                "Expert"
            ]
        )

    with col2:

        number_questions = st.selectbox(
            "🔢 Number of Questions",
            [5, 10, 15]
        )

        experience = st.selectbox(
            "👤 Candidate Experience",
            [
                "Fresher",
                "0–1 Years",
                "1–3 Years",
                "3+ Years"
            ]
        )

        custom_role = ""

        if job_role == "Custom Role":

            custom_role = st.text_input(
                "Enter your target role",
                placeholder="Example: Generative AI Developer"
            )

    st.write("")

    if st.button(
        "🚀 Start Interview",
        use_container_width=True
    ):

        selected_role = (
            custom_role
            if job_role == "Custom Role"
            and custom_role
            else job_role
        )

        st.session_state.interview_config = {
            "job_role": selected_role,
            "interview_type": interview_type,
            "difficulty": difficulty,
            "number_questions": number_questions,
            "experience": experience
        }

        reset_interview()

        # Restore configuration after reset
        st.session_state.interview_config = {
            "job_role": selected_role,
            "interview_type": interview_type,
            "difficulty": difficulty,
            "number_questions": number_questions,
            "experience": experience
        }

        st.session_state.interview_started = True
        st.session_state.page = "Mock Interview"

        st.rerun()


# ============================================================
# SHOW EVALUATION
# ============================================================

def show_evaluation(evaluation):

    if not evaluation:
        return

    st.markdown(
        "### 🤖 AI Feedback"
    )

    score = evaluation.get(
        "score",
        0
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Overall",
            f"{score}/10"
        )

    with col2:

        st.metric(
            "Correctness",
            f"{evaluation.get('correctness', 0)}/10"
        )

    with col3:

        st.metric(
            "Technical Knowledge",
            f"{evaluation.get('technical_knowledge', 0)}/10"
        )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Relevance",
            f"{evaluation.get('relevance', 0)}/10"
        )

    with col2:

        st.metric(
            "Communication",
            f"{evaluation.get('communication', 0)}/10"
        )

    with col3:

        st.metric(
            "Confidence",
            f"{evaluation.get('confidence', 0)}/10"
        )

    strengths = evaluation.get(
        "strengths",
        []
    )

    improvements = evaluation.get(
        "improvements",
        []
    )

    concepts = evaluation.get(
        "concepts_to_review",
        []
    )

    with st.expander("💪 Strengths", expanded=True):

        for item in strengths:

            st.write(
                f"✅ {item}"
            )

    with st.expander("📈 Areas to Improve", expanded=True):

        for item in improvements:

            st.write(
                f"🔹 {item}"
            )

    with st.expander("💡 Better Answer"):

        st.write(
            evaluation.get(
                "better_answer",
                "No improved answer available."
            )
        )

    with st.expander("📚 Concepts to Review"):

        if concepts:

            for item in concepts:

                st.write(
                    f"📌 {item}"
                )

        else:

            st.write(
                "No specific concepts to review."
            )


# ============================================================
# MOCK INTERVIEW
# ============================================================

def show_mock_interview():

    st.markdown(
        '<div class="section-title">'
        '🎤 Mock Interview'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.interview_started:

        st.info(
            "No interview is currently active. "
            "Go to Interview Setup to start one."
        )

        if st.button(
            "⚙️ Go to Interview Setup"
        ):

            st.session_state.page = "Interview Setup"
            st.rerun()

        return

    config = st.session_state.interview_config

    total_questions = config.get(
        "number_questions",
        5
    )

    current_index = st.session_state.current_question

    # Interview finished

    if current_index >= total_questions:

        st.session_state.interview_finished = True

        if not st.session_state.get(
            "result_counted",
            False
        ):

            st.session_state.interview_count += 1
            st.session_state.result_counted = True

        st.session_state.page = "Results"

        st.rerun()

        return

    # Generate question

    if len(st.session_state.questions) <= current_index:

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

    question_number = current_index + 1

    progress = (
        current_index
        / total_questions
    )

    st.progress(progress)

    st.caption(
        f"Question {question_number} of {total_questions}"
    )

    # Question card

    st.markdown(
        f"""
        <div class="card">

            <div class="ai-badge">
                🤖 AI INTERVIEWER
            </div>

            <div class="card-title">
                Question {question_number}
            </div>

            <div style="
                font-size:20px;
                font-weight:600;
                color:#111827;
                line-height:1.6;
            ">
                {question}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    answer = st.text_area(
        "📝 Your Answer",
        placeholder="Type your answer here...",
        height=220,
        key=f"answer_{current_index}"
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

    # ========================================================
    # SUBMIT ANSWER
    # ========================================================

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
                    answer
                )

            if evaluation:

                score = int(
                    evaluation.get(
                        "score",
                        0
                    )
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


    # ========================================================
    # SKIP QUESTION
    # ========================================================

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
                "Question was skipped."
            ],
            "better_answer": "",
            "concepts_to_review": []
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

    st.markdown(
        '<div class="section-title">'
        '🎯 Interview Complete!'
        '</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.scores:

        st.info(
            "Complete an interview to see your performance report."
        )

        return

    average = (
        sum(st.session_state.scores)
        / len(st.session_state.scores)
    )

    overall = average * 10

    if overall >= 90:

        performance = "Excellent 🏆"

    elif overall >= 80:

        performance = "Very Good 🌟"

    elif overall >= 70:

        performance = "Good 👍"

    else:

        performance = "Needs Improvement 📈"

    st.markdown(
        f"""
        <div class="card" style="text-align:center;">

            <div class="ai-badge">
                🤖 AI PERFORMANCE REPORT
            </div>

            <div class="score-big">
                {overall:.0f}/100
            </div>

            <h2>
                {performance}
            </h2>

            <p class="card-text">
                Your AI interview performance score
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 📊 Performance Breakdown")

    evaluations = st.session_state.evaluations

    def avg_metric(key):

        values = [
            evaluation.get(key, 0)
            for evaluation in evaluations
        ]

        if not values:
            return 0

        return sum(values) / len(values)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Technical Knowledge",
            f"{avg_metric('technical_knowledge'):.1f}/10"
        )

    with col2:

        st.metric(
            "Communication",
            f"{avg_metric('communication'):.1f}/10"
        )

    with col3:

        st.metric(
            "Correctness",
            f"{avg_metric('correctness'):.1f}/10"
        )

    with col4:

        st.metric(
            "Relevance",
            f"{avg_metric('relevance'):.1f}/10"
        )

    with col5:

        st.metric(
            "Confidence",
            f"{avg_metric('confidence'):.1f}/10"
        )

    # Strengths

    all_strengths = []

    for evaluation in evaluations:

        all_strengths.extend(
            evaluation.get(
                "strengths",
                []
            )
        )

    all_improvements = []

    for evaluation in evaluations:

        all_improvements.extend(
            evaluation.get(
                "improvements",
                []
            )
        )

    all_concepts = []

    for evaluation in evaluations:

        all_concepts.extend(
            evaluation.get(
                "concepts_to_review",
                []
            )
        )

    st.markdown("### 💪 Your Strengths")

    if all_strengths:

        for item in all_strengths[:6]:

            st.write(
                f"✅ {item}"
            )

    else:

        st.write(
            "No strengths recorded."
        )

    st.markdown("### 📈 Weak Areas")

    if all_improvements:

        for item in all_improvements[:6]:

            st.write(
                f"🔹 {item}"
            )

    else:

        st.write(
            "No major improvement areas recorded."
        )

    st.markdown("### 📚 AI Recommendations")

    if all_concepts:

        for item in all_concepts[:8]:

            st.write(
                f"📌 Review {item}"
            )

    else:

        st.write(
            "Keep practicing interview questions regularly."
        )

    st.markdown("### 📝 Interview Summary")

    st.write(
        f"""
        You completed an interview with
        {len(st.session_state.scores)} questions.

        Your average score was
        {average:.1f}/10.

        Overall performance:
        {performance}
        """
    )

    st.markdown("### 🔎 Question-by-Question Review")

    for index, evaluation in enumerate(
        evaluations
    ):

        with st.expander(
            f"Question {index + 1} — "
            f"Score: {evaluation.get('score', 0)}/10"
        ):

            if index < len(
                st.session_state.questions
            ):

                st.write(
                    "**Question:**"
                )

                st.write(
                    st.session_state.questions[index]
                )

            if index < len(
                st.session_state.answers
            ):

                st.write(
                    "**Your Answer:**"
                )

                st.write(
                    st.session_state.answers[index]
                )

            show_evaluation(
                evaluation
            )

    if st.button(
        "🔄 Start New Interview",
        use_container_width=True
    ):

        st.session_state.result_counted = False

        reset_interview()

        st.session_state.page = "Interview Setup"

        st.rerun()


# ============================================================
# HISTORY
# ============================================================

def show_history():

    st.markdown(
        '<div class="section-title">'
        '📚 Interview History'
        '</div>',
        unsafe_allow_html=True
    )

    if st.session_state.interview_count == 0:

        st.info(
            "No completed interviews yet."
        )

    else:

        st.success(
            f"You have completed "
            f"{st.session_state.interview_count} interview(s) "
            "in this session."
        )

        st.info(
            "Persistent interview history will be added "
            "in a future version."
        )


# ============================================================
# ABOUT
# ============================================================

def show_about():

    st.markdown(
        '<div class="section-title">'
        'ℹ️ About'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="card">

            <div class="card-title">
                🤖 AI Interview Simulator
            </div>

            <div class="card-text">

                An AI-powered mock interview platform that helps
                students and job seekers practice realistic interviews.

                <br><br>

                The application uses Generative AI to generate
                personalized interview questions and evaluate
                candidate responses.

                <br><br>

                <b>Built with:</b>

                Python • Streamlit • Groq • GitHub • Streamlit Cloud

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGE ROUTER
# ============================================================

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
    <div class="custom-footer">

        🤖 AI Interview Simulator
        &nbsp;•&nbsp;
        Practice. Improve. Get Interview-Ready.

        <br>

        Built with Python + Streamlit + Groq

    </div>
    """,
    unsafe_allow_html=True
)
