"""
Autonomous Learning Agent Dashboard
A modern, premium dashboard-style UI for the learning workflow
With Advanced Features: Quiz, Flashcards, Export, Chat, and more!
"""
import streamlit as st
import sys
import os
from pathlib import Path
import time
from datetime import datetime
import json
import base64
from io import BytesIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import create_learning_graph

# Optional imports for advanced features
try:
    from langchain_openai import ChatOpenAI
    from langchain_groq import ChatGroq
    from dotenv import load_dotenv
    load_dotenv()
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Learning Agent | AI-Powered Study Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# PREMIUM CSS STYLING - Modern SaaS Dashboard
# =========================================================
st.markdown("""
<style>
    /* ===== GLOBAL STYLES ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
    }
    
    .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
    
    [data-testid="stSidebar"] label {
        color: #b0b0b0 !important;
        font-weight: 500;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stTextArea textarea {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        color: #fff;
        padding: 12px;
    }
    
    [data-testid="stSidebar"] .stTextInput input:focus,
    [data-testid="stSidebar"] .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    
    /* ===== HEADER STYLES ===== */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
    }
    
    /* ===== CARD STYLES ===== */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        color: #1e293b !important;
    }
    
    .card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .card p, .card h1, .card h2, .card h3, .card strong {
        color: #1e293b !important;
    }
    
    /* ===== KPI CARDS ===== */
    .kpi-card {
        background: white;
        padding: 1.25rem 1.5rem;
        border-radius: 14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        text-align: center;
    }
    
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.25rem 0;
    }
    
    /* ===== PROGRESS TRACKER ===== */
    .progress-step {
        flex: 1;
        text-align: center;
        padding: 1rem 0.5rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .step-complete {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .step-current {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .step-pending {
        background: #e2e8f0;
        color: #64748b;
    }
    
    /* ===== SUMMARY BOX ===== */
    .summary-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #86efac;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        color: #166534 !important;
    }
    
    .summary-box p, .summary-box h1, .summary-box h2, .summary-box h3, .summary-box li, .summary-box strong, .summary-box span {
        color: #166534 !important;
    }
    
    .summary-title {
        color: #166534;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* ===== QUIZ STYLES ===== */
    .quiz-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid #f59e0b;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .flashcard {
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        border: 1px solid #6366f1;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #312e81 !important;
    }
    
    .flashcard h3 {
        color: #312e81 !important;
    }
    
    /* ===== CHAT STYLES ===== */
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        color: #1e293b !important;
    }
    
    .user-message {
        background: #e0e7ff;
        margin-left: 2rem;
        color: #312e81 !important;
    }
    
    .assistant-message {
        background: #f0fdf4;
        margin-right: 2rem;
        color: #166534 !important;
    }
    
    /* ===== BUTTON STYLES ===== */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
    }
    
    /* ===== TAB STYLES ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
    }
    
    /* ===== METRICS ===== */
    [data-testid="stMetric"] {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    [data-testid="stMetricLabel"] {
        color: #64748b !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #1e293b !important;
    }
    
    /* ===== MAIN CONTENT TEXT ===== */
    .main h1, .main h2, .main h3 {
        color: #1e293b !important;
    }
    
    .main p, .main li {
        color: #334155 !important;
    }
    
    /* ===== SIDEBAR BRANDING ===== */
    .sidebar-brand {
        padding: 1.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 1.5rem;
    }
    
    .sidebar-brand h2 {
        color: white;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0;
    }
    
    .sidebar-brand p {
        color: rgba(255,255,255,0.6);
        font-size: 0.8rem;
        margin: 0.25rem 0 0 0;
    }
    
    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }
    
    /* ===== DIVIDER ===== */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 2rem 0;
    }
    
    /* ===== HIDE STREAMLIT BRANDING ===== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================
if 'workflow_result' not in st.session_state:
    st.session_state.workflow_result = None
if 'execution_logs' not in st.session_state:
    st.session_state.execution_logs = []
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'feynman_explanation' not in st.session_state:
    st.session_state.feynman_explanation = None

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_config(key, default=None):
    """Get configuration from Streamlit secrets or environment variables.
    
    This allows the app to work both locally (with .env) and on Streamlit Cloud (with secrets).
    """
    # First try Streamlit secrets (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    
    # Fall back to environment variable (for local development)
    return os.getenv(key, default)

def get_llm():
    """Get LLM instance based on environment configuration"""
    provider = get_config("MODEL_PROVIDER", "groq").lower()
    
    if provider == "groq":
        api_key = get_config("GROQ_API_KEY")
        if not api_key:
            return None
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=api_key,
            temperature=0.7
        )
    elif provider == "openai":
        api_key = get_config("OPENAI_API_KEY")
        if not api_key:
            return None
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            temperature=0.7
        )
    return None


def log_step(message, status="info"):
    """Add a log entry with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.execution_logs.append({
        'time': timestamp,
        'message': message,
        'status': status
    })

def run_workflow(checkpoint, user_notes):
    """Execute the learning workflow with real-time updates"""
    log_step("Starting workflow execution", "info")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        log_step("Initializing state", "info")
        status_text.text("🔄 Initializing learning state...")
        progress_bar.progress(10)
        time.sleep(0.3)
        
        state = create_initial_state(
            checkpoint=checkpoint,
            user_notes=user_notes
        )
        
        log_step("Creating workflow graph", "info")
        status_text.text("📊 Building workflow graph...")
        progress_bar.progress(25)
        time.sleep(0.3)
        
        graph = create_learning_graph()
        
        log_step("Executing workflow nodes", "info")
        status_text.text("⚙️ Processing your learning materials...")
        progress_bar.progress(50)
        
        result = graph.invoke(state)
        
        progress_bar.progress(100)
        status_text.text("✅ Workflow completed successfully!")
        
        if result.get('error'):
            log_step(f"Completed with warning: {result['error']}", "warning")
        else:
            log_step("Workflow completed successfully", "success")
        
        return result
        
    except Exception as e:
        log_step(f"Error: {str(e)}", "error")
        st.error(f"❌ Error: {str(e)}")
        return None

def render_progress_tracker(current_stage):
    """Render the workflow progress tracker"""
    stages = [
        ("initialized", "Init", "🚀"),
        ("checkpoint_defined", "Checkpoint", "📌"),
        ("context_gathered", "Gathered", "📚"),
        ("context_validated", "Validated", "✓"),
        ("context_processed", "Processed", "✨")
    ]
    
    stage_order = [s[0] for s in stages]
    current_idx = stage_order.index(current_stage) if current_stage in stage_order else 0
    
    cols = st.columns(len(stages))
    for idx, (stage_id, label, icon) in enumerate(stages):
        with cols[idx]:
            if idx < current_idx:
                st.markdown(f'<div class="progress-step step-complete">{icon}<br>{label}</div>', unsafe_allow_html=True)
            elif idx == current_idx:
                st.markdown(f'<div class="progress-step step-current">{icon}<br>{label}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="progress-step step-pending">{icon}<br>{label}</div>', unsafe_allow_html=True)

# =========================================================
# FEATURE: EXPORT FUNCTIONS
# =========================================================

def export_to_markdown(topic, objectives, summary):
    """Export summary to Markdown format"""
    md_content = f"""# Learning Summary: {topic}

## 📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 🎯 Learning Objectives
"""
    for i, obj in enumerate(objectives, 1):
        md_content += f"{i}. {obj}\n"
    
    md_content += f"""
## 📝 Summary

{summary}

---
*Generated by Autonomous Learning Agent*
"""
    return md_content

def get_download_link(content, filename, file_type="text/markdown"):
    """Generate download link for content"""
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:{file_type};base64,{b64}" download="{filename}" style="text-decoration:none;"><button style="background:linear-gradient(135deg, #10b981 0%, #059669 100%);color:white;border:none;padding:10px 20px;border-radius:8px;cursor:pointer;font-weight:600;">📥 Download {filename}</button></a>'

# =========================================================
# FEATURE: QUIZ GENERATOR
# =========================================================

def generate_quiz(topic, summary, num_questions=5):
    """Generate quiz questions from summary"""
    if not LLM_AVAILABLE:
        return []
    
    try:
        llm = get_llm()
        if not llm:
            return []
        
        prompt = f"""Based on this learning summary about "{topic}", generate {num_questions} multiple-choice quiz questions.

Summary:
{summary[:2000]}

Return ONLY a JSON array with this exact format:
[
    {{
        "question": "Question text here?",
        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
        "correct": "A",
        "explanation": "Brief explanation why this is correct"
    }}
]

Generate {num_questions} questions that test understanding of key concepts."""

        response = llm.invoke(prompt)
        content = response.content
        
        # Extract JSON from response
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end > start:
            questions = json.loads(content[start:end])
            return questions
    except Exception as e:
        st.error(f"Quiz generation error: {e}")
    return []

# =========================================================
# FEATURE: FLASHCARD GENERATOR
# =========================================================

def generate_flashcards(topic, summary, num_cards=5):
    """Generate flashcards from summary"""
    if not LLM_AVAILABLE:
        return []
    
    try:
        llm = get_llm()
        if not llm:
            return []
        
        prompt = f"""Based on this learning summary about "{topic}", create {num_cards} study flashcards.

Summary:
{summary[:2000]}

Return ONLY a JSON array with this exact format:
[
    {{
        "front": "Term or Question",
        "back": "Definition or Answer"
    }}
]

Create {num_cards} flashcards covering the most important concepts."""

        response = llm.invoke(prompt)
        content = response.content
        
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end > start:
            cards = json.loads(content[start:end])
            return cards
    except Exception as e:
        st.error(f"Flashcard generation error: {e}")
    return []

# =========================================================
# FEATURE: FEYNMAN EXPLANATION
# =========================================================

def generate_feynman_explanation(topic, summary):
    """Generate simple Feynman-style explanation"""
    if not LLM_AVAILABLE:
        return None
    
    try:
        llm = get_llm()
        if not llm:
            return None
        
        prompt = f"""You are Richard Feynman, the famous physicist known for explaining complex topics simply.

Explain "{topic}" to a 12-year-old student using:
- Simple everyday language
- Real-world analogies and examples
- No jargon or technical terms
- Engaging, conversational tone

Context from study materials:
{summary[:1500]}

Start your explanation with an engaging hook and make it fun to read!"""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        st.error(f"Feynman explanation error: {e}")
    return None

# =========================================================
# FEATURE: CHAT WITH SUMMARY
# =========================================================

def chat_with_summary(question, summary, chat_history):
    """Answer questions about the summary"""
    if not LLM_AVAILABLE:
        return "Chat feature requires LLM configuration."
    
    try:
        llm = get_llm()
        if not llm:
            return "LLM not configured."
        
        history_text = "\n".join([f"User: {h['user']}\nAssistant: {h['assistant']}" for h in chat_history[-3:]])
        
        prompt = f"""You are a helpful study assistant. Answer questions based on this learning summary.

Summary:
{summary[:2000]}

Previous conversation:
{history_text}

User's question: {question}

Provide a helpful, accurate answer based on the summary. If the answer isn't in the summary, say so."""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {e}"

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown('''
        <div class="sidebar-brand">
            <h2>🎓 Learning Agent</h2>
            <p>AI-Powered Study Assistant</p>
        </div>
    ''', unsafe_allow_html=True)
    
    # Navigation
    st.markdown("#### 📍 Navigation")
    page = st.radio(
        "Select View",
        ["🏠 Dashboard", "🎯 Quiz & Flashcards", "💬 Chat", "📊 Analytics", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Learning Checkpoint Input
    st.markdown("#### 📝 Learning Checkpoint")
    
    topic = st.text_input(
        "Topic",
        value="",
        placeholder="e.g., Machine Learning Basics",
        help="What topic do you want to learn?"
    )
    
    objectives_text = st.text_area(
        "Learning Objectives",
        value="",
        placeholder="Enter objectives (one per line)",
        height=100,
        help="What do you want to achieve?"
    )
    
    # Summary Length Control
    summary_length = st.select_slider(
        "Summary Length",
        options=["Short", "Medium", "Detailed"],
        value="Medium",
        help="Control the length of generated summary"
    )
    
    user_notes = st.text_area(
        "Your Notes (Optional)",
        value="",
        placeholder="Paste your study notes here...",
        height=120,
        help="Add any existing notes or materials"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ About", expanded=False):
        st.markdown("""
        **Autonomous Learning Agent v2.0**
        
        Features:
        - 📚 Smart Context Gathering
        - 🎯 Quiz Generator
        - 📝 Flashcard Creator
        - 🧠 Feynman Explanations
        - 💬 Chat with Summary
        - 📥 Export to Markdown
        
        *Powered by LangGraph & Groq*
        """)

# =========================================================
# MAIN CONTENT
# =========================================================

# Header
st.markdown('''
    <div class="main-header">
        <h1>🎓 Autonomous Learning Agent</h1>
        <p>Transform any topic into a structured learning experience with AI-powered features.</p>
    </div>
''', unsafe_allow_html=True)

# Parse objectives
objectives = [obj.strip() for obj in objectives_text.split('\n') if obj.strip()]

# =========================================================
# PAGE: DASHBOARD
# =========================================================
if page == "🏠 Dashboard":
    
    # Quick Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Topic</div>
                <div class="kpi-value" style="font-size: 1rem;">{topic if topic else "Not Set"}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Objectives</div>
                <div class="kpi-value">{len(objectives)}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        contexts_count = len(st.session_state.workflow_result.get('gathered_contexts', [])) if st.session_state.workflow_result else 0
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Sources</div>
                <div class="kpi-value">{contexts_count}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        status = "Ready" if not st.session_state.workflow_result else "Complete"
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Status</div>
                <div class="kpi-value" style="font-size: 1rem;">{status}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Action Section
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("### 🚀 Workflow Execution")
        
        if topic and objectives:
            if st.button("▶️ Run Learning Workflow", use_container_width=True, type="primary"):
                st.session_state.execution_logs = []
                st.session_state.quiz_questions = []
                st.session_state.flashcards = []
                st.session_state.feynman_explanation = None
                st.session_state.chat_history = []
                
                checkpoint = Checkpoint(
                    topic=topic,
                    objectives=objectives
                )
                
                with st.spinner(""):
                    result = run_workflow(checkpoint, user_notes if user_notes else None)
                    st.session_state.workflow_result = result
                
                if result and not result.get('error'):
                    st.balloons()
        else:
            st.info("👈 Enter a **Topic** and at least one **Learning Objective** in the sidebar to get started.")
    
    with col_right:
        st.markdown("### 📋 Checkpoint Preview")
        if topic:
            st.markdown(f"**Topic:** {topic}")
            if objectives:
                st.markdown("**Objectives:**")
                for i, obj in enumerate(objectives, 1):
                    st.markdown(f"  {i}. {obj}")
        else:
            st.markdown("*No checkpoint defined yet*")
    
    # Results Section
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Progress Tracker
        st.markdown("### 📊 Workflow Progress")
        render_progress_tracker(result.get('current_stage', 'initialized'))
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Stage", result.get('current_stage', 'N/A').replace('_', ' ').title())
        with col2:
            st.metric("Contexts", len(result.get('gathered_contexts', [])))
        with col3:
            st.metric("Valid", "✅ Yes" if result.get('context_valid') else "❌ No")
        with col4:
            st.metric("Retries", result.get('retry_count', 0))
        
        # Error display
        if result.get('error'):
            st.error(f"⚠️ **Warning:** {result['error']}")
        
        # Summary Section
        if result.get('summary'):
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### 📝 Learning Summary")
            with col2:
                # Export Button
                md_content = export_to_markdown(topic, objectives, result['summary'])
                st.markdown(get_download_link(md_content, f"{topic.replace(' ', '_')}_summary.md"), unsafe_allow_html=True)
            
            st.markdown(f'''<div class="summary-box">{result['summary']}</div>''', unsafe_allow_html=True)
            
            # Feynman Explanation Button
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🧠 Generate Feynman Explanation", use_container_width=True):
                with st.spinner("Creating simple explanation..."):
                    explanation = generate_feynman_explanation(topic, result['summary'])
                    st.session_state.feynman_explanation = explanation
            
            if st.session_state.feynman_explanation:
                st.markdown("### 🧠 Feynman Explanation (ELI12)")
                st.markdown(f'''<div class="card">{st.session_state.feynman_explanation}</div>''', unsafe_allow_html=True)

# =========================================================
# PAGE: QUIZ & FLASHCARDS
# =========================================================
elif page == "🎯 Quiz & Flashcards":
    st.markdown("### 🎯 Quiz & Flashcards")
    
    if st.session_state.workflow_result and st.session_state.workflow_result.get('summary'):
        summary = st.session_state.workflow_result['summary']
        
        tab1, tab2 = st.tabs(["📝 Quiz", "📇 Flashcards"])
        
        with tab1:
            st.markdown("#### 📝 Quiz Generator")
            
            num_questions = st.slider("Number of Questions", 3, 10, 5)
            
            if st.button("🎲 Generate Quiz", use_container_width=True):
                with st.spinner("Generating quiz questions..."):
                    questions = generate_quiz(topic, summary, num_questions)
                    st.session_state.quiz_questions = questions
            
            if st.session_state.quiz_questions:
                st.markdown("---")
                for i, q in enumerate(st.session_state.quiz_questions, 1):
                    with st.expander(f"Question {i}: {q['question'][:50]}...", expanded=True):
                        st.markdown(f"**{q['question']}**")
                        
                        answer = st.radio(
                            "Select your answer:",
                            q['options'],
                            key=f"quiz_{i}"
                        )
                        
                        if st.button(f"Check Answer", key=f"check_{i}"):
                            selected_letter = answer[0] if answer else ""
                            if selected_letter == q['correct']:
                                st.success(f"✅ Correct! {q['explanation']}")
                            else:
                                st.error(f"❌ Incorrect. The correct answer is {q['correct']}. {q['explanation']}")
        
        with tab2:
            st.markdown("#### 📇 Flashcard Generator")
            
            num_cards = st.slider("Number of Flashcards", 3, 10, 5)
            
            if st.button("🎴 Generate Flashcards", use_container_width=True):
                with st.spinner("Creating flashcards..."):
                    cards = generate_flashcards(topic, summary, num_cards)
                    st.session_state.flashcards = cards
            
            if st.session_state.flashcards:
                st.markdown("---")
                
                if 'current_card' not in st.session_state:
                    st.session_state.current_card = 0
                if 'show_answer' not in st.session_state:
                    st.session_state.show_answer = False
                
                card = st.session_state.flashcards[st.session_state.current_card]
                
                st.markdown(f"**Card {st.session_state.current_card + 1} of {len(st.session_state.flashcards)}**")
                
                st.markdown(f'''
                    <div class="flashcard">
                        <h3>{card['back'] if st.session_state.show_answer else card['front']}</h3>
                    </div>
                ''', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("⬅️ Previous"):
                        st.session_state.current_card = max(0, st.session_state.current_card - 1)
                        st.session_state.show_answer = False
                        st.rerun()
                with col2:
                    if st.button("🔄 Flip Card"):
                        st.session_state.show_answer = not st.session_state.show_answer
                        st.rerun()
                with col3:
                    if st.button("➡️ Next"):
                        st.session_state.current_card = min(len(st.session_state.flashcards)-1, st.session_state.current_card + 1)
                        st.session_state.show_answer = False
                        st.rerun()
    else:
        st.info("📚 Run the learning workflow first to generate quiz and flashcards!")

# =========================================================
# PAGE: CHAT
# =========================================================
elif page == "💬 Chat":
    st.markdown("### 💬 Chat with Your Summary")
    
    if st.session_state.workflow_result and st.session_state.workflow_result.get('summary'):
        summary = st.session_state.workflow_result['summary']
        
        # Display chat history
        for chat in st.session_state.chat_history:
            st.markdown(f'''<div class="chat-message user-message"><strong>You:</strong> {chat['user']}</div>''', unsafe_allow_html=True)
            st.markdown(f'''<div class="chat-message assistant-message"><strong>Assistant:</strong> {chat['assistant']}</div>''', unsafe_allow_html=True)
        
        # Chat input
        user_question = st.text_input("Ask a question about the summary:", placeholder="e.g., What are the key concepts?")
        
        if st.button("📤 Send", use_container_width=True):
            if user_question:
                with st.spinner("Thinking..."):
                    response = chat_with_summary(user_question, summary, st.session_state.chat_history)
                    st.session_state.chat_history.append({
                        'user': user_question,
                        'assistant': response
                    })
                    st.rerun()
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.info("📚 Run the learning workflow first to start chatting!")

# =========================================================
# PAGE: ANALYTICS
# =========================================================
elif page == "📊 Analytics":
    st.markdown("### 📊 Analytics & Insights")
    
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result
        contexts = result.get('gathered_contexts', [])
        
        if contexts:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📚 Context Sources")
                user_notes_count = sum(1 for c in contexts if c.source == "user_notes")
                web_count = len(contexts) - user_notes_count
                
                st.markdown(f"""
                    <div class="card">
                        <p><strong>📝 From Your Notes:</strong> {user_notes_count}</p>
                        <p><strong>🌐 From Web Search:</strong> {web_count}</p>
                        <p><strong>📊 Total Sources:</strong> {len(contexts)}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 📈 Relevance Scores")
                avg_score = sum(c.relevance_score or 0 for c in contexts) / len(contexts) if contexts else 0
                st.markdown(f"""
                    <div class="card">
                        <p><strong>Average Relevance:</strong> {avg_score:.0%}</p>
                        <p><strong>Quality Rating:</strong> {'⭐' * int(avg_score * 5)}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("#### 📄 Source Details")
            for i, ctx in enumerate(contexts, 1):
                with st.expander(f"Source {i}: {ctx.source.replace('_', ' ').title()} ({ctx.relevance_score:.0%})"):
                    st.text(ctx.content[:500] + "..." if len(ctx.content) > 500 else ctx.content)
        else:
            st.info("Run the workflow to see analytics.")
    else:
        st.info("No data available yet. Run the workflow from the Dashboard.")

# =========================================================
# PAGE: SETTINGS
# =========================================================
elif page == "⚙️ Settings":
    st.markdown("### ⚙️ Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔧 Workflow Settings")
        with st.expander("Advanced Options", expanded=True):
            st.slider("Understanding Threshold", 0.0, 1.0, 0.55, 0.05)
            st.slider("Max Retries", 1, 5, 3)
            st.slider("Chunk Size", 100, 1000, 500, 50)
        
        st.markdown("#### 🤖 Model Info")
        provider = os.getenv("MODEL_PROVIDER", "Not Set")
        st.info(f"**Current Provider:** {provider.upper()}")
    
    with col2:
        st.markdown("#### 📋 Execution Logs")
        if st.session_state.execution_logs:
            for log in reversed(st.session_state.execution_logs[-10:]):
                icon = {'info': 'ℹ️', 'success': '✅', 'error': '❌', 'warning': '⚠️'}.get(log['status'], 'ℹ️')
                st.text(f"{icon} {log['time']} - {log['message']}")
        else:
            st.info("No logs yet.")

# =========================================================
# FOOTER
# =========================================================
st.markdown('''
    <div class="footer">
        <p><strong>Autonomous Learning Agent v2.0</strong> • AI-Powered Study Assistant</p>
        <p>Built with ❤️ using Streamlit, LangGraph & Groq</p>
        <p style="font-size: 0.75rem; color: #94a3b8;">Features: Quiz • Flashcards • Feynman • Chat • Export</p>
    </div>
''', unsafe_allow_html=True)
