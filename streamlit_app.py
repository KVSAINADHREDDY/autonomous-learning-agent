"""
Autonomous Learning Agent - Streamlit Application
A complete learning platform with study materials, quizzes, and Feynman teaching.
"""
import streamlit as st
import os
from datetime import datetime

# Set page config first
st.set_page_config(
    page_title="🎓 Autonomous Learning Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Streamlit Cloud secrets into environment variables (for deployment)
try:
    from src.utils.secrets import load_secrets_to_env
    load_secrets_to_env()
except Exception:
    pass

# Import modules after streamlit config
from src.data.checkpoints import (
    get_all_checkpoints, 
    get_checkpoint_by_id,
    CheckpointDefinition
)
from src.graph.learning_graph import get_learning_workflow, reset_learning_workflow, LearningState
from src.modules.progress_tracker import CheckpointStatus
from src.modules.quiz_generator import Question


# =========================================================
# CUSTOM CSS STYLING
# =========================================================

def apply_custom_css():
    """Apply custom CSS for beautiful UI."""
    st.markdown("""
    <style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Modern Headers */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem !important;
        letter-spacing: -0.02em;
    }
    
    h2, h3 {
        color: #e2e8f0;
        font-weight: 600;
    }
    
    /* Glassmorphism Cards */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
    }
    
    /* Step Progress Indicator */
    .step-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0;
        margin: 2rem 0;
        padding: 1.5rem;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 1;
    }
    
    .step-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    
    .step-circle.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 0 30px rgba(102, 126, 234, 0.5);
    }
    
    .step-circle.completed {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .step-circle.inactive {
        background: rgba(255, 255, 255, 0.1);
        color: #64748b;
    }
    
    .step-label {
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    .step-connector {
        width: 80px;
        height: 4px;
        background: rgba(255, 255, 255, 0.1);
        margin: 0 0.5rem;
        border-radius: 2px;
    }
    
    .step-connector.completed {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
    }
    
    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 10px;
    }
    
    /* Question Cards */
    .question-card {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.6) 0%, rgba(13, 33, 55, 0.8) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .question-card:hover {
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    }
    
    .question-card.correct {
        border-left: 4px solid #10b981;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(13, 33, 55, 0.8) 100%);
    }
    
    .question-card.incorrect {
        border-left: 4px solid #ef4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(13, 33, 55, 0.8) 100%);
    }
    
    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(10px);
        padding: 1.25rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
    }
    
    div[data-testid="stMetric"] div {
        color: #e2e8f0 !important;
    }
    
    /* Score Display */
    .score-display {
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .score-pass { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    .score-fail { 
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
    }
    
    /* Topic Cards on Home */
    .topic-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.4s ease;
        cursor: pointer;
    }
    
    .topic-card:hover {
        transform: translateY(-5px);
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    /* Feynman Explanation Box */
    .feynman-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
    }
    
    /* Hint Box */
    .hint-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(251, 191, 36, 0.2);
    }
    
    /* Radio buttons styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stRadio > div > label {
        color: #e2e8f0 !important;
        padding: 0.75rem 1rem !important;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .stRadio > div > label:hover {
        background: rgba(102, 126, 234, 0.2);
    }
    
    /* Text areas */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        justify-content: flex-start;
        background: rgba(255, 255, 255, 0.05);
        box-shadow: none;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(102, 126, 234, 0.3);
        transform: translateX(5px);
    }
    
    /* Tabs - Replace with Step Navigation */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-radius: 16px;
        padding: 0.5rem;
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        color: #94a3b8;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.2);
        color: #e2e8f0;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Success/Error/Warning boxes */
    .stSuccess {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%);
        border-left: 4px solid #10b981;
        border-radius: 12px;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border-left: 4px solid #ef4444;
        border-radius: 12px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.2) 0%, rgba(245, 158, 11, 0.2) 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 12px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        border-left: 4px solid #667eea;
        border-radius: 12px;
    }
    
    /* Animated gradient background (optional effect) */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 3s ease infinite;
        background-size: 200% 200%;
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Pulse animation for active elements */
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(102, 126, 234, 0); }
        100% { box-shadow: 0 0 0 0 rgba(102, 126, 234, 0); }
    }
    </style>
    """, unsafe_allow_html=True)


# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

def init_session_state():
    """Initialize session state variables."""
    defaults = {
        # Navigation
        "current_page": "home",
        "current_checkpoint_id": None,
        
        # Learning state
        "learning_state": None,
        "study_content": "",
        "sources": [],
        
        # Quiz state
        "questions": [],
        "current_question_idx": 0,
        "user_answers": {},
        "quiz_submitted": False,
        "quiz_result": None,
        "show_hint": False,
        
        # Teaching state
        "feynman_content": "",
        "teaching_complete": False,
        
        # Progress
        "attempt_number": 0,
        "session_started": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================================================
# COMPONENTS
# =========================================================

def render_header():
    """Render the main header."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🎓 Autonomous Learning Agent")
        st.caption("Learn AI concepts with interactive quizzes and personalized teaching")
    
    with col2:
        if st.session_state.session_started:
            workflow = get_learning_workflow()
            progress = workflow.get_progress_summary()
            completion = progress.get("completion_percentage", 0)
            st.metric("Progress", f"{completion:.0f}%")


def render_progress_sidebar():
    """Render the progress sidebar."""
    st.sidebar.markdown("### 📊 Learning Progress")
    
    workflow = get_learning_workflow()
    checkpoints = get_all_checkpoints()
    
    if st.session_state.session_started:
        progress = workflow.get_progress_summary()
        
        # Progress bar
        completion = progress.get("completion_percentage", 0)
        st.sidebar.progress(completion / 100)
        st.sidebar.caption(f"{progress.get('completed', 0)}/{progress.get('total_checkpoints', 0)} checkpoints completed")
        
        st.sidebar.markdown("---")
    
    # Checkpoint list
    st.sidebar.markdown("### 📚 Topics")
    
    for i, cp in enumerate(checkpoints, 1):
        # Get status icon
        if st.session_state.session_started:
            try:
                cp_progress = workflow.progress_tracker._get_progress(cp.id)
                if cp_progress.status == CheckpointStatus.PASSED:
                    icon = "✅"
                elif cp_progress.status in [CheckpointStatus.IN_PROGRESS, CheckpointStatus.STUDYING]:
                    icon = "📖"
                elif cp_progress.status == CheckpointStatus.NEEDS_TEACHING:
                    icon = "🎓"
                else:
                    icon = "⬜"
            except:
                icon = "⬜"
        else:
            icon = "⬜"
        
        if st.sidebar.button(f"{icon} {i}. {cp.topic}", key=f"nav_{cp.id}", use_container_width=True):
            # Start session if not started
            if not st.session_state.session_started:
                reset_learning_workflow()
                workflow = get_learning_workflow()
                workflow.start_learning_session(checkpoints)
                st.session_state.session_started = True
            
            # Navigate to the selected checkpoint
            st.session_state.current_checkpoint_id = cp.id
            st.session_state.current_page = "checkpoint"
            st.session_state.current_step = "study"  # Reset to study step
            
            # Reset quiz state for new topic
            st.session_state.quiz_questions = []
            st.session_state.quiz_submitted = False
            st.session_state.quiz_result = None
            st.session_state.flashcards = []
            st.session_state.flashcards_viewed = False
            
            st.rerun()


def render_home_page():
    """Render the home page with modern design."""
    
    # Subtitle Section (title already in header)
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <p style="font-size: 1.2rem; color: #94a3b8; max-width: 600px; margin: 0 auto;">
            Master AI concepts with personalized quizzes, instant feedback, and Feynman-style explanations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Feature Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: rgba(102, 126, 234, 0.1); border-radius: 16px; border: 1px solid rgba(102, 126, 234, 0.3);">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📚</div>
            <div style="font-weight: 600; color: #e2e8f0;">Smart Study</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">Curated materials</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: rgba(16, 185, 129, 0.1); border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.3);">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🃏</div>
            <div style="font-weight: 600; color: #e2e8f0;">Flashcards</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">Quick memorization</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: rgba(251, 191, 36, 0.1); border-radius: 16px; border: 1px solid rgba(251, 191, 36, 0.3);">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎓</div>
            <div style="font-weight: 600; color: #e2e8f0;">Feynman AI</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">Simple explanations</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: rgba(239, 68, 68, 0.1); border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.3);">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
            <div style="font-weight: 600; color: #e2e8f0;">Track Progress</div>
            <div style="font-size: 0.85rem; color: #94a3b8;">See improvement</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    
    # Topics Section
    st.markdown("### 📚 Available Learning Topics")
    st.markdown("")
    
    checkpoints = get_all_checkpoints()
    
    # Display topics in a grid
    for i in range(0, len(checkpoints), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(checkpoints):
                cp = checkpoints[i + j]
                with col:
                    # Topic Card
                    difficulty_color = {"beginner": "#10b981", "intermediate": "#f59e0b", "advanced": "#ef4444"}.get(cp.difficulty.lower(), "#667eea")
                    st.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
                        border-radius: 16px;
                        padding: 1.5rem;
                        margin-bottom: 1rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        transition: all 0.3s ease;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                            <h4 style="margin: 0; color: #e2e8f0;">{i + j + 1}. {cp.topic}</h4>
                            <span style="
                                background: {difficulty_color}22;
                                color: {difficulty_color};
                                padding: 0.25rem 0.75rem;
                                border-radius: 20px;
                                font-size: 0.75rem;
                                font-weight: 600;
                            ">{cp.difficulty.title()}</span>
                        </div>
                        <div style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1rem;">
                            ⏱️ {cp.estimated_minutes} min • 🎯 {len(cp.objectives)} objectives
                        </div>
                        <div style="color: #64748b; font-size: 0.85rem;">
                            {cp.objectives[0][:60]}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    
    # Start Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <p style="color: #94a3b8; font-size: 1rem;">Ready to begin your learning journey?</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Learning Journey", use_container_width=True, type="primary"):
            # Reset workflow to pick up latest .env settings
            reset_learning_workflow()
            
            # Initialize learning session
            workflow = get_learning_workflow()
            workflow.start_learning_session(checkpoints)
            
            st.session_state.session_started = True
            st.session_state.current_checkpoint_id = checkpoints[0].id
            st.session_state.current_page = "checkpoint"
            st.session_state.current_step = "study"  # Reset to study step
            st.rerun()


def render_checkpoint_page():
    """Render a checkpoint learning page with step-based navigation."""
    checkpoint_id = st.session_state.current_checkpoint_id
    
    # Initialize current step in session state
    if "current_step" not in st.session_state:
        st.session_state.current_step = "study"
    
    if not checkpoint_id:
        st.warning("No checkpoint selected. Please select a topic from the sidebar.")
        return
    
    try:
        checkpoint = get_checkpoint_by_id(checkpoint_id)
    except ValueError:
        st.error(f"Checkpoint not found: {checkpoint_id}")
        return
    
    workflow = get_learning_workflow()
    
    # Get progress for step states
    try:
        progress = workflow.progress_tracker._get_progress(checkpoint_id)
        study_complete = progress.study_material_loaded
        flashcards_viewed = st.session_state.get("flashcards_viewed", False)
        quiz_complete = st.session_state.quiz_submitted
        has_results = st.session_state.quiz_result is not None
    except:
        study_complete = False
        flashcards_viewed = False
        quiz_complete = False
        has_results = False
    
    # Topic Header with gradient
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.5rem;">📖 {checkpoint.topic}</h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">Master this topic step by step</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Step Progress Indicator (4 steps: Study -> Quiz -> Flashcards -> Results)
    step_1_class = "completed" if study_complete else ("active" if st.session_state.current_step == "study" else "inactive")
    step_2_class = "completed" if quiz_complete else ("active" if st.session_state.current_step == "quiz" else "inactive")
    step_3_class = "completed" if flashcards_viewed else ("active" if st.session_state.current_step == "flashcards" else "inactive")
    step_4_class = "active" if st.session_state.current_step == "results" and has_results else "inactive"
    
    connector_1_class = "completed" if study_complete else ""
    connector_2_class = "completed" if quiz_complete else ""
    connector_3_class = "completed" if flashcards_viewed else ""
    
    st.markdown(f"""
    <div class="step-container">
        <div class="step">
            <div class="step-circle {step_1_class}">{"✓" if study_complete else "1"}</div>
            <div class="step-label">Study</div>
        </div>
        <div class="step-connector {connector_1_class}"></div>
        <div class="step">
            <div class="step-circle {step_2_class}">{"✓" if quiz_complete else "2"}</div>
            <div class="step-label">Quiz</div>
        </div>
        <div class="step-connector {connector_2_class}"></div>
        <div class="step">
            <div class="step-circle {step_3_class}">{"✓" if flashcards_viewed else "3"}</div>
            <div class="step-label">Cards</div>
        </div>
        <div class="step-connector {connector_3_class}"></div>
        <div class="step">
            <div class="step-circle {step_4_class}">{"✓" if has_results and st.session_state.quiz_result.passed else "4"}</div>
            <div class="step-label">Results</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Step Navigation Buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📚 Study", use_container_width=True, 
                     type="primary" if st.session_state.current_step == "study" else "secondary"):
            st.session_state.current_step = "study"
            st.rerun()
    with col2:
        quiz_disabled = not study_complete
        if st.button("📝 Quiz", use_container_width=True, disabled=quiz_disabled,
                     type="primary" if st.session_state.current_step == "quiz" else "secondary"):
            st.session_state.current_step = "quiz"
            st.rerun()
    with col3:
        flashcards_disabled = not study_complete
        if st.button("🃏 Flashcards", use_container_width=True, disabled=flashcards_disabled,
                     type="primary" if st.session_state.current_step == "flashcards" else "secondary"):
            st.session_state.current_step = "flashcards"
            st.rerun()
    with col4:
        results_disabled = not has_results
        if st.button("📊 Results", use_container_width=True, disabled=results_disabled,
                     type="primary" if st.session_state.current_step == "results" else "secondary"):
            st.session_state.current_step = "results"
            st.rerun()
    
    st.markdown("---")
    
    # Progress Metrics
    try:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Attempts", f"{progress.attempt_count}/{progress.max_attempts}")
        with col2:
            st.metric("🏆 Best Score", f"{progress.best_score * 100:.0f}%")
        with col3:
            status_map = {
                CheckpointStatus.NOT_STARTED: "📋 Not Started",
                CheckpointStatus.STUDYING: "📖 Studying",
                CheckpointStatus.IN_PROGRESS: "📝 In Progress",
                CheckpointStatus.QUIZ_IN_PROGRESS: "📝 Quiz Active",
                CheckpointStatus.NEEDS_TEACHING: "🎓 Review",
                CheckpointStatus.PASSED: "✅ Passed",
                CheckpointStatus.FAILED: "❌ Failed"
            }
            st.metric("📊 Status", status_map.get(progress.status, "Unknown"))
        with col4:
            st.metric("⚡ Difficulty", checkpoint.difficulty.title())
    except:
        pass
    
    st.markdown("---")
    
    # Learning objectives in a nice card
    with st.expander("🎯 Learning Objectives", expanded=False):
        for i, obj in enumerate(checkpoint.objectives, 1):
            st.markdown(f"**{i}.** {obj}")
    
    st.markdown("")
    
    # Render current step content
    if st.session_state.current_step == "study":
        render_study_tab(checkpoint, workflow)
    elif st.session_state.current_step == "quiz":
        render_quiz_tab(checkpoint, workflow)
    elif st.session_state.current_step == "flashcards":
        render_flashcards_tab(checkpoint, workflow)
    elif st.session_state.current_step == "results":
        render_results_tab(checkpoint, workflow)


def render_study_tab(checkpoint: CheckpointDefinition, workflow):
    """Render the study material tab."""
    
    # User notes input
    user_notes = st.text_area(
        "📝 Add your own notes (optional)",
        placeholder="Paste any notes you have about this topic...",
        height=100
    )
    
    # Load study material button
    if st.button("📚 Load Study Material", type="primary"):
        with st.spinner("Collecting study material..."):
            content, sources = workflow.collect_study_material(checkpoint, user_notes)
            st.session_state.study_content = content
            st.session_state.sources = sources
            workflow.progress_tracker.mark_study_complete(checkpoint.id)
    
    # Display study content
    if st.session_state.study_content:
        st.markdown("### 📖 Study Material")
        
        # Source info
        st.info(f"📚 Content from {len(st.session_state.sources)} sources")
        
        # Main content
        st.markdown(st.session_state.study_content)
        
        # Sources accordion
        with st.expander("📋 View Sources"):
            for source in st.session_state.sources:
                st.markdown(f"**{source.get('title', 'Source')}** ({source.get('type', 'unknown')})")
                if source.get('url'):
                    st.caption(source['url'])
                st.markdown("---")
        
        st.success("✅ Study material loaded! When ready, go to the Flashcards or Quiz tab.")
    
    elif checkpoint.notes:
        # Show preview of predefined notes
        st.markdown("### 📖 Quick Preview")
        st.markdown(checkpoint.notes[:500] + "...")
        st.caption("Click 'Load Study Material' to see the full content")


def render_flashcards_tab(checkpoint: CheckpointDefinition, workflow):
    """Render the flashcards tab with interactive flip cards."""
    
    # Initialize flashcard state
    if "flashcards" not in st.session_state:
        st.session_state.flashcards = []
    if "current_card_idx" not in st.session_state:
        st.session_state.current_card_idx = 0
    if "card_flipped" not in st.session_state:
        st.session_state.card_flipped = False
    if "cards_reviewed" not in st.session_state:
        st.session_state.cards_reviewed = set()
    
    # Check if study is complete
    try:
        progress = workflow.progress_tracker._get_progress(checkpoint.id)
        if not progress.study_material_loaded:
            st.warning("📚 Please complete the study material first!")
            return
    except:
        st.warning("Please start the learning session from the home page.")
        return
    
    # Generate flashcards if needed
    if not st.session_state.flashcards:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🃏</div>
                <h3 style="color: #e2e8f0;">Study with Flashcards</h3>
                <p style="color: #94a3b8;">Interactive cards to help you memorize key concepts</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🃏 Generate Flashcards", type="primary", use_container_width=True):
                with st.spinner("Creating flashcards..."):
                    flashcards = workflow.generate_flashcards(checkpoint)
                    st.session_state.flashcards = flashcards
                    st.session_state.current_card_idx = 0
                    st.session_state.card_flipped = False
                    st.session_state.cards_reviewed = set()
                    st.session_state.flashcards_viewed = True
                st.rerun()
        return
    
    flashcards = st.session_state.flashcards
    total_cards = len(flashcards)
    current_idx = st.session_state.current_card_idx
    current_card = flashcards[current_idx]
    
    # Progress bar
    reviewed = len(st.session_state.cards_reviewed)
    st.progress(reviewed / total_cards if total_cards > 0 else 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📇 Card", f"{current_idx + 1} of {total_cards}")
    with col2:
        st.metric("✅ Reviewed", f"{reviewed}/{total_cards}")
    with col3:
        difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(current_card.difficulty, "⚪")
        st.metric("📊 Difficulty", f"{difficulty_emoji} {current_card.difficulty.title()}")
    
    st.markdown("---")
    
    # Flashcard Display
    is_flipped = st.session_state.card_flipped
    
    # Card styling based on flip state
    if not is_flipped:
        # Front of card (Question)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 3rem 2rem;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
            cursor: pointer;
            transition: all 0.3s ease;
        ">
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">
                {current_card.category} • Click to flip
            </div>
            <div style="font-size: 1.5rem; color: white; font-weight: 600; line-height: 1.5;">
                {current_card.front}
            </div>
            <div style="margin-top: 1.5rem;">
                <span style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; color: white;">
                    🔄 Click to reveal answer
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Back of card (Answer)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border-radius: 20px;
            padding: 3rem 2rem;
            min-height: 300px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            box-shadow: 0 20px 40px rgba(16, 185, 129, 0.3);
            cursor: pointer;
            transition: all 0.3s ease;
        ">
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-bottom: 1rem;">
                ✅ Answer
            </div>
            <div style="font-size: 1.3rem; color: white; font-weight: 500; line-height: 1.6;">
                {current_card.back}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mark as reviewed
        st.session_state.cards_reviewed.add(current_card.id)
    
    st.markdown("")
    
    # Control buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_card_idx -= 1
                st.session_state.card_flipped = False
                st.rerun()
    
    with col2:
        if st.button("🔄 Flip Card", type="primary", use_container_width=True):
            st.session_state.card_flipped = not st.session_state.card_flipped
            st.rerun()
    
    with col3:
        if current_idx < total_cards - 1:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_card_idx += 1
                st.session_state.card_flipped = False
                st.rerun()
    
    # Hint section
    if current_card.hint and not is_flipped:
        with st.expander("💡 Need a hint?"):
            st.info(current_card.hint)
    
    st.markdown("---")
    
    # Card navigation grid
    st.markdown("### 📇 All Cards")
    cols = st.columns(10)
    for i, card in enumerate(flashcards):
        with cols[i % 10]:
            is_reviewed = card.id in st.session_state.cards_reviewed
            is_current = i == current_idx
            
            btn_type = "primary" if is_current else "secondary"
            label = f"✓{i+1}" if is_reviewed else str(i+1)
            
            if st.button(label, key=f"card_nav_{i}", use_container_width=True,
                        type=btn_type if is_current else "secondary"):
                st.session_state.current_card_idx = i
                st.session_state.card_flipped = False
                st.rerun()
    
    # Completion message
    if reviewed == total_cards:
        st.success("🎉 You've reviewed all flashcards! Ready to take the quiz?")


def render_quiz_tab(checkpoint: CheckpointDefinition, workflow):
    """Render the quiz tab - displays all questions with instant feedback."""
    
    # Initialize feedback tracking in session state
    if "question_feedback" not in st.session_state:
        st.session_state.question_feedback = {}  # {question_id: {"checked": bool, "correct": bool, "explanation": str}}
    
    # Check if study is complete
    try:
        progress = workflow.progress_tracker._get_progress(checkpoint.id)
        
        if progress.status == CheckpointStatus.PASSED:
            st.success("🎉 You've already passed this checkpoint!")
            if st.button("📊 View Results"):
                st.session_state.current_page = "results"
            return
        
        if not progress.study_material_loaded:
            st.warning("📚 Please complete the study material first!")
            return
        
        if not progress.can_retry:
            st.error("❌ No more attempts remaining for this topic.")
            st.markdown("")
            
            # Show helpful options
            st.markdown("### 🎓 What would you like to do?")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; background: rgba(251, 191, 36, 0.1); border-radius: 12px; border: 1px solid rgba(251, 191, 36, 0.3);">
                    <div style="font-size: 2rem;">🎓</div>
                    <div style="font-weight: 600; color: #fbbf24;">Feynman Teaching</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Get simple explanations</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("📖 Get Teaching", use_container_width=True):
                    # Show Feynman explanation for the topic
                    with st.spinner("Generating Feynman explanation..."):
                        explanation = workflow.feynman_teacher.explain_concept(
                            concept=checkpoint.topic,
                            context=st.session_state.study_content or checkpoint.notes or "",
                            failed_question=f"Help me understand {checkpoint.topic} better"
                        )
                        if explanation:
                            st.markdown("### 🎓 Feynman Explanation")
                            st.info(f"**Simple Explanation:** {explanation.simple_explanation}")
                            if explanation.analogy:
                                st.success(f"**Analogy:** {explanation.analogy}")
            
            with col2:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; background: rgba(16, 185, 129, 0.1); border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
                    <div style="font-size: 2rem;">🔄</div>
                    <div style="font-weight: 600; color: #10b981;">Reset & Retry</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Start fresh with this topic</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🔄 Reset Topic", use_container_width=True):
                    # Reset this checkpoint's progress
                    workflow.progress_tracker.reset_checkpoint(checkpoint.id)
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_result = None
                    st.session_state.question_feedback = {}
                    st.session_state.current_step = "study"
                    st.success("✅ Topic reset! You can now retry.")
                    st.rerun()
            
            with col3:
                st.markdown("""
                <div style="text-align: center; padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 12px; border: 1px solid rgba(102, 126, 234, 0.3);">
                    <div style="font-size: 2rem;">➡️</div>
                    <div style="font-weight: 600; color: #667eea;">Next Topic</div>
                    <div style="font-size: 0.85rem; color: #94a3b8;">Move to next checkpoint</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("➡️ Next Topic", use_container_width=True):
                    # Find next checkpoint
                    checkpoints = get_all_checkpoints()
                    current_idx = next((i for i, cp in enumerate(checkpoints) if cp.id == checkpoint.id), 0)
                    next_idx = (current_idx + 1) % len(checkpoints)
                    next_checkpoint = checkpoints[next_idx]
                    
                    st.session_state.current_checkpoint_id = next_checkpoint.id
                    st.session_state.current_step = "study"
                    st.session_state.quiz_questions = []
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_result = None
                    st.session_state.flashcards = []
                    st.session_state.flashcards_viewed = False
                    st.rerun()
            
            return
            
    except:
        st.warning("Please start the learning session from the home page.")
        return
    
    # Generate quiz if needed
    if not st.session_state.questions or st.session_state.quiz_submitted:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Start Quiz (with Instant Feedback)", type="primary"):
                with st.spinner("Generating quiz questions..."):
                    questions = workflow.generate_quiz(checkpoint)
                    st.session_state.questions = questions
                    st.session_state.user_answers = {}
                    st.session_state.question_feedback = {}
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_result = None
                    st.session_state.instant_feedback_mode = True
                    
                    # Update progress
                    workflow.progress_tracker.start_quiz(checkpoint.id)
                    st.session_state.attempt_number = progress.attempt_count + 1
                    
                st.rerun()
        return
    
    # Display all questions at once with instant feedback
    questions = st.session_state.questions
    total_questions = len(questions)
    
    # Calculate stats
    answered = len(st.session_state.user_answers)
    checked = len(st.session_state.question_feedback)
    correct_count = sum(1 for f in st.session_state.question_feedback.values() if f.get("correct", False))
    
    # Header with progress
    st.progress(checked / total_questions if total_questions > 0 else 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 Answered", f"{answered}/{total_questions}")
    with col2:
        st.metric("✅ Checked", f"{checked}/{total_questions}")
    with col3:
        st.metric("🎯 Correct", f"{correct_count}/{checked}" if checked > 0 else "0/0")
    
    st.markdown("---")
    st.markdown("### 📝 Quiz with Instant Feedback")
    st.info("💡 **How it works:** Answer each question, then click **'Check Answer'** to get instant feedback. Wrong answers will show a simplified explanation!")
    
    # Display ALL questions with instant feedback
    for q_idx, question in enumerate(questions):
        st.markdown("---")
        
        # Get feedback status for this question
        feedback = st.session_state.question_feedback.get(question.id, {})
        is_checked = feedback.get("checked", False)
        is_correct = feedback.get("correct", False)
        
        # Question header with status indicator
        if is_checked:
            if is_correct:
                st.markdown(f"### ✅ Question {q_idx + 1} of {total_questions} - CORRECT!")
            else:
                st.markdown(f"### ❌ Question {q_idx + 1} of {total_questions} - INCORRECT")
        else:
            st.markdown(f"### Question {q_idx + 1} of {total_questions}")
        
        st.markdown(f"**{question.question_text}**")
        
        if question.objective:
            st.caption(f"📎 Related to: {question.objective}")
        
        # Answer input based on question type (disabled if already checked)
        current_answer = st.session_state.user_answers.get(question.id, "")
        
        if question.question_type == "multiple_choice" and question.options:
            answer = st.radio(
                f"Select your answer for Q{q_idx + 1}:",
                options=question.options,
                index=None,
                key=f"q_{question.id}",
                disabled=is_checked
            )
            if answer and not is_checked:
                st.session_state.user_answers[question.id] = answer[0]  # Just the letter
        
        elif question.question_type == "true_false":
            answer = st.radio(
                f"Select your answer for Q{q_idx + 1}:",
                options=["True", "False"],
                index=None,
                key=f"q_{question.id}",
                disabled=is_checked
            )
            if answer and not is_checked:
                st.session_state.user_answers[question.id] = answer
        
        else:  # short_answer
            answer = st.text_area(
                f"Your answer for Q{q_idx + 1}:",
                value=current_answer,
                key=f"q_{question.id}",
                height=80,
                disabled=is_checked
            )
            if answer and not is_checked:
                st.session_state.user_answers[question.id] = answer
        
        # Action buttons for each question
        if not is_checked:
            col1, col2 = st.columns([1, 3])
            with col1:
                # Check Answer button
                has_answer = question.id in st.session_state.user_answers and st.session_state.user_answers[question.id]
                if st.button(f"🔍 Check Answer", key=f"check_{question.id}", disabled=not has_answer):
                    user_answer = st.session_state.user_answers.get(question.id, "")
                    
                    # Evaluate the answer
                    is_correct = False
                    if question.question_type in ["multiple_choice", "true_false"]:
                        is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()
                    else:
                        # For short answers, check if keywords are present
                        answer_lower = user_answer.lower()
                        keyword_matches = sum(1 for kw in question.keywords if kw.lower() in answer_lower)
                        is_correct = keyword_matches >= len(question.keywords) * 0.5  # 50% keyword match
                    
                    # Generate explanation for wrong answers
                    explanation = ""
                    if not is_correct:
                        # Use Feynman teacher to generate simplified explanation
                        try:
                            feynman_result = workflow.feynman_teacher.explain_concept(
                                concept=question.objective or question.question_text[:50],
                                context=question.explanation or "",
                                failed_question=question.question_text
                            )
                            # Combine simple explanation with analogy for better understanding
                            explanation = f"{feynman_result.simple_explanation}\n\n**Analogy:** {feynman_result.analogy}"
                        except Exception as e:
                            explanation = question.explanation if question.explanation else f"The correct answer is: {question.correct_answer}"
                    
                    # Store feedback
                    st.session_state.question_feedback[question.id] = {
                        "checked": True,
                        "correct": is_correct,
                        "explanation": explanation,
                        "correct_answer": question.correct_answer
                    }
                    st.rerun()
            
            with col2:
                # Hint button
                if st.button(f"💡 Get Hint", key=f"hint_{question.id}"):
                    hint = workflow.get_hint(question)
                    st.info(f"💡 **Hint:** {hint}")
        
        # Show feedback if question was checked
        if is_checked:
            if is_correct:
                st.success(f"✅ **Correct!** Well done!")
                if question.explanation:
                    with st.expander("📖 Learn more"):
                        st.markdown(question.explanation)
            else:
                st.error(f"❌ **Incorrect.** The correct answer is: **{feedback.get('correct_answer', question.correct_answer)}**")
                
                # Show Feynman-style explanation
                st.markdown("---")
                st.markdown("#### 🎓 Let me explain this simply:")
                
                explanation = feedback.get("explanation", "")
                if explanation:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
                                color: #065f46; 
                                border-radius: 12px; 
                                padding: 1.5rem; 
                                margin: 0.5rem 0;">
                        <p style="margin: 0;">{explanation}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info(f"📖 {question.explanation if question.explanation else 'Review the study material for this concept.'}")
    
    # Submit section at the bottom
    st.markdown("---")
    st.markdown("---")
    
    # Summary
    all_checked = checked == total_questions
    
    col1, col2 = st.columns([2, 1])
    with col1:
        if not all_checked:
            remaining = total_questions - checked
            st.warning(f"⚠️ {remaining} question(s) not yet checked. Check all answers to see your final score!")
        else:
            score_percent = (correct_count / total_questions) * 100 if total_questions > 0 else 0
            if score_percent >= 70:
                st.success(f"🎉 **Score: {score_percent:.0f}%** - You passed! ({correct_count}/{total_questions} correct)")
            else:
                st.error(f"📚 **Score: {score_percent:.0f}%** - You need 70% to pass. ({correct_count}/{total_questions} correct)")
    
    with col2:
        if all_checked:
            if st.button("✅ Submit Final Results", type="primary"):
                with st.spinner("Saving your results..."):
                    result = workflow.evaluate_quiz(
                        questions=questions,
                        user_answers=st.session_state.user_answers,
                        checkpoint_id=checkpoint.id,
                        attempt_number=st.session_state.attempt_number
                    )
                    st.session_state.quiz_result = result
                    st.session_state.quiz_submitted = True
                st.rerun()


def render_results_tab(checkpoint: CheckpointDefinition, workflow):
    """Render the results tab."""
    result = st.session_state.quiz_result
    
    if not result:
        st.info("📝 Complete a quiz to see your results here.")
        return
    
    # Score display
    score_pct = result.total_score * 100
    passed = result.passed
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(
            f"<div class='score-display {'score-pass' if passed else 'score-fail'}'>"
            f"{score_pct:.0f}%</div>",
            unsafe_allow_html=True
        )
        
        if passed:
            st.success("🎉 Congratulations! You passed!")
        else:
            st.error(f"📚 You need 70% to pass. Keep learning!")
    
    with col2:
        st.markdown("### Quiz Summary")
        
        correct = sum(1 for s in result.scores.values() if s >= 0.7)
        total = len(result.scores)
        
        st.metric("Correct Answers", f"{correct}/{total}")
        st.metric("Attempt", f"#{result.attempt_number}")
        
        if result.weak_concepts:
            st.markdown("**Areas to Review:**")
            for concept in result.weak_concepts:
                st.markdown(f"- {concept}")
    
    st.markdown("---")
    
    # Detailed results
    st.markdown("### 📋 Detailed Answers")
    
    for i, q in enumerate(result.questions):
        score = result.scores.get(q.id, 0)
        user_ans = result.user_answers.get(q.id, "No answer")
        
        with st.expander(f"Q{i+1}: {q.question_text[:50]}... {'✅' if score >= 0.7 else '❌'}"):
            st.markdown(f"**Your Answer:** {user_ans}")
            st.markdown(f"**Correct Answer:** {q.correct_answer}")
            st.markdown(f"**Score:** {score * 100:.0f}%")
            if q.explanation:
                st.info(f"📖 {q.explanation}")
    
    st.markdown("---")
    
    # Next actions
    if passed:
        if st.button("➡️ Continue to Next Topic", type="primary"):
            next_cp = workflow.move_to_next_checkpoint()
            if next_cp:
                st.session_state.current_checkpoint_id = next_cp.checkpoint_id
                st.session_state.questions = []
                st.session_state.quiz_result = None
                st.session_state.study_content = ""
                st.rerun()
            else:
                st.balloons()
                st.success("🎓 Congratulations! You've completed all checkpoints!")
    else:
        # Show Feynman teaching
        if result.weak_concepts:
            st.markdown("### 🎓 Let's Review Together")
            st.markdown("I'll explain the concepts you struggled with in simple terms.")
            
            if st.button("📚 Get Personalized Explanation", type="primary"):
                with st.spinner("Creating your personalized lesson..."):
                    teaching_content = workflow.teach_weak_concepts(
                        result.weak_concepts,
                        checkpoint
                    )
                    st.session_state.feynman_content = teaching_content
                st.rerun()
        
        if st.session_state.feynman_content:
            st.markdown(st.session_state.feynman_content)
            
            # Check if can retry
            try:
                progress = workflow.progress_tracker._get_progress(checkpoint.id)
                if progress.can_retry:
                    st.markdown("---")
                    st.info(f"📝 You have {progress.attempts_remaining} attempts remaining.")
                    
                    if st.button("🔄 Retake Quiz", type="primary"):
                        st.session_state.questions = []
                        st.session_state.quiz_result = None
                        st.session_state.feynman_content = ""
                        st.session_state.quiz_submitted = False
                        st.rerun()
            except:
                pass


# =========================================================
# MAIN APPLICATION
# =========================================================

def main():
    """Main application entry point."""
    # Initialize
    apply_custom_css()
    init_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    render_progress_sidebar()
    
    # Main content
    if st.session_state.current_page == "home" or not st.session_state.session_started:
        render_home_page()
    elif st.session_state.current_page == "checkpoint":
        render_checkpoint_page()
    else:
        render_home_page()
    
    # Footer
    st.markdown("---")
    st.caption("🎓 Autonomous Learning Agent v3.0 • Built with Streamlit, FAISS & Hugging Face")


if __name__ == "__main__":
    main()
