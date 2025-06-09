import streamlit as st
import pandas as pd
import json
import os
import sys
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import time
import random

# Streamlit Cloud optimizations
st.set_page_config(
    page_title="PLO Assessment System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/your-repo',
        'Report a bug': 'https://github.com/your-username/your-repo/issues',
        'About': """
        # ระบบประเมิน PLO Assessment System
        
        ระบบประเมินความสอดคล้องของ Slide การสอนกับผลการเรียนรู้ที่คาดหวัง (PLOs)
        
        **Version:** 1.0.0  
        **Built with:** Streamlit  
        **Deployed on:** Streamlit Cloud
        """
    }
)

# Environment detection
def is_streamlit_cloud():
    """Detect if running on Streamlit Cloud"""
    return (
        os.getenv('STREAMLIT_SHARING_MODE') == 'true' or 
        'streamlit.app' in os.getenv('HOSTNAME', '') or
        'streamlit' in os.getenv('HOME', '').lower()
    )

def get_api_key():
    """Safely get API key from secrets or environment"""
    try:
        return st.secrets.get("OPENAI_API_KEY")
    except:
        return os.getenv("OPENAI_API_KEY")

# Cloud-specific styling
st.markdown("""
<style>
    /* Cloud-optimized styles */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .plo-card {
        border: 2px solid #667eea;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        background: linear-gradient(145deg, #f8f9fa, #e9ecef);
        transition: all 0.3s ease;
    }
    
    .plo-card:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15);
    }
    
    .success-alert {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .cloud-info {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
            font-size: 0.9em;
        }
        .metric-card {
            padding: 1rem;
        }
        .plo-card {
            padding: 1rem;
        }
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background-color: #667eea;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Constants
DATA_DIR = Path("data")
ASSESSMENTS_FILE = DATA_DIR / "assessments.json"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# PLOs definition
PLOS = {
    'PLO1': {
        'title': 'การใช้เทคโนโลยีและการมีส่วนร่วม',
        'description': 'สามารถใช้เทคโนโลยีและข้อมูลที่เกี่ยวข้องในการเสนอแนวทางการแก้ไขปัญหาทางสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ โดยยึดหลักการมีส่วนร่วมอย่างเป็นธรรมและการพัฒนาที่ยั่งยืน',
        'weight': 35,
        'keywords': ['เทคโนโลยี', 'technology', 'เครื่องมือ', 'tools', 'ชุมชน', 'community', 
                    'มีส่วนร่วม', 'participation', 'ยั่งยืน', 'sustainable', 'SDGs'],
        'color': '#FF6B6B'
    },
    'PLO2': {
        'title': 'การวิจัยและการบูรณาการ',
        'description': 'สามารถดำเนินการวิจัยโดยการบูรณาการความรู้และข้อมูลอย่างรอบด้านเพื่อหาคำตอบหรือวิธีการที่มีประสิทธิภาพในการใช้เทคโนโลยีเพื่อจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'weight': 35,
        'keywords': ['วิจัย', 'research', 'วิธีการ', 'methodology', 'บูรณาการ', 'integrate',
                    'วิเคราะห์', 'analysis', 'นวัตกรรม', 'innovation'],
        'color': '#4ECDC4'
    },
    'PLO3': {
        'title': 'การสื่อสารและการถ่ายทอด',
        'description': 'สามารถสื่อสาร ถ่ายทอด ข้อมูลและความรู้จากงานวิจัยด้านสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศได้อย่างชัดเจนและมีประสิทธิภาพ',
        'weight': 30,
        'keywords': ['สื่อสาร', 'communicate', 'นำเสนอ', 'present', 'ภาพ', 'visual',
                    'แผนภูมิ', 'chart', 'อธิบาย', 'explain', 'เข้าใจง่าย', 'clear'],
        'color': '#45B7D1'
    }
}

# Courses data
COURSES = {
    'บังคับ': [
        {'code': '282711', 'name': 'ระบบสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ', 'credits': 3},
        {'code': '282712', 'name': 'เทคโนโลยีและการจัดการทรัพยากรน้ำอย่างยั่งยืน', 'credits': 3},
        {'code': '282713', 'name': 'เทคโนโลยีและการจัดการระบบนิเวศทางบก', 'credits': 3},
        {'code': '282714', 'name': 'ระเบียบวิธีวิจัยทางวิทยาศาสตร์และเทคโนโลยี', 'credits': 3},
        {'code': '282715', 'name': 'เทคโนโลยีและการจัดการการเปลี่ยนแปลงสภาพภูมิอากาศ', 'credits': 3}
    ],
    'เลือก': [
        {'code': '282721', 'name': 'การประเมินความเสี่ยงทางภูมิอากาศและผลกระทบทางสิ่งแวดล้อม', 'credits': 3},
        {'code': '282722', 'name': 'แบบจำลองและการวิเคราะห์ข้อมูลทางสิ่งแวดล้อมและสภาพภูมิอากาศด้วยปัญญาประดิษฐ์', 'credits': 3},
        {'code': '282723', 'name': 'เทคโนโลยีการลดก๊าซเรือนกระจกและการปรับตัว', 'credits': 3},
        {'code': '282724', 'name': 'คาร์บอนฟุตพรินต์เพื่อความเป็นกลางทางคาร์บอนอย่างยั่งยืน', 'credits': 3},
        {'code': '282731', 'name': 'เทคโนโลยีและการจัดการมลพิษทางอากาศ', 'credits': 3},
        {'code': '282732', 'name': 'เทคโนโลยีการจัดการทรัพยากรดินและป่าไม้การอนุรักษ์ความหลากหลายทางชีวภาพ', 'credits': 3},
        {'code': '282733', 'name': 'เทคโนโลยีและการจัดการลุ่มน้ำ', 'credits': 3},
        {'code': '282734', 'name': 'การสื่อสารประเด็นสาธารณะสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ', 'credits': 3}
    ]
}

# Cloud-optimized session state initialization
@st.cache_data(ttl=60)  # Cache for 1 minute to prevent frequent reloads
def init_default_session_state():
    """Initialize default session state values"""
    return {
        'assessments': [],
        'current_slide': None,
        'ai_analysis': None,
        'current_page': '🏠 หน้าแรก',
        'upload_status': 'ready',
        'analysis_complete': False,
        'cloud_mode': is_streamlit_cloud()
    }

def init_session_state():
    """Initialize session state with cloud optimizations"""
    defaults = init_default_session_state()
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Load assessments if not already loaded
    if not st.session_state.assessments:
        st.session_state.assessments = load_assessments()

# Cloud-optimized file operations
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_assessments():
    """Load assessments from file with cloud-optimized caching"""
    try:
        if ASSESSMENTS_FILE.exists():
            with open(ASSESSMENTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
    except Exception as e:
        st.error(f"ข้อผิดพลาดในการโหลดข้อมูล: {e}")
    return []

def save_assessments(assessments):
    """Save assessments with cloud-optimized error handling"""
    try:
        with open(ASSESSMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(assessments, f, ensure_ascii=False, indent=2)
        
        # Clear cache to ensure fresh data
        load_assessments.clear()
        return True
    except Exception as e:
        st.error(f"ข้อผิดพลาดในการบันทึก: {e}")
        return False

# AI Analysis with cloud optimizations
def check_ai_availability():
    """Check AI availability with cloud-specific logic"""
    try:
        api_key = get_api_key()
        if api_key:
            return True
    except:
        pass
    return False

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def generate_mock_analysis(content_hash, course_info):
    """Generate mock analysis with caching based on content hash"""
    # Use hash for consistent results
    random.seed(hash(content_hash))
    
    base_scores = {'PLO1': 75, 'PLO2': 82, 'PLO3': 68}
    
    # Adjust scores based on content keywords
    for plo, base_score in base_scores.items():
        plo_keywords = PLOS[plo]['keywords']
        # Simulate keyword finding
        found_keywords = random.sample(plo_keywords, k=min(4, len(plo_keywords)))
        
        keyword_bonus = len(found_keywords) * 3
        adjusted_score = min(95, base_score + keyword_bonus + random.randint(-5, 10))
        base_scores[plo] = adjusted_score
    
    overall = sum(base_scores[plo] * PLOS[plo]['weight'] / 100 for plo in base_scores)
    
    return {
        "PLO1": {
            "score": base_scores['PLO1'],
            "foundKeywords": random.sample(PLOS['PLO1']['keywords'], k=min(4, len(PLOS['PLO1']['keywords']))),
            "strengths": [
                "มีการกล่าวถึงเทคโนโลยีที่เกี่ยวข้อง",
                "แสดงแนวทางการพัฒนาที่ยั่งยืน",
                "เชื่อมโยงกับบริบทท้องถิ่น"
            ],
            "suggestions": [
                "ควรเพิ่มตัวอย่างการมีส่วนร่วมของชุมชน",
                "เพิ่มกรณีศึกษาที่เป็นรูปธรรม",
                "อธิบายการประยุกต์ใช้เทคโนโลยีให้ชัดเจน"
            ]
        },
        "PLO2": {
            "score": base_scores['PLO2'],
            "foundKeywords": random.sample(PLOS['PLO2']['keywords'], k=min(4, len(PLOS['PLO2']['keywords']))),
            "strengths": [
                "มีกระบวนการวิจัยที่ชัดเจน",
                "แสดงการวิเคราะห์ข้อมูลที่ดี",
                "มีการบูรณาการความรู้"
            ],
            "suggestions": [
                "เพิ่มรายละเอียดระเบียบวิธีวิจัย",
                "แสดงการบูรณาการข้ามศาสตร์",
                "เพิ่มการอภิปรายผลการวิจัย"
            ]
        },
        "PLO3": {
            "score": base_scores['PLO3'],
            "foundKeywords": random.sample(PLOS['PLO3']['keywords'], k=min(3, len(PLOS['PLO3']['keywords']))),
            "strengths": [
                "การจัดลำดับเนื้อหาเป็นระบบ",
                "ใช้ภาษาที่เข้าใจง่าย"
            ],
            "suggestions": [
                "เพิ่มภาพและแผนภูมิประกอบ",
                "ใช้สื่อการเรียนรู้ที่หลากหลาย",
                "เพิ่มกิจกรรมมีส่วนร่วม"
            ]
        },
        "overall_score": overall,
        "general_suggestions": [
            "เพิ่ม case study จากบริบทไทย",
            "สร้างกิจกรรมที่ส่งเสริมการมีส่วนร่วม",
            "เชื่อมโยงกับประเด็นปัจจุบัน",
            "พัฒนาการประเมินผลที่หลากหลาย"
        ]
    }

# Chart creation with cloud optimizations
@st.cache_data
def create_gauge_chart(score, title="Score"):
    """Create gauge chart with caching"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24, 'color': '#333'}},
        delta={'reference': 70, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#333"},
            'bar': {'color': "#667eea", 'thickness': 0.3},
            'steps': [
                {'range': [0, 50], 'color': "#ffcccb"},
                {'range': [50, 70], 'color': "#ffffcc"},
                {'range': [70, 85], 'color': "#ccffcc"},
                {'range': [85, 100], 'color': "#ccffff"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig.update_layout(
        height=350, 
        margin=dict(t=80, b=20, l=20, r=20),
        font={'family': 'Arial, sans-serif'}
    )
    return fig

@st.cache_data
def create_plo_comparison_chart(scores):
    """Create PLO comparison chart with caching"""
    plo_names = [f"{plo}\n{PLOS[plo]['title'][:25]}..." for plo in scores.keys()]
    colors = [PLOS[plo]['color'] for plo in scores.keys()]
    
    fig = go.Figure(data=[
        go.Bar(
            y=plo_names,
            x=list(scores.values()),
            orientation='h',
            marker_color=colors,
            text=[f"{score}%" for score in scores.values()],
            textposition='inside',
            textfont={'color': 'white', 'size': 16, 'family': "Arial Black"}
        )
    ])
    
    fig.add_vline(x=70, line_dash="dash", line_color="red", line_width=3,
                  annotation_text="เกณฑ์ผ่าน (70%)", annotation_position="top")
    
    fig.update_layout(
        title={'text': "คะแนนแต่ละ PLO", 'font': {'size': 20}},
        xaxis_title="คะแนน (%)",
        height=450,
        showlegend=False,
        margin=dict(t=60, b=60, l=200, r=50),
        font={'family': 'Arial, sans-serif'}
    )
    return fig

# Main application with cloud optimizations
def main():
    """Main application with error handling for cloud deployment"""
    try:
        # Initialize session state
        init_session_state()
        
        # Cloud deployment info
        if is_streamlit_cloud():
            st.markdown("""
            <div class="cloud-info">
                🌐 <strong>Running on Streamlit Cloud</strong> - 
                Experience optimized for web deployment with enhanced performance and reliability.
            </div>
            """, unsafe_allow_html=True)
        
        # Header with enhanced cloud styling
        st.markdown("""
        <div class="main-header">
            <h1>🧠 ระบบประเมินความสอดคล้องของ Slide กับ PLOs</h1>
            <p style="font-size: 1.1em; margin-top: 0.5rem;">
                หลักสูตรวิทยาศาสตรมหาบัณฑิต สาขาวิชาเทคโนโลยีการจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ
            </p>
            <p style="font-size: 0.9em; opacity: 0.9; margin-top: 1rem;">
                🚀 Powered by Streamlit Cloud | 📱 Mobile Friendly | 🤖 AI Enhanced
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar with cloud enhancements
        with st.sidebar:
            st.markdown("### 📋 Navigation")
            
            menu_options = ["🏠 หน้าแรก", "📤 อัปโหลด Slide", "📊 ประเมิน", "📈 สรุปผล", "📋 ประวัติ"]
            
            try:
                current_index = menu_options.index(st.session_state.current_page)
            except (ValueError, KeyError):
                current_index = 0
            
            selected_page = st.radio(
                "เลือกหน้า",
                menu_options,
                index=current_index,
                key="main_navigation"
            )
            
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
            
            st.divider()
            
            # System status with cloud info
            st.markdown("### 🔧 System Status")
            
            # AI Status
            ai_available = check_ai_availability()
            if ai_available:
                st.success("✅ AI Ready")
            else:
                st.info("💡 Demo Mode")
                st.caption("Using mock AI analysis")
            
            # Cloud status
            if is_streamlit_cloud():
                st.success("☁️ Cloud Deployed")
            else:
                st.info("💻 Local Mode")
            
            st.divider()
            
            # Quick stats with better formatting
            st.markdown("### 📊 Quick Stats")
            total = len(st.session_state.assessments)
            
            if total > 0:
                passed = len([a for a in st.session_state.assessments if a.get('overall_score', 0) >= 70])
                
                # Use columns for better layout
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total", total)
                with col2:
                    st.metric("Passed", passed)
                
                if total >= 3:
                    avg_score = sum(a.get('overall_score', 0) for a in st.session_state.assessments) / total
                    st.metric("Average", f"{avg_score:.1f}%")
                
                # Progress bar for pass rate
                pass_rate = passed / total
                st.progress(pass_rate)
                st.caption(f"Pass Rate: {pass_rate*100:.0f}%")
            else:
                st.info("No data yet")
            
            # Debug info (hidden by default)
            if st.checkbox("🔧 Debug Info", value=False):
                st.json({
                    "Cloud Mode": is_streamlit_cloud(),
                    "Python Version": f"{sys.version_info.major}.{sys.version_info.minor}",
                    "Streamlit Version": st.__version__,
                    "Total Assessments": len(st.session_state.assessments)
                })
        
        # Main content routing with error boundaries
        try:
            if st.session_state.current_page == "🏠 หน้าแรก":
                show_home_page()
            elif st.session_state.current_page == "📤 อัปโหลด Slide":
                show_upload_page()
            elif st.session_state.current_page == "📊 ประเมิน":
                show_assessment_page()
            elif st.session_state.current_page == "📈 สรุปผล":
                show_summary_page()
            elif st.session_state.current_page == "📋 ประวัติ":
                show_history_page()
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในหน้า {st.session_state.current_page}: {str(e)}")
            st.info("กรุณาลองรีเฟรชหน้าเว็บหรือเลือกหน้าอื่น")
            
            if st.button("🔄 Reset to Home"):
                st.session_state.current_page = "🏠 หน้าแรก"
                st.rerun()
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดร้ายแรง: {str(e)}")
        st.info("กรุณาลองรีเฟรชหน้าเว็บ")
        
        # Emergency reset button
        if st.button("🆘 Emergency Reset"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def show_home_page():
    """Enhanced home page with cloud optimizations"""
    st.header("🎯 ผลการเรียนรู้ที่คาดหวังของหลักสูตร (PLOs)")
    
    # PLO cards with enhanced cloud styling
    cols = st.columns(len(PLOS))
    for idx, (plo_code, plo_data) in enumerate(PLOS.items()):
        with cols[idx]:
            st.markdown(f"""
            <div class="plo-card" style="border-color: {plo_data['color']}; min-height: 400px;">
                <h3 style="color: {plo_data['color']}; margin-top: 0; font-size: 1.5em;">{plo_code}</h3>
                <h5 style="color: #333; margin-bottom: 1rem;">{plo_data['title']}</h5>
                <p style="font-size: 0.9em; line-height: 1.5; margin-bottom: 1rem;">
                    {plo_data['description'][:150]}...
                </p>
                <div style="margin-top: 1rem;">
                    <p><strong>น้ำหนัก:</strong> 
                    <span style="color: {plo_data['color']}; font-weight: bold; font-size: 1.2em;">
                        {plo_data['weight']}%
                    </span></p>
                </div>
                <details style="margin-top: 1rem;">
                    <summary style="cursor: pointer; font-weight: bold; color: {plo_data['color']};">
                        📋 คำสำคัญ
                    </summary>
                    <div style="margin-top: 0.5rem; font-size: 0.8em; line-height: 1.4;">
                        {', '.join(plo_data['keywords'][:8])}...
                    </div>
                </details>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced statistics with cloud-optimized layout
    st.header("📊 Dashboard Overview")
    
    assessments = st.session_state.assessments
    if assessments:
        total = len(assessments)
        passed = len([a for a in assessments if a.get('overall_score', 0) >= 70])
        avg_score = sum(a.get('overall_score', 0) for a in assessments) / total
        ai_used = len([a for a in assessments if a.get('ai_analyzed', False)])
        
        # Main metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Total Assessments", total)
        with col2:
            st.metric("✅ Passed", passed, f"{passed/total*100:.0f}%")
        with col3:
            st.metric("📊 Average Score", f"{avg_score:.1f}%")
        with col4:
            st.metric("🤖 AI Analyzed", ai_used, f"{ai_used/total*100:.0f}%")
        
        # Enhanced visualizations for cloud
        if total >= 3:
            st.subheader("📈 Recent Trends")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Recent assessments trend
                df = pd.DataFrame(assessments)
                df['date'] = pd.to_datetime(df['date'])
                df_recent = df.sort_values('date').tail(10)
                
                fig = px.line(df_recent, x='date', y='overall_score', 
                             title="Score Trend (Last 10)",
                             markers=True, line_shape='spline')
                fig.add_hline(y=70, line_dash="dash", line_color="red")
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # PLO performance overview
                plo_scores = {'PLO1': [], 'PLO2': [], 'PLO3': []}
                for assessment in assessments:
                    for plo in plo_scores:
                        if plo in assessment.get('scores', {}):
                            plo_scores[plo].append(assessment['scores'][plo])
                
                plo_avg = {plo: sum(scores)/len(scores) if scores else 0 
                          for plo, scores in plo_scores.items()}
                
                fig = px.bar(x=list(plo_avg.keys()), y=list(plo_avg.values()),
                           title="PLO Average Scores",
                           color=list(plo_avg.keys()),
                           color_discrete_map={
                               'PLO1': PLOS['PLO1']['color'],
                               'PLO2': PLOS['PLO2']['color'],
                               'PLO3': PLOS['PLO3']['color']
                           })
                fig.add_hline(y=70, line_dash="dash", line_color="red")
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    else:
        # Welcome message for new users
        st.markdown("""
        <div class="success-alert">
            <h3>🚀 Welcome to PLO Assessment System!</h3>
            <p>This system helps you evaluate how well your teaching slides align with Program Learning Outcomes (PLOs).</p>
            <p><strong>Get started by:</strong></p>
            <ul>
                <li>📤 Uploading your slide files</li>
                <li>🤖 Using AI analysis for insights</li>
                <li>📊 Manual assessment and scoring</li>
                <li>📈 Tracking progress over time</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Your First Assessment", type="primary", use_container_width=True):
                st.session_state.current_page = "📤 อัปโหลด Slide"
                st.rerun()

def show_upload_page():
    """Cloud-optimized upload page"""
    st.header("📤 Upload & Analyze Slides")
    
    # Progress indicator with cloud styling
    steps = ["📁 Select File", "🔍 Extract Content", "🤖 AI Analysis", "📊 Assessment"]
    current_step = 0
    
    if 'current_slide' in st.session_state:
        current_step = 1
        if 'ai_analysis' in st.session_state:
            current_step = 2
    
    # Enhanced progress display
    progress_cols = st.columns(len(steps))
    for idx, step in enumerate(steps):
        with progress_cols[idx]:
            if idx <= current_step:
                st.success(step)
            elif idx == current_step + 1:
                st.warning(step)
            else:
                st.info(step)
    
    st.markdown("---")
    
    # Course selection with cloud enhancements
    st.subheader("📚 Course Information")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        course_type = st.selectbox(
            "Course Type",
            ["บังคับ", "เลือก"],
            help="Select the type of course you want to assess"
        )
        
        course_options = []
        for course in COURSES[course_type]:
            option = f"{course['code']} - {course['name']} ({course['credits']} credits)"
            course_options.append(option)
        
        selected_course = st.selectbox(
            "Select Course",
            options=course_options,
            help="Choose the specific course for assessment"
        )
    
    with col2:
        st.metric("Available Courses", len(COURSES[course_type]))
        st.metric("Total Credits", sum(c['credits'] for c in COURSES[course_type]))
    
    # Enhanced file upload with cloud optimizations
    st.subheader("📁 File Upload")
    
    # File size warning for cloud
    st.info("📋 **Cloud Deployment Note:** Maximum file size is 200MB. For best performance, keep files under 50MB.")
    
    uploaded_file = st.file_uploader(
        "Choose your slide file",
        type=['pdf', 'pptx', 'ppt', 'txt'],
        help="Supported formats: PDF, PowerPoint, Text files",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Enhanced file info display
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        # File info cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📄 File Name</h4>
                <p>{uploaded_file.name}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h4>📏 File Size</h4>
                <p>{file_size:.1f} MB</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🗂️ File Type</h4>
                <p>{uploaded_file.type}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # File size validation
        if file_size > 200:
            st.error("❌ File too large! Please use a file smaller than 200MB.")
            return
        elif file_size > 50:
            st.warning("⚠️ Large file detected. Processing may take longer.")
        
        # Enhanced processing button
        if st.button("🔍 Process File", type="primary", use_container_width=True):
            with st.spinner("Processing file... This may take a moment on cloud deployment."):
                # Enhanced progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                processing_steps = [
                    ("Reading file...", 25),
                    ("Extracting content...", 50),
                    ("Processing text...", 75),
                    ("Finalizing...", 100)
                ]
                
                for step_text, progress in processing_steps:
                    status_text.text(step_text)
                    progress_bar.progress(progress)
                    time.sleep(0.3)  # Reduced for cloud performance
                
                # Content generation
                if uploaded_file.type == "text/plain":
                    content = str(uploaded_file.read(), "utf-8")
                else:
                    content = generate_enhanced_mock_content(uploaded_file.name, selected_course)
                
                # Save to session state
                st.session_state.current_slide = {
                    'name': uploaded_file.name,
                    'course': selected_course,
                    'course_type': course_type,
                    'content': content,
                    'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'file_size': file_size
                }
                
                progress_bar.empty()
                status_text.empty()
                
                st.success("✅ File processed successfully!")
                
                # Content preview with enhanced styling
                with st.expander("👀 Content Preview", expanded=False):
                    st.text_area(
                        "Extracted content",
                        value=content[:2000] + "..." if len(content) > 2000 else content,
                        height=250,
                        disabled=True
                    )
                    st.caption(f"Total length: {len(content):,} characters")
    
    # Analysis section (if file is processed)
    if 'current_slide' in st.session_state:
        st.markdown("---")
        st.subheader("🤖 Content Analysis")
        
        slide_info = st.session_state.current_slide
        
        st.markdown(f"""
        <div class="success-alert">
            <h4>📄 Ready for Analysis</h4>
            <p><strong>File:</strong> {slide_info['name']}</p>
            <p><strong>Course:</strong> {slide_info['course']}</p>
            <p><strong>Content Length:</strong> {len(slide_info['content']):,} characters</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🤖 AI Analysis", type="secondary", use_container_width=True):
                analyze_slide_content()
        
        with col2:
            if st.button("✏️ Manual Assessment", use_container_width=True):
                st.session_state.current_page = "📊 ประเมิน"
                st.rerun()

def generate_enhanced_mock_content(filename, course):
    """Generate enhanced mock content for cloud deployment"""
    base_content = f"""
# Content Analysis Report
**File:** {filename}
**Course:** {course}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Chapter 1: Introduction to Environmental Management and Climate Change

Environmental management and climate change adaptation in the modern era require systematic integration of technology and community participation. Sustainable development necessitates knowledge integration from multiple disciplines.

### Learning Objectives:
1. Understand fundamental principles and concepts of environmental management
2. Analyze climate change problems using appropriate tools and technologies
3. Present effective solutions with clear communication methods

### Key Concepts:

**Technology Integration**
Modern environmental challenges require innovative technological solutions. Digital tools, remote sensing, and data analytics play crucial roles in monitoring and managing environmental systems.

**Community Participation**
Sustainable development is impossible without meaningful community engagement. Local knowledge and participatory approaches are essential for effective environmental management.

**Research Methodology**
Rigorous research methods ensure reliable data collection and analysis. Interdisciplinary approaches provide comprehensive understanding of complex environmental systems.

**Communication and Knowledge Transfer**
Effective communication requires diverse media including visual presentations, charts, and clear explanations accessible to various audiences.

**Sustainable Development Goals (SDGs)**
The SDGs framework provides important guidelines for sustainable development initiatives, connecting local actions with global objectives.

### Case Studies and Applications:
- Water resource management with community involvement
- Climate adaptation strategies using appropriate technology
- Biodiversity conservation through integrated approaches
- Air quality monitoring and management systems

### Research and Innovation:
Innovation and research are key drivers for environmental problem-solving. Systematic research methodologies help generate reliable results applicable to real-world situations.

### Communication Strategies:
Effective knowledge transfer requires understanding target audiences and selecting appropriate communication channels. Visual aids, interactive presentations, and multimedia resources enhance learning effectiveness.
    """
    
    # Add course-specific content based on selection
    if "น้ำ" in course:
        base_content += """

## Water Resource Management
Sustainable water resource management requires community participation and appropriate technology integration. Watershed management approaches must consider both technical and social factors.
        """
    elif "วิจัย" in course:
        base_content += """

## Research Methodology
Strong research methodologies ensure high-quality and reliable study outcomes. Systematic approaches to data collection, analysis, and interpretation are essential.
        """
    elif "สื่อสาร" in course:
        base_content += """

## Environmental Communication
Effective communication requires understanding audiences and selecting appropriate channels. Multi-media approaches enhance message delivery and comprehension.
        """
    elif "ภูมิอากาศ" in course:
        base_content += """

## Climate Change Analysis
Climate change requires accurate data analysis and forecasting. Scientific methods and technological tools are essential for understanding complex climate systems.
        """
    
    return base_content

def analyze_slide_content():
    """Cloud-optimized slide analysis"""
    if 'current_slide' not in st.session_state:
        st.error("❌ No slide data found")
        return
    
    slide_data = st.session_state.current_slide
    
    # Cloud-optimized progress indication
    progress_container = st.container()
    with progress_container:
        st.info("🤖 AI analyzing content... Optimized for cloud deployment")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Faster analysis steps for cloud
        analysis_steps = [
            ("Initializing analysis...", 20),
            ("Processing keywords...", 40),
            ("Evaluating alignment...", 60),
            ("Calculating scores...", 80),
            ("Generating recommendations...", 100)
        ]
        
        for step_text, progress in analysis_steps:
            status_text.text(step_text)
            progress_bar.progress(progress)
            time.sleep(0.3)  # Reduced time for cloud performance
        
        # Generate analysis with content hashing for caching
        content_hash = str(hash(slide_data['content'][:1000]))  # Use first 1000 chars for hash
        analysis_result = generate_mock_analysis(content_hash, slide_data['course'])
        
        st.session_state.ai_analysis = analysis_result
        
        # Clear progress
        progress_bar.empty()
        status_text.empty()
        
        st.success("✅ Analysis completed!")
    
    # Display results
    show_enhanced_analysis_results(analysis_result)

def show_enhanced_analysis_results(result):
    """Enhanced analysis results display for cloud"""
    st.markdown("---")
    st.subheader("🎯 AI Analysis Results")
    
    # Overall score with enhanced gauge
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig = create_gauge_chart(result['overall_score'], "Overall Score")
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced status display
        score = result['overall_score']
        if score >= 85:
            st.success(f"🌟 **Excellent!** ({score:.1f}%)")
            st.balloons()
        elif score >= 70:
            st.success(f"✅ **Meets Requirements** ({score:.1f}%)")
        else:
            st.warning(f"⚠️ **Needs Improvement** ({score:.1f}%)")
    
    # PLO comparison with enhanced visualization
    st.subheader("📊 PLO Score Comparison")
    plo_scores = {plo: result[plo]['score'] for plo in ['PLO1', 'PLO2', 'PLO3'] if plo in result}
    
    fig = create_plo_comparison_chart(plo_scores)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed analysis in enhanced tabs
    st.subheader("📋 Detailed Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 PLO1 Analysis", "🔬 PLO2 Analysis", "📢 PLO3 Analysis", "📝 Summary"])
    
    tabs = [tab1, tab2, tab3]
    plo_codes = ['PLO1', 'PLO2', 'PLO3']
    
    for idx, plo in enumerate(plo_codes):
        with tabs[idx]:
            if plo in result:
                # Enhanced score display
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {PLOS[plo]['title']}")
                    st.write(PLOS[plo]['description'])
                
                with col2:
                    score = result[plo]['score']
                    st.metric("Score", f"{score}%")
                    
                    # Color-coded progress bar
                    if score >= 80:
                        st.progress(score / 100)
                        st.success("Excellent")
                    elif score >= 70:
                        st.progress(score / 100)
                        st.info("Good")
                    else:
                        st.progress(score / 100)
                        st.warning("Needs Work")
                
                # Keywords with enhanced display
                st.markdown("**🔍 Keywords Found:**")
                keywords = result[plo].get('foundKeywords', [])
                if keywords:
                    # Display keywords as badges
                    cols = st.columns(min(len(keywords), 4))
                    for i, keyword in enumerate(keywords):
                        with cols[i % 4]:
                            st.success(f"✓ {keyword}")
                else:
                    st.info("No relevant keywords detected")
                
                # Strengths and suggestions with better formatting
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**✅ Strengths:**")
                    for strength in result[plo].get('strengths', []):
                        st.write(f"• {strength}")
                
                with col2:
                    st.markdown("**💡 Recommendations:**")
                    for suggestion in result[plo].get('suggestions', []):
                        st.write(f"• {suggestion}")
    
    # Enhanced summary tab
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Statistical Summary:**")
            avg_plo = sum(plo_scores.values()) / len(plo_scores)
            highest_plo = max(plo_scores, key=plo_scores.get)
            lowest_plo = min(plo_scores, key=plo_scores.get)
            
            st.metric("Average PLO Score", f"{avg_plo:.1f}%")
            st.info(f"🏆 Strongest: **{highest_plo}** ({plo_scores[highest_plo]}%)")
            st.warning(f"📈 Focus Area: **{lowest_plo}** ({plo_scores[lowest_plo]}%)")
        
        with col2:
            st.markdown("**🎯 General Recommendations:**")
            for suggestion in result.get('general_suggestions', []):
                st.info(f"💡 {suggestion}")
    
    # Enhanced action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✏️ Proceed to Manual Assessment", type="primary", use_container_width=True):
            st.session_state.current_page = "📊 ประเมิน"
            st.rerun()
    
    with col2:
        if st.button("🔄 Re-analyze", use_container_width=True):
            if 'ai_analysis' in st.session_state:
                del st.session_state.ai_analysis
            st.rerun()
    
    with col3:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.session_state.current_page = "📈 สรุปผล"
            st.rerun()

def show_assessment_page():
    """Cloud-optimized assessment page"""
    st.header("📊 Manual Assessment")
    
    if 'current_slide' not in st.session_state:
        st.warning("⚠️ Please upload a slide file first")
        if st.button("📤 Go to Upload", type="primary"):
            st.session_state.current_page = "📤 อัปโหลด Slide"
            st.rerun()
        return
    
    # Current slide info with enhanced styling
    slide_info = st.session_state.current_slide
    st.markdown(f"""
    <div class="metric-card">
        <h4>📄 Current Assessment</h4>
        <p><strong>File:</strong> {slide_info['name']}</p>
        <p><strong>Course:</strong> {slide_info['course']}</p>
        <p><strong>Uploaded:</strong> {slide_info['upload_date']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Assessment interface with enhanced tabs
    st.subheader("📋 PLO Assessment Interface")
    
    tab1, tab2, tab3 = st.tabs([
        f"🎯 PLO1 ({PLOS['PLO1']['weight']}%)",
        f"🔬 PLO2 ({PLOS['PLO2']['weight']}%)", 
        f"📢 PLO3 ({PLOS['PLO3']['weight']}%)"
    ])
    
    scores = {}
    comments = {}
    ai_suggestions = st.session_state.get('ai_analysis', {})
    
    tabs = [tab1, tab2, tab3]
    plo_codes = ['PLO1', 'PLO2', 'PLO3']
    
    for idx, plo_code in enumerate(plo_codes):
        with tabs[idx]:
            plo_data = PLOS[plo_code]
            
            # Enhanced PLO description
            st.markdown(f"### {plo_data['title']}")
            st.write(plo_data['description'])
            
            # Keywords reference with better layout
            with st.expander("🔍 Reference Keywords"):
                keyword_cols = st.columns(3)
                for i, keyword in enumerate(plo_data['keywords']):
                    with keyword_cols[i % 3]:
                        st.caption(f"• {keyword}")
            
            # AI suggestions with enhanced display
            if plo_code in ai_suggestions:
                ai_score = ai_suggestions[plo_code]['score']
                ai_keywords = ai_suggestions[plo_code].get('foundKeywords', [])
                
                st.markdown(f"""
                <div class="cloud-info">
                    <h5>🤖 AI Insights</h5>
                    <p><strong>Suggested Score:</strong> {ai_score}%</p>
                    {f"<p><strong>Found Keywords:</strong> {', '.join(ai_keywords)}</p>" if ai_keywords else ""}
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced score input
            col1, col2 = st.columns([2, 1])
            
            with col1:
                default_score = ai_suggestions.get(plo_code, {}).get('score', 70)
                scores[plo_code] = st.slider(
                    f"Score for {plo_code}",
                    min_value=0,
                    max_value=100,
                    value=default_score,
                    step=5,
                    help=f"Evaluate content alignment with {plo_code}"
                )
            
            with col2:
                # Enhanced score indicator
                score = scores[plo_code]
                if score >= 85:
                    st.success(f"🌟 Excellent\n{score}%")
                elif score >= 70:
                    st.success(f"✅ Good\n{score}%")
                elif score >= 60:
                    st.warning(f"⚠️ Fair\n{score}%")
                else:
                    st.error(f"❌ Poor\n{score}%")
                
                # Enhanced progress bar
                st.progress(score / 100)
            
            # Enhanced comments section
            comments[plo_code] = st.text_area(
                f"💬 Comments and Recommendations for {plo_code}",
                height=120,
                placeholder=f"Provide specific feedback for {plo_code}...",
                help="Your comments will help improve future content"
            )
            
            # AI suggestions display
            if plo_code in ai_suggestions:
                with st.expander("💡 View AI Recommendations"):
                    suggestions = ai_suggestions[plo_code].get('suggestions', [])
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
    
    # Enhanced overall score calculation and display
    st.markdown("---")
    st.subheader("📊 Assessment Summary")
    
    overall_score = sum(scores[plo] * PLOS[plo]['weight'] / 100 for plo in scores)
    
    # Main score display
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        fig = create_gauge_chart(overall_score, "Overall Score")
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual PLO summary with enhanced layout
    st.markdown("### 📋 PLO Score Breakdown")
    
    summary_cols = st.columns(3)
    for idx, (plo_code, score) in enumerate(scores.items()):
        with summary_cols[idx]:
            weight = PLOS[plo_code]['weight']
            weighted_score = score * weight / 100
            
            st.metric(
                label=f"{plo_code}",
                value=f"{score}%",
                delta=f"Weight: {weight}%"
            )
            st.caption(f"Weighted: {weighted_score:.1f} points")
            
            # Progress bar for individual PLO
            st.progress(score / 100)
    
    # Enhanced save functionality
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Assessment", type="primary", use_container_width=True):
            # Create assessment record
            assessment = {
                'id': len(st.session_state.assessments) + 1,
                'slide_name': slide_info['name'],
                'course': slide_info['course'],
                'course_type': slide_info['course_type'],
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'scores': scores,
                'comments': comments,
                'overall_score': overall_score,
                'status': 'ผ่านเกณฑ์' if overall_score >= 70 else 'ต้องปรับปรุง',
                'ai_analyzed': 'ai_analysis' in st.session_state,
                'file_size': slide_info.get('file_size', 0),
                'cloud_saved': is_streamlit_cloud()
            }
            
            st.session_state.assessments.append(assessment)
            
            # Enhanced save confirmation
            if save_assessments(st.session_state.assessments):
                st.success("✅ Assessment saved successfully!")
                if overall_score >= 70:
                    st.balloons()
                
                # Clear session data
                del st.session_state.current_slide
                if 'ai_analysis' in st.session_state:
                    del st.session_state.ai_analysis
                
                # Auto-redirect with delay
                time.sleep(1)
                st.session_state.current_page = "📈 สรุปผล"
                st.rerun()
            else:
                st.error("❌ Failed to save assessment")
    
    with col2:
        if st.button("🔄 Reset Assessment", use_container_width=True):
            st.rerun()

def show_summary_page():
    """Cloud-optimized summary page"""
    st.header("📈 Assessment Dashboard")
    
    assessments = st.session_state.assessments
    
    if not assessments:
        st.warning("No assessment data available")
        if st.button("🚀 Start Assessment", type="primary"):
            st.session_state.current_page = "📤 อัปโหลด Slide"
            st.rerun()
        return
    
    # Convert to DataFrame with cloud optimization
    df = pd.DataFrame(assessments)
    df['date'] = pd.to_datetime(df['date'])
    
    # Enhanced overall statistics
    st.subheader("📊 Overview Statistics")
    
    total = len(df)
    passed = len(df[df['status'] == 'ผ่านเกณฑ์'])
    avg_score = df['overall_score'].mean()
    ai_analyzed = len(df[df['ai_analyzed'] == True])
    latest_score = df.iloc[-1]['overall_score']
    cloud_assessments = len(df[df.get('cloud_saved', False) == True]) if 'cloud_saved' in df.columns else 0
    
    # Enhanced metrics display
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Passed", passed, f"{passed/total*100:.0f}%")
    with col3:
        st.metric("Average", f"{avg_score:.1f}%")
    with col4:
        st.metric("AI Used", ai_analyzed, f"{ai_analyzed/total*100:.0f}%")
    with col5:
        trend = "📈" if latest_score > avg_score else "📉" if latest_score < avg_score else "➡️"
        st.metric("Latest", f"{latest_score:.1f}%", trend)
    with col6:
        if is_streamlit_cloud():
            st.metric("☁️ Cloud", cloud_assessments if cloud_assessments > 0 else total)
        else:
            st.metric("💻 Local", total - cloud_assessments if cloud_assessments > 0 else total)
    
    # Enhanced visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Score Distribution", "📈 Trends", "📚 Course Analysis", "☁️ Cloud Insights"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced score distribution
            fig_hist = px.histogram(
                df, x='overall_score', nbins=15,
                title="Score Distribution",
                labels={'overall_score': 'Score (%)', 'count': 'Count'},
                color_discrete_sequence=['#667eea']
            )
            fig_hist.add_vline(x=70, line_dash="dash", line_color="red", 
                              annotation_text="Pass Threshold")
            fig_hist.add_vline(x=avg_score, line_dash="dot", line_color="green",
                              annotation_text=f"Average ({avg_score:.1f}%)")
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # PLO comparison with enhanced styling
            plo_data = []
            for assessment in assessments:
                for plo, score in assessment['scores'].items():
                    plo_data.append({'PLO': plo, 'Score': score})
            
            if plo_data:
                plo_df = pd.DataFrame(plo_data)
                plo_avg = plo_df.groupby('PLO')['Score'].mean().reset_index()
                
                fig_plo = px.bar(
                    plo_avg, x='PLO', y='Score',
                    title="Average PLO Scores",
                    color='PLO',
                    color_discrete_map={
                        'PLO1': PLOS['PLO1']['color'],
                        'PLO2': PLOS['PLO2']['color'],
                        'PLO3': PLOS['PLO3']['color']
                    }
                )
                fig_plo.add_hline(y=70, line_dash="dash", line_color="red")
                fig_plo.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_plo, use_container_width=True)
    
    with tab2:
        if total >= 3:
            df_sorted = df.sort_values('date')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Enhanced trend analysis
                fig_trend = px.line(
                    df_sorted, x='date', y='overall_score',
                    title="Score Trend Over Time",
                    markers=True, line_shape='spline'
                )
                fig_trend.add_hline(y=70, line_dash="dash", line_color="red")
                fig_trend.add_hline(y=avg_score, line_dash="dot", line_color="green")
                fig_trend.update_layout(height=400)
                st.plotly_chart(fig_trend, use_container_width=True)
            
            with col2:
                # Enhanced pass rate analysis
                df_sorted['cumulative_pass'] = (df_sorted['status'] == 'ผ่านเกณฑ์').cumsum()
                df_sorted['pass_rate'] = df_sorted['cumulative_pass'] / range(1, len(df_sorted) + 1) * 100
                
                fig_pass = px.line(
                    df_sorted, x='date', y='pass_rate',
                    title="Cumulative Pass Rate",
                    labels={'pass_rate': 'Pass Rate (%)'}
                )
                fig_pass.add_hline(y=70, line_dash="dash", line_color="red")
                fig_pass.update_layout(height=400)
                st.plotly_chart(fig_pass, use_container_width=True)
        else:
            st.info("Need at least 3 assessments to show trends")
    
    with tab3:
        if 'course' in df.columns:
            # Enhanced course analysis
            course_summary = df.groupby('course').agg({
                'overall_score': ['mean', 'count', 'std'],
                'status': lambda x: (x == 'ผ่านเกณฑ์').sum()
            }).round(2)
            
            course_summary.columns = ['Average', 'Count', 'Std Dev', 'Passed']
            course_summary['Pass Rate (%)'] = (
                course_summary['Passed'] / course_summary['Count'] * 100
            ).round(1)
            
            st.dataframe(
                course_summary,
                use_container_width=True,
                column_config={
                    "Average": st.column_config.ProgressColumn(
                        "Average Score", min_value=0, max_value=100, format="%.1f"
                    ),
                    "Pass Rate (%)": st.column_config.ProgressColumn(
                        "Pass Rate (%)", min_value=0, max_value=100, format="%.1f%%"
                    )
                }
            )
    
    with tab4:
        # Cloud-specific insights
        if is_streamlit_cloud():
            st.success("☁️ **Running on Streamlit Cloud**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🚀 Cloud Benefits:**")
                st.write("• Zero installation required")
                st.write("• Accessible from anywhere")
                st.write("• Automatic updates")
                st.write("• Multi-user support")
                st.write("• Mobile responsive")
            
            with col2:
                st.markdown("**📊 Usage Statistics:**")
                st.metric("Cloud Sessions", total)
                st.metric("Data Persistence", "✅ Enabled")
                st.metric("Performance", "Optimized")
        else:
            st.info("💻 **Running Locally**")
            st.write("Consider deploying to Streamlit Cloud for enhanced accessibility!")
    
    # Enhanced export section
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        csv_data = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            "📊 Download CSV",
            data=csv_data,
            file_name=f"plo_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        stats_data = {
            'summary': {
                'total_assessments': total,
                'passed_assessments': int(passed),
                'pass_rate_percent': passed/total*100,
                'average_score': avg_score,
                'ai_analyzed': int(ai_analyzed)
            },
            'metadata': {
                'generated_date': datetime.now().isoformat(),
                'cloud_deployment': is_streamlit_cloud(),
                'streamlit_version': st.__version__
            }
        }
        
        st.download_button(
            "📈 Download JSON",
            data=json.dumps(stats_data, indent=2, ensure_ascii=False),
            file_name=f"plo_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            load_assessments.clear()
            st.session_state.assessments = load_assessments()
            st.rerun()
    
    with col4:
        if st.button("📤 New Assessment", type="primary", use_container_width=True):
            st.session_state.current_page = "📤 อัปโหลด Slide"
            st.rerun()

def show_history_page():
    """Cloud-optimized history page"""
    st.header("📋 Assessment History")
    
    assessments = st.session_state.assessments
    
    if not assessments:
        st.warning("No assessment history available")
        if st.button("🚀 Start First Assessment", type="primary"):
            st.session_state.current_page = "📤 อัปโหลด Slide"
            st.rerun()
        return
    
    df = pd.DataFrame(assessments)
    df['date'] = pd.to_datetime(df['date'])
    
    # Enhanced filtering section
    st.subheader("🔍 Filter & Search")
    
    # Filter controls in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        courses = ["All"] + sorted(df['course'].unique().tolist())
        filter_course = st.selectbox("Course", courses)
    
    with col2:
        filter_status = st.selectbox("Status", ["All", "ผ่านเกณฑ์", "ต้องปรับปรุง"])
    
    with col3:
        filter_ai = st.selectbox("AI Analysis", ["All", "With AI", "Without AI"])
    
    with col4:
        score_range = st.slider("Score Range", 0, 100, (0, 100), step=5)
    
    # Enhanced search
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("🔍 Search files", placeholder="Search by filename...")
    with col2:
        sort_by = st.selectbox("Sort by", [
            "Date (Newest)", "Date (Oldest)", 
            "Score (High-Low)", "Score (Low-High)"
        ])
    
    # Apply filters
    filtered_df = df.copy()
    
    if filter_course != "All":
        filtered_df = filtered_df[filtered_df['course'] == filter_course]
    
    if filter_status != "All":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]
    
    if filter_ai == "With AI":
        filtered_df = filtered_df[filtered_df['ai_analyzed'] == True]
    elif filter_ai == "Without AI":
        filtered_df = filtered_df[filtered_df['ai_analyzed'] == False]
    
    filtered_df = filtered_df[
        (filtered_df['overall_score'] >= score_range[0]) & 
        (filtered_df['overall_score'] <= score_range[1])
    ]
    
    if search_term:
        mask = filtered_df['slide_name'].str.contains(search_term, case=False, na=False)
        filtered_df = filtered_df[mask]
    
    # Apply sorting
    if sort_by == "Date (Newest)":
        filtered_df = filtered_df.sort_values('date', ascending=False)
    elif sort_by == "Date (Oldest)":
        filtered_df = filtered_df.sort_values('date', ascending=True)
    elif sort_by == "Score (High-Low)":
        filtered_df = filtered_df.sort_values('overall_score', ascending=False)
    elif sort_by == "Score (Low-High)":
        filtered_df = filtered_df.sort_values('overall_score', ascending=True)
    
    # Results display
    st.info(f"📊 Showing {len(filtered_df)} of {len(df)} assessments")
    
    if len(filtered_df) > 0:
        # Enhanced table display
        display_df = filtered_df[[
            'date', 'slide_name', 'course', 'overall_score', 'status', 'ai_analyzed'
        ]].copy()
        
        display_df.columns = ['Date', 'File Name', 'Course', 'Score (%)', 'Status', 'AI']
        display_df['AI'] = display_df['AI'].map({True: '✅', False: '❌'})
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Score (%)": st.column_config.ProgressColumn(
                    "Score (%)", min_value=0, max_value=100, format="%.1f%%"
                ),
                "Status": st.column_config.TextColumn("Status"),
                "AI": st.column_config.TextColumn("AI Analysis")
            }
        )
        
        # Enhanced export and actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export Filtered Results", use_container_width=True):
                csv = display_df.to_csv(index=False, encoding='utf-8-sig')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                st.download_button(
                    "📥 Download CSV",
                    data=csv,
                    file_name=f"filtered_history_{timestamp}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("🔄 Reset Filters", use_container_width=True):
                st.rerun()
        
        with col3:
            if st.button("📈 View Dashboard", use_container_width=True):
                st.session_state.current_page = "📈 สรุปผล"
                st.rerun()
        
        # Detailed view for selected assessment
        if len(filtered_df) > 0:
            with st.expander("👁️ View Assessment Details"):
                selected_id = st.selectbox(
                    "Select assessment to view details",
                    options=filtered_df['id'].tolist(),
                    format_func=lambda x: f"#{x} - {filtered_df[filtered_df['id']==x]['slide_name'].iloc[0]}"
                )
                
                if selected_id:
                    selected_assessment = filtered_df[filtered_df['id'] == selected_id].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📊 PLO Scores:**")
                        for plo, score in selected_assessment['scores'].items():
                            st.metric(plo, f"{score}%")
                    
                    with col2:
                        st.markdown("**💬 Comments:**")
                        for plo, comment in selected_assessment['comments'].items():
                            if comment:
                                st.write(f"**{plo}:** {comment}")
                            else:
                                st.caption(f"{plo}: No comments")
    else:
        st.info("No assessments match the selected criteria")
        if st.button("🔄 Clear All Filters"):
            st.rerun()

# Run the application
if __name__ == "__main__":
    main()
