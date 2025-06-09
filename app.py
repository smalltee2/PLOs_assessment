import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Import custom modules with error handling
try:
    from utils.ai_analyzer import AIAnalyzer
    AI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import AI analyzer: {e}")
    AI_AVAILABLE = False

try:
    from utils.pdf_extractor import PDFExtractor
    PDF_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import PDF extractor: {e}")
    PDF_AVAILABLE = False

# Load environment variables
load_dotenv()

# Constants
DATA_DIR = Path("data")
ASSESSMENTS_FILE = DATA_DIR / "assessments.json"

# Page config
st.set_page_config(
    page_title="ระบบประเมิน Slide กับ PLOs (AI-Powered)",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PLOs definition with enhanced structure
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

# Enhanced courses structure
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

# Initialize session state
def init_session_state():
    if 'assessments' not in st.session_state:
        st.session_state.assessments = load_assessments()
    if 'current_assessment' not in st.session_state:
        st.session_state.current_assessment = None
    if 'page' not in st.session_state:
        st.session_state.page = "🏠 หน้าแรก"

# Enhanced file operations
def load_assessments():
    """Load assessments with error handling"""
    try:
        if ASSESSMENTS_FILE.exists():
            with open(ASSESSMENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading assessments: {e}")
    return []

def save_assessments(assessments):
    """Save assessments with error handling"""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        with open(ASSESSMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(assessments, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving assessments: {e}")
        return False

# Initialize AI Analyzer with caching
@st.cache_resource
def init_ai_analyzer():
    if AI_AVAILABLE:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return AIAnalyzer(
                provider=os.getenv('AI_PROVIDER', 'openai'),
                api_key=api_key
            )
    return None

# Enhanced UI components
def create_score_gauge(score, title="Score"):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig.update_layout(height=300)
    return fig

def create_plo_score_chart(scores):
    """Create horizontal bar chart for PLO scores"""
    plo_names = [f"{plo}\n{PLOS[plo]['title']}" for plo in scores.keys()]
    colors = [PLOS[plo]['color'] for plo in scores.keys()]
    
    fig = go.Figure(data=[
        go.Bar(
            y=plo_names,
            x=list(scores.values()),
            orientation='h',
            marker_color=colors,
            text=[f"{score}%" for score in scores.values()],
            textposition='inside'
        )
    ])
    
    fig.add_vline(x=70, line_dash="dash", line_color="red", 
                  annotation_text="เกณฑ์ผ่าน (70%)")
    
    fig.update_layout(
        title="คะแนนแต่ละ PLO",
        xaxis_title="คะแนน (%)",
        height=400,
        showlegend=False
    )
    return fig

# Main application
def main():
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-card {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    .warning-card {
        background-color: #fff3cd;
        border-color: #ffeaa7;
        color: #856404;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🧠 ระบบประเมินความสอดคล้องของ Slide กับ PLOs")
    st.caption("หลักสูตรวิทยาศาสตรมหาบัณฑิต สาขาวิชาเทคโนโลยีการจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 เมนูหลัก")
        
        # Navigation with session state
        menu_options = ["🏠 หน้าแรก", "📤 อัปโหลด Slide", "📊 ประเมิน", "📈 สรุปผล", "📋 ประวัติ"]
        
        if 'page' in st.session_state:
            try:
                current_index = menu_options.index(st.session_state.page)
            except ValueError:
                current_index = 0
        else:
            current_index = 0
            
        menu = st.radio(
            "เลือกฟังก์ชัน",
            menu_options,
            index=current_index
        )
        
        # Update session state if menu changed
        if menu != st.session_state.get('page'):
            st.session_state.page = menu
        
        st.divider()
        
        # Enhanced AI Status
        st.header("🤖 AI Status")
        ai_enabled = AI_AVAILABLE and os.getenv('OPENAI_API_KEY') is not None
        if ai_enabled:
            st.success("✅ AI พร้อมใช้งาน")
            st.caption(f"Provider: {os.getenv('AI_PROVIDER', 'openai')}")
        else:
            st.warning("⚠️ AI ไม่พร้อมใช้งาน")
            if not AI_AVAILABLE:
                st.caption("ติดตั้ง: pip install openai")
            else:
                st.caption("กรุณาตั้งค่า API Key ใน .env")
        
        # Quick stats
        st.divider()
        st.header("📊 สถิติด่วน")
        total_assessments = len(st.session_state.assessments)
        st.metric("การประเมินทั้งหมด", total_assessments)
        
        if total_assessments > 0:
            passed = len([a for a in st.session_state.assessments if a.get('overall_score', 0) >= 70])
            st.metric("ผ่านเกณฑ์", f"{passed}/{total_assessments}")
    
    # Main content routing
    if st.session_state.page == "🏠 หน้าแรก":
        show_home()
    elif st.session_state.page == "📤 อัปโหลด Slide":
        show_upload()
    elif st.session_state.page == "📊 ประเมิน":
        show_assessment()
    elif st.session_state.page == "📈 สรุปผล":
        show_summary()
    elif st.session_state.page == "📋 ประวัติ":
        show_history()

def show_home():
    """Enhanced home page with better layout"""
    
    # PLO Overview
    st.header("🎯 ผลการเรียนรู้ที่คาดหวังของหลักสูตร (PLOs)")
    
    # PLO Cards in columns
    cols = st.columns(len(PLOS))
    for idx, (plo_code, plo_data) in enumerate(PLOS.items()):
        with cols[idx]:
            with st.container():
                st.markdown(f"""
                <div style="border: 2px solid {plo_data['color']}; padding: 1rem; border-radius: 0.5rem; height: 300px;">
                    <h3 style="color: {plo_data['color']};">{plo_code}</h3>
                    <h5>{plo_data['title']}</h5>
                    <p style="font-size: 0.9em;">{plo_data['description'][:150]}...</p>
                    <p><strong>น้ำหนัก:</strong> {plo_data['weight']}%</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced Statistics
    st.header("📊 สถิติภาพรวม")
    
    total_assessments = len(st.session_state.assessments)
    if total_assessments > 0:
        passed = len([a for a in st.session_state.assessments if a.get('overall_score', 0) >= 70])
        avg_score = sum(a.get('overall_score', 0) for a in st.session_state.assessments) / total_assessments
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("จำนวนการประเมินทั้งหมด", total_assessments)
        with col2:
            st.metric("ผ่านเกณฑ์", passed, f"{passed/total_assessments*100:.0f}%")
        with col3:
            st.metric("ต้องปรับปรุง", total_assessments - passed)
        with col4:
            st.metric("คะแนนเฉลี่ย", f"{avg_score:.1f}%")
        
        # Quick visualization
        if total_assessments >= 3:
            st.subheader("📈 แนวโน้มคะแนน")
            df = pd.DataFrame(st.session_state.assessments)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            fig = px.line(df, x='date', y='overall_score', 
                         title="แนวโน้มคะแนนตามเวลา",
                         labels={'date': 'วันที่', 'overall_score': 'คะแนนรวม (%)'})
            fig.add_hline(y=70, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลการประเมิน เริ่มต้นโดยการอัปโหลด Slide")
        if st.button("🚀 เริ่มต้นใช้งาน", type="primary"):
            st.session_state.page = "📤 อัปโหลด Slide"
            st.rerun()

def show_upload():
    """Enhanced upload page with better UX"""
    st.header("📤 อัปโหลด Slide การสอน")
    
    # Progress indicator
    progress_steps = ["📁 เลือกไฟล์", "🔍 แปลงข้อความ", "🤖 วิเคราะห์ AI", "📊 ประเมิน"]
    current_step = 0
    
    if 'current_slide' in st.session_state:
        current_step = 2 if 'ai_analysis' not in st.session_state else 3
    
    # Show progress
    st.subheader("📋 ขั้นตอนการประเมิน")
    cols = st.columns(len(progress_steps))
    for idx, step in enumerate(progress_steps):
        with cols[idx]:
            if idx <= current_step:
                st.success(step)
            else:
                st.info(step)
    
    st.markdown("---")
    
    # Course selection with enhanced layout
    col1, col2 = st.columns([3, 1])
    with col1:
        course_type = st.selectbox("ประเภทวิชา", ["บังคับ", "เลือก"])
        
        # Format course options better
        course_options = []
        for course in COURSES[course_type]:
            option = f"{course['code']} - {course['name']} ({course['credits']} หน่วยกิต)"
            course_options.append(option)
            
        selected_course = st.selectbox(
            "เลือกรายวิชา",
            options=course_options
        )
    
    with col2:
        st.metric("จำนวนรายวิชา", len(COURSES[course_type]))
    
    # Enhanced file upload
    st.subheader("📁 อัปโหลดไฟล์")
    uploaded_file = st.file_uploader(
        "เลือกไฟล์ Slide",
        type=['pdf', 'pptx', 'ppt'],
        help="รองรับไฟล์ PDF, PPT, PPTX ขนาดไม่เกิน 200MB"
    )
    
    if uploaded_file is not None:
        # File info
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.success(f"✅ อัปโหลดไฟล์: {uploaded_file.name} ({file_size:.1f} MB)")
        
        # Extract text button with better UX
        if st.button("🔍 แปลงไฟล์เป็นข้อความ", type="primary", use_container_width=True):
            with st.spinner("กำลังแปลงไฟล์... กรุณารอสักครู่"):
                try:
                    # Simulate processing time for better UX
                    import time
                    time.sleep(1)
                    
                    if uploaded_file.type == "application/pdf" and PDF_AVAILABLE:
                        extractor = PDFExtractor()
                        text = extractor.extract_text(uploaded_file)
                    else:
                        # Enhanced fallback
                        text = generate_mock_content(uploaded_file.name, selected_course)
                    
                    # Save to session
                    st.session_state.current_slide = {
                        'name': uploaded_file.name,
                        'course': selected_course,
                        'course_type': course_type,
                        'content': text,
                        'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'file_size': file_size
                    }
                    
                    st.success("✅ แปลงไฟล์สำเร็จ!")
                    
                    # Show content preview with expandable section
                    with st.expander("👀 ดูตัวอย่างเนื้อหาที่แปลงได้", expanded=False):
                        st.text_area(
                            "เนื้อหาตัวอย่าง",
                            value=text[:2000] + "..." if len(text) > 2000 else text,
                            height=300,
                            disabled=True
                        )
                        st.caption(f"ความยาวทั้งหมด: {len(text)} ตัวอักษร")
                            
                except Exception as e:
                    st.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
        
        # Show AI analysis option if slide is ready
        if 'current_slide' in st.session_state:
            st.markdown("---")
            st.success("📄 ไฟล์พร้อมสำหรับการวิเคราะห์")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🤖 วิเคราะห์ด้วย AI", type="secondary", use_container_width=True):
                    analyze_with_ai()
            with col2:
                if st.button("✏️ ประเมินด้วยตนเอง", use_container_width=True):
                    st.session_state.page = "📊 ประเมิน"
                    st.rerun()

def generate_mock_content(filename, course):
    """Generate more realistic mock content based on filename and course"""
    base_content = f"""
    เนื้อหาจาก {filename}
    รายวิชา: {course}
    
    บทที่ 1: บทนำ
    การจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศเป็นประเด็นสำคัญในปัจจุบัน 
    เทคโนโลยีใหม่ๆ สามารถช่วยในการแก้ไขปัญหาเหล่านี้ได้อย่างมีประสิทธิภาพ
    
    การมีส่วนร่วมของชุมชนถือเป็นกุญแจสำคัญในการพัฒนาที่ยั่งยืน
    การวิจัยและการบูรณาการข้อมูลจะช่วยให้เราเข้าใจปัญหาได้ดีขึ้น
    
    การสื่อสารและการนำเสนอข้อมูลอย่างชัดเจนจะช่วยให้ผู้รับฟังเข้าใจได้ง่าย
    การใช้ภาพและแผนภูมิประกอบการอธิบายจะเพิ่มประสิทธิภาพในการสื่อสาร
    
    SDGs (Sustainable Development Goals) เป็นเป้าหมายที่เราควรมุ่งสู่
    นวัตกรรมและการวิเคราะห์ข้อมูลจะช่วยขับเคลื่อนการพัฒนา
    """
    
    # Add course-specific content
    if "น้ำ" in course:
        base_content += "\n\nการจัดการทรัพยากรน้ำอย่างยั่งยืนต้องอาศัยเทคโนโลยีและการมีส่วนร่วมของชุมชน"
    elif "วิจัย" in course:
        base_content += "\n\nระเบียบวิธีวิจัยที่เหมาะสมจะช่วยให้การศึกษาได้ผลลัพธ์ที่น่าเชื่อถือ"
    elif "สื่อสาร" in course:
        base_content += "\n\nการสื่อสารที่มีประสิทธิภาพต้องเข้าใจกลุ่มเป้าหมายและใช้ช่องทางที่เหมาะสม"
    
    return base_content

def analyze_with_ai():
    """Enhanced AI analysis with better UX and error handling"""
    
    if 'current_slide' not in st.session_state:
        st.warning("❌ กรุณาอัปโหลด Slide ก่อน")
        return
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    with col2:
        st.info("🤖 AI กำลังประมวลผล...")
    
    try:
        # Simulate AI processing steps
        steps = [
            ("กำลังเตรียมข้อมูล...", 20),
            ("วิเคราะห์เนื้อหา...", 40), 
            ("ตรวจสอบคำสำคัญ...", 60),
            ("คำนวณคะแนน...", 80),
            ("สร้างคำแนะนำ...", 100)
        ]
        
        for step_text, progress in steps:
            status_text.text(step_text)
            progress_bar.progress(progress)
            import time
            time.sleep(0.5)  # Simulate processing time
        
        # Get AI analysis
        ai_analyzer = init_ai_analyzer()
        if ai_analyzer and os.getenv('OPENAI_API_KEY'):
            result = ai_analyzer.analyze_slide(
                st.session_state.current_slide['content'],
                PLOS
            )
        else:
            # Enhanced mock analysis
            result = generate_enhanced_mock_analysis()
        
        st.session_state.ai_analysis = result
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        col2.empty()
        
        # Show results immediately
        show_ai_results(result)
        
    except Exception as e:
        st.error(f"⚠️ เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}")
        # Fallback to mock data
        result = generate_enhanced_mock_analysis()
        st.session_state.ai_analysis = result
        show_ai_results(result)

def generate_enhanced_mock_analysis():
    """Generate more realistic mock analysis"""
    import random
    
    # Generate realistic scores with some randomness
    base_scores = {'PLO1': 75, 'PLO2': 82, 'PLO3': 68}
    scores = {plo: max(50, min(95, score + random.randint(-10, 10))) 
              for plo, score in base_scores.items()}
    
    overall = sum(scores[plo] * PLOS[plo]['weight'] / 100 for plo in scores)
    
    return {
        "PLO1": {
            "score": scores['PLO1'],
            "foundKeywords": ["เทคโนโลยี", "ชุมชน", "ยั่งยืน", "SDGs"],
            "strengths": [
                "มีการกล่าวถึงเทคโนโลยีที่เกี่ยวข้องอย่างชัดเจน",
                "แสดงแนวทางการพัฒนาที่ยั่งยืน",
                "เชื่อมโยงกับ SDGs ได้ดี"
            ],
            "suggestions": [
                "ควรเพิ่มตัวอย่างการมีส่วนร่วมของชุมชนที่เป็นรูปธรรม",
                "เพิ่มกรณีศึกษาจากบริบทท้องถิ่น",
                "อธิบายการใช้เครื่องมือเทคโนโลยีให้ละเอียดขึ้น"
            ]
        },
        "PLO2": {
            "score": scores['PLO2'],
            "foundKeywords": ["วิจัย", "วิเคราะห์", "บูรณาการ", "นวัตกรรม"],
            "strengths": [
                "มีกระบวนการวิจัยที่ชัดเจนและเป็นระบบ",
                "แสดงการวิเคราะห์ข้อมูลที่ดี",
                "มีการบูรณาการความรู้จากหลายแหล่ง"
            ],
            "suggestions": [
                "เพิ่มรายละเอียดระเบียบวิธีวิจัยให้ชัดเจนขึ้น",
                "แสดงตัวอย่างการบูรณาการข้ามศาสตร์",
                "เพิ่มการอภิปรายผลการวิจัย"
            ]
        },
        "PLO3": {
            "score": scores['PLO3'],
            "foundKeywords": ["สื่อสาร", "นำเสนอ", "อธิบาย"],
            "strengths": [
                "การจัดลำดับเนื้อหาเป็นระบบและเข้าใจง่าย",
                "มีการอธิบายแนวคิดได้ชัดเจน"
            ],
            "suggestions": [
                "เพิ่มภาพและแผนภูมิประกอบการอธิบาย",
                "ใช้ภาษาที่เข้าใจง่ายและเหมาะกับกลุ่มเป้าหมาย",
                "เพิ่มกิจกรรมการมีส่วนร่วมในการนำเสนอ",
                "สร้างสื่อการเรียนรู้ที่หลากหลาย"
            ]
        },
        "overall_score": overall,
        "general_suggestions": [
            "เพิ่ม case study จากบริบทไทยและอาเซียน",
            "สร้างกิจกรรมที่ส่งเสริมการมีส่วนร่วมของผู้เรียน",
            "เชื่อมโยงเนื้อหากับประเด็นปัจจุบัน",
            "เพิ่มการประเมินผลการเรียนรู้ที่หลากหลาย"
        ]
    }

def show_ai_results(result):
    """Display AI analysis results with enhanced visualization"""
    
    st.markdown("---")
    st.subheader("🎯 ผลการวิเคราะห์จาก AI")
    
    # Overall score with enhanced gauge
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        fig = create_score_gauge(result['overall_score'], "คะแนนรวม")
        st.plotly_chart(fig, use_container_width=True)
        
        # Status badge
        if result['overall_score'] >= 80:
            st.success(f"🌟 ดีเยี่ยม ({result['overall_score']:.1f}%)")
        elif result['overall_score'] >= 70:
            st.success(f"✅ ผ่านเกณฑ์ ({result['overall_score']:.1f}%)")
        else:
            st.warning(f"⚠️ ต้องปรับปรุง ({result['overall_score']:.1f}%)")
    
    # PLO scores with enhanced chart
    st.subheader("📊 คะแนนแต่ละ PLO")
    
    plo_scores = {plo: result[plo]['score'] for plo in ['PLO1', 'PLO2', 'PLO3'] if plo in result}
    fig = create_plo_score_chart(plo_scores)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed analysis in tabs
    st.subheader("📋 รายละเอียดการวิเคราะห์")
    
    tab1, tab2, tab3, tab4 = st.tabs(["PLO1", "PLO2", "PLO3", "สรุปรวม"])
    
    for idx, plo in enumerate(['PLO1', 'PLO2', 'PLO3']):
        with [tab1, tab2, tab3][idx]:
            if plo in result:
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**คะแนน: {result[plo]['score']}%**")
                    st.progress(result[plo]['score'] / 100)
                    
                    st.markdown("**🔍 คำสำคัญที่พบ:**")
                    keywords = result[plo].get('foundKeywords', [])
                    if keywords:
                        for kw in keywords:
                            st.badge(kw, type="secondary")
                    else:
                        st.caption("ไม่พบคำสำคัญ")
                
                with col2:
                    st.markdown("**✅ จุดเด่น:**")
                    for strength in result[plo].get('strengths', []):
                        st.write(f"• {strength}")
                
                st.markdown("**💡 คำแนะนำการปรับปรุง:**")
                for suggestion in result[plo].get('suggestions', []):
                    st.info(f"💡 {suggestion}")
    
    with tab4:
        st.markdown("**📝 คำแนะนำทั่วไป:**")
        for suggestion in result.get('general_suggestions', []):
            st.info(f"🎯 {suggestion}")
        
        # Summary statistics
        st.markdown("**📊 สถิติสรุป:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_plo = sum(plo_scores.values()) / len(plo_scores)
            st.metric("คะแนน PLO เฉลี่ย", f"{avg_plo:.1f}%")
        with col2:
            highest_plo = max(plo_scores, key=plo_scores.get)
            st.metric("PLO ที่แข็งแกร่งที่สุด", highest_plo)
        with col3:
            lowest_plo = min(plo_scores, key=plo_scores.get)
            st.metric("PLO ที่ต้องปรับปรุง", lowest_plo)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✏️ ไปหน้าประเมินคะแนน", type="primary", use_container_width=True):
            st.session_state.page = "📊 ประเมิน"
            st.rerun()
    
    with col2:
        if st.button("🔄 วิเคราะห์ใหม่", use_container_width=True):
            if 'ai_analysis' in st.session_state:
                del st.session_state.ai_analysis
            st.rerun()
    
    with col3:
        if st.button("📊 ดูสรุปผล", use_container_width=True):
            st.session_state.page = "📈 สรุปผล"
            st.rerun()

def show_assessment():
    """Enhanced assessment page with better UX"""
    st.header("📊 ประเมินความสอดคล้อง")
    
    if 'current_slide' not in st.session_state:
        st.warning("⚠️ กรุณาอัปโหลด Slide ก่อนการประเมิน")
        if st.button("📤 ไปที่หน้าอัปโหลด", type="primary"):
            st.session_state.page = "📤 อัปโหลด Slide"
            st.rerun()
        return
    
    # Current slide info card
    with st.container():
        st.markdown(f"""
        <div class="metric-card">
            <h4>📄 {st.session_state.current_slide['name']}</h4>
            <p><strong>รายวิชา:</strong> {st.session_state.current_slide['course']}</p>
            <p><strong>อัปโหลดเมื่อ:</strong> {st.session_state.current_slide['upload_date']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Assessment form with enhanced layout
    st.subheader("📋 ให้คะแนนความสอดคล้องกับ PLOs")
    
    scores = {}
    comments = {}
    ai_suggestions = st.session_state.get('ai_analysis', {})
    
    # Create tabs for each PLO
    tab1, tab2, tab3 = st.tabs([f"PLO1 ({PLOS['PLO1']['weight']}%)", 
                                f"PLO2 ({PLOS['PLO2']['weight']}%)", 
                                f"PLO3 ({PLOS['PLO3']['weight']}%)"])
    
    tabs = [tab1, tab2, tab3]
    
    for idx, (plo_code, plo_data) in enumerate(PLOS.items()):
        with tabs[idx]:
            # PLO description
            st.markdown(f"### {plo_data['title']}")
            st.write(plo_data['description'])
            
            # Keywords reference
            with st.expander("🔍 คำสำคัญอ้างอิง"):
                keyword_cols = st.columns(3)
                for i, keyword in enumerate(plo_data['keywords']):
                    with keyword_cols[i % 3]:
                        st.caption(f"• {keyword}")
            
            # AI suggestion display
            if plo_code in ai_suggestions:
                ai_score = ai_suggestions[plo_code].get('score', 50)
                st.info(f"🤖 AI แนะนำคะแนน: **{ai_score}%**")
                
                # Show AI found keywords
                ai_keywords = ai_suggestions[plo_code].get('foundKeywords', [])
                if ai_keywords:
                    st.success(f"🎯 AI พบคำสำคัญ: {', '.join(ai_keywords)}")
            
            # Score input with better UX
            col1, col2 = st.columns([2, 1])
            
            with col1:
                default_score = ai_suggestions.get(plo_code, {}).get('score', 70)
                scores[plo_code] = st.slider(
                    f"คะแนน {plo_code} (0-100)",
                    min_value=0,
                    max_value=100,
                    value=default_score,
                    step=5,
                    help=f"ประเมินความสอดคล้องของเนื้อหากับ {plo_code}"
                )
            
            with col2:
                # Score indicator
                score_color = "🟢" if scores[plo_code] >= 80 else "🟡" if scores[plo_code] >= 60 else "🔴"
                score_text = "ดีเยี่ยม" if scores[plo_code] >= 80 else "ดี" if scores[plo_code] >= 70 else "พอใช้" if scores[plo_code] >= 60 else "ต้องปรับปรุง"
                st.markdown(f"### {score_color} {score_text}")
                st.progress(scores[plo_code] / 100)
            
            # Comments section
            comments[plo_code] = st.text_area(
                f"💬 หมายเหตุและข้อเสนอแนะสำหรับ {plo_code}",
                height=100,
                placeholder=f"ระบุข้อเสนอแนะเพิ่มเติมสำหรับ {plo_code}...",
                help="ข้อเสนอแนะจะช่วยในการปรับปรุงเนื้อหาให้สอดคล้องกับ PLO มากขึ้น"
            )
            
            # Show AI suggestions if available
            if plo_code in ai_suggestions:
                with st.expander("💡 ดูคำแนะนำจาก AI"):
                    suggestions = ai_suggestions[plo_code].get('suggestions', [])
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
    
    # Calculate and display overall score
    st.markdown("---")
    st.subheader("📊 สรุปคะแนนรวม")
    
    overall_score = sum(scores[plo] * PLOS[plo]['weight'] / 100 for plo in scores)
    
    # Enhanced score display
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create gauge chart for overall score
        fig = create_score_gauge(overall_score, "คะแนนรวม")
        st.plotly_chart(fig, use_container_width=True)
        
        # Status message
        if overall_score >= 80:
            st.success(f"🌟 **ดีเยี่ยม!** คะแนนรวม {overall_score:.1f}%")
        elif overall_score >= 70:
            st.success(f"✅ **ผ่านเกณฑ์** คะแนนรวม {overall_score:.1f}%")
        else:
            st.warning(f"⚠️ **ต้องปรับปรุง** คะแนนรวม {overall_score:.1f}%")
    
    # Individual PLO scores summary
    st.subheader("📋 สรุปคะแนนแต่ละ PLO")
    col1, col2, col3 = st.columns(3)
    
    for idx, (plo_code, score) in enumerate(scores.items()):
        with [col1, col2, col3][idx]:
            weight = PLOS[plo_code]['weight']
            weighted_score = score * weight / 100
            
            st.metric(
                label=f"{plo_code} (น้ำหนัก {weight}%)",
                value=f"{score}%",
                delta=f"คะแนนถ่วงน้ำหนัก: {weighted_score:.1f}"
            )
    
    # Save assessment
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 บันทึกการประเมิน", type="primary", use_container_width=True):
            assessment = {
                'id': len(st.session_state.assessments) + 1,
                'slide_name': st.session_state.current_slide['name'],
                'course': st.session_state.current_slide['course'],
                'course_type': st.session_state.current_slide['course_type'],
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'scores': scores,
                'comments': comments,
                'overall_score': overall_score,
                'status': 'ผ่านเกณฑ์' if overall_score >= 70 else 'ต้องปรับปรุง',
                'ai_analyzed': 'ai_analysis' in st.session_state,
                'file_size': st.session_state.current_slide.get('file_size', 0)
            }
            
            st.session_state.assessments.append(assessment)
            
            if save_assessments(st.session_state.assessments):
                st.success("✅ บันทึกการประเมินเรียบร้อย!")
                st.balloons()
                
                # Clear current slide data
                if 'current_slide' in st.session_state:
                    del st.session_state.current_slide
                if 'ai_analysis' in st.session_state:
                    del st.session_state.ai_analysis
                
                # Auto-redirect to summary after 2 seconds
                import time
                time.sleep(2)
                st.session_state.page = "📈 สรุปผล"
                st.rerun()
            else:
                st.error("❌ เกิดข้อผิดพลาดในการบันทึก")
    
    with col2:
        if st.button("🔄 รีเซ็ตการประเมิน", use_container_width=True):
            st.rerun()

def show_summary():
    """Enhanced summary page with better analytics"""
    st.header("📈 สรุปผลการประเมิน")
    
    if not st.session_state.assessments:
        st.warning("ยังไม่มีข้อมูลการประเมิน")
        if st.button("🚀 เริ่มประเมิน", type="primary"):
            st.session_state.page = "📤 อัปโหลด Slide"
            st.rerun()
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(st.session_state.assessments)
    df['date'] = pd.to_datetime(df['date'])
    
    # Enhanced overall statistics
    st.subheader("📊 สถิติภาพรวม")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_assessments = len(df)
    passed = len(df[df['status'] == 'ผ่านเกณฑ์'])
    avg_score = df['overall_score'].mean()
    ai_analyzed = len(df[df['ai_analyzed'] == True])
    
    with col1:
        st.metric("การประเมินทั้งหมด", total_assessments)
    with col2:
        st.metric("ผ่านเกณฑ์", passed, f"{passed/total_assessments*100:.0f}%")
    with col3:
        st.metric("คะแนนเฉลี่ย", f"{avg_score:.1f}%")
    with col4:
        st.metric("วิเคราะห์ด้วย AI", ai_analyzed, f"{ai_analyzed/total_assessments*100:.0f}%")
    with col5:
        latest_score = df.iloc[-1]['overall_score']
        trend = "📈" if latest_score > avg_score else "📉" if latest_score < avg_score else "➡️"
        st.metric("ล่าสุด", f"{latest_score:.1f}%", f"{trend}")
    
    # Score distribution with enhanced visualization
    st.subheader("📊 การกระจายคะแนน")
    
    tab1, tab2 = st.tabs(["การกระจายคะแนนรวม", "เปรียบเทียบ PLO"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            fig_hist = px.histogram(
                df, 
                x='overall_score', 
                nbins=15,
                title="การกระจายคะแนนรวม",
                labels={'overall_score': 'คะแนนรวม (%)', 'count': 'จำนวน'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_hist.add_vline(x=70, line_dash="dash", line_color="red", 
                              annotation_text="เกณฑ์ผ่าน (70%)")
            fig_hist.add_vline(x=avg_score, line_dash="dot", line_color="green",
                              annotation_text=f"เฉลี่ย ({avg_score:.1f}%)")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Box plot
            fig_box = px.box(
                df,
                y='overall_score',
                title="สถิติคะแนนรวม",
                labels={'overall_score': 'คะแนนรวม (%)'}
            )
            fig_box.add_hline(y=70, line_dash="dash", line_color="red")
            st.plotly_chart(fig_box, use_container_width=True)
    
    with tab2:
        # PLO comparison
        plo_data = []
        for assessment in st.session_state.assessments:
            for plo, score in assessment['scores'].items():
                plo_data.append({
                    'PLO': plo,
                    'Score': score,
                    'Assessment': assessment['id']
                })
        
        if plo_data:
            plo_df = pd.DataFrame(plo_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # PLO average scores
                plo_avg = plo_df.groupby('PLO')['Score'].mean().reset_index()
                fig_plo = px.bar(
                    plo_avg,
                    x='PLO',
                    y='Score',
                    title="คะแนนเฉลี่ยแต่ละ PLO",
                    labels={'Score': 'คะแนนเฉลี่ย (%)', 'PLO': 'PLO'},
                    color='PLO',
                    color_discrete_map={
                        'PLO1': PLOS['PLO1']['color'],
                        'PLO2': PLOS['PLO2']['color'],
                        'PLO3': PLOS['PLO3']['color']
                    }
                )
                fig_plo.add_hline(y=70, line_dash="dash", line_color="red")
                st.plotly_chart(fig_plo, use_container_width=True)
            
            with col2:
                # PLO score distribution
                fig_violin = px.violin(
                    plo_df,
                    x='PLO',
                    y='Score',
                    title="การกระจายคะแนนแต่ละ PLO",
                    labels={'Score': 'คะแนน (%)', 'PLO': 'PLO'}
                )
                fig_violin.add_hline(y=70, line_dash="dash", line_color="red")
                st.plotly_chart(fig_violin, use_container_width=True)
    
    # Time series analysis
    if total_assessments >= 3:
        st.subheader("📈 แนวโน้มตามเวลา")
        
        df_sorted = df.sort_values('date')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Overall score trend
            fig_trend = px.line(
                df_sorted, 
                x='date', 
                y='overall_score',
                title="แนวโน้มคะแนนรวมตามเวลา",
                labels={'date': 'วันที่', 'overall_score': 'คะแนนรวม (%)'},
                markers=True
            )
            fig_trend.add_hline(y=70, line_dash="dash", line_color="red")
            fig_trend.add_hline(y=avg_score, line_dash="dot", line_color="green")
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Moving average (if enough data)
            if total_assessments >= 5:
                df_sorted['moving_avg'] = df_sorted['overall_score'].rolling(window=3).mean()
                fig_ma = px.line(
                    df_sorted,
                    x='date',
                    y=['overall_score', 'moving_avg'],
                    title="คะแนนและค่าเฉลี่ยเคลื่อนที่",
                    labels={'date': 'วันที่', 'value': 'คะแนน (%)'}
                )
                st.plotly_chart(fig_ma, use_container_width=True)
            else:
                # Pass/Fail ratio over time
                df_sorted['cumulative_pass_rate'] = (df_sorted['status'] == 'ผ่านเกณฑ์').cumsum() / range(1, len(df_sorted) + 1) * 100
                fig_pass = px.line(
                    df_sorted,
                    x='date',
                    y='cumulative_pass_rate',
                    title="อัตราผ่านเกณฑ์สะสม",
                    labels={'date': 'วันที่', 'cumulative_pass_rate': 'อัตราผ่าน (%)'}
                )
                fig_pass.add_hline(y=70, line_dash="dash", line_color="red")
                st.plotly_chart(fig_pass, use_container_width=True)
    
    # Course analysis
    st.subheader("📚 วิเคราะห์ตามรายวิชา")
    
    if 'course' in df.columns:
        course_summary = df.groupby('course').agg({
            'overall_score': ['mean', 'count', 'std'],
            'status': lambda x: (x == 'ผ่านเกณฑ์').sum(),
            'ai_analyzed': lambda x: x.sum()
        }).round(2)
        
        course_summary.columns = ['คะแนนเฉลี่ย', 'จำนวนการประเมิน', 'ส่วนเบี่ยงเบนมาตรฐาน', 'ผ่านเกณฑ์', 'วิเคราะห์ด้วย AI']
        course_summary['อัตราผ่าน (%)'] = (course_summary['ผ่านเกณฑ์'] / course_summary['จำนวนการประเมิน'] * 100).round(1)
        
        # Style the dataframe
        st.dataframe(
            course_summary,
            use_container_width=True,
            column_config={
                "คะแนนเฉลี่ย": st.column_config.ProgressColumn(
                    "คะแนนเฉลี่ย",
                    help="คะแนนเฉลี่ยของรายวิชา",
                    format="%.1f",
                    min_value=0,
                    max_value=100,
                ),
                "อัตราผ่าน (%)": st.column_config.ProgressColumn(
                    "อัตราผ่าน (%)",
                    help="เปอร์เซ็นต์การผ่านเกณฑ์",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            }
        )
        
        # Course performance chart
        if len(course_summary) > 1:
            fig_course = px.scatter(
                course_summary.reset_index(),
                x='จำนวนการประเมิน',
                y='คะแนนเฉลี่ย',
                size='อัตราผ่าน (%)',
                title="ความสัมพันธ์ระหว่างจำนวนการประเมินและคะแนนเฉลี่ย",
                labels={'จำนวนการประเมิน': 'จำนวนการประเมิน', 'คะแนนเฉลี่ย': 'คะแนนเฉลี่ย (%)'},
                hover_data=['course']
            )
            fig_course.add_hline(y=70, line_dash="dash", line_color="red")
            st.plotly_chart(fig_course, use_container_width=True)
    
    # Export functionality
    st.subheader("📥 ส่งออกข้อมูล")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export สรุปเป็น CSV", use_container_width=True):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Download Summary CSV",
                data=csv,
                file_name=f"plo_assessment_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("📈 Export สถิติเป็น JSON", use_container_width=True):
            stats = {
                'total_assessments': total_assessments,
                'passed': int(passed),
                'pass_rate': passed/total_assessments*100,
                'average_score': avg_score,
                'ai_analyzed': int(ai_analyzed),
                'generated_date': datetime.now().isoformat()
            }
            
            st.download_button(
                label="📥 Download Stats JSON",
                data=json.dumps(stats, indent=2, ensure_ascii=False),
                file_name=f"plo_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col3:
        if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
            st.session_state.assessments = load_assessments()
            st.rerun()

def show_history():
    """Enhanced history page with advanced filtering and search"""
    st.header("📋 ประวัติการประเมิน")
    
    if not st.session_state.assessments:
        st.warning("ยังไม่มีประวัติการประเมิน")
        if st.button("🚀 เริ่มประเมิน", type="primary"):
            st.session_state.page = "📤 อัปโหลด Slide"
            st.rerun()
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.assessments)
    df['date'] = pd.to_datetime(df['date'])
    
    # Enhanced filtering section
    st.subheader("🔍 กรองและค้นหาข้อมูล")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Course filter
        all_courses = ["ทั้งหมด"] + sorted(df['course'].unique().tolist())
        filter_course = st.selectbox("กรองตามรายวิชา", all_courses)
    
    with col2:
        # Status filter
        filter_status = st.selectbox(
            "กรองตามสถานะ",
            ["ทั้งหมด", "ผ่านเกณฑ์", "ต้องปรับปรุง"]
        )
    
    with col3:
        # AI analysis filter
        filter_ai = st.selectbox(
            "กรองตาม AI",
            ["ทั้งหมด", "วิเคราะห์ด้วย AI", "ไม่ได้ใช้ AI"]
        )
    
    with col4:
        # Score range filter
        score_range = st.slider(
            "ช่วงคะแนน",
            min_value=0,
            max_value=100,
            value=(0, 100),
            step=5
        )
    
    # Search functionality
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            "🔍 ค้นหาชื่อไฟล์หรือรายวิชา",
            placeholder="พิมพ์คำที่ต้องการค้นหา..."
        )
    with col2:
        sort_by = st.selectbox(
            "เรียงตาม",
            ["วันที่ (ใหม่ไปเก่า)", "วันที่ (เก่าไปใหม่)", "คะแนน (สูงไปต่ำ)", "คะแนน (ต่ำไปสูง)"]
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if filter_course != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df['course'] == filter_course]
    
    if filter_status != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]
    
    if filter_ai == "วิเคราะห์ด้วย AI":
        filtered_df = filtered_df[filtered_df['ai_analyzed'] == True]
    elif filter_ai == "ไม่ได้ใช้ AI":
        filtered_df = filtered_df[filtered_df['ai_analyzed'] == False]
    
    # Score range filter
    filtered_df = filtered_df[
        (filtered_df['overall_score'] >= score_range[0]) & 
        (filtered_df['overall_score'] <= score_range[1])
    ]
    
    # Search filter
    if search_term:
        mask = (
            filtered_df['slide_name'].str.contains(search_term, case=False, na=False) |
            filtered_df['course'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    
    # Apply sorting
    if sort_by == "วันที่ (ใหม่ไปเก่า)":
        filtered_df = filtered_df.sort_values('date', ascending=False)
    elif sort_by == "วันที่ (เก่าไปใหม่)":
        filtered_df = filtered_df.sort_values('date', ascending=True)
    elif sort_by == "คะแนน (สูงไปต่ำ)":
        filtered_df = filtered_df.sort_values('overall_score', ascending=False)
    elif sort_by == "คะแนน (ต่ำไปสูง)":
        filtered_df = filtered_df.sort_values('overall_score', ascending=True)
    
    # Show filtered results count
    st.info(f"📊 แสดงผล {len(filtered_df)} รายการ จากทั้งหมด {len(df)} รายการ")
    
    # Display results
    if len(filtered_df) > 0:
        # Prepare display DataFrame
        display_df = filtered_df[[
            'date', 'slide_name', 'course', 'overall_score', 'status', 'ai_analyzed'
        ]].copy()
        
        display_df.columns = ['วันที่', 'ชื่อ Slide', 'รายวิชา', 'คะแนนรวม (%)', 'สถานะ', 'AI']
        display_df['AI'] = display_df['AI'].map({True: '✅', False: '❌'})
        display_df['วันที่'] = display_df['วันที่'].dt.strftime('%Y-%m-%d %H:%M')
        
        # Enhanced dataframe display
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "คะแนนรวม (%)": st.column_config.ProgressColumn(
                    "คะแนนรวม (%)",
                    help="คะแนนรวมที่ได้จากการประเมิน",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
                "สถานะ": st.column_config.TextColumn(
                    "สถานะ",
                    help="สถานะการผ่านเกณฑ์"
                ),
                "AI": st.column_config.TextColumn(
                    "AI",
                    help="ใช้ AI วิเคราะห์หรือไม่"
                )
            }
        )
        
        # Detailed view expander
        with st.expander("👁️ ดูรายละเอียดเพิ่มเติม"):
            selected_id = st.selectbox(
                "เลือกการประเมินที่ต้องการดูรายละเอียด",
                options=filtered_df['id'].tolist(),
                format_func=lambda x: f"#{x} - {filtered_df[filtered_df['id']==x]['slide_name'].iloc[0]}"
            )
            
            if selected_id:
                selected_assessment = filtered_df[filtered_df['id'] == selected_id].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 คะแนนแต่ละ PLO:**")
                    for plo, score in selected_assessment['scores'].items():
                        st.metric(plo, f"{score}%")
                
                with col2:
                    st.markdown("**💬 ความคิดเห็น:**")
                    for plo, comment in selected_assessment['comments'].items():
                        if comment:
                            st.write(f"**{plo}:** {comment}")
                        else:
                            st.caption(f"{plo}: ไม่มีความคิดเห็น")
        
        # Export filtered results
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export ผลกรองเป็น CSV", use_container_width=True):
                csv = display_df.to_csv(index=False, encoding='utf-8-sig')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                st.download_button(
                    label="📥 Download Filtered CSV",
                    data=csv,
                    file_name=f"filtered_assessments_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            if st.button("🗑️ ลบข้อมูลที่เลือก", use_container_width=True):
                st.warning("⚠️ ฟีเจอร์นี้อยู่ระหว่างการพัฒนา")
        
        with col3:
            if st.button("🔄 รีเซ็ตตัวกรอง", use_container_width=True):
                st.rerun()
    
    else:
        st.info("ไม่พบข้อมูลตามเงื่อนไขที่เลือก")
        if st.button("🔄 ล้างตัวกรอง"):
            st.rerun()

if __name__ == "__main__":
    main()
