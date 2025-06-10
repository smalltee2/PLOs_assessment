import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import re
from collections import defaultdict

# Course Learning Outcomes (CLO) with detailed descriptions
COURSE_DESCRIPTIONS = {
    '282711': {
        'name': 'ระบบสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'description': 'ปัจจัยที่มีผลต่อสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ พลวัตของระบบภูมิอากาศโลก ผลกระทบของการเปลี่ยนแปลงสภาพภูมิอากาศต่อระบบนิเวศและความหลากหลายทางชีวภาพ',
        'clo': {
            'CLO1': 'อธิบายปัจจัยและพลวัตของระบบภูมิอากาศโลกได้',
            'CLO2': 'วิเคราะห์ผลกระทบของการเปลี่ยนแปลงสภาพภูมิอากาศต่อระบบนิเวศได้',
            'CLO3': 'ประเมินเทคโนโลยีและเครื่องมือในการจัดการปัญหาสิ่งแวดล้อมได้'
        },
        'keywords': {
            'CLO1': ['ปัจจัย', 'พลวัต', 'ระบบภูมิอากาศ', 'โลก', 'สภาพภูมิอากาศ', 'เรือนกระจก', 'factors', 'dynamics', 'climate system'],
            'CLO2': ['ผลกระทบ', 'ระบบนิเวศ', 'ความหลากหลายทางชีวภาพ', 'ecosystem', 'biodiversity', 'impact', 'effects'],
            'CLO3': ['เทคโนโลยี', 'เครื่องมือ', 'จัดการ', 'แบบจำลอง', 'technology', 'tools', 'management', 'model']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO1.1']
    },
    '282712': {
        'name': 'เทคโนโลยีและการจัดการทรัพยากรน้ำอย่างยั่งยืน',
        'description': 'สถานการณ์และปัญหาทรัพยากรน้ำ ผลกระทบของการเปลี่ยนแปลงสภาพภูมิอากาศต่อทรัพยากรน้ำ การใช้น้ำและจัดหาน้ำที่ยั่งยืน เทคโนโลยีสารสนเทศภูมิศาสตร์เพื่อการจัดการทรัพยากรน้ำ',
        'clo': {
            'CLO1': 'วิเคราะห์สถานการณ์และปัญหาทรัพยากรน้ำได้',
            'CLO2': 'ประยุกต์ใช้เทคโนโลยี GIS ในการจัดการทรัพยากรน้ำได้',
            'CLO3': 'ออกแบบระบบการจัดการน้ำแบบยั่งยืนได้'
        },
        'keywords': {
            'CLO1': ['ทรัพยากรน้ำ', 'สถานการณ์', 'ปัญหา', 'การเปลี่ยนแปลง', 'water resources', 'situation', 'problems'],
            'CLO2': ['GIS', 'เทคโนโลยี', 'สารสนเทศภูมิศาสตร์', 'การจัดการ', 'technology', 'geographic information'],
            'CLO3': ['ยั่งยืน', 'ระบบ', 'การจัดหา', 'sustainable', 'system', 'supply', 'integrated']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO1.1', 'YLO1.2']
    },
    '282713': {
        'name': 'เทคโนโลยีและการจัดการระบบนิเวศทางบก',
        'description': 'สถานการณ์และปัญหาของระบบนิเวศทางบก การอนุรักษ์และฟื้นฟูระบบนิเวศทางบก การบริหารจัดการป่าไม้อย่างยั่งยืน ความหลากหลายทางชีวภาพ',
        'clo': {
            'CLO1': 'วิเคราะห์สถานการณ์และปัญหาระบบนิเวศทางบกได้',
            'CLO2': 'ออกแบบแผนการอนุรักษ์และฟื้นฟูระบบนิเวศได้',
            'CLO3': 'ประเมินความหลากหลายทางชีวภาพและการจัดการได้'
        },
        'keywords': {
            'CLO1': ['ระบบนิเวศ', 'ทางบก', 'สถานการณ์', 'ปัญหา', 'terrestrial', 'ecosystem', 'situation'],
            'CLO2': ['อนุรักษ์', 'ฟื้นฟู', 'แผน', 'conservation', 'restoration', 'rehabilitation'],
            'CLO3': ['ความหลากหลายทางชีวภาพ', 'ป่าไม้', 'biodiversity', 'forest', 'species']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO1.1']
    },
    '282714': {
        'name': 'ระเบียบวิธีวิจัยทางวิทยาศาสตร์และเทคโนโลยี',
        'description': 'หลักและระเบียบวิธีการวิจัย การวิเคราะห์ปัญหา การสืบค้นและวิเคราะห์งานก่อนหน้า การทบทวนวรรณกรรม การพัฒนาวิธีการศึกษา การวิเคราะห์ทางสถิติ',
        'clo': {
            'CLO1': 'ออกแบบกระบวนการวิจัยที่เหมาะสมได้',
            'CLO2': 'ทบทวนวรรณกรรมอย่างเป็นระบบได้',
            'CLO3': 'วิเคราะห์และแปลผลข้อมูลทางสถิติได้',
            'CLO4': 'เขียนรายงานวิจัยตามมาตรฐานวิชาการได้'
        },
        'keywords': {
            'CLO1': ['ระเบียบวิธี', 'วิจัย', 'กระบวนการ', 'methodology', 'research', 'process'],
            'CLO2': ['วรรณกรรม', 'ทบทวน', 'สืบค้น', 'literature', 'review', 'systematic'],
            'CLO3': ['สถิติ', 'วิเคราะห์', 'ข้อมูล', 'statistics', 'analysis', 'data'],
            'CLO4': ['รายงาน', 'เขียน', 'มาตรฐาน', 'report', 'writing', 'academic']
        },
        'plo_mapping': ['PLO2', 'PLO3'],
        'ylo_mapping': ['YLO1.2', 'YLO1.3']
    },
    '282715': {
        'name': 'เทคโนโลยีและการจัดการการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'description': 'เทคโนโลยีการตรวจวัดและติดตามการเปลี่ยนแปลงสภาพภูมิอากาศ เทคโนโลยีพลังงานสะอาด การกักเก็บคาร์บอน เทคโนโลยีการเกษตรและป่าไม้',
        'clo': {
            'CLO1': 'ประยุกต์ใช้เทคโนโลยีการตรวจวัดภูมิอากาศได้',
            'CLO2': 'ประเมินเทคโนโลยีพลังงานสะอาดได้',
            'CLO3': 'ออกแบบระบบการกักเก็บคาร์บอนได้'
        },
        'keywords': {
            'CLO1': ['เทคโนโลยี', 'ตรวจวัด', 'ติดตาม', 'technology', 'monitoring', 'measurement'],
            'CLO2': ['พลังงานสะอาด', 'พลังงานทดแทน', 'clean energy', 'renewable energy'],
            'CLO3': ['คาร์บอน', 'กักเก็บ', 'carbon', 'capture', 'storage', 'sequestration']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO1.1', 'YLO2.1']
    }
}

# Year Learning Outcomes (YLO) Configuration
YLO_STRUCTURE = {
    'YLO1.1': {
        'description': 'สามารถอธิบายหลักการพื้นฐานของระบบสิ่งแวดล้อม การเปลี่ยนแปลงสภาพภูมิอากาศ การจัดการทรัพยากรน้ำ และระบบนิเวศทางบก',
        'plo_mapping': ['PLO1', 'PLO2'],
        'level': 'Year 1',
        'cognitive_level': 'Understanding'
    },
    'YLO1.2': {
        'description': 'สามารถออกแบบและวางแผนการวิจัย โดยบูรณาการความรู้ทางวิทยาศาสตร์ เทคโนโลยี และการมีส่วนร่วมของชุมชน',
        'plo_mapping': ['PLO1', 'PLO2'],
        'level': 'Year 1',
        'cognitive_level': 'Applying'
    },
    'YLO1.3': {
        'description': 'สามารถใช้เทคโนโลยีในการสืบค้นความรู้และคัดกรองข้อมูลทั้งจากเอกสารและสื่อออนไลน์',
        'plo_mapping': ['PLO2', 'PLO3'],
        'level': 'Year 1',
        'cognitive_level': 'Applying'
    },
    'YLO1.4': {
        'description': 'สามารถนำเสนอและอภิปรายหัวข้อวิจัยในด้านเทคโนโลยีการจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'plo_mapping': ['PLO3'],
        'level': 'Year 1',
        'cognitive_level': 'Evaluating'
    },
    'YLO2.1': {
        'description': 'สามารถใช้เทคโนโลยีที่เหมาะสมและแนวทางการจัดการแบบบูรณาการในการแก้ไขปัญหาด้านสิ่งแวดล้อม',
        'plo_mapping': ['PLO1', 'PLO2'],
        'level': 'Year 2',
        'cognitive_level': 'Creating'
    },
    'YLO2.2': {
        'description': 'สามารถดำเนินการวิจัยเชิงสหวิทยาการ วิเคราะห์ผล และอภิปรายผลการวิจัย',
        'plo_mapping': ['PLO2'],
        'level': 'Year 2',
        'cognitive_level': 'Evaluating'
    },
    'YLO2.3': {
        'description': 'สามารถสื่อสาร ถ่ายทอดองค์ความรู้ที่ได้จากกระบวนการวิจัยที่มีคุณภาพ',
        'plo_mapping': ['PLO3'],
        'level': 'Year 2',
        'cognitive_level': 'Creating'
    }
}

# Enhanced PLO Configuration
ENHANCED_PLOS = {
    'PLO1': {
        'title': 'การใช้เทคโนโลยีและการมีส่วนร่วม',
        'description': 'สามารถใช้เทคโนโลยีและข้อมูลที่เกี่ยวข้องในการเสนอแนวทางการแก้ไขปัญหาทางสิ่งแวดล้อม',
        'weight': 35,
        'color': '#FF6B6B'
    },
    'PLO2': {
        'title': 'การวิจัยและการบูรณาการ',
        'description': 'สามารถดำเนินการวิจัยโดยการบูรณาการความรู้และข้อมูลอย่างรอบด้าน',
        'weight': 35,
        'color': '#4ECDC4'
    },
    'PLO3': {
        'title': 'การสื่อสารและการถ่ายทอด',
        'description': 'สามารถสื่อสาร ถ่ายทอด ข้อมูลและความรู้จากงานวิจัยได้อย่างชัดเจน',
        'weight': 30,
        'color': '#45B7D1'
    }
}

class MultiLevelAssessmentEngine:
    """Multi-Level Assessment Engine for CLO-PLO-YLO alignment"""
    
    def __init__(self):
        self.course_descriptions = COURSE_DESCRIPTIONS
        self.ylo_structure = YLO_STRUCTURE
        self.plos = ENHANCED_PLOS
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        if not text:
            return ""
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def calculate_clo_alignment(self, content, course_code):
        """Calculate Course Learning Outcome alignment"""
        if course_code not in self.course_descriptions:
            return {}
        
        course_data = self.course_descriptions[course_code]
        content_processed = self.preprocess_text(content)
        
        clo_results = {}
        
        for clo_code, clo_description in course_data['clo'].items():
            # Find keywords for this CLO
            keywords = course_data['keywords'].get(clo_code, [])
            found_keywords = []
            
            for keyword in keywords:
                keyword_processed = self.preprocess_text(keyword)
                if keyword_processed in content_processed:
                    found_keywords.append(keyword)
            
            # Calculate score based on keyword coverage
            if keywords:
                coverage = len(found_keywords) / len(keywords)
                base_score = 50
                coverage_score = coverage * 40
                
                # Bonus for description relevance
                desc_words = self.preprocess_text(clo_description).split()
                desc_matches = sum(1 for word in desc_words if word in content_processed)
                desc_bonus = min(desc_matches * 2, 10)
                
                final_score = min(100, base_score + coverage_score + desc_bonus)
            else:
                final_score = 50
            
            clo_results[clo_code] = {
                'score': round(final_score, 1),
                'description': clo_description,
                'found_keywords': found_keywords,
                'total_keywords': len(keywords),
                'coverage': len(found_keywords) / len(keywords) if keywords else 0
            }
        
        return clo_results
    
    def calculate_multi_level_alignment(self, content, course_code):
        """Calculate alignment across CLO-PLO-YLO levels"""
        results = {
            'course_code': course_code,
            'course_name': self.course_descriptions.get(course_code, {}).get('name', 'Unknown'),
            'clo_results': {},
            'plo_results': {},
            'ylo_results': {},
            'alignment_matrix': {},
            'overall_scores': {}
        }
        
        # 1. CLO Analysis
        clo_results = self.calculate_clo_alignment(content, course_code)
        results['clo_results'] = clo_results
        
        # 2. PLO Analysis (mapped from CLOs)
        if course_code in self.course_descriptions:
            course_data = self.course_descriptions[course_code]
            mapped_plos = course_data.get('plo_mapping', [])
            
            for plo_code in mapped_plos:
                # Calculate PLO score based on CLO scores
                related_clos = [clo for clo in clo_results.keys()]
                if related_clos:
                    plo_score = sum(clo_results[clo]['score'] for clo in related_clos) / len(related_clos)
                else:
                    plo_score = 0
                
                results['plo_results'][plo_code] = {
                    'score': round(plo_score, 1),
                    'related_clos': related_clos,
                    'description': self.plos[plo_code]['description']
                }
        
        # 3. YLO Analysis (mapped from PLOs)
        if course_code in self.course_descriptions:
            course_data = self.course_descriptions[course_code]
            mapped_ylos = course_data.get('ylo_mapping', [])
            
            for ylo_code in mapped_ylos:
                ylo_data = self.ylo_structure[ylo_code]
                related_plos = ylo_data['plo_mapping']
                
                # Calculate YLO score based on PLO scores
                ylo_scores = []
                for plo_code in related_plos:
                    if plo_code in results['plo_results']:
                        ylo_scores.append(results['plo_results'][plo_code]['score'])
                
                ylo_score = sum(ylo_scores) / len(ylo_scores) if ylo_scores else 0
                
                results['ylo_results'][ylo_code] = {
                    'score': round(ylo_score, 1),
                    'related_plos': related_plos,
                    'description': ylo_data['description'],
                    'level': ylo_data['level'],
                    'cognitive_level': ylo_data['cognitive_level']
                }
        
        # 4. Create alignment matrix
        results['alignment_matrix'] = self.create_alignment_matrix(results)
        
        # 5. Calculate overall scores
        results['overall_scores'] = {
            'clo_average': sum(clo['score'] for clo in clo_results.values()) / len(clo_results) if clo_results else 0,
            'plo_average': sum(plo['score'] for plo in results['plo_results'].values()) / len(results['plo_results']) if results['plo_results'] else 0,
            'ylo_average': sum(ylo['score'] for ylo in results['ylo_results'].values()) / len(results['ylo_results']) if results['ylo_results'] else 0
        }
        
        return results
    
    def create_alignment_matrix(self, results):
        """Create alignment matrix showing CLO-PLO-YLO relationships"""
        matrix = {
            'clo_to_plo': {},
            'plo_to_ylo': {},
            'clo_to_ylo': {}
        }
        
        # CLO to PLO mapping
        for plo_code, plo_data in results['plo_results'].items():
            related_clos = plo_data['related_clos']
            for clo_code in related_clos:
                if clo_code not in matrix['clo_to_plo']:
                    matrix['clo_to_plo'][clo_code] = []
                matrix['clo_to_plo'][clo_code].append(plo_code)
        
        # PLO to YLO mapping
        for ylo_code, ylo_data in results['ylo_results'].items():
            related_plos = ylo_data['related_plos']
            for plo_code in related_plos:
                if plo_code not in matrix['plo_to_ylo']:
                    matrix['plo_to_ylo'][plo_code] = []
                matrix['plo_to_ylo'][plo_code].append(ylo_code)
        
        return matrix

def create_multi_level_dashboard(results):
    """Create comprehensive multi-level dashboard"""
    st.header("🎯 Multi-Level Learning Outcome Assessment")
    
    # Course Information
    st.subheader(f"📚 {results['course_name']}")
    st.write(f"**Course Code:** {results['course_code']}")
    
    # Overall Scores Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        clo_avg = results['overall_scores']['clo_average']
        st.metric("CLO Average", f"{clo_avg:.1f}%", 
                 delta=f"{clo_avg-70:.1f}%" if clo_avg >= 70 else f"{clo_avg-70:.1f}%")
    
    with col2:
        plo_avg = results['overall_scores']['plo_average']
        st.metric("PLO Average", f"{plo_avg:.1f}%",
                 delta=f"{plo_avg-70:.1f}%" if plo_avg >= 70 else f"{plo_avg-70:.1f}%")
    
    with col3:
        ylo_avg = results['overall_scores']['ylo_average']
        st.metric("YLO Average", f"{ylo_avg:.1f}%",
                 delta=f"{ylo_avg-70:.1f}%" if ylo_avg >= 70 else f"{ylo_avg-70:.1f}%")
    
    # Multi-level Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 CLO Analysis", "🎯 PLO Analysis", "📈 YLO Analysis", "🔗 Alignment Matrix"])
    
    with tab1:
        display_clo_analysis(results['clo_results'])
    
    with tab2:
        display_plo_analysis(results['plo_results'])
    
    with tab3:
        display_ylo_analysis(results['ylo_results'])
    
    with tab4:
        display_alignment_matrix(results)

def display_clo_analysis(clo_results):
    """Display Course Learning Outcome analysis"""
    st.subheader("📋 Course Learning Outcomes (CLO) Analysis")
    
    if not clo_results:
        st.warning("No CLO data available for this course")
        return
    
    # CLO Scores Chart
    clo_scores = {clo: data['score'] for clo, data in clo_results.items()}
    
    fig = px.bar(
        x=list(clo_scores.keys()),
        y=list(clo_scores.values()),
        title="CLO Alignment Scores",
        labels={'x': 'CLO', 'y': 'Score (%)'},
        color=list(clo_scores.values()),
        color_continuous_scale='RdYlGn'
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Pass Threshold")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed CLO Analysis
    for clo_code, clo_data in clo_results.items():
        with st.expander(f"{clo_code}: {clo_data['description'][:60]}..."):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {clo_data['description']}")
                st.write(f"**Keywords Found:** {', '.join(clo_data['found_keywords']) if clo_data['found_keywords'] else 'None'}")
                
                # Coverage bar
                coverage = clo_data['coverage']
                st.progress(coverage)
                st.caption(f"Keyword Coverage: {coverage*100:.1f}% ({len(clo_data['found_keywords'])}/{clo_data['total_keywords']})")
            
            with col2:
                score = clo_data['score']
                if score >= 80:
                    st.success(f"Score: {score:.1f}%")
                elif score >= 70:
                    st.info(f"Score: {score:.1f}%")
                elif score >= 60:
                    st.warning(f"Score: {score:.1f}%")
                else:
                    st.error(f"Score: {score:.1f}%")

def display_plo_analysis(plo_results):
    """Display Program Learning Outcome analysis"""
    st.subheader("🎯 Program Learning Outcomes (PLO) Analysis")
    
    if not plo_results:
        st.warning("No PLO mapping available for this course")
        return
    
    # PLO Scores Chart
    plo_scores = {plo: data['score'] for plo, data in plo_results.items()}
    
    fig = px.bar(
        x=list(plo_scores.keys()),
        y=list(plo_scores.values()),
        title="PLO Alignment Scores",
        labels={'x': 'PLO', 'y': 'Score (%)'},
        color=list(plo_scores.values()),
        color_continuous_scale='Viridis'
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Pass Threshold")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed PLO Analysis
    for plo_code, plo_data in plo_results.items():
        with st.expander(f"{plo_code}: {ENHANCED_PLOS[plo_code]['title']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {plo_data['description']}")
                st.write(f"**Related CLOs:** {', '.join(plo_data['related_clos'])}")
            
            with col2:
                score = plo_data['score']
                st.metric(f"{plo_code} Score", f"{score:.1f}%")

def display_ylo_analysis(ylo_results):
    """Display Year Learning Outcome analysis"""
    st.subheader("📈 Year Learning Outcomes (YLO) Analysis")
    
    if not ylo_results:
        st.warning("No YLO mapping available for this course")
        return
    
    # YLO by Year and Cognitive Level
    ylo_df = []
    for ylo_code, ylo_data in ylo_results.items():
        ylo_df.append({
            'YLO': ylo_code,
            'Score': ylo_data['score'],
            'Level': ylo_data['level'],
            'Cognitive': ylo_data['cognitive_level']
        })
    
    ylo_df = pd.DataFrame(ylo_df)
    
    if not ylo_df.empty:
        # Chart by Year Level
        fig1 = px.bar(
            ylo_df, x='YLO', y='Score', color='Level',
            title="YLO Scores by Year Level",
            labels={'Score': 'Score (%)'}
        )
        fig1.add_hline(y=70, line_dash="dash", line_color="red")
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Chart by Cognitive Level
        fig2 = px.scatter(
            ylo_df, x='YLO', y='Score', color='Cognitive', size='Score',
            title="YLO Scores by Cognitive Level",
            labels={'Score': 'Score (%)'}
        )
        fig2.add_hline(y=70, line_dash="dash", line_color="red")
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed YLO Analysis
    for ylo_code, ylo_data in ylo_results.items():
        with st.expander(f"{ylo_code}: {ylo_data['level']} - {ylo_data['cognitive_level']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {ylo_data['description']}")
                st.write(f"**Related PLOs:** {', '.join(ylo_data['related_plos'])}")
                st.write(f"**Year Level:** {ylo_data['level']}")
                st.write(f"**Cognitive Level:** {ylo_data['cognitive_level']}")
            
            with col2:
                score = ylo_data['score']
                st.metric(f"{ylo_code} Score", f"{score:.1f}%")

def display_alignment_matrix(results):
    """Display alignment matrix visualization"""
    st.subheader("🔗 Learning Outcome Alignment Matrix")
    
    # Sankey Diagram for CLO-PLO-YLO Flow
    st.subheader("📊 Learning Outcome Flow")
    
    # Prepare data for Sankey diagram
    nodes = []
    links = []
    node_colors = []
    
    # Add CLO nodes
    clo_nodes = list(results['clo_results'].keys())
    for clo in clo_nodes:
        nodes.append(f"CLO: {clo}")
        node_colors.append('#FF9999')
    
    # Add PLO nodes
    plo_nodes = list(results['plo_results'].keys())
    for plo in plo_nodes:
        nodes.append(f"PLO: {plo}")
        node_colors.append('#99CCFF')
    
    # Add YLO nodes
    ylo_nodes = list(results['ylo_results'].keys())
    for ylo in ylo_nodes:
        nodes.append(f"YLO: {ylo}")
        node_colors.append('#99FF99')
    
    # Create links
    matrix = results['alignment_matrix']
    
    # CLO to PLO links
    for clo, plos in matrix['clo_to_plo'].items():
        clo_idx = nodes.index(f"CLO: {clo}")
        for plo in plos:
            plo_idx = nodes.index(f"PLO: {plo}")
            links.append({
                'source': clo_idx,
                'target': plo_idx,
                'value': results['clo_results'][clo]['score']
            })
    
    # PLO to YLO links
    for plo, ylos in matrix['plo_to_ylo'].items():
        plo_idx = nodes.index(f"PLO: {plo}")
        for ylo in ylos:
            ylo_idx = nodes.index(f"YLO: {ylo}")
            links.append({
                'source': plo_idx,
                'target': ylo_idx,
                'value': results['plo_results'][plo]['score']
            })
    
    # Create Sankey diagram
    if nodes and links:
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color=node_colors
            ),
            link=dict(
                source=[link['source'] for link in links],
                target=[link['target'] for link in links],
                value=[link['value'] for link in links]
            )
        )])
        
        fig.update_layout(
            title_text="Learning Outcome Alignment Flow",
            font_size=12,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Alignment Summary Table
    st.subheader("📋 Alignment Summary")
    
    alignment_data = []
    for clo_code, clo_data in results['clo_results'].items():
        related_plos = matrix['clo_to_plo'].get(clo_code, [])
        related_ylos = []
        for plo in related_plos:
            related_ylos.extend(matrix['plo_to_ylo'].get(plo, []))
        
        alignment_data.append({
            'CLO': clo_code,
            'CLO Score': f"{clo_data['score']:.1f}%",
            'Related PLOs': ', '.join(related_plos),
            'Related YLOs': ', '.join(set(related_ylos))
        })
    
    if alignment_data:
        alignment_df = pd.DataFrame(alignment_data)
        st.dataframe(alignment_df, use_container_width=True)

# Main Application
def main():
    st.set_page_config(
        page_title="Multi-Level Assessment System",
        page_icon="🎯",
        layout="wide"
    )
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1>🎯 Multi-Level Learning Outcome Assessment</h1>
        <p style="font-size: 1.1em;">ระบบประเมินความสอดคล้องแบบหลายระดับ: CLO → PLO → YLO</p>
        <p style="font-size: 0.9em; opacity: 0.9;">
            📋 Course Level | 🎯 Program Level | 📈 Year Level Assessment
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Course Selection
    st.subheader("📚 Select Course for Assessment")
    
    course_options = {}
    for code, data in COURSE_DESCRIPTIONS.items():
        course_options[f"{code} - {data['name']}"] = code
    
    selected_course_display = st.selectbox(
        "Choose Course:",
        options=list(course_options.keys())
    )
    
    selected_course_code = course_options[selected_course_display]
    
    # Display course information
    course_info = COURSE_DESCRIPTIONS[selected_course_code]
    
    with st.expander("📖 Course Information"):
        st.write(f"**Description:** {course_info['description']}")
        st.write(f"**CLOs:** {len(course_info['clo'])}")
        st.write(f"**Mapped PLOs:** {', '.join(course_info['plo_mapping'])}")
        st.write(f"**Mapped YLOs:** {', '.join(course_info['ylo_mapping'])}")
    
    # Content Input
    st.subheader("📝 Enter Slide Content for Analysis")
    
    sample_content = f"""
    # บทที่ 1: การจัดการทรัพยากรน้ำอย่างยั่งยืน
    
    ## วัตถุประสงค์การเรียนรู้
    - เข้าใจสถานการณ์และปัญหาทรัพยากรน้ำในปัจจุบัน
    - สามารถประยุกต์ใช้เทคโนโลยี GIS ในการวิเคราะห์ข้อมูลน้ำ
    - ออกแบบระบบการจัดการน้ำแบบยั่งยืนและมีส่วนร่วมของชุมชน
    
    ## เนื้อหาบทเรียน
    
    ### 1. สถานการณ์ทรัพยากรน้ำ
    ปัจจุบันทรัพยากรน้ำเป็นปัญหาสำคัญที่ต้องการการจัดการอย่างเป็นระบบ 
    ผลกระทบจากการเปลี่ยนแปลงสภาพภูมิอากาศทำให้รูปแบบการตกของฝนเปลี่ยนแปลง
    
    ### 2. เทคโนโลยี GIS สำหรับการจัดการน้ำ
    - การใช้ระบบสารสนเทศภูมิศาสตร์ในการวิเคราะห์ลุ่มน้ำ
    - การสร้างแบบจำลองการไหลของน้ำ
    - การประเมินคุณภาพน้ำด้วยเทคโนโลยี Remote Sensing
    
    ### 3. การจัดการแบบยั่งยืน
    ระบบการจัดการน้ำที่ยั่งยืนต้องประกอบด้วย:
    - การมีส่วนร่วมของชุมชนในการตัดสินใจ
    - การใช้เทคโนโลยีที่เหมาะสม
    - การบูรณาการความรู้จากหลายสาขา
    
    ### 4. กรณีศึกษา
    การจัดการน้ำในพื้นที่ลุ่มน้ำโขง โดยใช้การวิจัยเชิงสหวิทยาการ
    และการวิเคราะห์ข้อมูลด้วยเทคนิคทางสถิติ
    """
    
    content = st.text_area(
        "📄 Slide Content:",
        value=sample_content,
        height=400,
        help="Paste your slide content here for multi-level analysis"
    )
    
    # Analysis Button
    if st.button("🔍 Perform Multi-Level Analysis", type="primary", use_container_width=True):
        if content.strip():
            with st.spinner("Performing comprehensive CLO-PLO-YLO analysis..."):
                # Initialize assessment engine
                engine = MultiLevelAssessmentEngine()
                
                # Perform multi-level analysis
                results = engine.calculate_multi_level_alignment(content, selected_course_code)
                
                # Display comprehensive results
                create_multi_level_dashboard(results)
                
                # Generate recommendations
                st.markdown("---")
                st.subheader("💡 Improvement Recommendations")
                
                recommendations = generate_improvement_recommendations(results)
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")
        else:
            st.warning("Please enter some content to analyze.")

def generate_improvement_recommendations(results):
    """Generate specific improvement recommendations"""
    recommendations = []
    
    # CLO-based recommendations
    clo_scores = [data['score'] for data in results['clo_results'].values()]
    if clo_scores:
        avg_clo = sum(clo_scores) / len(clo_scores)
        if avg_clo < 70:
            recommendations.append("ปรับปรุงเนื้อหาให้สอดคล้องกับวัตถุประสงค์รายวิชา (CLO) มากขึ้น")
    
    # PLO-based recommendations
    plo_scores = [data['score'] for data in results['plo_results'].values()]
    if plo_scores:
        avg_plo = sum(plo_scores) / len(plo_scores)
        if avg_plo < 70:
            recommendations.append("เสริมเนื้อหาให้เชื่อมโยงกับผลการเรียนรู้ของหลักสูตร (PLO) ให้ชัดเจนขึ้น")
    
    # YLO-based recommendations
    ylo_scores = [data['score'] for data in results['ylo_results'].values()]
    if ylo_scores:
        avg_ylo = sum(ylo_scores) / len(ylo_scores)
        if avg_ylo < 70:
            recommendations.append("ปรับระดับเนื้อหาให้เหมาะสมกับผลการเรียนรู้ระดับชั้นปี (YLO)")
    
    # Specific content recommendations
    low_clos = [clo for clo, data in results['clo_results'].items() if data['score'] < 70]
    if low_clos:
        recommendations.append(f"เพิ่มเนื้อหาที่เกี่ยวข้องกับ {', '.join(low_clos)}")
    
    if not recommendations:
        recommendations.append("เนื้อหามีความสอดคล้องในระดับดี ควรรักษาคุณภาพและพัฒนาต่อไป")
    
    return recommendations

if __name__ == "__main__":
    main()
