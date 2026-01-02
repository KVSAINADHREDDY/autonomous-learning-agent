"""
Autonomous Learning Agent Dashboard
A modern, premium dashboard-style UI for the learning workflow
Designed with SaaS-inspired aesthetics (Notion, Linear style)
"""
import streamlit as st
import sys
from pathlib import Path
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.checkpoint import Checkpoint
from src.models.state import create_initial_state
from src.graph.learning_graph import create_learning_graph

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
    }
    
    .card:hover {
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .card-header {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .card-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .card-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
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
    
    /* ===== STATUS BADGES ===== */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-pending {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .status-info {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
    }
    
    /* ===== PROGRESS TRACKER ===== */
    .progress-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        gap: 0.5rem;
    }
    
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
        animation: pulse 2s infinite;
    }
    
    .step-pending {
        background: #e2e8f0;
        color: #64748b;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* ===== SUMMARY BOX ===== */
    .summary-box {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #86efac;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .summary-title {
        color: #166534;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
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
    
    /* ===== EXPANDER STYLES ===== */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        font-weight: 600;
    }
    
    /* ===== METRICS ===== */
    [data-testid="stMetric"] {
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
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
        display: flex;
        align-items: center;
        gap: 0.5rem;
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
    
    .footer a {
        color: #6366f1;
        text-decoration: none;
        font-weight: 500;
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

# =========================================================
# HELPER FUNCTIONS
# =========================================================
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
                st.markdown(f'''
                    <div class="progress-step step-complete">
                        {icon}<br>{label}
                    </div>
                ''', unsafe_allow_html=True)
            elif idx == current_idx:
                st.markdown(f'''
                    <div class="progress-step step-current">
                        {icon}<br>{label}
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div class="progress-step step-pending">
                        {icon}<br>{label}
                    </div>
                ''', unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    # Brand Header
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
        ["🏠 Dashboard", "📊 Analytics", "⚙️ Settings"],
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
        placeholder="Enter objectives (one per line):\n• Understand key concepts\n• Learn practical applications",
        height=120,
        help="What do you want to achieve?"
    )
    
    user_notes = st.text_area(
        "Your Notes (Optional)",
        value="",
        placeholder="Paste your study notes or materials here...",
        height=150,
        help="Add any existing notes or materials"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Project Info
    with st.expander("ℹ️ About", expanded=False):
        st.markdown("""
        **Autonomous Learning Agent**
        
        An AI-powered system that:
        - 📚 Gathers learning materials
        - ✅ Validates content relevance
        - 📝 Generates smart summaries
        - 🎯 Tracks your objectives
        
        *Powered by LangGraph & Groq*
        """)

# =========================================================
# MAIN CONTENT
# =========================================================

# Header
st.markdown('''
    <div class="main-header">
        <h1>🎓 Autonomous Learning Agent</h1>
        <p>Transform any topic into a structured learning experience with AI-powered context gathering and intelligent summarization.</p>
    </div>
''', unsafe_allow_html=True)

# Parse objectives
objectives = [obj.strip() for obj in objectives_text.split('\n') if obj.strip()]

# Content based on navigation
if page == "🏠 Dashboard":
    
    # Quick Stats Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('''
            <div class="kpi-card">
                <div class="kpi-label">Topic</div>
                <div class="kpi-value" style="font-size: 1rem;">''' + (topic if topic else "Not Set") + '''</div>
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
        status_color = "#6366f1" if status == "Ready" else "#10b981"
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-label">Status</div>
                <div class="kpi-value" style="color: {status_color}; font-size: 1rem;">{status}</div>
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
            st.markdown('''
                <div class="summary-box">
                    <div class="summary-title">📝 Learning Summary</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(result['summary'])

elif page == "📊 Analytics":
    st.markdown("### 📊 Analytics & Insights")
    
    if st.session_state.workflow_result:
        result = st.session_state.workflow_result
        contexts = result.get('gathered_contexts', [])
        
        if contexts:
            # Source Analysis
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
            
            # Detailed Context View
            st.markdown("#### 📄 Source Details")
            for i, ctx in enumerate(contexts, 1):
                with st.expander(f"Source {i}: {ctx.source.replace('_', ' ').title()} ({ctx.relevance_score:.0%} relevance)"):
                    st.markdown(f"**Content Preview:**")
                    st.text(ctx.content[:500] + "..." if len(ctx.content) > 500 else ctx.content)
        else:
            st.info("Run the workflow to see analytics.")
    else:
        st.info("No data available yet. Run the workflow from the Dashboard.")

elif page == "⚙️ Settings":
    st.markdown("### ⚙️ Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔧 Workflow Settings")
        with st.expander("Advanced Options", expanded=True):
            st.slider("Understanding Threshold", 0.0, 1.0, 0.55, 0.05)
            st.slider("Max Retries", 1, 5, 3)
            st.slider("Chunk Size", 100, 1000, 500, 50)
    
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
        <p><strong>Autonomous Learning Agent</strong> • AI-Powered Study Assistant</p>
        <p>Built with ❤️ using Streamlit, LangGraph & Groq</p>
        <p style="font-size: 0.75rem; color: #94a3b8;">Version 2.0 • © 2025</p>
    </div>
''', unsafe_allow_html=True)
