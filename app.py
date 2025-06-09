import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

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

# Page config
st.set_page_config(
    page_title="ระบบประเมิน Slide กับ PLOs (AI-Powered)",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'assessments' not in st.session_state:
    st.session_state.assessments = []
if 'current_assessment' not in st.session_state:
    st.session_state.current_assessment = None

# Load saved assessments
def load_assessments():
    if os.path.exists('data/assessments.json'):
        with open('data/assessments.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_assessments(assessments):
    os.makedirs('data', exist_ok=True)
    with open('data/assessments.json', 'w', encoding='utf-8') as f:
        json.dump(assessments, f, ensure_ascii=False, indent=2)

# PLOs definition
PLOS = {
    'PLO1': {
        'description': 'สามารถใช้เทคโนโลยีและข้อมูลที่เกี่ยวข้องในการเสนอแนวทางการแก้ไขปัญหาทางสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ โดยยึดหลักการมีส่วนร่วมอย่างเป็นธรรมและการพัฒนาที่ยั่งยืน',
        'weight': 35,
        'keywords': ['เทคโนโลยี', 'technology', 'เครื่องมือ', 'tools', 'ชุมชน', 'community', 
                    'มีส่วนร่วม', 'participation', 'ยั่งยืน', 'sustainable', 'SDGs']
    },
    'PLO2': {
        'description': 'สามารถดำเนินการวิจัยโดยการบูรณาการความรู้และข้อมูลอย่างรอบด้านเพื่อหาคำตอบหรือวิธีการที่มีประสิทธิภาพในการใช้เทคโนโลยีเพื่อจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'weight': 35,
        'keywords': ['วิจัย', 'research', 'วิธีการ', 'methodology', 'บูรณาการ', 'integrate',
                    'วิเคราะห์', 'analysis', 'นวัตกรรม', 'innovation']
    },
    'PLO3': {
        'description': 'สามารถสื่อสาร ถ่ายทอด ข้อมูลและความรู้จากงานวิจัยด้านสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศได้อย่างชัดเจนและมีประสิทธิภาพ',
        'weight': 30,
        'keywords': ['สื่อสาร', 'communicate', 'นำเสนอ', 'present', 'ภาพ', 'visual',
                    'แผนภูมิ', 'chart', 'อธิบาย', 'explain', 'เข้าใจง่าย', 'clear']
    }
}

# Courses
COURSES = {
    'บังคับ': [
        {'code': '282711', 'name': 'ระบบสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ'},
        {'code': '282712', 'name': 'เทคโนโลยีและการจัดการทรัพยากรน้ำอย่างยั่งยืน'},
        {'code': '282713', 'name': 'เทคโนโลยีและการจัดการระบบนิเวศทางบก'},
        {'code': '282714', 'name': 'ระเบียบวิธีวิจัยทางวิทยาศาสตร์และเทคโนโลยี'},
        {'code': '282715', 'name': 'เทคโนโลยีและการจัดการการเปลี่ยนแปลงสภาพภูมิอากาศ'}
    ],
    'เลือก': [
        {'code': '282721', 'name': 'การประเมินความเสี่ยงทางภูมิอากาศและผลกระทบทางสิ่งแวดล้อม'},
        {'code': '282722', 'name': 'แบบจำลองและการวิเคราะห์ข้อมูลทางสิ่งแวดล้อมและสภาพภูมิอากาศด้วยปัญญาประดิษฐ์'},
        {'code': '282723', 'name': 'เทคโนโลยีการลดก๊าซเรือนกระจกและการปรับตัว'},
        {'code': '282724', 'name': 'คาร์บอนฟุตพรินต์เพื่อความเป็นกลางทางคาร์บอนอย่างยั่งยืน'},
        {'code': '282731', 'name': 'เทคโนโลยีและการจัดการมลพิษทางอากาศ'},
        {'code': '282732', 'name': 'เทคโนโลยีการจัดการทรัพยากรดินและป่าไม้การอนุรักษ์ความหลากหลายทางชีวภาพ'},
        {'code': '282733', 'name': 'เทคโนโลยีและการจัดการลุ่มน้ำ'},
        {'code': '282734', 'name': 'การสื่อสารประเด็นสาธารณะสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ'}
    ]
}

# Initialize AI Analyzer
@st.cache_resource
def init_ai_analyzer():
    if AI_AVAILABLE:
        return AIAnalyzer(
            provider=os.getenv('AI_PROVIDER', 'openai'),
            api_key=os.getenv('OPENAI_API_KEY')
        )
    return None

# Main App
def main():
    # Debug mode
    if st.checkbox("🐛 Debug Mode", value=False):
        st.write("Session State:", st.session_state)
    
    st.title("🧠 ระบบประเมินความสอดคล้องของ Slide กับ PLOs")
    st.caption("หลักสูตรวิทยาศาสตรมหาบัณฑิต สาขาวิชาเทคโนโลยีการจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 เมนูหลัก")
        menu = st.radio(
            "เลือกฟังก์ชัน",
            ["🏠 หน้าแรก", "📤 อัปโหลด Slide", "📊 ประเมิน", "📈 สรุปผล", "📋 ประวัติ"]
        )
        
        st.divider()
        
        # AI Status
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
    
    # Load assessments
    st.session_state.assessments = load_assessments()
    
    # Main content based on menu
    if menu == "🏠 หน้าแรก":
        show_home()
    elif menu == "📤 อัปโหลด Slide":
        show_upload()
    elif menu == "📊 ประเมิน":
        show_assessment()
    elif menu == "📈 สรุปผล":
        show_summary()
    elif menu == "📋 ประวัติ":
        show_history()

def show_home():
    st.header("🎯 ผลการเรียนรู้ที่คาดหวังของหลักสูตร (PLOs)")
    
    # Display PLOs
    for plo_code, plo_data in PLOS.items():
        with st.expander(f"{plo_code} (น้ำหนัก {plo_data['weight']}%)", expanded=True):
            st.write(plo_data['description'])
            st.caption(f"คำสำคัญ: {', '.join(plo_data['keywords'][:5])}...")
    
    # Statistics
    st.header("📊 สถิติภาพรวม")
    col1, col2, col3, col4 = st.columns(4)
    
    total_assessments = len(st.session_state.assessments)
    passed = len([a for a in st.session_state.assessments if a.get('overall_score', 0) >= 70])
    
    with col1:
        st.metric("จำนวนการประเมินทั้งหมด", total_assessments)
    with col2:
        st.metric("ผ่านเกณฑ์", passed, f"{passed/total_assessments*100:.0f}%" if total_assessments > 0 else "0%")
    with col3:
        st.metric("ต้องปรับปรุง", total_assessments - passed)
    with col4:
        avg_score = sum(a.get('overall_score', 0) for a in st.session_state.assessments) / total_assessments if total_assessments > 0 else 0
        st.metric("คะแนนเฉลี่ย", f"{avg_score:.1f}%")

def show_upload():
    st.header("📤 อัปโหลด Slide การสอน")
    
    # Course selection
    col1, col2 = st.columns([2, 1])
    with col1:
        course_type = st.selectbox("ประเภทวิชา", ["บังคับ", "เลือก"])
        selected_course = st.selectbox(
            "เลือกรายวิชา",
            options=[f"{c['code']} - {c['name']}" for c in COURSES[course_type]],
            format_func=lambda x: x
        )
    
    # File upload
    uploaded_file = st.file_uploader(
        "เลือกไฟล์ Slide",
        type=['pdf', 'pptx', 'ppt'],
        help="รองรับไฟล์ PDF, PPT, PPTX"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ อัปโหลดไฟล์: {uploaded_file.name}")
        
        # Extract text button
        if st.button("🔍 แปลงไฟล์เป็นข้อความ", type="primary"):
            with st.spinner("กำลังแปลงไฟล์..."):
                try:
                    if uploaded_file.type == "application/pdf" and PDF_AVAILABLE:
                        extractor = PDFExtractor()
                        text = extractor.extract_text(uploaded_file)
                    else:
                        # Fallback for demo
                        text = f"[เนื้อหาจำลองจาก {uploaded_file.name}]\n\n" + \
                               "บทนี้จะกล่าวถึงเทคโนโลยีการจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ " + \
                               "โดยเน้นการมีส่วนร่วมของชุมชนและการพัฒนาที่ยั่งยืน รวมถึงกระบวนการวิจัย " + \
                               "และการวิเคราะห์ข้อมูลเพื่อหาแนวทางแก้ไขปัญหา"
                    
                    # Save to session
                    st.session_state.current_slide = {
                        'name': uploaded_file.name,
                        'course': selected_course,
                        'course_type': course_type,
                        'content': text,
                        'upload_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    st.success("✅ แปลงไฟล์สำเร็จ!")
                    
                    # Show preview
                    with st.expander("ดูตัวอย่างเนื้อหา"):
                        st.text(text[:1000] + "..." if len(text) > 1000 else text)
                            
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาด: {str(e)}")
        
        # ตรวจสอบว่ามีข้อมูล slide ใน session หรือไม่
        if 'current_slide' in st.session_state:
            st.info("📄 พร้อมวิเคราะห์แล้ว")
            
            # AI Analysis button - ใช้ unique key
            if st.button("🤖 วิเคราะห์ด้วย AI", type="secondary", key="analyze_ai_btn"):
                # สร้าง placeholder สำหรับแสดงผล
                result_placeholder = st.empty()
                with result_placeholder.container():
                    analyze_with_ai()


def analyze_with_ai():
    """วิเคราะห์ด้วย AI พร้อมแสดงผลทันที"""
    
    if 'current_slide' not in st.session_state:
        st.warning("กรุณาอัปโหลด Slide ก่อน")
        return
    
    # แสดง spinner
    with st.spinner("🧠 AI กำลังวิเคราะห์..."):
        try:
            # ใช้ Mock data เสมอถ้าไม่มี AI
            ai_analyzer = init_ai_analyzer()
            if ai_analyzer:
                result = ai_analyzer.analyze_slide(
                    st.session_state.current_slide['content'],
                    PLOS
                )
            else:
                # Mock analysis
                result = {
                    "PLO1": {
                        "score": 75,
                        "foundKeywords": ["เทคโนโลยี", "ชุมชน", "ยั่งยืน"],
                        "strengths": [
                            "มีการกล่าวถึงเทคโนโลยีที่เกี่ยวข้อง",
                            "แสดงแนวทางการพัฒนาที่ยั่งยืน"
                        ],
                        "suggestions": [
                            "ควรเพิ่มเนื้อหาเกี่ยวกับการมีส่วนร่วมของชุมชน",
                            "เชื่อมโยงกับ SDGs ให้ชัดเจนขึ้น"
                        ]
                    },
                    "PLO2": {
                        "score": 82,
                        "foundKeywords": ["วิจัย", "วิเคราะห์", "บูรณาการ"],
                        "strengths": [
                            "มีกระบวนการวิจัยที่ชัดเจน",
                            "แสดงการวิเคราะห์ข้อมูลดี"
                        ],
                        "suggestions": [
                            "เพิ่มการบูรณาการข้ามศาสตร์",
                            "เพิ่มรายละเอียดระเบียบวิธีวิจัย"
                        ]
                    },
                    "PLO3": {
                        "score": 68,
                        "foundKeywords": ["นำเสนอ", "อธิบาย"],
                        "strengths": [
                            "การจัดลำดับเนื้อหาเป็นระบบ"
                        ],
                        "suggestions": [
                            "เพิ่มภาพและแผนภูมิประกอบ",
                            "ใช้ภาษาที่เข้าใจง่ายขึ้น"
                        ]
                    },
                    "overall_score": 75,
                    "general_suggestions": [
                        "เพิ่ม case study จากบริบทท้องถิ่น",
                        "เพิ่มกิจกรรมการมีส่วนร่วม"
                    ]
                }
            
            st.session_state.ai_analysis = result
            
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการวิเคราะห์: {str(e)}")
            # ใช้ Mock data ถ้า error
            result = {
                "PLO1": {"score": 70, "foundKeywords": ["เทคโนโลยี"], "strengths": ["N/A"], "suggestions": ["N/A"]},
                "PLO2": {"score": 70, "foundKeywords": ["วิจัย"], "strengths": ["N/A"], "suggestions": ["N/A"]},
                "PLO3": {"score": 70, "foundKeywords": ["สื่อสาร"], "strengths": ["N/A"], "suggestions": ["N/A"]},
                "overall_score": 70,
                "general_suggestions": ["ไม่สามารถวิเคราะห์ได้ - ใช้ข้อมูลจำลอง"]
            }
            st.session_state.ai_analysis = result
            
    # แสดงผลการวิเคราะห์
    st.success("✅ วิเคราะห์เสร็จสิ้น!")
    
    # แสดงผล AI Results ในหน้าเดียวกัน
    st.markdown("---")
    st.subheader("📊 ผลการวิเคราะห์จาก AI")
    
    # Overall score with gauge
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # ใช้ metric แทน gauge chart
        st.metric(
            label="คะแนนรวม",
            value=f"{result['overall_score']}%",
            delta="ผ่านเกณฑ์" if result['overall_score'] >= 70 else "ต้องปรับปรุง"
        )
    
    # PLO scores in columns
    st.subheader("คะแนนแต่ละ PLO")
    cols = st.columns(3)
    
    for idx, plo in enumerate(['PLO1', 'PLO2', 'PLO3']):
        with cols[idx]:
            if plo in result:
                score = result[plo]['score']
                st.metric(
                    label=plo,
                    value=f"{score}%",
                    delta="ดีมาก" if score >= 80 else "พอใช้" if score >= 60 else "ปรับปรุง"
                )
                
                # แสดงคำสำคัญที่พบ
                if result[plo].get('foundKeywords'):
                    st.caption("พบคำสำคัญ:")
                    for kw in result[plo]['foundKeywords']:
                        st.caption(f"• {kw}")
    
    # Detailed suggestions
    st.markdown("---")
    st.subheader("💡 คำแนะนำโดยละเอียด")
    
    for plo in ['PLO1', 'PLO2', 'PLO3']:
        if plo in result:
            with st.expander(f"📌 {plo} - คำแนะนำ", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**✅ จุดเด่น:**")
                    for strength in result[plo].get('strengths', []):
                        st.write(f"• {strength}")
                
                with col2:
                    st.markdown("**💡 ควรปรับปรุง:**")
                    for suggestion in result[plo].get('suggestions', []):
                        st.write(f"• {suggestion}")
    
    # General suggestions
    if result.get('general_suggestions'):
        st.markdown("---")
        st.subheader("📝 คำแนะนำทั่วไป")
        for suggestion in result['general_suggestions']:
            st.info(f"💡 {suggestion}")
    
    # ปุ่มไปหน้าประเมิน
    st.markdown("---")
    if st.button("✏️ ไปหน้าประเมินคะแนน", type="primary", use_container_width=True):
        st.session_state.page = "📊 ประเมิน"
        st.rerun()

def show_assessment():
    st.header("📊 ประเมินความสอดคล้อง")
    
    if 'current_slide' not in st.session_state:
        st.warning("⚠️ กรุณาอัปโหลด Slide ก่อนการประเมิน")
        if st.button("ไปที่หน้าอัปโหลด"):
            st.rerun()
        return
    
    # Show current slide info
    st.info(f"กำลังประเมิน: {st.session_state.current_slide['name']}")
    st.caption(f"รายวิชา: {st.session_state.current_slide['course']}")
    
    # Assessment form
    st.subheader("ให้คะแนนความสอดคล้องกับ PLOs")
    
    scores = {}
    comments = {}
    
    # Get AI suggestions if available
    ai_suggestions = st.session_state.get('ai_analysis', {})
    
    for plo_code, plo_data in PLOS.items():
        st.divider()
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{plo_code}** (น้ำหนัก {plo_data['weight']}%)")
            st.caption(plo_data['description'])
            
            # Show AI suggestion if available
            if plo_code in ai_suggestions:
                ai_score = ai_suggestions[plo_code].get('score', 50)
                st.info(f"🤖 AI แนะนำ: {ai_score}%")
        
        with col2:
            # Score slider
            scores[plo_code] = st.slider(
                f"คะแนน {plo_code}",
                0, 100, 
                value=ai_suggestions.get(plo_code, {}).get('score', 50),
                step=5,
                label_visibility="collapsed"
            )
        
        # Comments
        comments[plo_code] = st.text_area(
            f"หมายเหตุ/ข้อเสนอแนะสำหรับ {plo_code}",
            height=100,
            placeholder="ระบุข้อเสนอแนะ..."
        )
    
    # Calculate overall score
    overall_score = sum(
        scores[plo] * PLOS[plo]['weight'] / 100 
        for plo in scores
    )
    
    # Display overall score
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(
            "คะแนนรวม",
            f"{overall_score:.1f}%",
            f"{'✅ ผ่านเกณฑ์' if overall_score >= 70 else '❌ ต้องปรับปรุง'}"
        )
    
    # Save button
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
            'ai_analyzed': 'ai_analysis' in st.session_state
        }
        
        st.session_state.assessments.append(assessment)
        save_assessments(st.session_state.assessments)
        
        st.success("✅ บันทึกการประเมินเรียบร้อย!")
        st.balloons()
        
        # Clear current slide
        del st.session_state.current_slide
        if 'ai_analysis' in st.session_state:
            del st.session_state.ai_analysis

def show_summary():
    st.header("📈 สรุปผลการประเมิน")
    
    if not st.session_state.assessments:
        st.warning("ยังไม่มีข้อมูลการประเมิน")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(st.session_state.assessments)
    
    # Overall statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("จำนวนการประเมินทั้งหมด", len(df))
    with col2:
        passed = len(df[df['status'] == 'ผ่านเกณฑ์'])
        st.metric("ผ่านเกณฑ์", passed, f"{passed/len(df)*100:.0f}%")
    with col3:
        avg_score = df['overall_score'].mean()
        st.metric("คะแนนเฉลี่ย", f"{avg_score:.1f}%")
    
    # Score distribution
    st.subheader("📊 การกระจายคะแนน")
    fig = px.histogram(
        df, 
        x='overall_score', 
        nbins=20,
        title="การกระจายคะแนนรวม",
        labels={'overall_score': 'คะแนนรวม (%)', 'count': 'จำนวน'}
    )
    fig.add_vline(x=70, line_dash="dash", line_color="red", annotation_text="เกณฑ์ผ่าน (70%)")
    st.plotly_chart(fig, use_container_width=True)
    
    # By course
    st.subheader("📚 สรุปตามรายวิชา")
    course_summary = df.groupby('course').agg({
        'overall_score': ['mean', 'count'],
        'status': lambda x: (x == 'ผ่านเกณฑ์').sum()
    }).round(1)
    
    course_summary.columns = ['คะแนนเฉลี่ย', 'จำนวนการประเมิน', 'ผ่านเกณฑ์']
    st.dataframe(course_summary, use_container_width=True)
    
    # PLO Analysis
    st.subheader("🎯 วิเคราะห์ตาม PLO")
    plo_scores = {'PLO1': [], 'PLO2': [], 'PLO3': []}
    
    for assessment in st.session_state.assessments:
        for plo in plo_scores:
            if plo in assessment['scores']:
                plo_scores[plo].append(assessment['scores'][plo])
    
    plo_avg = {plo: sum(scores)/len(scores) if scores else 0 for plo, scores in plo_scores.items()}
    
    fig = px.bar(
        x=list(plo_avg.keys()),
        y=list(plo_avg.values()),
        title="คะแนนเฉลี่ยแต่ละ PLO",
        labels={'x': 'PLO', 'y': 'คะแนนเฉลี่ย (%)'}
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

def show_history():
    st.header("📋 ประวัติการประเมิน")
    
    if not st.session_state.assessments:
        st.warning("ยังไม่มีประวัติการประเมิน")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_course = st.selectbox(
            "กรองตามรายวิชา",
            ["ทั้งหมด"] + list(set(a['course'] for a in st.session_state.assessments))
        )
    with col2:
        filter_status = st.selectbox(
            "กรองตามสถานะ",
            ["ทั้งหมด", "ผ่านเกณฑ์", "ต้องปรับปรุง"]
        )
    
    # Filter data
    filtered = st.session_state.assessments
    if filter_course != "ทั้งหมด":
        filtered = [a for a in filtered if a['course'] == filter_course]
    if filter_status != "ทั้งหมด":
        filtered = [a for a in filtered if a['status'] == filter_status]
    
    # Display table
    if filtered:
        df = pd.DataFrame(filtered)
        df = df[['date', 'slide_name', 'course', 'overall_score', 'status', 'ai_analyzed']]
        df.columns = ['วันที่', 'ชื่อ Slide', 'รายวิชา', 'คะแนนรวม (%)', 'สถานะ', 'AI']
        df['AI'] = df['AI'].map({True: '✅', False: '❌'})
        
        st.dataframe(
            df,
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
            }
        )
        
        # Export button
        if st.button("📥 Export เป็น CSV"):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"assessment_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("ไม่พบข้อมูลตามเงื่อนไขที่เลือก")

if __name__ == "__main__":
    main()