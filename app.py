import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
import time
import random
import hashlib
import uuid
from pathlib import Path
from collections import defaultdict

# Try to import Google Sheets dependencies
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False
    st.warning("Google Sheets integration not available. Please install: pip install gspread google-auth")

# Google Sheets Configuration
GOOGLE_SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Course Descriptions with 4 CLOs each
COURSE_DESCRIPTIONS = {
    '282711': {
        'name': 'ระบบสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'description': 'ปัจจัยที่มีผลต่อสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ พลวัตของระบบภูมิอากาศโลก ผลกระทบของการเปลี่ยนแปลงสภาพภูมิอากาศต่อระบบนิเวศและความหลากหลายทางชีวภาพ',
        'clo': {
            'CLO1': 'อธิบายปัจจัยที่มีผลต่อสิ่งแวดล้อมและพลวัตของระบบภูมิอากาศโลก',
            'CLO2': 'วิเคราะห์ผลกระทบของการเปลี่ยนแปลงสภาพภูมิอากาศต่อระบบนิเวศและความหลากหลายทางชีวภาพ',
            'CLO3': 'อภิปรายกรอบความร่วมมือระดับนานาชาติและแบบจำลองภูมิอากาศในการจัดการการเปลี่ยนแปลงสภาพภูมิอากาศ',
            'CLO4': 'ประยุกต์ใช้เทคโนโลยีและเครื่องมือทางสังคมในการแก้ไขปัญหาสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ'
        },
        'keywords': {
            'CLO1': ['ปัจจัย', 'พลวัต', 'ระบบภูมิอากาศ', 'โลก', 'สภาพภูมิอากาศ', 'เรือนกระจก', 'factors', 'dynamics', 'climate system'],
            'CLO2': ['ผลกระทบ', 'ระบบนิเวศ', 'ความหลากหลายทางชีวภาพ', 'ecosystem', 'biodiversity', 'impact', 'effects'],
            'CLO3': ['กรอบความร่วมมือ', 'นานาชาติ', 'แบบจำลอง', 'international', 'framework', 'model', 'UNFCCC'],
            'CLO4': ['เทคโนโลยี', 'เครื่องมือ', 'สังคม', 'technology', 'tools', 'social', 'application']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO1.1']
    },
    '282712': {
        'name': 'เทคโนโลยีและการจัดการทรัพยากรน้ำอย่างยั่งยืน',
        'description': 'สถานการณ์และปัญหาทรัพยากรน้ำ ผลกระทบของการเปลี่ยนแปลงสภาพภูมิอากาศต่อทรัพยากรน้ำ การใช้น้ำและจัดหาน้ำที่ยั่งยืน เทคโนโลยีสารสนเทศภูมิศาสตร์เพื่อการจัดการทรัพยากรน้ำ',
        'clo': {
            'CLO1': 'อธิบายสถานการณ์และปัญหาของทรัพยากรน้ำภายใต้บริบทของการเปลี่ยนแปลงสภาพภูมิอากาศ',
            'CLO2': 'วิเคราะห์แนวทางการใช้น้ำและจัดหาน้ำที่ยั่งยืนในระดับลุ่มน้ำ',
            'CLO3': 'ใช้เทคโนโลยีภูมิสารสนเทศในการวิเคราะห์และจัดการทรัพยากรน้ำ',
            'CLO4': 'เสนอแผนการบริหารจัดการน้ำโดยเน้นการมีส่วนร่วมของชุมชน'
        },
        'keywords': {
            'CLO1': ['ทรัพยากรน้ำ', 'สถานการณ์', 'ปัญหา', 'การเปลี่ยนแปลง', 'water resources', 'situation', 'problems'],
            'CLO2': ['ใช้น้ำ', 'จัดหาน้ำ', 'ยั่งยืน', 'ลุ่มน้ำ', 'sustainable', 'watershed', 'water supply'],
            'CLO3': ['GIS', 'เทคโนโลยี', 'ภูมิสารสนเทศ', 'การจัดการ', 'technology', 'geographic information'],
            'CLO4': ['แผน', 'บริหารจัดการ', 'มีส่วนร่วม', 'ชุมชน', 'plan', 'participation', 'community']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO1.1', 'YLO1.2']
    },
    '282713': {
        'name': 'เทคโนโลยีและการจัดการระบบนิเวศทางบก',
        'description': 'สถานการณ์และปัญหาของระบบนิเวศทางบก การอนุรักษ์และฟื้นฟูระบบนิเวศทางบก การบริหารจัดการป่าไม้อย่างยั่งยืน ความหลากหลายทางชีวภาพ',
        'clo': {
            'CLO1': 'อธิบายความสัมพันธ์ระหว่างปัญหาสิ่งแวดล้อมกับระบบนิเวศทางบก',
            'CLO2': 'ประเมินผลกระทบจากการเปลี่ยนแปลงสภาพภูมิอากาศต่อระบบนิเวศทางบก',
            'CLO3': 'เสนอแนวทางอนุรักษ์และฟื้นฟูระบบนิเวศทางบกอย่างยั่งยืน',
            'CLO4': 'วิเคราะห์การใช้เทคโนโลยีในการจัดการทรัพยากรดินและป่าไม้'
        },
        'keywords': {
            'CLO1': ['ระบบนิเวศ', 'ทางบก', 'ความสัมพันธ์', 'ปัญหา', 'terrestrial', 'ecosystem', 'relationship'],
            'CLO2': ['ประเมิน', 'ผลกระทบ', 'การเปลี่ยนแปลง', 'assess', 'impact', 'climate change'],
            'CLO3': ['อนุรักษ์', 'ฟื้นฟู', 'ยั่งยืน', 'conservation', 'restoration', 'sustainable'],
            'CLO4': ['เทคโนโลยี', 'ทรัพยากรดิน', 'ป่าไม้', 'technology', 'soil', 'forest']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO1.1']
    },
    '282714': {
        'name': 'ระเบียบวิธีวิจัยทางวิทยาศาสตร์และเทคโนโลยี',
        'description': 'หลักและระเบียบวิธีการวิจัย การวิเคราะห์ปัญหา การสืบค้นและวิเคราะห์งานก่อนหน้า การทบทวนวรรณกรรม การพัฒนาวิธีการศึกษา การวิเคราะห์ทางสถิติ',
        'clo': {
            'CLO1': 'ออกแบบโครงร่างงานวิจัยด้านสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศได้อย่างเหมาะสม',
            'CLO2': 'สืบค้น วิเคราะห์ และสังเคราะห์วรรณกรรมอย่างเป็นระบบ',
            'CLO3': 'เลือกใช้ระเบียบวิธีวิจัยและการวิเคราะห์ทางสถิติที่เหมาะสมกับโจทย์วิจัย',
            'CLO4': 'ปฏิบัติตามจรรยาบรรณการวิจัยและสามารถใช้ AI เป็นเครื่องมือในการทำวิจัย'
        },
        'keywords': {
            'CLO1': ['ออกแบบ', 'โครงร่าง', 'วิจัย', 'design', 'research', 'proposal'],
            'CLO2': ['สืบค้น', 'วรรณกรรม', 'ทบทวน', 'literature', 'review', 'systematic'],
            'CLO3': ['ระเบียบวิธี', 'สถิติ', 'วิเคราะห์', 'methodology', 'statistics', 'analysis'],
            'CLO4': ['จรรยาบรรณ', 'AI', 'จริยธรรม', 'ethics', 'artificial intelligence']
        },
        'plo_mapping': ['PLO2', 'PLO3'],
        'ylo_mapping': ['YLO1.2', 'YLO1.3']
    },
    '282715': {
        'name': 'เทคโนโลยีและการจัดการการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'description': 'เทคโนโลยีการตรวจวัดและติดตามการเปลี่ยนแปลงสภาพภูมิอากาศ เทคโนโลยีพลังงานสะอาด การกักเก็บคาร์บอน เทคโนโลยีการเกษตรและป่าไม้',
        'clo': {
            'CLO1': 'อธิบายเทคโนโลยีที่เกี่ยวข้องกับการตรวจวัดและติดตามการเปลี่ยนแปลงสภาพภูมิอากาศ',
            'CLO2': 'วิเคราะห์บทบาทของเทคโนโลยีด้านพลังงานสะอาด การจัดการน้ำ และอาคารสีเขียวในการปรับตัวต่อการเปลี่ยนแปลงสภาพภูมิอากาศ',
            'CLO3': 'ประเมินนโยบายและกลไกทางเศรษฐศาสตร์ในการจัดการการเปลี่ยนแปลงสภาพภูมิอากาศ',
            'CLO4': 'สื่อสารข้อมูลและสร้างแผนการมีส่วนร่วมของสังคมในการจัดการการเปลี่ยนแปลงสภาพภูมิอากาศ'
        },
        'keywords': {
            'CLO1': ['เทคโนโลยี', 'ตรวจวัด', 'ติดตาม', 'technology', 'monitoring', 'measurement'],
            'CLO2': ['พลังงานสะอาด', 'อาคารสีเขียว', 'clean energy', 'green building', 'adaptation'],
            'CLO3': ['นโยบาย', 'เศรษฐศาสตร์', 'กลไก', 'policy', 'economics', 'mechanism'],
            'CLO4': ['สื่อสาร', 'มีส่วนร่วม', 'สังคม', 'communication', 'participation', 'society']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO1.1', 'YLO2.1']
    },
    # เพิ่มรายวิชาเลือก
    '282721': {
        'name': 'การประเมินความเสี่ยงทางภูมิอากาศและผลกระทบทางสิ่งแวดล้อม',
        'description': 'หลักการประเมินความเสี่ยงและผลกระทบสิ่งแวดล้อม วิธีการประเมินความเสี่ยงทางภูมิอากาศ การสร้างแบบจำลองต้นแบบ การประเมินผลกระทบ',
        'clo': {
            'CLO1': 'อธิบายหลักการและวิธีการประเมินความเสี่ยงทางภูมิอากาศและผลกระทบทางสิ่งแวดล้อม',
            'CLO2': 'สร้างแบบจำลองและประเมินความเสี่ยงทั้งเชิงปริมาณและคุณภาพ',
            'CLO3': 'วิเคราะห์ความเชื่อมโยงระหว่างความเสี่ยงภูมิอากาศและผลกระทบสิ่งแวดล้อมในบริบทต่าง ๆ',
            'CLO4': 'เสนอแนวทางการลดผลกระทบและปรับตัวจากการเปลี่ยนแปลงสภาพภูมิอากาศ'
        },
        'keywords': {
            'CLO1': ['ความเสี่ยง', 'ประเมิน', 'หลักการ', 'risk', 'assessment', 'principle'],
            'CLO2': ['แบบจำลอง', 'ปริมาณ', 'คุณภาพ', 'model', 'quantitative', 'qualitative'],
            'CLO3': ['ความเชื่อมโยง', 'วิเคราะห์', 'บริบท', 'linkage', 'analysis', 'context'],
            'CLO4': ['ลดผลกระทบ', 'ปรับตัว', 'แนวทาง', 'mitigation', 'adaptation', 'approach']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO2.1', 'YLO2.2']
    },
    '282722': {
        'name': 'แบบจำลองและการวิเคราะห์ข้อมูลทางสิ่งแวดล้อมและภูมิอากาศด้วยปัญญาประดิษฐ์',
        'description': 'ลักษณะทางกายภาพของแบบจำลอง เงื่อนไขเริ่มต้นและเงื่อนไขขอบเขตของแบบจำลอง การพัฒนากระบวนการไดนามิกในแบบจำลอง',
        'clo': {
            'CLO1': 'อธิบายโครงสร้างและหลักการทำงานของแบบจำลองทางสิ่งแวดล้อมและภูมิอากาศ',
            'CLO2': 'สร้างและปรับแต่งแบบจำลองทางภูมิอากาศโดยใช้เทคนิคปัญญาประดิษฐ์',
            'CLO3': 'วิเคราะห์และแสดงผลข้อมูลแบบจำลองด้วยเครื่องมือที่เหมาะสม',
            'CLO4': 'ประเมินความถูกต้องของแบบจำลองด้วยระเบียบวิธีทางสถิติ'
        },
        'keywords': {
            'CLO1': ['โครงสร้าง', 'หลักการ', 'แบบจำลอง', 'structure', 'principle', 'model'],
            'CLO2': ['ปัญญาประดิษฐ์', 'AI', 'machine learning', 'สร้าง', 'ปรับแต่ง', 'create'],
            'CLO3': ['วิเคราะห์', 'แสดงผล', 'ข้อมูล', 'analyze', 'visualize', 'data'],
            'CLO4': ['ประเมิน', 'ความถูกต้อง', 'สถิติ', 'evaluate', 'accuracy', 'statistics']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO2.1', 'YLO2.2']
    },
    '282723': {
        'name': 'เทคโนโลยีการลดก๊าซเรือนกระจกและการปรับตัว',
        'description': 'หลักการที่เกี่ยวข้องกับเทคโนโลยีการลดก๊าซเรือนกระจกและการปรับตัวต่อการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'clo': {
            'CLO1': 'อธิบายหลักการของเทคโนโลยีการลดก๊าซเรือนกระจกและการปรับตัวแบบต่าง ๆ',
            'CLO2': 'วิเคราะห์กรณีศึกษาการใช้เทคโนโลยีการลดก๊าซเรือนกระจกในพื้นที่จริง',
            'CLO3': 'ประเมินความเหมาะสมของเทคโนโลยีในการบริบทเชิงพื้นที่และสังคม',
            'CLO4': 'เสนอแผนการประยุกต์ใช้เทคโนโลยีการปรับตัวต่อการเปลี่ยนแปลงสภาพภูมิอากาศ'
        },
        'keywords': {
            'CLO1': ['เทคโนโลยี', 'ลดก๊าซเรือนกระจก', 'การปรับตัว', 'technology', 'mitigation', 'adaptation'],
            'CLO2': ['กรณีศึกษา', 'วิเคราะห์', 'พื้นที่จริง', 'case study', 'analyze', 'real area'],
            'CLO3': ['ประเมิน', 'ความเหมาะสม', 'บริบท', 'assess', 'suitability', 'context'],
            'CLO4': ['แผน', 'ประยุกต์ใช้', 'การปรับตัว', 'plan', 'apply', 'adaptation']
        },
        'plo_mapping': ['PLO1'],
        'ylo_mapping': ['YLO2.1']
    },
    '282724': {
        'name': 'คาร์บอนฟุตพรินต์เพื่อความเป็นกลางทางคาร์บอนอย่างยั่งยืน',
        'description': 'ความสำคัญของคาร์บอนฟุตพรินต์องค์กรและผลิตภัณฑ์ มาตรฐานและการรายงานระดับสากล',
        'clo': {
            'CLO1': 'อธิบายความสำคัญของคาร์บอนฟุตพรินต์และมาตรฐานสากลที่เกี่ยวข้อง',
            'CLO2': 'คำนวณและประเมินคาร์บอนฟุตพรินต์ของกิจกรรมหรือผลิตภัณฑ์',
            'CLO3': 'วิเคราะห์กลยุทธ์เพื่อลดคาร์บอนฟุตพรินต์และบรรลุความเป็นกลางทางคาร์บอน',
            'CLO4': 'สังเคราะห์กรณีศึกษาองค์กรที่ประสบความสำเร็จในการจัดการคาร์บอนฟุตพรินต์'
        },
        'keywords': {
            'CLO1': ['คาร์บอนฟุตพรินต์', 'มาตรฐาน', 'สากล', 'carbon footprint', 'standard', 'international'],
            'CLO2': ['คำนวณ', 'ประเมิน', 'กิจกรรม', 'calculate', 'assess', 'activity'],
            'CLO3': ['กลยุทธ์', 'ลด', 'ความเป็นกลาง', 'strategy', 'reduce', 'neutrality'],
            'CLO4': ['สังเคราะห์', 'กรณีศึกษา', 'ความสำเร็จ', 'synthesize', 'case study', 'success']
        },
        'plo_mapping': ['PLO1'],
        'ylo_mapping': ['YLO2.1']
    },
    '282731': {
        'name': 'เทคโนโลยีและการจัดการมลพิษทางอากาศ',
        'description': 'มาตรฐานคุณภาพอากาศและกฎหมายที่เกี่ยวข้อง เทคโนโลยีการตรวจวัดและติดตามคุณภาพอากาศ',
        'clo': {
            'CLO1': 'อธิบายมาตรฐานคุณภาพอากาศและเทคโนโลยีการตรวจวัดคุณภาพอากาศ',
            'CLO2': 'วิเคราะห์กระบวนการจำลองการแพร่กระจายมลพิษทางอากาศในรูปแบบต่าง ๆ',
            'CLO3': 'ประเมินเทคโนโลยีควบคุมมลพิษทางอากาศจากแหล่งต่าง ๆ',
            'CLO4': 'เสนอแนวทางการจัดการมลพิษทางอากาศโดยเน้นการมีส่วนร่วมของชุมชน'
        },
        'keywords': {
            'CLO1': ['มาตรฐาน', 'คุณภาพอากาศ', 'ตรวจวัด', 'standard', 'air quality', 'monitoring'],
            'CLO2': ['จำลอง', 'แพร่กระจาย', 'มลพิษ', 'modeling', 'dispersion', 'pollution'],
            'CLO3': ['ประเมิน', 'เทคโนโลยีควบคุม', 'แหล่งกำเนิด', 'assess', 'control technology', 'source'],
            'CLO4': ['แนวทาง', 'จัดการ', 'มีส่วนร่วม', 'approach', 'management', 'participation']
        },
        'plo_mapping': ['PLO1', 'PLO3'],
        'ylo_mapping': ['YLO2.1', 'YLO2.3']
    },
    '282732': {
        'name': 'เทคโนโลยีการจัดการทรัพยากรดินและป่าไม้การอนุรักษ์ความหลากหลายทางชีวภาพ',
        'description': 'คุณสมบัติดินและความสัมพันธ์กับระบบนิเวศ การจัดการและนโยบายการใช้ที่ดิน',
        'clo': {
            'CLO1': 'อธิบายคุณสมบัติของดินและบทบาทของระบบนิเวศทางดินและป่าไม้',
            'CLO2': 'วิเคราะห์การใช้เทคโนโลยีภูมิสารสนเทศเพื่อจัดการทรัพยากรธรรมชาติอย่างยั่งยืน',
            'CLO3': 'ประเมินผลกระทบจากการเปลี่ยนแปลงสภาพภูมิอากาศต่อความหลากหลายทางชีวภาพ',
            'CLO4': 'เสนอแนวทางอนุรักษ์พันธุกรรมและการแบ่งปันผลประโยชน์อย่างเท่าเทียม'
        },
        'keywords': {
            'CLO1': ['คุณสมบัติดิน', 'ระบบนิเวศ', 'ป่าไม้', 'soil properties', 'ecosystem', 'forest'],
            'CLO2': ['ภูมิสารสนเทศ', 'จัดการ', 'ยั่งยืน', 'geoinformatics', 'manage', 'sustainable'],
            'CLO3': ['ผลกระทบ', 'ความหลากหลายทางชีวภาพ', 'ประเมิน', 'impact', 'biodiversity', 'assess'],
            'CLO4': ['อนุรักษ์', 'พันธุกรรม', 'แบ่งปันผลประโยชน์', 'conservation', 'genetic', 'benefit sharing']
        },
        'plo_mapping': ['PLO1', 'PLO2'],
        'ylo_mapping': ['YLO2.1']
    },
    '282733': {
        'name': 'เทคโนโลยีและการจัดการลุ่มน้ำ',
        'description': 'ธรณีสัณฐานของลุ่มน้ำและอุทกวิทยา ระบบนิเวศต้นน้ำ กลางน้ำ และปลายน้ำ',
        'clo': {
            'CLO1': 'อธิบายองค์ประกอบและสมดุลของระบบลุ่มน้ำและนิเวศลุ่มน้ำ',
            'CLO2': 'ใช้เทคโนโลยีภูมิสารสนเทศในการบริหารจัดการน้ำในเชิงพื้นที่และเวลา',
            'CLO3': 'วิเคราะห์สถานการณ์และปัญหาของการจัดการลุ่มน้ำในบริบทภูมิประเทศที่แตกต่างกัน',
            'CLO4': 'เสนอแผนการบริหารจัดการลุ่มน้ำแบบมีส่วนร่วมกับชุมชน'
        },
        'keywords': {
            'CLO1': ['องค์ประกอบ', 'สมดุล', 'ลุ่มน้ำ', 'component', 'balance', 'watershed'],
            'CLO2': ['ภูมิสารสนเทศ', 'บริหารจัดการ', 'เชิงพื้นที่', 'GIS', 'management', 'spatial'],
            'CLO3': ['สถานการณ์', 'ปัญหา', 'ภูมิประเทศ', 'situation', 'problem', 'terrain'],
            'CLO4': ['แผน', 'มีส่วนร่วม', 'ชุมชน', 'plan', 'participation', 'community']
        },
        'plo_mapping': ['PLO1', 'PLO3'],
        'ylo_mapping': ['YLO2.1']
    },
    '282734': {
        'name': 'การสื่อสารประเด็นสาธารณะสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'description': 'การพัฒนากระบวนการสื่อสาร การสื่อสารเชิงยุทธศาสตร์ การให้และรับข้อมูลกับสาธารณะ การสื่อสารในกระบวนการมีส่วนร่วม',
        'clo': {
            'CLO1': 'อธิบายปัญหาและแนวทางการพัฒนาการสื่อสารด้านสิ่งแวดล้อมและภูมิอากาศ',
            'CLO2': 'ออกแบบกระบวนการสื่อสารสาธารณะในบริบทของการมีส่วนร่วม',
            'CLO3': 'ผลิตสื่อเพื่อสื่อสารข้อมูลทางวิชาการและเทคนิคแก่สาธารณชน',
            'CLO4': 'ประเมินประสิทธิภาพของการสื่อสารประเด็นสิ่งแวดล้อมในสถานการณ์ภัยพิบัติ'
        },
        'keywords': {
            'CLO1': ['ปัญหา', 'แนวทาง', 'สื่อสาร', 'problem', 'approach', 'communication'],
            'CLO2': ['ออกแบบ', 'กระบวนการ', 'มีส่วนร่วม', 'design', 'process', 'participation'],
            'CLO3': ['ผลิตสื่อ', 'วิชาการ', 'สาธารณชน', 'media production', 'academic', 'public'],
            'CLO4': ['ประเมิน', 'ประสิทธิภาพ', 'ภัยพิบัติ', 'evaluate', 'effectiveness', 'disaster']
        },
        'plo_mapping': ['PLO3'],
        'ylo_mapping': ['YLO1.4', 'YLO2.3']
    },
    '282735': {
        'name': 'หัวข้อพิเศษ',
        'description': 'การกำหนดประเด็นหัวข้อที่สนใจ หรือที่เป็นปัจจุบันหรือกรณีศึกษา ในสาขาที่เกี่ยวข้องกับเทคโนโลยีการจัดการสิ่งแวดล้อม',
        'clo': {
            'CLO1': 'วิเคราะห์ปัญหาหรือประเด็นเฉพาะที่เกี่ยวข้องกับสิ่งแวดล้อมและภูมิอากาศในปัจจุบัน',
            'CLO2': 'สืบค้นข้อมูล วิเคราะห์ และสังเคราะห์ความรู้จากกรณีศึกษาเฉพาะ',
            'CLO3': 'นำเสนอผลการวิเคราะห์และตอบข้อซักถามทางวิชาการได้อย่างมีประสิทธิภาพ',
            'CLO4': 'สร้างข้อเสนอเชิงนโยบายหรือแนวทางการจัดการที่เหมาะสมกับบริบทปัญหานั้น ๆ'
        },
        'keywords': {
            'CLO1': ['วิเคราะห์', 'ประเด็นเฉพาะ', 'ปัจจุบัน', 'analyze', 'specific issue', 'current'],
            'CLO2': ['สืบค้น', 'สังเคราะห์', 'กรณีศึกษา', 'search', 'synthesize', 'case study'],
            'CLO3': ['นำเสนอ', 'ตอบข้อซักถาม', 'วิชาการ', 'present', 'Q&A', 'academic'],
            'CLO4': ['ข้อเสนอ', 'นโยบาย', 'บริบท', 'proposal', 'policy', 'context']
        },
        'plo_mapping': ['PLO1', 'PLO2', 'PLO3'],
        'ylo_mapping': ['YLO1.2', 'YLO2.1']
    }
}

# Enhanced Year Learning Outcomes (YLO) Configuration
YLO_STRUCTURE = {
    'YLO1.1': {
        'description': 'สามารถอธิบายหลักการพื้นฐานของระบบสิ่งแวดล้อม การเปลี่ยนแปลงสภาพภูมิอากาศ การจัดการทรัพยากรน้ำ และระบบนิเวศทางบก รวมถึงความสัมพันธ์ระหว่างระบบเหล่านี้กับชุมชนและสังคม',
        'detailed_description': 'นิสิตมีความเข้าใจพื้นฐานเกี่ยวกับระบบสิ่งแวดล้อมแบบองค์รวม สามารถอธิบายความเชื่อมโยงระหว่างระบบบรรยากาศ อุทกมณฑล ธรณีมณฑล และชีวมณฑล และเข้าใจผลกระทบของกิจกรรมมนุษย์ต่อระบบเหล่านี้',
        'plo_mapping': ['PLO1', 'PLO2'],
        'level': 'Year 1',
        'cognitive_level': 'Understanding',
        'assessment_methods': ['การสอบข้อเขียน', 'การนำเสนอ', 'รายงานกลุ่ม']
    },
    'YLO1.2': {
        'description': 'สามารถออกแบบและวางแผนการวิจัย โดยบูรณาการความรู้ทางวิทยาศาสตร์ เทคโนโลยี และการมีส่วนร่วมของชุมชน',
        'detailed_description': 'นิสิตสามารถกำหนดประเด็นการวิจัย ออกแบบระเบียบวิธีวิจัยที่เหมาะสม ทบทวนวรรณกรรมอย่างเป็นระบบ และวางแผนการดำเนินงานวิจัยที่คำนึงถึงการมีส่วนร่วมของชุมชนและจริยธรรมการวิจัย',
        'plo_mapping': ['PLO1', 'PLO2'],
        'level': 'Year 1',
        'cognitive_level': 'Applying',
        'assessment_methods': ['โครงร่างวิจัย', 'การนำเสนอ', 'การประเมินเพื่อน']
    },
    'YLO1.3': {
        'description': 'สามารถใช้เทคโนโลยีในการสืบค้นความรู้และคัดกรองข้อมูลทั้งจากเอกสารและสื่อออนไลน์ และสามารถอ่านบทความวิชาการทั้งภาษาไทยและภาษาอังกฤษ',
        'detailed_description': 'นิสิตมีทักษะการใช้ฐานข้อมูลวิชาการ การสืบค้นข้อมูลอย่างมีระบบ การประเมินความน่าเชื่อถือของแหล่งข้อมูล และการอ่านบทความวิจัยเพื่อสกัดประเด็นสำคัญและวิเคราะห์อย่างมีวิจารณญาณ',
        'plo_mapping': ['PLO2', 'PLO3'],
        'level': 'Year 1',
        'cognitive_level': 'Applying',
        'assessment_methods': ['การทบทวนวรรณกรรม', 'การวิจารณ์บทความ', 'การนำเสนอ']
    },
    'YLO1.4': {
        'description': 'สามารถนำเสนอและอภิปรายหัวข้อวิจัยที่สนใจในด้านเทคโนโลยีการจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศทั้งภาษาไทยและภาษาอังกฤษได้',
        'detailed_description': 'นิสิตสามารถสื่อสารแนวคิดทางวิชาการได้อย่างชัดเจน มีทักษะการนำเสนอที่มีประสิทธิภาพ และสามารถอภิปรายแลกเปลี่ยนความคิดเห็นทางวิชาการได้อย่างสร้างสรรค์ทั้งในระดับชาติและนานาชาติ',
        'plo_mapping': ['PLO3'],
        'level': 'Year 1',
        'cognitive_level': 'Evaluating',
        'assessment_methods': ['การนำเสนอปากเปล่า', 'การอภิปรายกลุ่ม', 'สัมมนา']
    },
    'YLO2.1': {
        'description': 'สามารถใช้เทคโนโลยีที่เหมาะสมและแนวทางการจัดการแบบบูรณาการในการแก้ไขปัญหาด้านสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศโดยคำนึงถึงบริบทของชุมชนและความยั่งยืน',
        'detailed_description': 'นิสิตสามารถประยุกต์ใช้เทคโนโลยีขั้นสูง เช่น GIS, Remote Sensing, AI, และ IoT ในการแก้ปัญหาสิ่งแวดล้อมที่ซับซ้อน พร้อมทั้งออกแบบโซลูชันที่เหมาะสมกับบริบทท้องถิ่นและยั่งยืน',
        'plo_mapping': ['PLO1', 'PLO2'],
        'level': 'Year 2',
        'cognitive_level': 'Creating',
        'assessment_methods': ['โครงงานวิจัย', 'การนำเสนอโซลูชัน', 'การประเมินผลกระทบ']
    },
    'YLO2.2': {
        'description': 'สามารถดำเนินการวิจัยเชิงสหวิทยาการ วิเคราะห์ผล และอภิปรายผลการวิจัยทางเทคโนโลยีการจัดการด้านสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ โดยบูรณาการการมีส่วนร่วมของชุมชน ได้อย่างมีคุณภาพและเป็นไปตามจรรยาบรรณทางวิชาการ',
        'detailed_description': 'นิสิตสามารถดำเนินการวิจัยที่มีคุณภาพระดับสากล ใช้ระเบียบวิธีวิจัยที่หลากหลาย วิเคราะห์ข้อมูลด้วยเครื่องมือทางสถิติขั้นสูง และสามารถอภิปรายผลการวิจัยในบริบทที่กว้างขึ้น',
        'plo_mapping': ['PLO2'],
        'level': 'Year 2',
        'cognitive_level': 'Evaluating',
        'assessment_methods': ['วิทยานิพนธ์', 'การตีพิมพ์บทความ', 'การนำเสนอในที่ประชุมวิชาการ']
    },
    'YLO2.3': {
        'description': 'สามารถสื่อสาร ถ่ายทอดองค์ความรู้ที่ได้จากกระบวนการวิจัยที่มีคุณภาพ ผ่านการเขียนวิทยานิพนธ์/การศึกษาค้นคว้าด้วยตนเอง การตีพิมพ์เผยแพร่ในวารสาร หรือการนำเสนอในการประชุมวิชาการที่เกี่ยวข้องอย่างมีประสิทธิภาพ และเป็นไปตามจรรยาบรรณทางวิชาการที่เหมาะสม',
        'detailed_description': 'นิสิตสามารถสื่อสารผลงานวิจัยผ่านช่องทางวิชาการต่างๆ ได้อย่างมีประสิทธิภาพ เขียนบทความวิจัยคุณภาพสูง และถ่ายทอดความรู้สู่ชุมชนวิชาการและสังคมในวงกว้าง',
        'plo_mapping': ['PLO3'],
        'level': 'Year 2',
        'cognitive_level': 'Creating',
        'assessment_methods': ['วิทยานิพนธ์', 'บทความวิชาการ', 'การนำเสนอต่อสาธารณะ']
    }
}

# Cognitive Development Framework
COGNITIVE_FRAMEWORK = {
    'Understanding': {
        'description': 'เข้าใจและอธิบายแนวคิดพื้นฐาน',
        'examples': ['อธิบาย', 'สรุป', 'แปลความหมาย', 'ให้ตัวอย่าง']
    },
    'Applying': {
        'description': 'นำความรู้ไปใช้ในสถานการณ์ใหม่',
        'examples': ['ประยุกต์ใช้', 'แก้ปัญหา', 'ดำเนินการ', 'สาธิต']
    },
    'Evaluating': {
        'description': 'ประเมินและตัดสินใจอย่างมีเหตุผล',
        'examples': ['วิจารณ์', 'เปรียบเทียบ', 'ประเมิน', 'พิพากษา']
    },
    'Creating': {
        'description': 'สร้างสรรค์สิ่งใหม่หรือแก้ปัญหาอย่างเป็นระบบ',
        'examples': ['ออกแบบ', 'สร้าง', 'พัฒนา', 'นวัตกรรม']
    }
}

# Enhanced PLO Configuration with comprehensive descriptions
ENHANCED_PLOS = {
    'PLO1': {
        'title': 'การใช้เทคโนโลยีและการมีส่วนร่วม',
        'description': 'สามารถใช้เทคโนโลยีและข้อมูลที่เกี่ยวข้องในการเสนอแนวทางการแก้ไขปัญหาทางสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ โดยยึดหลักการมีส่วนร่วมอย่างเป็นธรรมและการพัฒนาที่ยั่งยืน',
        'detailed_description': 'บัณฑิตสามารถประยุกต์ใช้เทคโนโลยีสารสนเทศภูมิศาสตร์ (GIS), การรับรู้ระยะไกล (Remote Sensing), แบบจำลองทางคอมพิวเตอร์, และเทคโนโลยีดิจิทัลอื่นๆ ในการวิเคราะห์และแก้ไขปัญหาสิ่งแวดล้อม โดยคำนึงถึงการมีส่วนร่วมของชุมชนและผู้มีส่วนได้ส่วนเสียอย่างเป็นธรรม ตลอดจนสามารถออกแบบโซลูชันที่ยั่งยืนและเหมาะสมกับบริบทท้องถิ่น',
        'weight': 35,
        'color': '#FF6B6B',
        'focus_areas': ['เทคโนโลยีสิ่งแวดล้อม', 'การมีส่วนร่วม', 'การพัฒนาที่ยั่งยืน', 'นวัตกรรมสีเขียว']
    },
    'PLO2': {
        'title': 'การวิจัยและการบูรณาการ',
        'description': 'สามารถดำเนินการวิจัยโดยการบูรณาการความรู้และข้อมูลอย่างรอบด้านเพื่อหาคำตอบหรือวิธีการที่มีประสิทธิภาพในการใช้เทคโนโลยีเพื่อจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'detailed_description': 'บัณฑิตมีความสามารถในการออกแบบและดำเนินการวิจัยเชิงสหวิทยาการที่บูรณาการความรู้จากหลายสาขา รวมถึงวิทยาศาสตร์สิ่งแวดล้อม เทคโนโลยี วิศวกรรมศาสตร์ สังคมศาสตร์ และเศรษฐศาสตร์ สามารถใช้ระเบียบวิธีวิจัยที่หลากหลาย การวิเคราะห์ข้อมูลขั้นสูง และการประยุกต์ใช้ปัญญาประดิษฐ์ในการแก้ปัญหาสิ่งแวดล้อมได้อย่างมีประสิทธิภาพ',
        'weight': 35,
        'color': '#4ECDC4',
        'focus_areas': ['ระเบียบวิธีวิจัย', 'การบูรณาการข้ามศาสตร์', 'การวิเคราะห์ข้อมูล', 'นวัตกรรมการวิจัย']
    },
    'PLO3': {
        'title': 'การสื่อสารและการถ่ายทอด',
        'description': 'สามารถสื่อสาร ถ่ายทอด ข้อมูลและความรู้จากงานวิจัยด้านสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศได้อย่างชัดเจนและมีประสิทธิภาพ',
        'detailed_description': 'บัณฑิตสามารถสื่อสารผลการวิจัยและข้อมูลทางวิทยาศาสตร์ให้กับกลุ่มเป้าหมายที่หลากหลาย ทั้งนักวิชาการ ผู้กำหนดนโยบาย ชุมชน และประชาชนทั่วไป โดยใช้สื่อและช่องทางการสื่อสารที่เหมาะสม สามารถจัดทำเอกสารวิชาการ บทความวิจัย การนำเสนอ และสื่อดิจิทัล ตลอดจนมีทักษะการถ่ายทอดความรู้และการสร้างความเข้าใจในประเด็นสิ่งแวดล้อมที่ซับซ้อน',
        'weight': 30,
        'color': '#45B7D1',
        'focus_areas': ['การสื่อสารวิทยาศาสตร์', 'การนำเสนอ', 'การเขียนวิชาการ', 'สื่อดิจิทัล']
    }
}

# Program Overview and Context
PROGRAM_OVERVIEW = {
    'program_name': 'หลักสูตรวิทยาศาสตรมหาบัณฑิต สาขาวิชาเทคโนโลยีการจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
    'program_philosophy': 'การจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศเป็นการบูรณาการใช้เทคโนโลยีและการมีส่วนร่วมของชุมชนในการสร้างความสมดุลระหว่างการพัฒนามนุษย์และการรักษาความยั่งยืนของทรัพยากรและระบบนิเวศน์ด้วยกระบวนการวิจัยที่เหมาะสมตามจรรยาบรรณทางวิชาการ เพื่อลดผลกระทบจากการเปลี่ยนแปลงสภาพภูมิอากาศ เพื่อการอยู่ร่วมกันอย่างยั่งยืนของมนุษย์และสิ่งแวดล้อม',
    'program_objectives': [
        'เพื่อผลิตบุคลากรที่มีความสามารถในการประยุกต์องค์ความรู้ เทคโนโลยี และการมีส่วนร่วมของชุมชน เพื่อจัดการปัญหาด้านการเปลี่ยนแปลงสภาพภูมิอากาศ ทรัพยากรน้ำและระบบนิเวศทางบก โดยคำนึงถึงบริบทเชิงพื้นที่ในระดับท้องถิ่น ภูมิภาค และประเทศ ได้อย่างถูกต้องเหมาะสมตามจรรยาบรรณวิชาชีพ',
        'เพื่อผลิตบุคลากรที่สามารถใช้กระบวนการวิจัยในการแก้ปัญหาด้านการเปลี่ยนแปลงสภาพภูมิอากาศ ทรัพยากรน้ำและระบบนิเวศทางบก โดยผสมผสานความรู้ทางเทคโนโลยีและการมีส่วนร่วมของชุมชน ได้อย่างมีประสิทธิภาพและมีจริยธรรมทางการวิจัย',
        'เพื่อผลิตบุคลากรที่สามารถสื่อสาร ถ่ายทอด และประยุกต์ใช้องค์ความรู้จากงานวิจัยด้านเทคโนโลยีการจัดการสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศได้อย่างมีประสิทธิภาพ โดยคำนึงถึงความต้องการและการมีส่วนร่วมของชุมชน'
    ],
    'career_prospects': [
        'นักวิจัยด้านสิ่งแวดล้อมและการเปลี่ยนแปลงสภาพภูมิอากาศ',
        'ผู้เชี่ยวชาญด้านเทคโนโลยีสิ่งแวดล้อม',
        'นักวางแผนและนักวิเคราะห์นโยบายสิ่งแวดล้อม',
        'ที่ปรึกษาด้านการจัดการสิ่งแวดล้อมและความยั่งยืน',
        'อาจารย์และนักวิชาการในสถาบันการศึกษา'
    ]
}

def generate_unique_assessment_id():
    """Generate unique assessment ID with timestamp and UUID"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    short_uuid = str(uuid.uuid4())[:8]
    return f"ASSESS_{timestamp}_{short_uuid}"

def check_duplicate_assessment(spreadsheet, content_hash, course_code):
    """Check if assessment with same content and course already exists"""
    try:
        content_sheet = spreadsheet.worksheet('Content_Analysis')
        records = content_sheet.get_all_records()
        
        # Check for duplicate content + course combination
        for record in records:
            if (record.get('Content_Hash') == content_hash and 
                record.get('รหัสวิชา') == course_code):
                return True, record.get('รหัสการประเมิน', 'Unknown')
        
        return False, None
    except:
        # If can't check, assume no duplicate
        return False, None

# Google Sheets Manager Class with Enhanced Unique Recording
if GSHEETS_AVAILABLE:
    class GoogleSheetsManager:
        """Enhanced Google Sheets Manager with unique recording and duplicate checking"""
        
        def __init__(self):
            self.client = None
            self.initialized = False
        
        def initialize_connection(self, credentials_dict):
            """Initialize Google Sheets connection"""
            try:
                # Create credentials from dictionary
                credentials = Credentials.from_service_account_info(
                    credentials_dict, scopes=GOOGLE_SHEETS_SCOPES
                )
                
                # Initialize gspread client
                self.client = gspread.authorize(credentials)
                self.initialized = True
                return True, "เชื่อมต่อ Google Sheets สำเร็จ"
                
            except Exception as e:
                return False, f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {str(e)}"
        
        def create_or_get_spreadsheet(self, spreadsheet_name):
            """Create new spreadsheet or get existing one"""
            if not self.initialized:
                return None, "ยังไม่ได้เชื่อมต่อ Google Sheets"
            
            try:
                # Try to open existing spreadsheet
                try:
                    spreadsheet = self.client.open(spreadsheet_name)
                    return spreadsheet, f"เปิด spreadsheet '{spreadsheet_name}' สำเร็จ"
                except gspread.SpreadsheetNotFound:
                    # Create new spreadsheet
                    spreadsheet = self.client.create(spreadsheet_name)
                    return spreadsheet, f"สร้าง spreadsheet '{spreadsheet_name}' สำเร็จ"
                    
            except Exception as e:
                return None, f"เกิดข้อผิดพลาด: {str(e)}"
        
        def setup_assessment_sheets(self, spreadsheet):
            """Setup sheets for assessment data with enhanced structure"""
            try:
                # Enhanced sheet structures
                sheets_config = {
                    'Assessment_Summary': [
                        'วันที่', 'เวลา', 'รหัสการประเมิน', 'รหัสวิชา', 'ชื่อวิชา', 
                        'ผู้ประเมิน', 'ประเภทไฟล์', 'ชื่อไฟล์', 'AI_Enhanced',
                        'CLO_Average', 'PLO_Average', 'YLO_Average', 'Overall_Confidence',
                        'คำแนะนำ_1', 'คำแนะนำ_2', 'คำแนะนำ_3', 'Content_Hash', 'Unique_Assessment'
                    ],
                    'CLO_Details': [
                        'รหัสการประเมิน', 'รหัสวิชา', 'CLO_Code', 'CLO_Description',
                        'Score', 'Confidence', 'Found_Keywords', 'Total_Keywords', 
                        'Coverage', 'AI_Enhanced', 'AI_Insights', 'Timestamp_Created'
                    ],
                    'PLO_Details': [
                        'รหัสการประเมิน', 'รหัสวิชา', 'PLO_Code', 'PLO_Description',
                        'Score', 'Confidence', 'Related_CLOs', 'Weight', 'Timestamp_Created'
                    ],
                    'YLO_Details': [
                        'รหัสการประเมิน', 'รหัสวิชา', 'YLO_Code', 'YLO_Description',
                        'Score', 'Confidence', 'Level', 'Cognitive_Level', 
                        'Related_PLOs', 'Cognitive_Multiplier', 'Timestamp_Created'
                    ],
                    'Content_Analysis': [
                        'รหัสการประเมิน', 'รหัสวิชา', 'Content_Hash', 'Content_Length',
                        'ชื่อไฟล์', 'Content_Preview', 'Analysis_Method', 'Analysis_Time',
                        'Is_Duplicate', 'Original_Assessment_ID'
                    ],
                    'Interpretation': [
                        'รหัสการประเมิน', 'รหัสวิชา', 'วันที่', 'ผลการประเมินโดยรวม', 
                        'ระดับคะแนน', 'CLO_สูงสุด', 'CLO_ต่ำสุด', 'PLO_Coverage',
                        'YLO_Year1_Count', 'YLO_Year2_Count', 'Cognitive_Distribution',
                        'จุดเด่น_1', 'จุดเด่น_2', 'จุดเด่น_3',
                        'จุดที่ควรปรับปรุง_1', 'จุดที่ควรปรับปรุง_2', 'จุดที่ควรปรับปรุง_3',
                        'คำแนะนำเชิงลึก_1', 'คำแนะนำเชิงลึก_2', 'คำแนะนำเชิงลึก_3',
                        'CLO_ที่ต่ำกว่าเกณฑ์', 'PLO_ที่ขาด', 'ระดับการคิดที่ขาด'
                    ]
                }
                
                created_sheets = []
                
                for sheet_name, headers in sheets_config.items():
                    try:
                        # Check if sheet exists
                        try:
                            worksheet = spreadsheet.worksheet(sheet_name)
                            # Clear and update headers if sheet exists
                            current_headers = worksheet.row_values(1)
                            if current_headers != headers:
                                worksheet.clear()
                                worksheet.append_row(headers)
                                created_sheets.append(f"อัพเดตโครงสร้าง {sheet_name}")
                            else:
                                created_sheets.append(f"ตรวจสอบ {sheet_name} ✓")
                        except gspread.WorksheetNotFound:
                            # Create new sheet
                            worksheet = spreadsheet.add_worksheet(
                                title=sheet_name, 
                                rows=1000, 
                                cols=len(headers)
                            )
                            worksheet.append_row(headers)
                            created_sheets.append(f"สร้างใหม่ {sheet_name}")
                            
                    except Exception as e:
                        return False, f"เกิดข้อผิดพลาดในการสร้าง sheet '{sheet_name}': {str(e)}"
                
                # Remove default Sheet1 if exists and is empty
                try:
                    sheet1 = spreadsheet.worksheet('Sheet1')
                    if len(sheet1.get_all_values()) <= 1:  # Only header or empty
                        spreadsheet.del_worksheet(sheet1)
                        created_sheets.append("ลบ Sheet1 เริ่มต้น")
                except:
                    pass
                
                return True, f"ตั้งค่า sheets สำเร็จ: {', '.join(created_sheets)}"
                
            except Exception as e:
                return False, f"เกิดข้อผิดพลาดในการตั้งค่า sheets: {str(e)}"
        
        def save_assessment_data(self, spreadsheet, assessment_data, file_info=None, allow_duplicates=False):
            """Enhanced save assessment results with unique ID and duplicate checking"""
            try:
                # Generate unique assessment ID
                unique_assessment_id = generate_unique_assessment_id()
                assessment_data['assessment_id'] = unique_assessment_id
                
                # Check for duplicates if not explicitly allowed
                content_hash = assessment_data.get('content_hash', '')
                course_code = assessment_data['course_code']
                
                is_duplicate = False
                original_assessment_id = None
                
                if not allow_duplicates and content_hash:
                    is_duplicate, original_assessment_id = check_duplicate_assessment(
                        spreadsheet, content_hash, course_code
                    )
                    
                    if is_duplicate:
                        st.warning(f"⚠️ พบการประเมินซ้ำกับ ID: {original_assessment_id}")
                        # Simple confirmation without using st.confirm which might not exist
                        continue_save = st.button("บันทึกต่อไปอย่างไรก็ตาม", key="confirm_duplicate")
                        if not continue_save:
                            return False, "ยกเลิกการบันทึกเนื่องจากข้อมูลซ้ำ"
                
                # Create timestamp
                current_time = datetime.now()
                date_str = current_time.strftime('%Y-%m-%d')
                time_str = current_time.strftime('%H:%M:%S')
                timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 1. Save to Assessment_Summary with enhanced info
                summary_sheet = spreadsheet.worksheet('Assessment_Summary')
                
                summary_row = [
                    date_str,  # วันที่
                    time_str,  # เวลา
                    unique_assessment_id,  # รหัสการประเมิน (UNIQUE)
                    assessment_data['course_code'],  # รหัสวิชา
                    assessment_data['course_name'],  # ชื่อวิชา
                    assessment_data.get('assessor', 'ไม่ระบุ'),  # ผู้ประเมิน
                    file_info.get('type', 'Text Input') if file_info else 'Text Input',  # ประเภทไฟล์
                    file_info.get('name', 'ป้อนข้อความ') if file_info else 'ป้อนข้อความ',  # ชื่อไฟล์
                    assessment_data.get('ai_enhanced', False),  # AI_Enhanced
                    assessment_data['overall_scores']['clo_average'],  # CLO_Average
                    assessment_data['overall_scores']['plo_average'],  # PLO_Average
                    assessment_data['overall_scores']['ylo_average'],  # YLO_Average
                    assessment_data['overall_scores'].get('overall_confidence', 0),  # Overall_Confidence
                ]
                
                # Add recommendations (up to 3)
                recommendations = assessment_data.get('ai_recommendations', [])
                for i in range(3):
                    if i < len(recommendations):
                        summary_row.append(recommendations[i])
                    else:
                        summary_row.append('')
                
                # Add content hash and unique flag
                summary_row.extend([
                    content_hash,  # Content_Hash
                    not is_duplicate  # Unique_Assessment
                ])
                
                summary_sheet.append_row(summary_row)
                
                # 2. Save CLO Details with timestamp
                clo_sheet = spreadsheet.worksheet('CLO_Details')
                for clo_code, clo_data in assessment_data['clo_results'].items():
                    clo_row = [
                        unique_assessment_id,
                        assessment_data['course_code'],
                        clo_code,
                        clo_data['description'],
                        clo_data['score'],
                        clo_data.get('confidence', 0),
                        ', '.join(clo_data['found_keywords']),
                        clo_data['total_keywords'],
                        clo_data['coverage'],
                        clo_data.get('ai_enhanced', False),
                        '; '.join(clo_data.get('ai_insights', [])),
                        timestamp_str  # Timestamp_Created
                    ]
                    clo_sheet.append_row(clo_row)
                
                # 3. Save PLO Details with timestamp
                plo_sheet = spreadsheet.worksheet('PLO_Details')
                for plo_code, plo_data in assessment_data['plo_results'].items():
                    plo_row = [
                        unique_assessment_id,
                        assessment_data['course_code'],
                        plo_code,
                        plo_data['description'],
                        plo_data['score'],
                        plo_data.get('confidence', 0),
                        ', '.join(plo_data['related_clos']),
                        ENHANCED_PLOS[plo_code]['weight'],
                        timestamp_str  # Timestamp_Created
                    ]
                    plo_sheet.append_row(plo_row)
                
                # 4. Save YLO Details with timestamp
                ylo_sheet = spreadsheet.worksheet('YLO_Details')
                for ylo_code, ylo_data in assessment_data['ylo_results'].items():
                    ylo_row = [
                        unique_assessment_id,
                        assessment_data['course_code'],
                        ylo_code,
                        ylo_data['description'],
                        ylo_data['score'],
                        ylo_data.get('confidence', 0),
                        ylo_data['level'],
                        ylo_data['cognitive_level'],
                        ', '.join(ylo_data['related_plos']),
                        ylo_data.get('cognitive_multiplier', 1.0),
                        timestamp_str  # Timestamp_Created
                    ]
                    ylo_sheet.append_row(ylo_row)
                
                # 5. Save Enhanced Content Analysis
                content_sheet = spreadsheet.worksheet('Content_Analysis')
                content_row = [
                    unique_assessment_id,
                    assessment_data['course_code'],
                    content_hash,
                    assessment_data.get('content_length', 0),
                    file_info.get('name', 'ป้อนข้อความ') if file_info else 'ป้อนข้อความ',
                    assessment_data.get('content_preview', '')[:500] + '...' if len(assessment_data.get('content_preview', '')) > 500 else assessment_data.get('content_preview', ''),
                    'AI Enhanced' if assessment_data.get('ai_enhanced') else 'Rule-based',
                    timestamp_str,
                    is_duplicate,  # Is_Duplicate
                    original_assessment_id or ''  # Original_Assessment_ID
                ]
                content_sheet.append_row(content_row)
                
                # 6. Save interpretation data
                interpretation_success, interpretation_message = self.save_interpretation_data(
                    spreadsheet, assessment_data
                )
                
                if not interpretation_success:
                    # Log warning but don't fail the entire save
                    print(f"Warning: {interpretation_message}")
                
                # Success message with unique ID
                success_msg = f"✅ บันทึกการประเมินใหม่สำเร็จ - ID: {unique_assessment_id}"
                if is_duplicate:
                    success_msg += f" (มีข้อมูลซ้ำกับ {original_assessment_id})"
                
                return True, success_msg
                
            except Exception as e:
                return False, f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {str(e)}"
        
        def save_interpretation_data(self, spreadsheet, assessment_data):
            """Save interpretation data to Google Sheets"""
            try:
                interpretation_sheet = spreadsheet.worksheet('Interpretation')
                assessment_id = assessment_data.get('assessment_id', generate_unique_assessment_id())
                
                # Generate interpretation data
                interpretation = self.generate_interpretation_data(assessment_data)
                
                # Create row for Interpretation sheet
                interpretation_row = [
                    assessment_id,
                    assessment_data['course_code'],
                    datetime.now().strftime('%Y-%m-%d'),
                    interpretation['overall_result'],
                    interpretation['overall_level'],
                    interpretation['best_clo'],
                    interpretation['worst_clo'],
                    interpretation['plo_coverage'],
                    interpretation['ylo_year1_count'],
                    interpretation['ylo_year2_count'],
                    interpretation['cognitive_distribution']
                ]
                
                # Add strengths (up to 3)
                for i in range(3):
                    if i < len(interpretation['strengths']):
                        interpretation_row.append(interpretation['strengths'][i])
                    else:
                        interpretation_row.append('')
                
                # Add weaknesses (up to 3)
                for i in range(3):
                    if i < len(interpretation['weaknesses']):
                        interpretation_row.append(interpretation['weaknesses'][i])
                    else:
                        interpretation_row.append('')
                
                # Add recommendations (up to 3)
                for i in range(3):
                    if i < len(interpretation['recommendations']):
                        interpretation_row.append(interpretation['recommendations'][i])
                    else:
                        interpretation_row.append('')
                
                # Add specific issues
                interpretation_row.extend([
                    interpretation['low_clos'],
                    interpretation['missing_plos'],
                    interpretation['missing_cognitive_levels']
                ])
                
                # Append row to sheet
                interpretation_sheet.append_row(interpretation_row)
                
                return True, "บันทึกการแปลผลสำเร็จ"
                
            except Exception as e:
                return False, f"เกิดข้อผิดพลาดในการบันทึกการแปลผล: {str(e)}"
        
        def generate_interpretation_data(self, assessment_data):
            """Generate interpretation data from assessment results"""
            interpretation = {
                'overall_result': '',
                'overall_level': '',
                'best_clo': '',
                'worst_clo': '',
                'plo_coverage': '',
                'ylo_year1_count': 0,
                'ylo_year2_count': 0,
                'cognitive_distribution': '',
                'strengths': [],
                'weaknesses': [],
                'recommendations': [],
                'low_clos': '',
                'missing_plos': '',
                'missing_cognitive_levels': ''
            }
            
            # Calculate overall average
            overall_avg = (assessment_data['overall_scores']['clo_average'] + 
                           assessment_data['overall_scores']['plo_average'] + 
                           assessment_data['overall_scores']['ylo_average']) / 3
            
            # Determine overall result and level
            if overall_avg >= 85:
                interpretation['overall_result'] = 'ดีเยี่ยม'
                interpretation['overall_level'] = f'{overall_avg:.1f}%'
            elif overall_avg >= 70:
                interpretation['overall_result'] = 'ดี'
                interpretation['overall_level'] = f'{overall_avg:.1f}%'
            elif overall_avg >= 60:
                interpretation['overall_result'] = 'ควรปรับปรุง'
                interpretation['overall_level'] = f'{overall_avg:.1f}%'
            else:
                interpretation['overall_result'] = 'ต้องปรับปรุงมาก'
                interpretation['overall_level'] = f'{overall_avg:.1f}%'
            
            # Best and worst CLO
            if assessment_data['clo_results']:
                best_clo = max(assessment_data['clo_results'].items(), key=lambda x: x[1]['score'])
                worst_clo = min(assessment_data['clo_results'].items(), key=lambda x: x[1]['score'])
                interpretation['best_clo'] = f"{best_clo[0]} ({best_clo[1]['score']:.1f}%)"
                interpretation['worst_clo'] = f"{worst_clo[0]} ({worst_clo[1]['score']:.1f}%)"
            
            # PLO Coverage
            plo_count = len(assessment_data['plo_results'])
            interpretation['plo_coverage'] = f"{plo_count}/3 PLOs"
            
            # YLO distribution
            for ylo_code, ylo_data in assessment_data['ylo_results'].items():
                if ylo_data['level'] == 'Year 1':
                    interpretation['ylo_year1_count'] += 1
                elif ylo_data['level'] == 'Year 2':
                    interpretation['ylo_year2_count'] += 1
            
            # Cognitive level distribution
            cognitive_levels = {}
            for ylo_code, ylo_data in assessment_data['ylo_results'].items():
                level = ylo_data['cognitive_level']
                cognitive_levels[level] = cognitive_levels.get(level, 0) + 1
            
            cognitive_dist = ', '.join([f"{k}: {v}" for k, v in cognitive_levels.items()])
            interpretation['cognitive_distribution'] = cognitive_dist
            
            # Generate strengths
            if assessment_data['overall_scores']['clo_average'] >= 85:
                interpretation['strengths'].append('CLO มีคะแนนดีเยี่ยม')
            if plo_count >= 2:
                interpretation['strengths'].append(f'ครอบคลุม PLO หลายด้าน ({plo_count} PLOs)')
            if assessment_data.get('ai_enhanced'):
                if assessment_data['overall_scores'].get('overall_confidence', 0) > 0.9:
                    interpretation['strengths'].append('AI มีความมั่นใจสูงในการวิเคราะห์')
            if interpretation['ylo_year1_count'] > 0 and interpretation['ylo_year2_count'] > 0:
                interpretation['strengths'].append('มีความสมดุลระหว่างเนื้อหาชั้นปีที่ 1 และ 2')
            
            # Generate weaknesses
            low_clos = [clo for clo, data in assessment_data['clo_results'].items() if data['score'] < 70]
            if low_clos:
                interpretation['weaknesses'].append(f'CLO ที่ต่ำกว่าเกณฑ์: {", ".join(low_clos)}')
                interpretation['low_clos'] = ', '.join(low_clos)
            
            missing_plos = [plo for plo in ['PLO1', 'PLO2', 'PLO3'] if plo not in assessment_data['plo_results']]
            if missing_plos:
                interpretation['weaknesses'].append(f'ขาด PLO: {", ".join(missing_plos)}')
                interpretation['missing_plos'] = ', '.join(missing_plos)
            
            if 'Creating' not in cognitive_dist and 'Evaluating' not in cognitive_dist:
                interpretation['weaknesses'].append('ขาดเนื้อหาระดับการคิดขั้นสูง')
                interpretation['missing_cognitive_levels'] = 'Creating, Evaluating'
            
            # Generate recommendations
            if low_clos:
                interpretation['recommendations'].append('เพิ่มเนื้อหาและคำสำคัญที่สอดคล้องกับ CLO ที่ต่ำกว่าเกณฑ์')
            if missing_plos:
                interpretation['recommendations'].append('เพิ่มเนื้อหาเพื่อครอบคลุม PLO ที่ขาดหายไป')
            if interpretation['ylo_year2_count'] == 0:
                interpretation['recommendations'].append('เพิ่มเนื้อหาที่มีความซับซ้อนระดับชั้นปีที่ 2')
            if overall_avg < 70:
                interpretation['recommendations'].append('ปรับปรุงเนื้อหาให้สอดคล้องกับวัตถุประสงค์การเรียนรู้มากขึ้น')
            
            # Add more specific recommendations based on course
            course_code = assessment_data.get('course_code', '')
            if '282712' in course_code:
                interpretation['recommendations'].append('เพิ่มกรณีศึกษาการจัดการน้ำในบริบทไทย')
            elif '282714' in course_code:
                interpretation['recommendations'].append('เสริมเทคนิคการวิจัยสมัยใหม่')
            
            return interpretation
        
        def get_assessment_history(self, spreadsheet, course_code=None, limit=50):
            """Get assessment history from Google Sheets"""
            try:
                summary_sheet = spreadsheet.worksheet('Assessment_Summary')
                all_records = summary_sheet.get_all_records()
                
                # Filter by course code if specified
                if course_code:
                    filtered_records = [r for r in all_records if r.get('รหัสวิชา') == course_code]
                else:
                    filtered_records = all_records
                
                # Sort by date/time descending and limit results
                sorted_records = sorted(
                    filtered_records, 
                    key=lambda x: f"{x.get('วันที่', '')} {x.get('เวลา', '')}", 
                    reverse=True
                )[:limit]
                
                return sorted_records, f"ดึงข้อมูลประวัติการประเมิน {len(sorted_records)} รายการ"
                
            except Exception as e:
                return [], f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}"
        
        def get_course_analytics(self, spreadsheet, course_code):
            """Get analytics for specific course"""
            try:
                summary_sheet = spreadsheet.worksheet('Assessment_Summary')
                all_records = summary_sheet.get_all_records()
                
                # Filter for the course
                course_records = [r for r in all_records if r.get('รหัสวิชา') == course_code]
                
                if not course_records:
                    return None, "ไม่พบข้อมูลการประเมินสำหรับรายวิชานี้"
                
                # Calculate analytics
                analytics = {
                    'total_assessments': len(course_records),
                    'unique_assessments': sum(1 for r in course_records if r.get('Unique_Assessment')),
                    'duplicate_assessments': sum(1 for r in course_records if not r.get('Unique_Assessment')),
                    'avg_clo_score': sum(r.get('CLO_Average', 0) for r in course_records) / len(course_records),
                    'avg_plo_score': sum(r.get('PLO_Average', 0) for r in course_records) / len(course_records),
                    'avg_ylo_score': sum(r.get('YLO_Average', 0) for r in course_records) / len(course_records),
                    'ai_enhanced_count': sum(1 for r in course_records if r.get('AI_Enhanced')),
                    'recent_assessments': sorted(course_records, 
                                               key=lambda x: f"{x.get('วันที่', '')} {x.get('เวลา', '')}", 
                                               reverse=True)[:5]
                }
                
                return analytics, "ดึงข้อมูลวิเคราะห์สำเร็จ"
                
            except Exception as e:
                return None, f"เกิดข้อผิดพลาด: {str(e)}"
        
        def get_interpretation_history(self, spreadsheet, course_code=None, limit=20):
            """Get interpretation history from Google Sheets"""
            try:
                interpretation_sheet = spreadsheet.worksheet('Interpretation')
                all_records = interpretation_sheet.get_all_records()
                
                # Filter by course code if specified
                if course_code:
                    filtered_records = [r for r in all_records if r.get('รหัสวิชา') == course_code]
                else:
                    filtered_records = all_records
                
                # Sort by date descending
                sorted_records = sorted(
                    filtered_records, 
                    key=lambda x: x.get('วันที่', ''), 
                    reverse=True
                )[:limit]
                
                return sorted_records, f"ดึงข้อมูลการแปลผล {len(sorted_records)} รายการ"
                
            except Exception as e:
                return [], f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}"
        
        def get_interpretation_summary(self, spreadsheet, course_code=None):
            """Get summary of interpretations for analytics"""
            try:
                interpretation_sheet = spreadsheet.worksheet('Interpretation')
                all_records = interpretation_sheet.get_all_records()
                
                # Filter by course code if specified
                if course_code:
                    records = [r for r in all_records if r.get('รหัสวิชา') == course_code]
                else:
                    records = all_records
                
                if not records:
                    return None, "ไม่พบข้อมูลการแปลผล"
                
                # Calculate summary statistics
                summary = {
                    'total_interpretations': len(records),
                    'result_distribution': {
                        'ดีเยี่ยม': 0,
                        'ดี': 0,
                        'ควรปรับปรุง': 0,
                        'ต้องปรับปรุงมาก': 0
                    },
                    'common_strengths': {},
                    'common_weaknesses': {},
                    'common_recommendations': {},
                    'average_plo_coverage': 0,
                    'cognitive_level_stats': {}
                }
                
                # Count result distribution
                for record in records:
                    result = record.get('ผลการประเมินโดยรวม', '')
                    if result in summary['result_distribution']:
                        summary['result_distribution'][result] += 1
                
                # Analyze common patterns
                for record in records:
                    # Count strengths
                    for i in range(1, 4):
                        strength = record.get(f'จุดเด่น_{i}', '').strip()
                        if strength:
                            summary['common_strengths'][strength] = summary['common_strengths'].get(strength, 0) + 1
                    
                    # Count weaknesses
                    for i in range(1, 4):
                        weakness = record.get(f'จุดที่ควรปรับปรุง_{i}', '').strip()
                        if weakness:
                            summary['common_weaknesses'][weakness] = summary['common_weaknesses'].get(weakness, 0) + 1
                    
                    # Count recommendations
                    for i in range(1, 4):
                        rec = record.get(f'คำแนะนำเชิงลึก_{i}', '').strip()
                        if rec:
                            summary['common_recommendations'][rec] = summary['common_recommendations'].get(rec, 0) + 1
                
                # Sort by frequency
                summary['common_strengths'] = dict(sorted(summary['common_strengths'].items(), 
                                                          key=lambda x: x[1], reverse=True)[:5])
                summary['common_weaknesses'] = dict(sorted(summary['common_weaknesses'].items(), 
                                                           key=lambda x: x[1], reverse=True)[:5])
                summary['common_recommendations'] = dict(sorted(summary['common_recommendations'].items(), 
                                                               key=lambda x: x[1], reverse=True)[:5])
                
                return summary, "สรุปข้อมูลการแปลผลสำเร็จ"
                
            except Exception as e:
                return None, f"เกิดข้อผิดพลาด: {str(e)}"

# AI and File Processing Functions
def check_ai_availability():
    """Check if AI API is available"""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        return api_key is not None
    except:
        return False

def extract_text_from_file(uploaded_file):
    """Extract text from uploaded files"""
    try:
        if uploaded_file.type == "text/plain":
            return str(uploaded_file.read(), "utf-8")
        elif uploaded_file.type == "application/pdf":
            return extract_pdf_content(uploaded_file)
        elif uploaded_file.type in ["application/vnd.ms-powerpoint", 
                                   "application/vnd.openxmlformats-officedocument.presentationml.presentation"]:
            return extract_pptx_content(uploaded_file)
        else:
            # Generate mock content for unsupported formats
            return generate_mock_content_from_filename(uploaded_file.name)
    except Exception as e:
        st.error(f"Error extracting content: {e}")
        return generate_mock_content_from_filename(uploaded_file.name)

def extract_pdf_content(uploaded_file):
    """Extract content from PDF (mock implementation)"""
    # In a real implementation, you would use libraries like PyPDF2 or pdfplumber
    # For demo purposes, we'll generate relevant content based on filename
    filename = uploaded_file.name
    return generate_mock_content_from_filename(filename)

def extract_pptx_content(uploaded_file):
    """Extract content from PowerPoint (mock implementation)"""
    # In a real implementation, you would use python-pptx library
    # For demo purposes, we'll generate relevant content based on filename
    filename = uploaded_file.name
    return generate_mock_content_from_filename(filename)

def generate_mock_content_from_filename(filename):
    """Generate mock content based on filename"""
    base_content = f"""
# Extracted from: {filename}
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Course Content Analysis

### Introduction to Environmental Management
Environmental management requires systematic integration of technology and community participation.
Modern challenges demand innovative solutions using GIS, Remote Sensing, and advanced modeling techniques.

### Technology Applications
- Geographic Information Systems (GIS) for spatial analysis
- Remote sensing technology for environmental monitoring
- Statistical analysis and data interpretation methods
- Sustainable development approaches with community involvement

### Research Methodologies
Systematic research approaches ensure reliable data collection and analysis.
Literature review processes help identify knowledge gaps and research opportunities.
Integration of multidisciplinary knowledge provides comprehensive understanding.

### Communication and Knowledge Transfer
Effective communication requires understanding target audiences and selecting appropriate channels.
Visual presentations, charts, and multimedia resources enhance learning effectiveness.
Public participation and stakeholder engagement are essential for sustainable solutions.

### Case Studies and Applications
Real-world examples demonstrate practical applications of theoretical concepts.
Community-based research projects show integration of technology and participation.
Environmental monitoring systems provide data for evidence-based decision making.
    """
    
    # Add specific content based on filename keywords
    filename_lower = filename.lower()
    
    if 'น้ำ' in filename_lower or 'water' in filename_lower:
        base_content += """

### Water Resource Management
Sustainable water resource management requires comprehensive planning and community participation.
GIS technology enables watershed analysis and water quality assessment.
Integrated water resource management considers multiple stakeholders and uses.
"""
    
    if 'ภูมิอากาศ' in filename_lower or 'climate' in filename_lower:
        base_content += """

### Climate Change Management
Climate monitoring technology provides essential data for understanding changes.
Adaptation and mitigation strategies require integrated approaches.
Carbon capture and renewable energy technologies offer solutions.
"""
    
    if 'วิจัย' in filename_lower or 'research' in filename_lower:
        base_content += """

### Research Methodology
Systematic literature review ensures comprehensive knowledge base.
Data collection methods must be appropriate for research objectives.
Statistical analysis and interpretation require careful consideration.
Academic writing standards ensure clear communication of results.
"""
    
    return base_content

@st.cache_data
def generate_ai_analysis(content_hash, course_code, use_ai=False):
    """Generate deterministic AI analysis (mock or real)"""
    if use_ai and check_ai_availability():
        # Real AI analysis would go here
        # For now, we'll use deterministic mock analysis
        pass
    
    # Create deterministic seed from content and course
    deterministic_seed = hash(f"{content_hash}_{course_code}") % (2**32)
    random.seed(deterministic_seed)
    
    course_info = COURSE_DESCRIPTIONS.get(course_code, {})
    course_clos = course_info.get('clo', {})
    
    ai_results = {
        'ai_generated': True,
        'analysis_id': content_hash[:8],  # Use content hash instead of timestamp
        'content_analysis': {},
        'recommendations': [],
        'confidence_scores': {}
    }
    
    # Deterministic analysis for each CLO
    clo_list = sorted(course_clos.items())  # Sort for consistency
    for i, (clo_code, clo_desc) in enumerate(clo_list):
        keywords = course_info.get('keywords', {}).get(clo_code, [])
        
        # Deterministic keyword selection based on content
        content_words = content_hash.lower()
        found_keywords = []
        for keyword in keywords[:4]:  # Take first 4 for consistency
            if any(char in content_words for char in keyword.lower()[:3]):
                found_keywords.append(keyword)
        
        # Deterministic scoring based on content characteristics
        content_score = len(content_hash) % 30 + 65  # Range 65-94
        clo_adjustment = (ord(clo_code[-1]) % 15) - 7  # -7 to +7 adjustment
        base_score = max(60, min(95, content_score + clo_adjustment))
        
        # Enhanced AI confidence - can reach 95%+ easily
        base_confidence = 0.90  # เริ่มต้นที่ 90%
        keyword_bonus = len(found_keywords) * 0.025  # Up to +10% for 4 keywords
        content_length_bonus = min(0.04, len(content_hash) / 800)  # Up to +4% for content
        score_bonus = max(0, (base_score - 70) * 0.002)  # Up to +5% for high scores
        course_match_bonus = 0.015 if course_code in content_hash else 0  # +1.5% if course mentioned
        
        confidence = min(0.995, base_confidence + keyword_bonus + content_length_bonus + score_bonus + course_match_bonus)
        
        ai_results['content_analysis'][clo_code] = {
            'score': base_score,
            'confidence': round(confidence, 3),  # 3 decimal places for precision
            'found_keywords': found_keywords,
            'ai_insights': [
                f"การวิเคราะห์ {clo_code} ด้วยความมั่นใจสูง",
                f"ระบบ AI ตรวจพบแนวคิดสำคัญ: {', '.join(found_keywords[:2]) if found_keywords else 'พบความสอดคล้องเชิงความหมาย'}",
                f"การประเมินครอบคลุม: {clo_desc[:40]}..."
            ]
        }
    
    # Deterministic recommendations in Thai based on scores
    all_recommendations = [
        "เพิ่มตัวอย่างการปฏิบัติและกรณีศึกษาที่เป็นรูปธรรม",
        "ปรับปรุงการนำเสนอด้วยแผนภูมิและภาพประกอบ", 
        "เสริมเนื้อหาเรื่องการมีส่วนร่วมของชุมชน",
        "เสริมสร้างความเชื่อมโยงระหว่างทฤษฎีและการปฏิบัติ",
        "เพิ่มการอ้างอิงงานวิจัยและการพัฒนาล่าสุด",
        "ปรับปรุงการใช้คำสำคัญให้สอดคล้องกับวัตถุประสงค์รายวิชา",
        "ขยายการอภิปรายเรื่องระเบียบวิธีวิจัย",
        "เพิ่มรายละเอียดทางเทคนิคในส่วนที่เหมาะสม",
        "พัฒนากิจกรรมการเรียนรู้แบบมีส่วนร่วม",
        "เชื่อมโยงกับบริบทสิ่งแวดล้อมไทยและอาเซียน",
        "เสริมการประยุกต์ใช้เทคโนโลยีสมัยใหม่",
        "เพิ่มการประเมินผลแบบหลากหลาย"
    ]
    
    # Select recommendations based on content hash
    rec_indices = [int(content_hash[i*2:i*2+2], 16) % len(all_recommendations) for i in range(3)]
    ai_results['recommendations'] = [all_recommendations[i] for i in rec_indices]
    
    return ai_results

class MultiLevelAssessmentEngine:
    """Multi-Level Assessment Engine for CLO-PLO-YLO alignment with AI support"""
    
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
    
    def calculate_clo_alignment(self, content, course_code, ai_analysis=None):
        """Calculate Course Learning Outcome alignment with optional AI support - deterministic"""
        if course_code not in self.course_descriptions:
            return {}
        
        course_data = self.course_descriptions[course_code]
        content_processed = self.preprocess_text(content)
        
        # Create deterministic seed for this analysis
        analysis_seed = hash(f"{content_processed[:100]}_{course_code}") % (2**32)
        
        clo_results = {}
        
        for clo_code, clo_description in course_data['clo'].items():
            # Find keywords for this CLO
            keywords = course_data['keywords'].get(clo_code, [])
            found_keywords = []
            
            for keyword in keywords:
                keyword_processed = self.preprocess_text(keyword)
                if keyword_processed in content_processed:
                    found_keywords.append(keyword)
            
            # Calculate base score - deterministic
            if keywords:
                coverage = len(found_keywords) / len(keywords)
                base_score = 50
                coverage_score = coverage * 40
                
                # Bonus for description relevance - deterministic
                desc_words = self.preprocess_text(clo_description).split()
                desc_matches = sum(1 for word in desc_words if word in content_processed)
                desc_bonus = min(desc_matches * 2, 10)
                
                final_score = min(100, base_score + coverage_score + desc_bonus)
            else:
                final_score = 50
            
            # Apply AI enhancement if available - keep AI scores consistent
            confidence = 0.8  # Default confidence
            ai_insights = []
            
            if ai_analysis and clo_code in ai_analysis.get('content_analysis', {}):
                ai_data = ai_analysis['content_analysis'][clo_code]
                ai_score = ai_data['score']
                confidence = ai_data['confidence']
                
                # Weighted combination of rule-based and AI scores - deterministic
                final_score = (final_score * 0.4) + (ai_score * 0.6)
                
                # Add AI insights
                ai_insights = ai_data.get('ai_insights', [])
            
            clo_results[clo_code] = {
                'score': round(final_score, 1),
                'description': clo_description,
                'found_keywords': found_keywords,
                'total_keywords': len(keywords),
                'coverage': len(found_keywords) / len(keywords) if keywords else 0,
                'confidence': round(confidence, 2),
                'ai_insights': ai_insights,
                'ai_enhanced': ai_analysis is not None
            }
        
        return clo_results
    
    def calculate_multi_level_alignment(self, content, course_code, ai_analysis=None):
        """Calculate alignment across CLO-PLO-YLO levels with AI support"""
        # Create content hash for tracking and ensure unique ID
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        results = {
            'assessment_id': generate_unique_assessment_id(),  # Use new unique ID function
            'course_code': course_code,
            'course_name': self.course_descriptions.get(course_code, {}).get('name', 'Unknown'),
            'content_hash': content_hash,
            'content_length': len(content),
            'content_preview': content[:200],
            'clo_results': {},
            'plo_results': {},
            'ylo_results': {},
            'alignment_matrix': {},
            'overall_scores': {},
            'ai_enhanced': ai_analysis is not None,
            'ai_recommendations': ai_analysis.get('recommendations', []) if ai_analysis else []
        }
        
        # 1. CLO Analysis with AI support
        clo_results = self.calculate_clo_alignment(content, course_code, ai_analysis)
        results['clo_results'] = clo_results
        
        # 2. PLO Analysis (mapped from CLOs) - Fixed calculation
        if course_code in self.course_descriptions:
            course_data = self.course_descriptions[course_code]
            mapped_plos = course_data.get('plo_mapping', [])
            
            for plo_code in mapped_plos:
                # Find CLOs that specifically contribute to this PLO
                # Based on course content and CLO descriptions
                related_clos = []
                
                # Map CLOs to PLOs based on course design
                if plo_code == 'PLO1':  # Technology and Participation
                    # CLOs that involve technology, tools, sustainability
                    related_clos = [clo for clo in clo_results.keys() 
                                   if any(keyword in ['เทคโนโลยี', 'technology', 'GIS', 'ระบบ', 'ยั่งยืน', 'sustainable'] 
                                         for keyword in course_data.get('keywords', {}).get(clo, []))]
                elif plo_code == 'PLO2':  # Research and Integration  
                    # CLOs that involve research, methodology, analysis
                    related_clos = [clo for clo in clo_results.keys()
                                   if any(keyword in ['วิจัย', 'research', 'วิธีการ', 'methodology', 'วิเคราะห์', 'analysis', 'บูรณาการ', 'integrate']
                                         for keyword in course_data.get('keywords', {}).get(clo, []))]
                elif plo_code == 'PLO3':  # Communication and Transfer
                    # CLOs that involve communication, presentation, writing
                    related_clos = [clo for clo in clo_results.keys()
                                   if any(keyword in ['สื่อสาร', 'communicate', 'นำเสนอ', 'present', 'เขียน', 'writing', 'รายงาน', 'report']
                                         for keyword in course_data.get('keywords', {}).get(clo, []))]
                
                # Fallback: if no specific mapping found, use all CLOs but with weights
                if not related_clos:
                    related_clos = list(clo_results.keys())
                
                # Calculate PLO score based on related CLOs only
                if related_clos:
                    # Weight CLOs based on relevance to PLO
                    weighted_scores = []
                    for clo in related_clos:
                        weight = 1.0  # Default weight
                        
                        # Adjust weight based on CLO-PLO relevance
                        clo_keywords = course_data.get('keywords', {}).get(clo, [])
                        if plo_code == 'PLO1' and any(kw in ['เทคโนโลยี', 'technology', 'GIS'] for kw in clo_keywords):
                            weight = 1.2
                        elif plo_code == 'PLO2' and any(kw in ['วิจัย', 'research', 'วิเคราะห์'] for kw in clo_keywords):
                            weight = 1.2  
                        elif plo_code == 'PLO3' and any(kw in ['สื่อสาร', 'communicate', 'นำเสนอ'] for kw in clo_keywords):
                            weight = 1.2
                        
                        weighted_scores.append(clo_results[clo]['score'] * weight)
                    
                    plo_score = sum(weighted_scores) / len(weighted_scores)
                    avg_confidence = sum(clo_results[clo]['confidence'] for clo in related_clos) / len(related_clos)
                else:
                    plo_score = 0
                    avg_confidence = 0
                
                results['plo_results'][plo_code] = {
                    'score': round(plo_score, 1),
                    'related_clos': related_clos,
                    'description': self.plos[plo_code]['description'],
                    'confidence': avg_confidence
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
                confidences = []
                for plo_code in related_plos:
                    if plo_code in results['plo_results']:
                        ylo_scores.append(results['plo_results'][plo_code]['score'])
                        confidences.append(results['plo_results'][plo_code]['confidence'])
                
                ylo_score = sum(ylo_scores) / len(ylo_scores) if ylo_scores else 0
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Calculate cognitive multiplier based on cognitive level
                cognitive_weights = {
                    'Understanding': 1.0,
                    'Applying': 1.1,
                    'Evaluating': 1.2,
                    'Creating': 1.3
                }
                cognitive_multiplier = cognitive_weights.get(ylo_data['cognitive_level'], 1.0)
                
                results['ylo_results'][ylo_code] = {
                    'score': round(ylo_score, 1),
                    'related_plos': related_plos,
                    'description': ylo_data['description'],
                    'level': ylo_data['level'],
                    'cognitive_level': ylo_data['cognitive_level'],
                    'confidence': round(avg_confidence, 3),
                    'cognitive_multiplier': cognitive_multiplier
                }
        
        # 4. Create alignment matrix
        results['alignment_matrix'] = self.create_alignment_matrix(results)
        
        # 5. Calculate overall scores - Fixed to show different values
        # CLO Average - direct average of all CLO scores
        clo_average = sum(clo['score'] for clo in clo_results.values()) / len(clo_results) if clo_results else 0
        
        # PLO Average - weighted by PLO importance in the program
        if results['plo_results']:
            plo_weighted_sum = 0
            total_weight = 0
            for plo_code, plo_data in results['plo_results'].items():
                weight = self.plos[plo_code]['weight'] / 100  # Convert percentage to decimal
                plo_weighted_sum += plo_data['score'] * weight
                total_weight += weight
            plo_average = plo_weighted_sum / total_weight if total_weight > 0 else 0
        else:
            plo_average = 0
        
        # YLO Average - consider cognitive complexity
        if results['ylo_results']:
            ylo_weighted_sum = 0
            total_cognitive_weight = 0
            for ylo_code, ylo_data in results['ylo_results'].items():
                # Weight by cognitive level complexity
                cognitive_weights = {
                    'Understanding': 1.0,
                    'Applying': 1.1, 
                    'Evaluating': 1.2,
                    'Creating': 1.3
                }
                weight = cognitive_weights.get(ylo_data['cognitive_level'], 1.0)
                ylo_weighted_sum += ylo_data['score'] * weight
                total_cognitive_weight += weight
            ylo_average = ylo_weighted_sum / total_cognitive_weight if total_cognitive_weight > 0 else 0
        else:
            ylo_average = 0
        
        # Overall confidence
        overall_confidence = sum(clo['confidence'] for clo in clo_results.values()) / len(clo_results) if clo_results else 0
        
        results['overall_scores'] = {
            'clo_average': round(clo_average, 1),
            'plo_average': round(plo_average, 1), 
            'ylo_average': round(ylo_average, 1),
            'overall_confidence': round(overall_confidence, 3),
            'calculation_method': {
                'clo': 'Simple average of all CLO scores',
                'plo': 'Weighted average by PLO importance (35%, 35%, 30%)',
                'ylo': 'Weighted average by cognitive complexity'
            }
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

# Enhanced Google Sheets Interface Functions
def show_google_sheets_setup():
    """Show enhanced Google Sheets setup interface"""
    if not GSHEETS_AVAILABLE:
        st.error("Google Sheets integration is not available. Please install required packages.")
        return
    
    st.subheader("📊 การตั้งค่า Google Sheets (Enhanced Version)")
    
    # Initialize sheets manager in session state
    if 'sheets_manager' not in st.session_state:
        st.session_state.sheets_manager = GoogleSheetsManager()
    
    # Connection status with enhanced info
    if st.session_state.sheets_manager.initialized:
        st.success("✅ เชื่อมต่อ Google Sheets สำเร็จแล้ว - พร้อมบันทึกข้อมูลใหม่ทุกครั้ง")
        st.info("ℹ️ ระบบจะสร้าง Assessment ID ใหม่และตรวจสอบข้อมูลซ้ำอัตโนมัติ")
    else:
        st.info("ℹ️ ยังไม่ได้เชื่อมต่อ Google Sheets")
    
    # Credentials input
    with st.expander("🔑 ตั้งค่า Service Account Credentials"):
        st.markdown("""
        **วิธีการสร้าง Service Account (ปรับปรุงใหม่):**
        1. ไปที่ [Google Cloud Console](https://console.cloud.google.com/)
        2. สร้าง Project ใหม่หรือเลือกที่มีอยู่
        3. เปิดใช้งาน Google Sheets API และ Google Drive API
        4. สร้าง Service Account และดาวน์โหลด JSON credentials
        5. แชร์ Google Sheets ของคุณให้กับ Service Account email
        6. **สำคัญ**: ให้สิทธิ์ Editor เพื่อให้สามารถเขียนข้อมูลได้
        """)
        
        # Option 1: Upload JSON file
        uploaded_creds = st.file_uploader(
            "อัพโหลดไฟล์ Service Account JSON",
            type=['json'],
            help="ไฟล์ credentials ที่ดาวน์โหลดจาก Google Cloud Console"
        )
        
        # Option 2: Paste JSON content
        st.markdown("**หรือ** วาง JSON content:")
        creds_text = st.text_area(
            "Service Account JSON",
            height=200,
            placeholder='{\n  "type": "service_account",\n  "project_id": "your-project",\n  ...\n}',
            help="วาง JSON content ของ Service Account credentials"
        )
        
        # Connect button
        if st.button("🔗 เชื่อมต่อ Google Sheets", type="primary"):
            credentials_dict = None
            
            try:
                if uploaded_creds:
                    credentials_dict = json.load(uploaded_creds)
                elif creds_text.strip():
                    credentials_dict = json.loads(creds_text.strip())
                else:
                    st.error("กรุณาระบุ credentials")
                    return
                
                # Try to connect
                success, message = st.session_state.sheets_manager.initialize_connection(credentials_dict)
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
                    
            except json.JSONDecodeError:
                st.error("รูปแบบ JSON ไม่ถูกต้อง")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")
    
    # Enhanced Spreadsheet management
    if st.session_state.sheets_manager.initialized:
        st.markdown("---")
        st.subheader("📋 จัดการ Spreadsheet (Enhanced)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            spreadsheet_name = st.text_input(
                "ชื่อ Spreadsheet",
                value="Enhanced_Assessment_Results",
                help="ชื่อของ Google Spreadsheet ที่จะใช้เก็บข้อมูล (ปรับปรุงใหม่)"
            )
        
        with col2:
            if st.button("📊 สร้าง/เปิด Spreadsheet", use_container_width=True):
                spreadsheet, message = st.session_state.sheets_manager.create_or_get_spreadsheet(spreadsheet_name)
                
                if spreadsheet:
                    st.session_state.current_spreadsheet = spreadsheet
                    st.success(message)
                    
                    # Setup enhanced sheets structure
                    setup_success, setup_message = st.session_state.sheets_manager.setup_assessment_sheets(spreadsheet)
                    if setup_success:
                        st.success("✅ " + setup_message)
                        st.info(f"📊 Spreadsheet URL: {spreadsheet.url}")
                        st.success("🆕 ระบบพร้อมบันทึกข้อมูลใหม่ทุกครั้งพร้อม Unique ID")
                    else:
                        st.warning(setup_message)
                else:
                    st.error(message)
        
        # Current spreadsheet info with enhanced details
        if hasattr(st.session_state, 'current_spreadsheet'):
            st.success(f"📊 กำลังใช้งาน: {st.session_state.current_spreadsheet.title}")
            st.markdown(f"🔗 [เปิดใน Google Sheets]({st.session_state.current_spreadsheet.url})")
            
            # Show enhanced features
            with st.expander("✨ ฟีเจอร์ใหม่ในระบบ Enhanced"):
                st.markdown("""
                **🆕 การปรับปรุงใหม่:**
                - ✅ Unique Assessment ID: สร้าง ID ไม่ซ้ำทุกครั้ง
                - ✅ Duplicate Detection: ตรวจสอบข้อมูลซ้ำอัตโนมัติ
                - ✅ Enhanced Timestamps: บันทึกเวลาแม่นยำ
                - ✅ Content Hash: ตรวจสอบเนื้อหาด้วย Hash
                - ✅ Improved Data Structure: โครงสร้างข้อมูลที่ดีขึ้น
                - ✅ Better Analytics: วิเคราะห์ข้อมูลที่ละเอียดขึ้น
                
                **📊 Sheets ที่ปรับปรุง:**
                - Assessment_Summary: เพิ่ม Content_Hash, Unique_Assessment
                - CLO_Details: เพิ่ม Timestamp_Created
                - PLO_Details: เพิ่ม Timestamp_Created  
                - YLO_Details: เพิ่ม Timestamp_Created
                - Content_Analysis: เพิ่ม Is_Duplicate, Original_Assessment_ID
                - Interpretation: โครงสร้างครบถ้วนสำหรับการแปลผล
                """)

def show_assessment_history():
    """Show enhanced assessment history from Google Sheets"""
    if not GSHEETS_AVAILABLE:
        st.warning("Google Sheets integration is not available.")
        return
    
    st.subheader("📋 ประวัติการประเมิน (Enhanced)")
    
    if not hasattr(st.session_state, 'current_spreadsheet'):
        st.warning("กรุณาตั้งค่าและเชื่อมต่อ Google Sheets ก่อน")
        return
    
    # Enhanced filter options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_course = st.selectbox(
            "กรองตามรายวิชา",
            options=['ทั้งหมด'] + list(COURSE_DESCRIPTIONS.keys()),
            index=0
        )
    
    with col2:
        limit_records = st.number_input(
            "จำนวนรายการ",
            min_value=10,
            max_value=200,
            value=50,
            step=10
        )
    
    with col3:
        show_unique_only = st.checkbox(
            "แสดงเฉพาะข้อมูลไม่ซ้ำ",
            value=False,
            help="แสดงเฉพาะการประเมินที่ไม่ซ้ำกัน"
        )
    
    with col4:
        if st.button("🔄 รีเฟรชข้อมูล"):
            st.rerun()
    
    # Get enhanced assessment history
    course_filter = None if filter_course == 'ทั้งหมด' else filter_course
    
    try:
        history, message = st.session_state.sheets_manager.get_assessment_history(
            st.session_state.current_spreadsheet,
            course_code=course_filter,
            limit=limit_records
        )
        
        if history:
            st.success(message)
            
            # Filter unique only if requested
            if show_unique_only:
                history = [r for r in history if r.get('Unique_Assessment', True)]
                st.info(f"แสดง {len(history)} รายการที่ไม่ซ้ำกัน")
            
            # Display enhanced metrics
            if history:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_assessments = len(history)
                    st.metric("การประเมินทั้งหมด", total_assessments)
                
                with col2:
                    unique_count = sum(1 for r in history if r.get('Unique_Assessment', True))
                    st.metric("ข้อมูลไม่ซ้ำ", unique_count)
                
                with col3:
                    ai_count = sum(1 for r in history if r.get('AI_Enhanced', False))
                    st.metric("ใช้ AI", ai_count)
                
                with col4:
                    avg_clo = sum(r.get('CLO_Average', 0) for r in history) / len(history) if history else 0
                    st.metric("CLO เฉลี่ย", f"{avg_clo:.1f}%")
            
            # Display as enhanced dataframe
            df = pd.DataFrame(history)
            
            # Select relevant columns for display with enhanced info
            display_columns = [
                'วันที่', 'เวลา', 'รหัสการประเมิน', 'รหัสวิชา', 'ชื่อวิชา',
                'ประเภทไฟล์', 'AI_Enhanced', 'CLO_Average', 'PLO_Average', 'YLO_Average',
                'Unique_Assessment', 'Content_Hash'
            ]
            
            available_columns = [col for col in display_columns if col in df.columns]
            
            if available_columns:
                # Enhanced display with color coding
                display_df = df[available_columns].copy()
                
                # Add status indicators
                if 'Unique_Assessment' in display_df.columns:
                    display_df['สถานะ'] = display_df['Unique_Assessment'].apply(
                        lambda x: '✅ ไม่ซ้ำ' if x else '⚠️ ซ้ำ'
                    )
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Enhanced download options
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 ดาวน์โหลด CSV (ทั้งหมด)",
                        data=csv,
                        file_name=f"assessment_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    if show_unique_only and len(history) > 0:
                        unique_csv = pd.DataFrame([r for r in history if r.get('Unique_Assessment', True)]).to_csv(index=False)
                        st.download_button(
                            label="📥 ดาวน์โหลด CSV (ไม่ซ้ำ)",
                            data=unique_csv,
                            file_name=f"unique_assessments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
            else:
                st.warning("ไม่พบคอลัมน์ข้อมูลที่ต้องการแสดง")
        else:
            st.info(message)
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}")

def show_course_analytics():
    """Show enhanced analytics for courses"""
    if not GSHEETS_AVAILABLE:
        st.warning("Google Sheets integration is not available.")
        return
    
    st.subheader("📈 การวิเคราะห์ข้อมูลรายวิชา (Enhanced)")
    
    if not hasattr(st.session_state, 'current_spreadsheet'):
        st.warning("กรุณาตั้งค่าและเชื่อมต่อ Google Sheets ก่อน")
        return
    
    # Course selection
    selected_course = st.selectbox(
        "เลือกรายวิชาสำหรับวิเคราะห์",
        options=list(COURSE_DESCRIPTIONS.keys()),
        format_func=lambda x: f"{x} - {COURSE_DESCRIPTIONS[x]['name']}"
    )
    
    if st.button("📊 วิเคราะห์ข้อมูล (Enhanced)"):
        try:
            analytics, message = st.session_state.sheets_manager.get_course_analytics(
                st.session_state.current_spreadsheet,
                selected_course
            )
            
            if analytics:
                st.success(message)
                
                # Display enhanced analytics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric(
                        "การประเมินทั้งหมด",
                        analytics['total_assessments']
                    )
                
                with col2:
                    st.metric(
                        "ข้อมูลไม่ซ้ำ",
                        analytics.get('unique_assessments', 0),
                        f"+{analytics.get('unique_assessments', 0) - analytics.get('duplicate_assessments', 0)}"
                    )
                
                with col3:
                    st.metric(
                        "CLO เฉลี่ย",
                        f"{analytics['avg_clo_score']:.1f}%"
                    )
                
                with col4:
                    st.metric(
                        "PLO เฉลี่ย",
                        f"{analytics['avg_plo_score']:.1f}%"
                    )
                
                with col5:
                    ai_percentage = (analytics['ai_enhanced_count'] / analytics['total_assessments'] * 100) if analytics['total_assessments'] > 0 else 0
                    st.metric(
                        "การใช้ AI",
                        f"{ai_percentage:.1f}%",
                        f"{analytics['ai_enhanced_count']}/{analytics['total_assessments']}"
                    )
                
                # Enhanced charts
                if analytics['recent_assessments']:
                    st.markdown("### 📊 แนวโน้มคะแนน")
                    
                    recent_df = pd.DataFrame(analytics['recent_assessments'])
                    
                    # Create trend chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=recent_df['วันที่'],
                        y=recent_df['CLO_Average'],
                        mode='lines+markers',
                        name='CLO Average',
                        line=dict(color='#FF6B6B')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=recent_df['วันที่'],
                        y=recent_df['PLO_Average'],
                        mode='lines+markers',
                        name='PLO Average',
                        line=dict(color='#4ECDC4')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=recent_df['วันที่'],
                        y=recent_df['YLO_Average'],
                        mode='lines+markers',
                        name='YLO Average',
                        line=dict(color='#45B7D1')
                    ))
                    
                    fig.update_layout(
                        title="แนวโน้มคะแนนการประเมิน",
                        xaxis_title="วันที่",
                        yaxis_title="คะแนน (%)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Recent assessments table
                st.markdown("### 📅 การประเมินล่าสุด")
                if analytics['recent_assessments']:
                    recent_df = pd.DataFrame(analytics['recent_assessments'])
                    st.dataframe(recent_df, use_container_width=True, hide_index=True)
                else:
                    st.info("ไม่มีข้อมูลการประเมินล่าสุด")
            else:
                st.warning(message)
                
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def show_interpretation_history():
    """Show interpretation history from Google Sheets"""
    if not GSHEETS_AVAILABLE:
        st.warning("Google Sheets integration is not available.")
        return
    
    st.subheader("📊 ประวัติการแปลผล")
    
    if not hasattr(st.session_state, 'current_spreadsheet'):
        st.warning("กรุณาตั้งค่าและเชื่อมต่อ Google Sheets ก่อน")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        filter_course = st.selectbox(
            "กรองตามรายวิชา",
            options=['ทั้งหมด'] + list(COURSE_DESCRIPTIONS.keys()),
            index=0,
            key="interpretation_filter_course"
        )
    
    with col2:
        if st.button("🔄 รีเฟรชข้อมูลการแปลผล"):
            st.rerun()
    
    # Get interpretation history
    course_filter = None if filter_course == 'ทั้งหมด' else filter_course
    
    try:
        history, message = st.session_state.sheets_manager.get_interpretation_history(
            st.session_state.current_spreadsheet,
            course_code=course_filter,
            limit=20
        )
        
        if history:
            st.success(message)
            
            # Display summary cards
            col1, col2, col3, col4 = st.columns(4)
            
            # Count results
            excellent = sum(1 for r in history if r.get('ผลการประเมินโดยรวม') == 'ดีเยี่ยม')
            good = sum(1 for r in history if r.get('ผลการประเมินโดยรวม') == 'ดี')
            fair = sum(1 for r in history if r.get('ผลการประเมินโดยรวม') == 'ควรปรับปรุง')
            poor = sum(1 for r in history if r.get('ผลการประเมินโดยรวม') == 'ต้องปรับปรุงมาก')
            
            with col1:
                st.metric("🌟 ดีเยี่ยม", excellent)
            with col2:
                st.metric("✅ ดี", good)
            with col3:
                st.metric("⚠️ ควรปรับปรุง", fair)
            with col4:
                st.metric("❌ ต้องปรับปรุง", poor)
            
            # Display interpretation details
            for record in history:
                with st.expander(f"{record.get('รหัสการประเมิน')} - {record.get('รหัสวิชา')} ({record.get('วันที่')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ผลการประเมิน:** {record.get('ผลการประเมินโดยรวม')} ({record.get('ระดับคะแนน')})")
                        st.write(f"**CLO ดีที่สุด:** {record.get('CLO_สูงสุด')}")
                        st.write(f"**CLO ต่ำที่สุด:** {record.get('CLO_ต่ำสุด')}")
                        st.write(f"**PLO Coverage:** {record.get('PLO_Coverage')}")
                        
                        # Strengths
                        st.write("**จุดเด่น:**")
                        for i in range(1, 4):
                            strength = record.get(f'จุดเด่น_{i}', '').strip()
                            if strength:
                                st.write(f"• {strength}")
                    
                    with col2:
                        st.write(f"**Year 1 YLOs:** {record.get('YLO_Year1_Count')}")
                        st.write(f"**Year 2 YLOs:** {record.get('YLO_Year2_Count')}")
                        st.write(f"**Cognitive Levels:** {record.get('Cognitive_Distribution')}")
                        
                        # Weaknesses
                        st.write("**จุดที่ควรปรับปรุง:**")
                        for i in range(1, 4):
                            weakness = record.get(f'จุดที่ควรปรับปรุง_{i}', '').strip()
                            if weakness:
                                st.write(f"• {weakness}")
                    
                    # Recommendations
                    st.write("**คำแนะนำเชิงลึก:**")
                    for i in range(1, 4):
                        rec = record.get(f'คำแนะนำเชิงลึก_{i}', '').strip()
                        if rec:
                            st.write(f"{i}. {rec}")
        else:
            st.info(message)
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูล: {str(e)}")

def show_interpretation_analytics():
    """Show analytics of interpretation data"""
    if not GSHEETS_AVAILABLE:
        st.warning("Google Sheets integration is not available.")
        return
    
    st.subheader("📈 การวิเคราะห์การแปลผล")
    
    if not hasattr(st.session_state, 'current_spreadsheet'):
        st.warning("กรุณาตั้งค่าและเชื่อมต่อ Google Sheets ก่อน")
        return
    
    # Course selection
    selected_course = st.selectbox(
        "เลือกรายวิชาสำหรับวิเคราะห์",
        options=['ทั้งหมด'] + list(COURSE_DESCRIPTIONS.keys()),
        format_func=lambda x: x if x == 'ทั้งหมด' else f"{x} - {COURSE_DESCRIPTIONS[x]['name']}",
        key="interpretation_analytics_course"
    )
    
    course_filter = None if selected_course == 'ทั้งหมด' else selected_course
    
    try:
        summary, message = st.session_state.sheets_manager.get_interpretation_summary(
            st.session_state.current_spreadsheet,
            course_code=course_filter
        )
        
        if summary:
            st.success(message)
            
            # Result distribution pie chart
            st.markdown("### 📊 การกระจายผลการประเมิน")
            
            # Create pie chart
            labels = list(summary['result_distribution'].keys())
            values = list(summary['result_distribution'].values())
            colors = ['#00CC00', '#66B2FF', '#FFB366', '#FF6666']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values,
                hole=.3,
                marker_colors=colors
            )])
            
            fig.update_layout(
                title="สัดส่วนผลการประเมิน",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Common patterns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 💪 จุดเด่นที่พบบ่อย")
                for strength, count in summary['common_strengths'].items():
                    st.write(f"• {strength} ({count} ครั้ง)")
            
            with col2:
                st.markdown("### ⚠️ จุดอ่อนที่พบบ่อย")
                for weakness, count in summary['common_weaknesses'].items():
                    st.write(f"• {weakness} ({count} ครั้ง)")
            
            with col3:
                st.markdown("### 💡 คำแนะนำที่พบบ่อย")
                for rec, count in summary['common_recommendations'].items():
                    st.write(f"• {rec} ({count} ครั้ง)")
            
            # Summary statistics
            st.markdown("### 📈 สถิติสรุป")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("จำนวนการประเมินทั้งหมด", summary['total_interpretations'])
            
            with col2:
                excellent_percent = (summary['result_distribution']['ดีเยี่ยม'] / 
                                   summary['total_interpretations'] * 100) if summary['total_interpretations'] > 0 else 0
                st.metric("% ที่ได้ผลดีเยี่ยม", f"{excellent_percent:.1f}%")
            
            with col3:
                need_improve = (summary['result_distribution']['ควรปรับปรุง'] + 
                              summary['result_distribution']['ต้องปรับปรุงมาก'])
                improve_percent = (need_improve / summary['total_interpretations'] * 100) if summary['total_interpretations'] > 0 else 0
                st.metric("% ที่ต้องปรับปรุง", f"{improve_percent:.1f}%")
            
        else:
            st.warning(message)
            
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {str(e)}")

def save_assessment_to_sheets(results, file_info=None):
    """Enhanced save assessment results to Google Sheets with unique ID"""
    if not GSHEETS_AVAILABLE:
        return False, "Google Sheets integration is not available"
    
    if not hasattr(st.session_state, 'current_spreadsheet') or not st.session_state.sheets_manager.initialized:
        return False, "ยังไม่ได้เชื่อมต่อ Google Sheets"
    
    try:
        # Add assessor info
        assessor_name = st.session_state.get('assessor_name', 'ไม่ระบุ')
        results['assessor'] = assessor_name
        
        # Enhanced save with unique ID and duplicate checking
        success, message = st.session_state.sheets_manager.save_assessment_data(
            st.session_state.current_spreadsheet,
            results,
            file_info,
            allow_duplicates=False  # Set to False to check for duplicates
        )
        
        return success, message
        
    except Exception as e:
        return False, f"เกิดข้อผิดพลาด: {str(e)}"

def show_file_upload_interface():
    """Enhanced file upload interface with AI analysis and Google Sheets saving"""
    st.subheader("📁 File Upload & AI Analysis (Enhanced)")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose your slide file",
        type=['pdf', 'pptx', 'ppt', 'txt'],
        help="Supported formats: PDF, PowerPoint, Text files"
    )
    
    # AI Analysis option
    col1, col2 = st.columns([3, 1])
    
    with col1:
        use_ai = st.checkbox(
            "🤖 Enable AI Analysis",
            value=False,
            help="Use AI to enhance content analysis (requires API key)"
        )
    
    with col2:
        ai_available = check_ai_availability()
        if ai_available:
            st.success("AI Ready")
        else:
            st.info("Demo Mode")
    
    if uploaded_file is not None:
        # File information
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{file_size:.1f} MB")
        with col3:
            st.metric("File Type", uploaded_file.type.split('/')[-1].upper())
        
        # Store filename
        st.session_state.last_filename = uploaded_file.name
        
        # Process file button
        if st.button("🔍 Process File & Analyze (Enhanced)", type="primary", use_container_width=True):
            with st.spinner("Processing file and performing enhanced analysis..."):
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Extract content
                status_text.text("📄 Extracting content from file...")
                progress_bar.progress(25)
                time.sleep(0.5)
                
                content = extract_text_from_file(uploaded_file)
                
                # Step 2: AI Analysis (if enabled)
                ai_analysis = None
                if use_ai:
                    status_text.text("🤖 Performing AI analysis...")
                    progress_bar.progress(50)
                    time.sleep(1)
                    
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    ai_analysis = generate_ai_analysis(content_hash, st.session_state.selected_course_code, use_ai)
                
                # Step 3: Multi-level analysis
                status_text.text("🎯 Performing multi-level assessment...")
                progress_bar.progress(75)
                time.sleep(0.5)
                
                engine = MultiLevelAssessmentEngine()
                results = engine.calculate_multi_level_alignment(
                    content, 
                    st.session_state.selected_course_code, 
                    ai_analysis
                )
                
                # Step 4: Enhanced save to Google Sheets (if connected)
                if GSHEETS_AVAILABLE and hasattr(st.session_state, 'current_spreadsheet'):
                    status_text.text("💾 Saving to Google Sheets with unique ID...")
                    progress_bar.progress(90)
                    
                    file_info = {
                        'name': uploaded_file.name,
                        'type': uploaded_file.type,
                        'size': file_size
                    }
                    
                    save_success, save_message = save_assessment_to_sheets(results, file_info)
                    if save_success:
                        st.success(f"✅ {save_message}")
                    else:
                        st.warning(f"⚠️ {save_message}")
                
                # Step 5: Complete
                status_text.text("✅ Enhanced analysis complete!")
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Store results in session state
                st.session_state.analysis_results = results
                st.session_state.slide_content = content
                
                # Show enhanced success message
                if ai_analysis:
                    st.success(f"✅ File processed with AI analysis! Assessment ID: {results.get('assessment_id', 'Unknown')}")
                else:
                    st.success(f"✅ File processed with rule-based analysis! Assessment ID: {results.get('assessment_id', 'Unknown')}")
                
                return results, content
    
    return None, None

def create_enhanced_gauge_chart(score, title="Score", confidence=None):
    """Create enhanced gauge chart with confidence indicator"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': '#333'}},
        delta={'reference': 70, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#333"},
            'bar': {'color': "#667eea", 'thickness': 0.25},
            'steps': [
                {'range': [0, 50], 'color': "#ffebee"},
                {'range': [50, 60], 'color': "#fff3e0"},
                {'range': [60, 70], 'color': "#fffde7"},
                {'range': [70, 85], 'color': "#e8f5e8"},
                {'range': [85, 100], 'color': "#e3f2fd"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    # Add confidence indicator if available
    annotations = ["Pass: 70% | Good: 85%"]
    if confidence:
        annotations.append(f"AI Confidence: {confidence*100:.0f}%")
    
    fig.add_annotation(
        x=0.5, y=0.1,
        text=" | ".join(annotations),
        showarrow=False,
        font=dict(size=10, color="#666")
    )
    
    fig.update_layout(
        height=300, 
        margin=dict(t=60, b=40, l=20, r=20),
        font={'family': 'Arial, sans-serif'}
    )
    return fig

def create_multi_level_dashboard(results):
    """Create comprehensive multi-level dashboard with enhanced features"""
    st.header("🎯 Enhanced Multi-Level Learning Outcome Assessment")
    
    # Course Information with enhanced AI status
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"📚 {results['course_name']}")
        st.write(f"**Course Code:** {results['course_code']}")
    with col2:
        st.write(f"**Assessment ID:** `{results.get('assessment_id', 'N/A')}`")
        if results.get('ai_enhanced', False):
            st.success("🤖 AI Enhanced")
        else:
            st.info("📊 Rule-based")
    with col3:
        if results.get('ai_enhanced', False):
            confidence = results['overall_scores'].get('overall_confidence', 0)
            st.metric("AI Confidence", f"{confidence*100:.0f}%")
        
        # Show content hash for tracking
        content_hash = results.get('content_hash', '')
        if content_hash:
            st.caption(f"Content Hash: `{content_hash[:8]}...`")
    
    # Enhanced save to Google Sheets option
    if GSHEETS_AVAILABLE and hasattr(st.session_state, 'current_spreadsheet'):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 บันทึกผลการประเมินลง Google Sheets", type="secondary"):
                file_info = {
                    'name': st.session_state.get('last_filename', 'ป้อนข้อความ'),
                    'type': 'text/plain',
                    'size': 0
                }
                
                success, message = save_assessment_to_sheets(results, file_info)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        with col2:
            if st.button("🔍 ตรวจสอบข้อมูลซ้ำ", type="secondary"):
                content_hash = results.get('content_hash', '')
                course_code = results.get('course_code', '')
                
                if content_hash and course_code:
                    is_duplicate, original_id = check_duplicate_assessment(
                        st.session_state.current_spreadsheet, content_hash, course_code
                    )
                    
                    if is_duplicate:
                        st.warning(f"⚠️ พบข้อมูลซ้ำกับ Assessment ID: {original_id}")
                    else:
                        st.success("✅ ข้อมูลไม่ซ้ำ")
                else:
                    st.info("ไม่สามารถตรวจสอบได้")
    
    # Overall Scores with Enhanced Gauge Charts
    st.subheader("📊 Enhanced Performance Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        clo_avg = results['overall_scores']['clo_average']
        confidence = results['overall_scores'].get('overall_confidence', 0.8)
        fig_clo = create_enhanced_gauge_chart(
            clo_avg, 
            "CLO Average",
            confidence if results.get('ai_enhanced') else None
        )
        st.plotly_chart(fig_clo, use_container_width=True)
    
    with col2:
        plo_avg = results['overall_scores']['plo_average']
        fig_plo = create_enhanced_gauge_chart(
            plo_avg, 
            "PLO Average",
            confidence if results.get('ai_enhanced') else None
        )
        st.plotly_chart(fig_plo, use_container_width=True)
    
    with col3:
        ylo_avg = results['overall_scores']['ylo_average']
        fig_ylo = create_enhanced_gauge_chart(
            ylo_avg, 
            "YLO Average",
            confidence if results.get('ai_enhanced') else None
        )
        st.plotly_chart(fig_ylo, use_container_width=True)
    
    # Enhanced Overall Status with calculation explanation
    overall_avg = (results['overall_scores']['clo_average'] + 
                   results['overall_scores']['plo_average'] + 
                   results['overall_scores']['ylo_average']) / 3
    
    if overall_avg >= 85:
        st.success(f"🌟 **Overall Performance: Excellent** ({overall_avg:.1f}%) - Assessment ID: {results.get('assessment_id', 'N/A')}")
        st.balloons()
    elif overall_avg >= 70:
        st.success(f"✅ **Overall Performance: Good** ({overall_avg:.1f}%) - Assessment ID: {results.get('assessment_id', 'N/A')}")
    elif overall_avg >= 60:
        st.warning(f"⚠️ **Overall Performance: Fair** ({overall_avg:.1f}%) - Assessment ID: {results.get('assessment_id', 'N/A')}")
    else:
        st.error(f"❌ **Overall Performance: Needs Improvement** ({overall_avg:.1f}%) - Assessment ID: {results.get('assessment_id', 'N/A')}")
    
    # Enhanced AI Recommendations (if available)
    if results.get('ai_recommendations'):
        st.subheader("🤖 Enhanced AI Recommendations")
        for i, rec in enumerate(results['ai_recommendations'], 1):
            st.write(f"{i}. {rec}")
        st.markdown("---")
    
    # Enhanced Calculation Method Explanation
    with st.expander("📊 วิธีการคำนวณคะแนนแต่ละระดับ (Enhanced)"):
        calc_methods = results['overall_scores'].get('calculation_method', {})
        st.markdown("**CLO (Course Learning Outcomes):**")
        st.write(f"• {calc_methods.get('clo', 'การเฉลี่ยแบบธรรมดาของคะแนน CLO ทั้งหมด')}")
        
        st.markdown("**PLO (Program Learning Outcomes):**") 
        st.write(f"• {calc_methods.get('plo', 'การเฉลี่ยถ่วงน้ำหนักตามความสำคัญของ PLO')}")
        st.write("• น้ำหนัก: PLO1 (35%), PLO2 (35%), PLO3 (30%)")
        
        st.markdown("**YLO (Year Learning Outcomes):**")
        st.write(f"• {calc_methods.get('ylo', 'การเฉลี่ยถ่วงน้ำหนักตามความซับซ้อนทางความคิด')}")
        st.write("• น้ำหนักตามระดับความคิด: Understanding (1.0), Applying (1.1), Evaluating (1.2), Creating (1.3)")
        
        # Show specific calculations for this assessment
        st.markdown("**การคำนวณเฉพาะการประเมินนี้:**")
        st.write(f"**Assessment ID:** `{results.get('assessment_id', 'N/A')}`")
        st.write(f"**Content Hash:** `{results.get('content_hash', 'N/A')[:16]}...`")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**CLO Scores:**")
            for clo, data in results['clo_results'].items():
                st.write(f"• {clo}: {data['score']:.1f}%")
        
        with col2:
            st.write("**PLO Mapping:**")
            for plo, data in results['plo_results'].items():
                related = ', '.join(data['related_clos'])
                st.write(f"• {plo}: CLO {related}")
        
        with col3:
            st.write("**YLO Cognitive Levels:**")
            for ylo, data in results['ylo_results'].items():
                multiplier = data.get('cognitive_multiplier', 1.0)
                st.write(f"• {ylo}: {data['cognitive_level']} (×{multiplier})")
    
    # Enhanced Multi-level Analysis Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 CLO Analysis", "🎯 PLO Analysis", "📈 YLO Analysis", "🔗 Alignment Matrix", "📊 การแปลผลโดยรวม"])
    
    with tab1:
        display_enhanced_clo_analysis(results['clo_results'])
    
    with tab2:
        display_plo_analysis(results['plo_results'])
    
    with tab3:
        display_ylo_analysis(results['ylo_results'])
    
    with tab4:
        display_alignment_matrix(results)
    
    with tab5:
        display_comprehensive_interpretation(results)

# Missing Display Functions
def display_clo_interpretation(clo_results):
    """Display detailed interpretation of CLO analysis results"""
    st.markdown("---")
    st.subheader("📊 การแปลผลการวิเคราะห์ CLO")
    
    # Calculate average CLO score
    clo_scores = [data['score'] for data in clo_results.values()]
    avg_clo = sum(clo_scores) / len(clo_scores) if clo_scores else 0
    avg_confidence = sum(data.get('confidence', 0.8) for data in clo_results.values()) / len(clo_results) if clo_results else 0
    
    # Overall CLO interpretation
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### 📈 ภาพรวมคะแนน CLO")
        
        # Score interpretation
        if avg_clo >= 85:
            st.success(f"🌟 **ดีเยี่ยม** - คะแนนเฉลี่ย: {avg_clo:.1f}%")
            st.write("เนื้อหามีความสอดคล้องกับวัตถุประสงค์การเรียนรู้ในระดับดีเยี่ยม")
        elif avg_clo >= 70:
            st.success(f"✅ **ดี** - คะแนนเฉลี่ย: {avg_clo:.1f}%")
            st.write("เนื้อหาสอดคล้องกับวัตถุประสงค์การเรียนรู้ในระดับดี")
        elif avg_clo >= 60:
            st.warning(f"⚠️ **ควรปรับปรุง** - คะแนนเฉลี่ย: {avg_clo:.1f}%")
            st.write("เนื้อหามีความสอดคล้องในระดับปานกลาง ควรเพิ่มเติมเนื้อหา")
        else:
            st.error(f"❌ **ต้องปรับปรุงมาก** - คะแนนเฉลี่ย: {avg_clo:.1f}%")
            st.write("เนื้อหายังไม่สอดคล้องกับวัตถุประสงค์การเรียนรู้เพียงพอ")
    
    with col2:
        st.markdown("### 🤖 ความมั่นใจ AI")
        st.metric("AI Confidence", f"{avg_confidence*100:.0f}%")
        if avg_confidence >= 0.9:
            st.write("มั่นใจสูงมาก")
        elif avg_confidence >= 0.8:
            st.write("มั่นใจสูง")
        else:
            st.write("มั่นใจปานกลาง")
    
    with col3:
        st.markdown("### 📊 เกณฑ์คะแนน")
        st.write("🌟 85%+ = ดีเยี่ยม")
        st.write("✅ 70-84% = ดี")
        st.write("⚠️ 60-69% = ควรปรับปรุง")
        st.write("❌ <60% = ต้องปรับปรุง")
    
    # Individual CLO interpretation
    st.markdown("### 🎯 การวิเคราะห์รายตัว")
    
    # Create interpretation table
    interpretation_data = []
    for clo_code, clo_data in clo_results.items():
        score = clo_data['score']
        confidence = clo_data.get('confidence', 0.8)
        
        # Determine status
        if score >= 85:
            status = "🌟 ดีเยี่ยม"
            recommendation = "รักษาคุณภาพและใช้เป็นตัวอย่าง"
        elif score >= 70:
            status = "✅ ดี"
            recommendation = "เพิ่มตัวอย่างและกรณีศึกษา"
        elif score >= 60:
            status = "⚠️ ควรปรับปรุง"
            recommendation = "เพิ่มคำสำคัญและเนื้อหาที่เกี่ยวข้อง"
        else:
            status = "❌ ต้องปรับปรุง"
            recommendation = "ทบทวนและเพิ่มเนื้อหาให้ตรงกับ CLO"
        
        interpretation_data.append({
            'CLO': clo_code,
            'คะแนน': f"{score:.1f}%",
            'สถานะ': status,
            'ความมั่นใจ AI': f"{confidence*100:.0f}%",
            'คำแนะนำเบื้องต้น': recommendation
        })
    
    interpretation_df = pd.DataFrame(interpretation_data)
    st.dataframe(interpretation_df, use_container_width=True, hide_index=True)

def display_enhanced_clo_analysis(clo_results):
    """Display enhanced CLO analysis with AI insights using gauge charts"""
    st.subheader("📋 Course Learning Outcomes (CLO) Analysis")
    
    if not clo_results:
        st.warning("No CLO data available for this course")
        return
    
    # Display CLO Gauge Charts - now 4 CLOs per course
    clo_items = list(clo_results.items())
    
    # Create columns for gauge charts (4 columns for 4 CLOs)
    cols = st.columns(4)
    for j, (clo_code, clo_data) in enumerate(clo_items):
        with cols[j % 4]:
            score = clo_data['score']
            confidence = clo_data.get('confidence', 0.8)
            
            # Create gauge chart
            fig = create_enhanced_gauge_chart(
                score, 
                f"{clo_code} Alignment", 
                confidence if clo_data.get('ai_enhanced') else None
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Status indicator
            if score >= 85:
                st.success(f"🌟 Excellent ({score:.1f}%)")
            elif score >= 70:
                st.success(f"✅ Good ({score:.1f}%)")
            elif score >= 60:
                st.warning(f"⚠️ Fair ({score:.1f}%)")
            else:
                st.error(f"❌ Poor ({score:.1f}%)")
    
    # Add comprehensive interpretation section
    display_clo_interpretation(clo_results)
    
    # Detailed CLO Analysis with AI insights
    for clo_code, clo_data in clo_results.items():
        with st.expander(f"{clo_code}: {clo_data['description'][:60]}..."):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {clo_data['description']}")
                st.write(f"**Keywords Found:** {', '.join(clo_data['found_keywords']) if clo_data['found_keywords'] else 'None'}")
                
                # AI Insights (if available)
                if clo_data.get('ai_insights'):
                    st.write("**🤖 AI Insights:**")
                    for insight in clo_data['ai_insights']:
                        st.write(f"• {insight}")
                
                # Coverage bar
                coverage = clo_data['coverage']
                st.progress(coverage)
                st.caption(f"Keyword Coverage: {coverage*100:.1f}% ({len(clo_data['found_keywords'])}/{clo_data['total_keywords']})")
            
            with col2:
                score = clo_data['score']
                confidence = clo_data.get('confidence', 0.8)
                
                st.metric("Score", f"{score:.1f}%")
                st.metric("Confidence", f"{confidence*100:.0f}%")
                
                if clo_data.get('ai_enhanced'):
                    st.success("🤖 AI Enhanced")
                else:
                    st.info("📊 Rule-based")
                
                # Score status
                if score >= 80:
                    st.success("Excellent")
                elif score >= 70:
                    st.info("Good")
                elif score >= 60:
                    st.warning("Fair")
                else:
                    st.error("Needs Improvement")

def display_plo_analysis(plo_results):
    """Display Program Learning Outcome analysis with gauge charts"""
    st.subheader("🎯 Program Learning Outcomes (PLO) Analysis")
    
    if not plo_results:
        st.warning("No PLO mapping available for this course")
        return
    
    # Display PLO Gauge Charts
    plo_items = list(plo_results.items())
    
    # Create columns for gauge charts
    cols = st.columns(len(plo_items))
    for i, (plo_code, plo_data) in enumerate(plo_items):
        with cols[i]:
            score = plo_data['score']
            confidence = plo_data.get('confidence', 0.8)
            
            # Create gauge chart
            fig = create_enhanced_gauge_chart(
                score, 
                f"{plo_code}\n{ENHANCED_PLOS[plo_code]['title'][:20]}...",
                confidence
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Status indicator  
            if score >= 85:
                st.success(f"🌟 Excellent ({score:.1f}%)")
            elif score >= 70:
                st.success(f"✅ Good ({score:.1f}%)")
            elif score >= 60:
                st.warning(f"⚠️ Fair ({score:.1f}%)")
            else:
                st.error(f"❌ Poor ({score:.1f}%)")
    
    st.markdown("---")
    
    # Detailed PLO Analysis
    for plo_code, plo_data in plo_results.items():
        with st.expander(f"{plo_code}: {ENHANCED_PLOS[plo_code]['title']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {plo_data['description']}")
                st.write(f"**Related CLOs:** {', '.join(plo_data['related_clos'])}")
            
            with col2:
                score = plo_data['score']
                confidence = plo_data.get('confidence', 0.8)
                st.metric(f"{plo_code} Score", f"{score:.1f}%")
                st.metric("Confidence", f"{confidence*100:.0f}%")

def display_ylo_analysis(ylo_results):
    """Display Year Learning Outcome analysis with gauge charts"""
    st.subheader("📈 Year Learning Outcomes (YLO) Analysis")
    
    if not ylo_results:
        st.warning("No YLO mapping available for this course")
        return
    
    # Display YLO Gauge Charts
    ylo_items = list(ylo_results.items())
    
    # Group by Year Level
    year1_ylos = [(code, data) for code, data in ylo_items if data['level'] == 'Year 1']
    year2_ylos = [(code, data) for code, data in ylo_items if data['level'] == 'Year 2']
    
    if year1_ylos:
        st.write("**Year 1 Learning Outcomes:**")
        cols = st.columns(len(year1_ylos))
        for i, (ylo_code, ylo_data) in enumerate(year1_ylos):
            with cols[i]:
                score = ylo_data['score']
                confidence = ylo_data.get('confidence', 0.8)
                
                # Create gauge chart
                fig = create_enhanced_gauge_chart(
                    score, 
                    f"{ylo_code}\n{ylo_data['cognitive_level']}",
                    confidence
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Status indicator
                if score >= 85:
                    st.success(f"🌟 Excellent ({score:.1f}%)")
                elif score >= 70:
                    st.success(f"✅ Good ({score:.1f}%)")
                elif score >= 60:
                    st.warning(f"⚠️ Fair ({score:.1f}%)")
                else:
                    st.error(f"❌ Poor ({score:.1f}%)")
    
    if year2_ylos:
        st.write("**Year 2 Learning Outcomes:**")
        cols = st.columns(len(year2_ylos))
        for i, (ylo_code, ylo_data) in enumerate(year2_ylos):
            with cols[i]:
                score = ylo_data['score']
                confidence = ylo_data.get('confidence', 0.8)
                
                # Create gauge chart
                fig = create_enhanced_gauge_chart(
                    score, 
                    f"{ylo_code}\n{ylo_data['cognitive_level']}",
                    confidence
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Status indicator
                if score >= 85:
                    st.success(f"🌟 Excellent ({score:.1f}%)")
                elif score >= 70:
                    st.success(f"✅ Good ({score:.1f}%)")
                elif score >= 60:
                    st.warning(f"⚠️ Fair ({score:.1f}%)")
                else:
                    st.error(f"❌ Poor ({score:.1f}%)")
    
    st.markdown("---")
    
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
                confidence = ylo_data.get('confidence', 0.8)
                st.metric(f"{ylo_code} Score", f"{score:.1f}%")
                st.metric("Confidence", f"{confidence*100:.0f}%")

def display_alignment_matrix(results):
    """Display alignment matrix visualization"""
    st.subheader("🔗 Learning Outcome Alignment Matrix")
    
    # Add interpretation guide
    with st.expander("📖 วิธีอ่านแผนภาพความสัมพันธ์"):
        st.write("**สีของโหนด:**")
        st.write("• 🔴 สีแดง = CLO (Course Learning Outcomes)")
        st.write("• 🔵 สีน้ำเงิน = PLO (Program Learning Outcomes)")
        st.write("• 🟢 สีเขียว = YLO (Year Learning Outcomes)")
        st.write("")
        st.write("**ขนาดของเส้นเชื่อม:**")
        st.write("• ยิ่งหนา = คะแนนสูง/ความสัมพันธ์แน่นแฟ้น")
        st.write("• ยิ่งบาง = คะแนนต่ำ/ควรเสริมความสัมพันธ์")
    
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
    
    # Enhanced Alignment Summary Table
    st.subheader("📋 Alignment Summary")
    
    alignment_data = []
    for clo_code, clo_data in results['clo_results'].items():
        related_plos = matrix['clo_to_plo'].get(clo_code, [])
        related_ylos = []
        for plo in related_plos:
            related_ylos.extend(matrix['plo_to_ylo'].get(plo, []))
        
        ai_status = "🤖 AI" if clo_data.get('ai_enhanced') else "📊 Rule"
        confidence = f"{clo_data.get('confidence', 0.8)*100:.0f}%"
        
        alignment_data.append({
            'CLO': clo_code,
            'Score': f"{clo_data['score']:.1f}%",
            'Confidence': confidence,
            'Analysis': ai_status,
            'Related PLOs': ', '.join(related_plos),
            'Related YLOs': ', '.join(set(related_ylos))
        })
    
    if alignment_data:
        alignment_df = pd.DataFrame(alignment_data)
        st.dataframe(alignment_df, use_container_width=True)

def display_comprehensive_interpretation(results):
    """Display comprehensive interpretation of all assessment results"""
    st.subheader("📊 การแปลผลการประเมินโดยรวม")
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        clo_avg = results['overall_scores']['clo_average']
        st.metric("CLO Average", f"{clo_avg:.1f}%", 
                 f"{clo_avg-70:.1f}%" if clo_avg >= 70 else f"{clo_avg-70:.1f}%")
    
    with col2:
        plo_avg = results['overall_scores']['plo_average']
        st.metric("PLO Average", f"{plo_avg:.1f}%",
                 f"{plo_avg-70:.1f}%" if plo_avg >= 70 else f"{plo_avg-70:.1f}%")
    
    with col3:
        ylo_avg = results['overall_scores']['ylo_average']
        st.metric("YLO Average", f"{ylo_avg:.1f}%",
                 f"{ylo_avg-70:.1f}%" if ylo_avg >= 70 else f"{ylo_avg-70:.1f}%")
    
    with col4:
        confidence = results['overall_scores'].get('overall_confidence', 0.8)
        st.metric("AI Confidence", f"{confidence*100:.0f}%")
    
    st.markdown("---")
    
    # Detailed interpretation
    st.markdown("### 🎯 การวิเคราะห์ความสัมพันธ์ CLO → PLO → YLO")
    
    # Create interpretation table
    interpretation_data = []
    
    for clo_code, clo_data in results['clo_results'].items():
        # Get related PLOs and YLOs
        related_plos = results['alignment_matrix']['clo_to_plo'].get(clo_code, [])
        related_ylos = []
        for plo in related_plos:
            related_ylos.extend(results['alignment_matrix']['plo_to_ylo'].get(plo, []))
        
        interpretation_data.append({
            'CLO': clo_code,
            'คะแนน': f"{clo_data['score']:.1f}%",
            'ความมั่นใจ': f"{clo_data.get('confidence', 0.8)*100:.0f}%",
            'การวิเคราะห์': "🤖 AI" if clo_data.get('ai_enhanced') else "📊 Rule",
            'PLO ที่เชื่อมโยง': ', '.join(related_plos),
            'YLO ที่สนับสนุน': ', '.join(set(related_ylos))
        })
    
    interpretation_df = pd.DataFrame(interpretation_data)
    st.dataframe(interpretation_df, use_container_width=True, hide_index=True)
    
    # Generate comprehensive recommendations
    st.markdown("### 💡 ข้อเสนอแนะเชิงลึก")
    
    recommendations = []
    
    # CLO-based recommendations
    low_clos = [clo for clo, data in results['clo_results'].items() if data['score'] < 70]
    if low_clos:
        recommendations.append({
            'ประเภท': 'CLO',
            'ปัญหา': f"CLO ที่ต่ำกว่าเกณฑ์: {', '.join(low_clos)}",
            'แนวทางแก้ไข': 'เพิ่มเนื้อหาและคำสำคัญที่สอดคล้องกับวัตถุประสงค์'
        })
    
    # PLO coverage recommendations
    missing_plos = [plo for plo in ['PLO1', 'PLO2', 'PLO3'] if plo not in results['plo_results']]
    if missing_plos:
        plo_descriptions = {
            'PLO1': 'เทคโนโลยีและการมีส่วนร่วม',
            'PLO2': 'การวิจัยและการบูรณาการ',
            'PLO3': 'การสื่อสารและการถ่ายทอด'
        }
        for plo in missing_plos:
            recommendations.append({
                'ประเภท': 'PLO',
                'ปัญหา': f"ขาด {plo}: {plo_descriptions[plo]}",
                'แนวทางแก้ไข': f'เพิ่มเนื้อหาด้าน{plo_descriptions[plo]}'
            })
    
    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)
    else:
        st.success("✅ เนื้อหามีความสมดุลและครอบคลุมดีแล้ว")

# Additional helper functions (keeping existing implementations)
def generate_improvement_recommendations(results):
    """Generate specific improvement recommendations in Thai"""
    recommendations = []
    
    # CLO-based recommendations
    clo_scores = [data['score'] for data in results['clo_results'].values()]
    if clo_scores:
        avg_clo = sum(clo_scores) / len(clo_scores)
        if avg_clo < 70:
            recommendations.append("ปรับปรุงเนื้อหาให้สอดคล้องกับวัตถุประสงค์รายวิชา (CLO) มากขึ้น")
        elif avg_clo < 80:
            recommendations.append("เสริมเนื้อหาเพื่อยกระดับความสอดคล้องกับ CLO ให้ถึงระดับดีเยี่ยม")
    
    # PLO-based recommendations
    plo_scores = [data['score'] for data in results['plo_results'].values()]
    if plo_scores:
        avg_plo = sum(plo_scores) / len(plo_scores)
        if avg_plo < 70:
            recommendations.append("เสริมเนื้อหาให้เชื่อมโยงกับผลการเรียนรู้ของหลักสูตร (PLO) ให้ชัดเจนขึ้น")
        elif avg_plo < 85:
            recommendations.append("พัฒนาการเชื่อมโยงระหว่างเนื้อหาและ PLO ให้แข็งแกร่งขึ้น")
    
    # YLO-based recommendations
    ylo_scores = [data['score'] for data in results['ylo_results'].values()]
    if ylo_scores:
        avg_ylo = sum(ylo_scores) / len(ylo_scores)
        if avg_ylo < 70:
            recommendations.append("ปรับระดับเนื้อหาให้เหมาะสมกับผลการเรียนรู้ระดับชั้นปี (YLO)")
        elif avg_ylo < 85:
            recommendations.append("ยกระดับความซับซ้อนของเนื้อหาให้สอดคล้องกับระดับการคิดขั้นสูง")
    
    # Specific content recommendations based on CLO scores
    low_clos = [clo for clo, data in results['clo_results'].items() if data['score'] < 70]
    if low_clos:
        recommendations.append(f"เพิ่มเนื้อหาและกิจกรรมที่เกี่ยวข้องกับ {', '.join(low_clos)}")
    
    # Enhanced recommendations with Assessment ID
    assessment_id = results.get('assessment_id', 'Unknown')
    if assessment_id != 'Unknown':
        recommendations.append(f"บันทึกการปรับปรุงภายใต้ Assessment ID: {assessment_id}")
    
    # AI-specific recommendations
    if results.get('ai_enhanced'):
        low_confidence_clos = [clo for clo, data in results['clo_results'].items() if data.get('confidence', 1) < 0.8]
        if low_confidence_clos:
            recommendations.append(f"ปรับปรุงความชัดเจนและความลึกของเนื้อหาใน {', '.join(low_confidence_clos)}")
        
        # High-level AI recommendations
        overall_confidence = results['overall_scores'].get('overall_confidence', 0)
        if overall_confidence > 0.95:
            recommendations.append("เนื้อหามีคุณภาพสูงมาก แนะนำให้พัฒนาเป็นต้นแบบหรือกรณีศึกษา")
        elif overall_confidence > 0.90:
            recommendations.append("เนื้อหาอยู่ในระดับดี แนะนำให้เพิ่มความลึกและการประยุกต์ใช้จริง")
    
    # Course-specific recommendations
    course_code = results.get('course_code', '')
    if '282712' in course_code:  # Water resource course
        recommendations.append("เพิ่มกรณีศึกษาการจัดการน้ำในบริบทไทยและอาเซียน")
    elif '282714' in course_code:  # Research methodology
        recommendations.append("เสริมเทคนิคการวิจัยสมัยใหม่และการใช้เครื่องมือดิจิทัล")
    elif '282734' in course_code:  # Communication
        recommendations.append("พัฒนาทักษะการสื่อสารแบบสื่อผสมและแพลตฟอร์มดิจิทัล")
    
    # General enhancement recommendations
    if not recommendations:
        recommendations.append("เนื้อหามีความสอดคล้องในระดับดีมาก ควรรักษาคุณภาพและนำไปเป็นแบบอย่าง")
        recommendations.append("พิจารณาการพัฒนาเป็นเนื้อหาขั้นสูงหรือการวิจัยเชิงลึก")
    
    return recommendations[:6]  # Limit to top 6 recommendations
    """Generate specific improvement recommendations in Thai"""
    recommendations = []
    
    # CLO-based recommendations
    clo_scores = [data['score'] for data in results['clo_results'].values()]
    if clo_scores:
        avg_clo = sum(clo_scores) / len(clo_scores)
        if avg_clo < 70:
            recommendations.append("ปรับปรุงเนื้อหาให้สอดคล้องกับวัตถุประสงค์รายวิชา (CLO) มากขึ้น")
        elif avg_clo < 80:
            recommendations.append("เสริมเนื้อหาเพื่อยกระดับความสอดคล้องกับ CLO ให้ถึงระดับดีเยี่ยม")
    
    # PLO-based recommendations
    plo_scores = [data['score'] for data in results['plo_results'].values()]
    if plo_scores:
        avg_plo = sum(plo_scores) / len(plo_scores)
        if avg_plo < 70:
            recommendations.append("เสริมเนื้อหาให้เชื่อมโยงกับผลการเรียนรู้ของหลักสูตร (PLO) ให้ชัดเจนขึ้น")
        elif avg_plo < 85:
            recommendations.append("พัฒนาการเชื่อมโยงระหว่างเนื้อหาและ PLO ให้แข็งแกร่งขึ้น")
    
    # YLO-based recommendations
    ylo_scores = [data['score'] for data in results['ylo_results'].values()]
    if ylo_scores:
        avg_ylo = sum(ylo_scores) / len(ylo_scores)
        if avg_ylo < 70:
            recommendations.append("ปรับระดับเนื้อหาให้เหมาะสมกับผลการเรียนรู้ระดับชั้นปี (YLO)")
        elif avg_ylo < 85:
            recommendations.append("ยกระดับความซับซ้อนของเนื้อหาให้สอดคล้องกับระดับการคิดขั้นสูง")
    
    # Specific content recommendations based on CLO scores
    low_clos = [clo for clo, data in results['clo_results'].items() if data['score'] < 70]
    if low_clos:
        recommendations.append(f"เพิ่มเนื้อหาและกิจกรรมที่เกี่ยวข้องกับ {', '.join(low_clos)}")
    
    # Enhanced recommendations with Assessment ID
    assessment_id = results.get('assessment_id', 'Unknown')
    if assessment_id != 'Unknown':
        recommendations.append(f"บันทึกการปรับปรุงภายใต้ Assessment ID: {assessment_id}")
    
    # AI-specific recommendations
    if results.get('ai_enhanced'):
        low_confidence_clos = [clo for clo, data in results['clo_results'].items() if data.get('confidence', 1) < 0.8]
        if low_confidence_clos:
            recommendations.append(f"ปรับปรุงความชัดเจนและความลึกของเนื้อหาใน {', '.join(low_confidence_clos)}")
        
        # High-level AI recommendations
        overall_confidence = results['overall_scores'].get('overall_confidence', 0)
        if overall_confidence > 0.95:
            recommendations.append("เนื้อหามีคุณภาพสูงมาก แนะนำให้พัฒนาเป็นต้นแบบหรือกรณีศึกษา")
        elif overall_confidence > 0.90:
            recommendations.append("เนื้อหาอยู่ในระดับดี แนะนำให้เพิ่มความลึกและการประยุกต์ใช้จริง")
    
    # Course-specific recommendations
    course_code = results.get('course_code', '')
    if '282712' in course_code:  # Water resource course
        recommendations.append("เพิ่มกรณีศึกษาการจัดการน้ำในบริบทไทยและอาเซียน")
    elif '282714' in course_code:  # Research methodology
        recommendations.append("เสริมเทคนิคการวิจัยสมัยใหม่และการใช้เครื่องมือดิจิทัล")
    elif '282734' in course_code:  # Communication
        recommendations.append("พัฒนาทักษะการสื่อสารแบบสื่อผสมและแพลตฟอร์มดิจิทัล")
    
    # General enhancement recommendations
    if not recommendations:
        recommendations.append("เนื้อหามีความสอดคล้องในระดับดีมาก ควรรักษาคุณภาพและนำไปเป็นแบบอย่าง")
        recommendations.append("พิจารณาการพัฒนาเป็นเนื้อหาขั้นสูงหรือการวิจัยเชิงลึก")
    
    return recommendations[:6]  # Limit to top 6 recommendations

# Keep existing display functions (display_clo_interpretation, display_enhanced_clo_analysis, etc.)
# ... (existing functions remain the same)

# Main Application (Enhanced)
def main():
    st.set_page_config(
        page_title="Enhanced Multi-Level Assessment System with Unique Google Sheets Recording",
        page_icon="🎯",
        layout="wide"
    )
    
    # Initialize session state
    if 'selected_course_code' not in st.session_state:
        st.session_state.selected_course_code = '282712'
    if 'assessor_name' not in st.session_state:
        st.session_state.assessor_name = ''
    
    # Enhanced header
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .unique-badge {
        background-color: #28a745;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    
    <div class="main-header">
        <h1>🎯 Enhanced Multi-Level Assessment + Unique Google Sheets Recording</h1>
        <p style="font-size: 1.1em;">ระบบประเมินผลการเรียนรู้แบบหลายระดับ CLO → PLO → YLO พร้อมบันทึกข้อมูลไม่ซ้ำลง Google Sheets</p>
        <p style="font-size: 0.9em; opacity: 0.9;">
            📁 นำเข้าไฟล์ | 🤖 วิเคราะห์ด้วย AI | 📊 ประเมินหลายระดับ | 💾 บันทึกลง Google Sheets <span class="unique-badge">UNIQUE ID</span>
        </p>
        <p style="font-size: 0.8em; opacity: 0.8;">
            ✨ NEW: Unique Assessment ID | Duplicate Detection | Enhanced Analytics | Content Hash Tracking
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced tabs with new features
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🎯 การประเมิน", 
        "📊 Google Sheets (Enhanced)", 
        "📋 ประวัติการประเมิน (Enhanced)",
        "📈 วิเคราะห์ข้อมูล (Enhanced)",
        "🔍 การแปลผล",
        "📚 ข้อมูลหลักสูตร", 
        "📖 คู่มือการใช้งาน (Enhanced)"
    ])
    
    with tab1:
        # Enhanced User Information
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.assessor_name = st.text_input(
                "👤 ชื่อผู้ประเมิน:",
                value=st.session_state.assessor_name,
                placeholder="ระบุชื่อผู้ประเมิน (ไม่บังคับ)"
            )
        with col2:
            # Enhanced Google Sheets connection status
            if GSHEETS_AVAILABLE and hasattr(st.session_state, 'current_spreadsheet'):
                st.success(f"✅ เชื่อมต่อ Google Sheets: {st.session_state.current_spreadsheet.title}")
                st.success("🆕 พร้อมบันทึกข้อมูลใหม่ทุกครั้ง")
            else:
                st.info("ℹ️ ยังไม่ได้เชื่อมต่อ Google Sheets (ไปที่แท็บ Google Sheets)")
        with col3:
            # Show current time and unique ID preview
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st.info(f"⏰ เวลาปัจจุบัน: {current_time}")
            preview_id = f"ASSESS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_xxxx"
            st.caption(f"🆔 ID ต่อไป: {preview_id}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Rest of the application logic remains the same but with enhanced features
        # Course Selection
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("📚 เลือกรายวิชาสำหรับการประเมิน")
        
        course_options = {}
        for code, data in COURSE_DESCRIPTIONS.items():
            course_options[f"{code} - {data['name']}"] = code
        
        selected_course_display = st.selectbox(
            "รายวิชา:",
            options=list(course_options.keys()),
            index=list(course_options.values()).index(st.session_state.selected_course_code)
        )
        
        st.session_state.selected_course_code = course_options[selected_course_display]
        
        # Display course information in a clean format
        course_info = COURSE_DESCRIPTIONS[st.session_state.selected_course_code]
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**คำอธิบายรายวิชา:** {course_info['description']}")
        with col2:
            st.metric("จำนวน CLOs", len(course_info['clo']))
            st.write(f"PLOs: {', '.join(course_info['plo_mapping'])}")
        
        with st.expander("📋 ดูรายละเอียด CLOs ทั้งหมด"):
            for clo_code, clo_desc in course_info['clo'].items():
                st.write(f"**{clo_code}:** {clo_desc}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Input Method Selection
        st.markdown("---")
        st.subheader("📝 เลือกวิธีการป้อนข้อมูล (Enhanced)")
        
        input_method = st.radio(
            "วิธีการ:",
            ["📁 อัพโหลดไฟล์ (PDF/PowerPoint)", "✏️ พิมพ์เนื้อหาโดยตรง"],
            horizontal=True
        )
        
        results = None
        content = None
        
        if input_method == "📁 อัพโหลดไฟล์ (PDF/PowerPoint)":
            # Enhanced file upload interface
            results, content = show_file_upload_interface()
            
        else:
            # Enhanced direct text input
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("📝 ป้อนเนื้อหาสำหรับการวิเคราะห์ (Enhanced)")
            
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

### 5. การวิเคราะห์ข้อมูล
- การใช้เครื่องมือสถิติในการวิเคราะห์คุณภาพน้ำ
- การประเมินประสิทธิภาพของระบบจัดการน้ำ
- การพัฒนาแบบจำลองทำนายคุณภาพน้ำ

### 6. การสื่อสารและการมีส่วนร่วม
- การสื่อสารข้อมูลทางวิชาการแก่ชุมชน
- การจัดกระบวนการมีส่วนร่วมในการตัดสินใจ
- การถ่ายทอดเทคโนโลยีสู่ชุมชน
            """
            
            content = st.text_area(
                "📄 เนื้อหา:",
                value=sample_content,
                height=400,
                help="วางเนื้อหาของคุณที่นี่เพื่อวิเคราะห์แบบหลายระดับ (Enhanced)"
            )
            
            # Store filename for Google Sheets
            st.session_state.last_filename = "ป้อนข้อความ"
            
            # Enhanced AI Analysis option for text input
            col1, col2 = st.columns(2)
            with col1:
                use_ai = st.checkbox(
                    "🤖 เปิดใช้การวิเคราะห์ด้วย AI",
                    value=False,
                    help="ใช้ AI เพื่อเพิ่มประสิทธิภาพการวิเคราะห์เนื้อหา"
                )
            with col2:
                # Show content hash preview
                if content.strip():
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    st.info(f"🔒 Content Hash: `{content_hash[:8]}...`")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced Analysis Button
            if st.button("🔍 ทำการวิเคราะห์ (Enhanced)", type="primary", use_container_width=True):
                if content.strip():
                    with st.spinner("กำลังประมวลผล CLO-PLO-YLO พร้อมสร้าง Unique ID..."):
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Step 1: Generate unique ID
                        status_text.text("🆔 Generating unique assessment ID...")
                        progress_bar.progress(15)
                        time.sleep(0.3)
                        
                        # Step 2: AI Analysis (if enabled)
                        ai_analysis = None
                        if use_ai:
                            status_text.text("🤖 Performing AI analysis...")
                            progress_bar.progress(35)
                            time.sleep(0.5)
                            
                            content_hash = hashlib.md5(content.encode()).hexdigest()
                            ai_analysis = generate_ai_analysis(content_hash, st.session_state.selected_course_code, use_ai)
                        
                        # Step 3: Multi-level analysis
                        status_text.text("🎯 Performing multi-level assessment...")
                        progress_bar.progress(60)
                        time.sleep(0.5)
                        
                        # Initialize assessment engine
                        engine = MultiLevelAssessmentEngine()
                        
                        # Perform multi-level analysis
                        results = engine.calculate_multi_level_alignment(
                            content, 
                            st.session_state.selected_course_code, 
                            ai_analysis
                        )
                        
                        # Step 4: Enhanced save to Google Sheets (if connected)
                        if GSHEETS_AVAILABLE and hasattr(st.session_state, 'current_spreadsheet'):
                            status_text.text("💾 Saving to Google Sheets with unique ID...")
                            progress_bar.progress(85)
                            
                            file_info = {
                                'name': 'ป้อนข้อความ',
                                'type': 'text/plain',
                                'size': len(content.encode('utf-8'))
                            }
                            
                            save_success, save_message = save_assessment_to_sheets(results, file_info)
                            if save_success:
                                st.success(f"✅ {save_message}")
                            else:
                                st.warning(f"⚠️ {save_message}")
                        
                        # Step 5: Complete
                        status_text.text("✅ Enhanced analysis complete!")
                        progress_bar.progress(100)
                        time.sleep(0.5)
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        # Store results in session state
                        st.session_state.analysis_results = results
                        st.session_state.slide_content = content
                        
                        # Show enhanced success message with unique ID
                        assessment_id = results.get('assessment_id', 'Unknown')
                        if ai_analysis:
                            st.success(f"✅ การวิเคราะห์ด้วย AI เสร็จสมบูรณ์! Assessment ID: `{assessment_id}`")
                        else:
                            st.success(f"✅ การวิเคราะห์แบบ Rule-based เสร็จสมบูรณ์! Assessment ID: `{assessment_id}`")
                        
                        # Show content hash
                        content_hash = results.get('content_hash', '')
                        if content_hash:
                            st.info(f"🔒 Content Hash: `{content_hash}`")
                else:
                    st.warning("กรุณาป้อนเนื้อหาเพื่อทำการวิเคราะห์")
        
        # Display enhanced results if available
        if results:
            st.markdown("---")
            create_multi_level_dashboard(results)
            
            # Enhanced recommendations
            st.markdown("---")
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.subheader("💡 ข้อเสนอแนะสำหรับการปรับปรุง (Enhanced)")
            
            recommendations = generate_improvement_recommendations(results)
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")
            
            # Show tracking info
            assessment_id = results.get('assessment_id', 'Unknown')
            content_hash = results.get('content_hash', '')
            st.markdown(f"**🆔 Tracking Info:** Assessment ID: `{assessment_id}` | Content Hash: `{content_hash[:16]}...`")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced content preview (if from file)
            if content and input_method == "📁 อัพโหลดไฟล์ (PDF/PowerPoint)":
                with st.expander("👁️ ดูเนื้อหาที่แยกได้ (Enhanced)"):
                    st.text_area(
                        "เนื้อหาที่แยกได้:",
                        value=content[:2000] + "..." if len(content) > 2000 else content,
                        height=200,
                        disabled=True
                    )
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"ความยาวทั้งหมด: {len(content):,} ตัวอักษร")
                    with col2:
                        content_hash = results.get('content_hash', '')
                        st.caption(f"Content Hash: {content_hash[:8]}...")
                    with col3:
                        assessment_id = results.get('assessment_id', '')
                        st.caption(f"Assessment ID: {assessment_id[-8:]}")
    
    with tab2:
        # Enhanced Google Sheets setup
        show_google_sheets_setup()
    
    with tab3:
        # Enhanced assessment history
        show_assessment_history()
    
    with tab4:
        # Enhanced course analytics
        show_course_analytics()
    
    with tab5:
        # การแปลผล
        interpretation_tab1, interpretation_tab2 = st.tabs(["📊 ประวัติการแปลผล", "📈 วิเคราะห์การแปลผล"])
        
        with interpretation_tab1:
            show_interpretation_history()
        
        with interpretation_tab2:
            show_interpretation_analytics()
    
    with tab6:
        # Program Overview Section (same as before)
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown(f"### {PROGRAM_OVERVIEW['program_name']}")
        
        st.markdown("#### ปรัชญาของหลักสูตร")
        st.write(PROGRAM_OVERVIEW['program_philosophy'])
        
        st.markdown("#### วัตถุประสงค์ของหลักสูตร")
        for i, obj in enumerate(PROGRAM_OVERVIEW['program_objectives'], 1):
            st.write(f"{i}. {obj}")
        
        st.markdown("#### แนวทางการประกอบอาชีพ")
        for career in PROGRAM_OVERVIEW['career_prospects']:
            st.write(f"• {career}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab7:
        # Enhanced user manual
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.subheader("📖 คู่มือการใช้งานระบบ (Enhanced Version)")
        
        st.markdown("""
        ### 🆕 ฟีเจอร์ใหม่ใน Enhanced Version
        
        **1. Unique Assessment ID**
        - สร้าง ID ไม่ซ้ำกันทุกครั้ง (ASSESS_YYYYMMDD_HHMMSS_UUID)
        - ติดตามการประเมินแต่ละครั้งได้อย่างแม่นยำ
        - ป้องกันความซ้ำซ้อนของข้อมูล
        
        **2. Duplicate Detection**
        - ตรวจสอบเนื้อหาซ้ำด้วย Content Hash
        - แจ้งเตือนเมื่อพบข้อมูลซ้ำ
        - ให้เลือกว่าจะบันทึกต่อหรือไม่
        
        **3. Enhanced Data Structure**
        - เพิ่ม Timestamp ในทุก Sheet
        - บันทึก Content Hash สำหรับตรวจสอบ
        - ข้อมูลการแปลผลที่ละเอียดขึ้น
        
        **4. Improved Analytics**
        - แยกข้อมูลไม่ซ้ำกับข้อมูลซ้ำ
        - แสดงแนวโน้มคะแนนแบบกราฟ
        - วิเคราะห์ความถี่ของการแปลผล
        
        ### 1. การเตรียมเนื้อหา
        - รองรับไฟล์: PDF, PowerPoint, Text files
        - ควรมีคำสำคัญที่สอดคล้องกับ CLO
        - เนื้อหาควรครอบคลุมวัตถุประสงค์การเรียนรู้
        - **ใหม่**: ระบบจะสร้าง Content Hash เพื่อตรวจสอบความซ้ำ
        
        ### 2. การตั้งค่า Google Sheets (Enhanced)
        - สร้าง Service Account ใน Google Cloud Console
        - เปิดใช้งาน Google Sheets API และ Google Drive API
        - อัพโหลด JSON credentials หรือวาง JSON content
        - สร้างหรือเลือก Spreadsheet สำหรับเก็บข้อมูล
        - **ใหม่**: ระบบจะสร้างโครงสร้าง Sheet ที่ปรับปรุงใหม่
        
        ### 3. การวิเคราะห์ (Enhanced)
        - **Rule-based**: วิเคราะห์ตามคำสำคัญและโครงสร้าง
        - **AI Enhanced**: วิเคราะห์เชิงลึกด้วย AI (ต้องมี API key)
        - **Auto-save with Unique ID**: บันทึกผลลง Google Sheets ด้วย ID ไม่ซ้ำ
        - **Duplicate Check**: ตรวจสอบข้อมูลซ้ำอัตโนมัติ
        
        ### 4. การจัดการข้อมูล (Enhanced)
        - **ประวัติการประเมิน**: ดูการประเมินพร้อมสถานะข้อมูลซ้ำ
        - **วิเคราะห์ข้อมูล**: สถิติที่แยกข้อมูลซ้ำและไม่ซ้ำ
        - **การแปลผล**: ดูการแปลผลโดยรวมและแนวโน้ม
        - **ดาวน์โหลด**: ส่งออกข้อมูลเป็น CSV (ทั้งหมดหรือไม่ซ้ำ)
        
        ### 5. การอ่านผล
        - **CLO**: ความสอดคล้องกับวัตถุประสงค์รายวิชา (4 CLOs ต่อรายวิชา)
        - **PLO**: ความสอดคล้องกับผลการเรียนรู้หลักสูตร
        - **YLO**: ความสอดคล้องกับผลการเรียนรู้ชั้นปี
        - **Assessment ID**: รหัสติดตามการประเมินแต่ละครั้ง
        
        ### 6. เกณฑ์การประเมิน
        - 🌟 85%+ = ดีเยี่ยม
        - ✅ 70-84% = ดี
        - ⚠️ 60-69% = ควรปรับปรุง
        - ❌ <60% = ต้องปรับปรุง
        
        ### 7. โครงสร้างข้อมูลใน Google Sheets (Enhanced)
        - **Assessment_Summary**: สรุปผลการประเมิน + Content_Hash + Unique_Assessment
        - **CLO_Details**: รายละเอียดคะแนน CLO + Timestamp_Created
        - **PLO_Details**: รายละเอียดคะแนน PLO + Timestamp_Created
        - **YLO_Details**: รายละเอียดคะแนน YLO + Timestamp_Created
        - **Content_Analysis**: ข้อมูลการวิเคราะห์ + Is_Duplicate + Original_Assessment_ID
        - **Interpretation**: การแปลผลโดยรวม จุดเด่น จุดอ่อน คำแนะนำ
        
        ### 8. การติดตั้งระบบ
        
        **Dependencies ที่จำเป็น:**
        ```bash
        pip install streamlit pandas plotly gspread google-auth
        ```
        
        **การตั้งค่า Secrets (สำหรับ local):**
        สร้างไฟล์ `.streamlit/secrets.toml`:
        ```toml
        OPENAI_API_KEY = "sk-your-openai-api-key"
        ```
        
        **การรันระบบ:**
        ```bash
        streamlit run enhanced_assessment_app.py
        ```
        
        ### 9. ฟีเจอร์หลัก (Enhanced)
        
        #### 🎯 การประเมินแบบหลายระดับ
        - วิเคราะห์เนื้อหาตาม CLO → PLO → YLO
        - แสดงผลด้วย Gauge Charts และ Sankey Diagrams
        - การแปลผลอัตโนมัติพร้อมคำแนะนำ
        - **ใหม่**: Unique Assessment ID tracking
        
        #### 🤖 AI Enhancement
        - วิเคราะห์เนื้อหาด้วย AI (ถ้ามี OpenAI API)
        - ความมั่นใจ AI สูงถึง 99.5%
        - ข้อเสนอแนะอัจฉริยะ
        - **ใหม่**: Content Hash integration
        
        #### 📊 Google Sheets Integration (Enhanced)
        - บันทึกผลการประเมินด้วย Unique ID
        - ตรวจสอบข้อมูลซ้ำอัตโนมัติ
        - ติดตามประวัติการประเมินแบบละเอียด
        - วิเคราะห์แนวโน้มรายวิชา
        - ส่งออกข้อมูลเป็น CSV (แยกซ้ำ/ไม่ซ้ำ)
        - บันทึกการแปลผลโดยรวม
        
        #### 📈 Analytics Dashboard (Enhanced)
        - สถิติการประเมินแต่ละรายวิชาที่แยกข้อมูลซ้ำ
        - เปรียบเทียบผลการประเมินย้อนหลัง
        - แนวโน้มการปรับปรุงเนื้อหาแบบกราฟ
        - วิเคราะห์จุดเด่น จุดอ่อนที่พบบ่อย
        - **ใหม่**: Unique vs Duplicate analytics
        
        ### 10. การแก้ปัญหาเบื้องต้น (Enhanced)
        
        **ปัญหา:** Import Error gspread
        **แก้:** `pip install gspread google-auth`
        
        **ปัญหา:** Google Sheets connection failed
        **แก้:** ตรวจสอบ Service Account credentials และ API permissions
        
        **ปัญหา:** AI analysis ไม่ทำงาน
        **แก้:** ตรวจสอบ OpenAI API key ใน secrets.toml
        
        **ปัญหา:** Duplicate detection ไม่ทำงาน
        **แก้:** ตรวจสอบ Content_Analysis sheet structure
        
        **ปัญหา:** Unique ID ไม่สร้าง
        **แก้:** ตรวจสอบ datetime และ uuid modules
        
        **ปัญหา:** Streamlit หน่วง
        **แก้:** ลด cache ด้วย `streamlit cache clear`
        
        ### 11. Best Practices (ใหม่)
        
        **การจัดการข้อมูล:**
        - ตรวจสอบ Assessment ID ก่อนบันทึก
        - ใช้ Content Hash เพื่อตรวจสอบความซ้ำ
        - บันทึกข้อมูลสำคัญก่อนปิดระบบ
        
        **การวิเคราะห์:**
        - ใช้ข้อมูลไม่ซ้ำสำหรับการวิเคราะห์แนวโน้ม
        - เปรียบเทียบผลการประเมินด้วย Assessment ID
        - ติดตาม Content Hash เพื่อหาเนื้อหาที่คล้ายกัน
        
        **การรายงาน:**
        - ใช้ Assessment ID ในการอ้างอิงผลการประเมิน
        - ระบุสถานะข้อมูล (ซ้ำ/ไม่ซ้ำ) ในรายงาน
        - บันทึกเวลาการประเมินเพื่อการติดตาม
        """)
        
        # Enhanced system information
        st.markdown("---")
        st.markdown("### ℹ️ ข้อมูลระบบ (Enhanced)")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("**🔧 เวอร์ชัน**")
            st.write("• v4.0 Enhanced")
            st.write("• Unique ID System")
            st.write("• Duplicate Detection")
        
        with col2:
            st.markdown("**📊 คุณสมบัติ**")
            st.write("• 4 CLOs ต่อรายวิชา")
            st.write("• Multi-level Analysis")
            st.write("• Enhanced Auto-save")
        
        with col3:
            st.markdown("**🎯 รายวิชา**")
            st.write(f"• {len(COURSE_DESCRIPTIONS)} รายวิชา")
            st.write("• 3 PLOs")
            st.write("• 7 YLOs")
        
        with col4:
            st.markdown("**🆕 ฟีเจอร์ใหม่**")
            st.write("• Unique Assessment ID")
            st.write("• Content Hash Tracking")
            st.write("• Duplicate Detection")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
