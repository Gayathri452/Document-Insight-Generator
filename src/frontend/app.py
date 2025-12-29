import streamlit as st
import requests
import re
from datetime import datetime
import time

API_URL = "http://127.0.0.1:8000/analyze"

# Page configuration with modern theme
st.set_page_config(
    page_title="Document Insight Generator",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "📄 **Document Insight Generator** - Enterprise-grade RAG analysis"
    }
)

# Modern CSS with harmonious color theory
st.markdown("""
<style>
    /* Color Theory: Analogous + Complementary
       Primary: Deep Blue (#1e40af)
       Secondary: Cyan/Teal (#06B6D4)
       Accent: Coral (#FF6B6B)
       Supporting: Purple (#8B5CF6)
       Neutral: Slate (#64748B)
    */
    
    * {
        margin: 0;
        padding: 0;
    }
    
    .main {
        background: linear-gradient(135deg, #f0f4f8 0%, #d9e8f5 100%);
        min-height: 100vh;
        padding-top: 2rem;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Main container */
    [data-testid="stMainBlockContainer"] {
        background: linear-gradient(to bottom, #ffffff 0%, #f8fafc 100%);
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 20px 60px rgba(30, 64, 175, 0.1);
        margin: 20px;
        border: 1px solid #e0e7ff;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #1e40af 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5em !important;
        font-weight: 800 !important;
        margin-bottom: 10px !important;
    }
    
    h2 {
        color: #1e40af;
        font-size: 1.8em !important;
        font-weight: 700 !important;
        margin: 30px 0 15px 0 !important;
    }
    
    h3 {
        color: #06B6D4;
        font-size: 1.3em !important;
        font-weight: 600 !important;
    }
    
    /* Section headers with vibrant gradient */
    .section-header {
        background: linear-gradient(135deg, #1e40af 0%, #06B6D4 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        font-size: 1.3em;
        font-weight: bold;
        margin: 30px 0 20px 0;
        box-shadow: 0 5px 15px rgba(30, 64, 175, 0.25);
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Cards styling */
    .card {
        background: black;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e7ff;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        margin: 15px 0;
    }
    
    .card:hover {
        box-shadow: 0 15px 40px rgba(30, 64, 175, 0.15);
        transform: translateY(-2px);
    }
    
    /* Metric cards with gradient cycling */
    .metric-card {
        background: linear-gradient(135deg, #1e40af 0%, #06B6D4 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(30, 64, 175, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, transparent, rgba(255, 107, 107, 0.1), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translate(-100%, -100%) rotate(45deg); }
        100% { transform: translate(100%, 100%) rotate(45deg); }
    }
    
    .metric-value {
        font-size: 2em;
        font-weight: 800;
        margin: 10px 0;
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        position: relative;
        z-index: 1;
    }
    
    .metric-label {
        font-size: 0.9em;
        opacity: 0.95;
        color: white;
        position: relative;
        z-index: 1;
    }
    
    /* File uploader styling */
    .stFileUploader {
        border-radius: 15px !important;
        border: 2px dashed #06B6D4 !important;
    }
    
    /* Buttons styling - Cyan to Teal gradient */
    .stButton > button {
        background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(6, 182, 212, 0.3) !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 10px 25px rgba(6, 182, 212, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #e0e7ff;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1e40af !important;
        padding: 12px 20px !important;
        border-radius: 10px 10px 0 0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%) !important;
        color: white !important;
    }
    
    /* Success/Error/Info alerts with custom colors */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
        padding: 15px !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Sidebar with deep blue and cyan accents */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e40af 0%, #1e3a8a 100%);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent;
    }
    
    /* Sidebar text styling */
    [data-testid="stSidebar"] h2 {
        color: #00d4ff !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    [data-testid="stSidebar"] p {
        color: #e0f2fe !important;
    }
    
    [data-testid="stSidebar"] li {
        color: #e0f2fe !important;
    }
    
    [data-testid="stSidebar"] b {
        color: #00d4ff !important;
    }
    
    .sidebar-text {
        color: white;
        font-weight: 500;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        border-radius: 10px !important;
        border: 2px solid #e0e7ff !important;
        background: #f8fafc !important;
        color: #1e40af !important;
        font-weight: 500;
    }
    
    /* Expander */
    .streamlit-expanderContent {
        border: 1px solid #e0e7ff !important;
        border-radius: 10px !important;
        background: #f8fafc !important;
    }
    
    /* Divider */
    hr {
        border: 1px solid #e0e7ff !important;
        margin: 20px 0 !important;
    }
    
    /* Insights markdown */
    .insights-content {
        line-height: 1.8;
        font-size: 1.05em;
        color: #475569;
    }
    
    .insights-content h3 {
        color: #06B6D4;
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: 700;
    }
    
    .insights-content ul, .insights-content ol {
        margin-left: 20px;
        margin-bottom: 10px;
        color: #475569;
    }
    
    .insights-content li {
        margin-bottom: 8px;
        color: #475569;
        border-left: 3px solid #06B6D4;
        padding-left: 10px;
    }
    
    .insights-content strong {
        color: #1e40af;
        font-weight: 700;
    }
    
    .insights-content em {
        color: #FF6B6B;
        font-style: italic;
    }
    
    /* Accent elements in coral */
    .accent-coral {
        color: #FF6B6B;
        font-weight: 600;
    }
    
    .accent-purple {
        color: #8B5CF6;
        font-weight: 600;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #f0f4f8 0%, #e0f2fe 100%);
        color: #1e40af;
        font-size: 0.9em;
        margin-top: 40px;
        font-weight: 600;
        border-radius: 10px;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Custom markdown colors */
    .stMarkdown {
        color: #475569 !important;
    }
    
    /* Better link colors */
    a {
        color: #06B6D4 !important;
        text-decoration: none;
        font-weight: 600;
    }
    
    a:hover {
        color: #FF6B6B !important;
    }
    
    /* Success/Warning/Error colors with theme */
    .stSuccess {
        background: linear-gradient(135deg, #d1fae5 0%, #c6f6d5 100%) !important;
        color: #065f46 !important;
        border: 2px solid #6ee7b7 !important;
        border-left: 4px solid #06B6D4 !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%) !important;
        color: #7f1d1d !important;
        border: 2px solid #fca5a5 !important;
        border-left: 4px solid #FF6B6B !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
        color: #92400e !important;
        border: 2px solid #fcd34d !important;
        border-left: 4px solid #FF6B6B !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #cffafe 0%, #a5f3fc 100%) !important;
        color: #0c4a6e !important;
        border: 2px solid #67e8f9 !important;
        border-left: 4px solid #06B6D4 !important;
    }
    /* FIX: Expander (Pro Tips & How RAG Works) hover color */
    [data-testid="stExpander"] > details > summary:hover {
    background: rgba(6, 182, 212, 0.25) !important; /* cyan tint */
    color: white !important;
    }

/* Ensure text inside expander header stays visible */
    [data-testid="stExpander"] > details > summary span {
    color: white !important;
    font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Header with gradient
st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1>📄 Document Insight Generator</h1>
    <p style='font-size: 1.2em; color: #0052cc; margin: 10px 0; font-weight: 600;'>
        ✨ Transform documents into actionable intelligence with AI-powered RAG analysis
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("<h2 style='color: white; text-align: center;'>ℹ️ Guide</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 20px; color: white;'>
        <b>🚀 Quick Start:</b>
        <p> 1. Upload a PDF or TXT</p>
        <p> 2. Wait for analysis</p>
        <p> 3. Review insights</p>
        <p> 4. Download results</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div style='color: white; text-align: center;'><b>📄</b><br>PDF</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='color: white; text-align: center;'><b>📝</b><br>TXT</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("💡 Pro Tips"):
        st.markdown("""
         - Well-structured documents lead to higher-quality insights 
        - Specific questions outperform generic ones
        - More context improves reasoning accuracy
        """)
    
    with st.expander("🔧 How RAG Works"):
        st.markdown("""
        **Retrieval-Augmented Generation:**
        - Chunks your document
        - Creates semantic embeddings
        - Retrieves relevant sections
        - Generates focused insights
        """)

# Main content area
col_main = st.container()

with col_main:
    # Upload section
    st.markdown('<div class="section-header">📤 Upload Document</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1], gap="large")
    with col2:
        uploaded_file = st.file_uploader(
            "Choose a PDF or TXT file",
            type=["pdf", "txt"],
            help="Max 200MB | Supported: PDF, TXT"
        )
    
    if uploaded_file is not None:
        # File stats
        st.markdown('<div class="section-header">📊 File Information</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📦 Size</div>
                <div class="metric-value">{uploaded_file.size / 1024:.1f}</div>
                <div class="metric-label">KB</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📋 Type</div>
                <div class="metric-value">{uploaded_file.type.split('/')[-1].upper()}</div>
                <div class="metric-label">File</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">📝 Name</div>
                <div class="metric-value" style='font-size: 1.2em;'>{uploaded_file.name[:10]}...</div>
                <div class="metric-label">Document</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⏰ Time</div>
                <div class="metric-value">{datetime.now().strftime('%H:%M')}</div>
                <div class="metric-label">Now</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Analysis section
        st.markdown('<div class="section-header">🔄 Analyzing Document...</div>', unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }

        try:
            # Simulate progress
            for i in range(30):
                progress_bar.progress(i / 100)
                time.sleep(0.01)
            
            status_text.info("⏳ Processing with Gemini AI...")
            
            response = requests.post(API_URL, files=files, timeout=300)
            
            # Complete progress
            for i in range(30, 101):
                progress_bar.progress(i / 100)
                time.sleep(0.01)
            
        except requests.exceptions.RequestException as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"""
            ❌ **Connection Error**
            
            Could not reach the backend server.
            
            **Fix:**
            ```bash
            python -m uvicorn src.backend.main:app --reload --port 8000
            ```
            """)
        else:
            progress_bar.empty()
            status_text.empty()
            
            if response.status_code != 200:
                error_msg = response.json().get("detail", response.text) if response.headers.get("content-type") == "application/json" else response.text
                st.error(f"❌ **Backend Error:** {error_msg}")
            else:
                data = response.json()
                
                # Success animation
                st.balloons()
                st.success("✅ Analysis Complete! Insights Ready", icon="✨")
                
                st.markdown("---")
                
                # Insights section
                st.markdown('<div class="section-header">🧠 Smart Insights</div>', unsafe_allow_html=True)
                
                # Format insights
                insights = data["insights"]
                insights = re.sub(r'^### (\d+\. .+)$', r'### **\1**', insights, flags=re.MULTILINE)
                insights = re.sub(r'^(\d+\. [^\n]+)$', r'**\1**', insights, flags=re.MULTILINE)
                
                # Tabbed interface
                tab1, tab2, tab3, tab4 = st.tabs(["📖 Full Analysis", "💾 Export", "🔍 Summary", "📊 Stats"])
                
                with tab1:
                    st.markdown(f'<div class="insights-content">{insights}</div>', unsafe_allow_html=True)
                
                with tab2:
                    st.markdown("### Download Your Insights")
                    
                    col1, col2, col3 = st.columns(3, gap="medium")
                    
                    with col1:
                        st.download_button(
                            "📥 TXT Format",
                            data=insights,
                            file_name=f"insights_{uploaded_file.name.split('.')[0]}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.download_button(
                            "📥 Markdown",
                            data=insights,
                            file_name=f"insights_{uploaded_file.name.split('.')[0]}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    
                    with col3:
                        st.button(
                            "📋 Copy Text",
                            use_container_width=True,
                            help="Copy insights to clipboard"
                        )
                    
                    st.markdown("---")
                    st.markdown("### Full Text Preview")
                    st.text_area("Insights", value=insights, height=350, disabled=True, label_visibility="collapsed")
                
                with tab3:
                    summary_match = re.search(r'### \*\*1\. Executive Summary\*\*(.*?)(?=###|$)', insights, re.DOTALL)
                    if summary_match:
                        st.markdown("### Executive Summary")
                        st.markdown(summary_match.group(1).strip())
                    else:
                        st.markdown(insights[:500] + "...")
                
                with tab4:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📄 Document", uploaded_file.name)
                        st.metric("📦 Size", f"{uploaded_file.size / 1024:.1f} KB")
                    with col2:
                        st.metric("⏰ Analyzed", datetime.now().strftime("%H:%M:%S"))
                        st.metric("🔍 Sections", "4 (Summary, Insights, Risks, Recommendations)")
                
                st.markdown("---")
                
                # Call to action
                st.markdown('<div class="section-header">🚀 Next Steps</div>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2, gap="medium")
                
                with col1:
                    if st.button("➕ Analyze Another Document", use_container_width=True):
                        st.rerun()
                
                with col2:
                    # st.info("💾 Save these insights for your records", icon="💡")
                    st.download_button(
                        label="💾 Save Insights",
                        data=insights,
                        file_name=f"insights_{uploaded_file.name.split('.')[0]}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # with col3:
                #     st.success("✨ Share with your team", icon="👥")

# Footer
st.markdown("---")
st.markdown("""
<div class='footer'>
    <p><b>Document Insight Generator</b> | Powered by Google Gemini AI & RAG Technology</p>
    <p>© 2025 | Enterprise-Grade Document Analysis</p>
</div>
""", unsafe_allow_html=True)

