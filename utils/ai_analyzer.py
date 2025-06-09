import os
import json
from typing import Dict, Any

class AIAnalyzer:
    def __init__(self, provider='openai', api_key=None):
        self.provider = provider
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.client = None
        
        if self.provider == 'openai' and self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("Warning: OpenAI library not installed. AI features disabled.")
                self.client = None
    
    def analyze_slide(self, content: str, plos: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze slide content against PLOs"""
        
        if not self.api_key or not self.client:
            return self._get_mock_analysis()
        
        try:
            prompt = self._create_prompt(content, plos)
            
            if self.provider == 'openai':
                return self._analyze_with_openai(prompt)
            else:
                return self._get_mock_analysis()
                
        except Exception as e:
            print(f"AI Analysis Error: {e}")
            return self._get_mock_analysis()
    
    def _create_prompt(self, content: str, plos: Dict[str, Any]) -> str:
        """Create analysis prompt"""
        prompt = f"""
วิเคราะห์เนื้อหา Slide การสอนต่อไปนี้ และประเมินความสอดคล้องกับผลการเรียนรู้ที่คาดหวัง (PLOs):

เนื้อหา Slide (ส่วนแรก):
{content[:2000]}...

ผลการเรียนรู้ที่คาดหวัง (PLOs):
"""
        
        for plo_code, plo_data in plos.items():
            prompt += f"""
- {plo_code} ({plo_data['weight']}%): {plo_data['description']}
  คำสำคัญ: {', '.join(plo_data['keywords'][:5])}
"""
        
        prompt += """

กรุณาวิเคราะห์และให้ผลลัพธ์ในรูปแบบ JSON ดังนี้:
{
  "PLO1": {
    "score": <คะแนน 0-100>,
    "foundKeywords": [<คำสำคัญที่พบ 3-5 คำ>],
    "strengths": [<จุดเด่น 2-3 ข้อ>],
    "suggestions": [<ข้อเสนอแนะ 2-3 ข้อ>]
  },
  "PLO2": { ... },
  "PLO3": { ... },
  "overall_score": <คะแนนรวมถ่วงน้ำหนัก>,
  "general_suggestions": [<คำแนะนำทั่วไป 2-3 ข้อ>]
}

ตอบเป็น JSON เท่านั้น ไม่ต้องมีคำอธิบายเพิ่มเติม
"""
        return prompt
    
    def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้เชี่ยวชาญด้านการประเมินคุณภาพการศึกษา ตอบเป็น JSON เท่านั้น"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={ "type": "json_object" }
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return self._get_mock_analysis()
    
    def _get_mock_analysis(self) -> Dict[str, Any]:
        """Return mock analysis for demo"""
        import random
        
        # สุ่มคะแนนให้สมจริง
        plo1_score = random.randint(65, 85)
        plo2_score = random.randint(70, 90)
        plo3_score = random.randint(60, 80)
        
        overall = round((plo1_score * 0.35 + plo2_score * 0.35 + plo3_score * 0.30))
        
        return {
            "PLO1": {
                "score": plo1_score,
                "foundKeywords": ["เทคโนโลยี", "ชุมชน", "ยั่งยืน"],
                "strengths": [
                    "มีการกล่าวถึงเทคโนโลยีที่เกี่ยวข้องกับสิ่งแวดล้อม",
                    "แสดงแนวทางการพัฒนาที่ยั่งยืน"
                ],
                "suggestions": [
                    "ควรเพิ่มเนื้อหาเกี่ยวกับการมีส่วนร่วมของชุมชนให้ชัดเจนขึ้น",
                    "แนะนำให้เชื่อมโยงกับ SDGs มากขึ้น"
                ]
            },
            "PLO2": {
                "score": plo2_score,
                "foundKeywords": ["วิจัย", "วิเคราะห์", "บูรณาการ"],
                "strengths": [
                    "มีกระบวนการวิจัยที่ชัดเจน",
                    "แสดงการวิเคราะห์ข้อมูลอย่างเป็นระบบ"
                ],
                "suggestions": [
                    "ควรเพิ่มการบูรณาการข้ามศาสตร์",
                    "เพิ่มรายละเอียดระเบียบวิธีวิจัย"
                ]
            },
            "PLO3": {
                "score": plo3_score,
                "foundKeywords": ["นำเสนอ", "อธิบาย", "สื่อสาร"],
                "strengths": [
                    "การจัดลำดับเนื้อหามีความเป็นระบบ",
                    "ใช้ภาษาที่เข้าใจได้"
                ],
                "suggestions": [
                    "ควรเพิ่มภาพ แผนภูมิ และ infographic",
                    "ใช้ตัวอย่างที่เข้าใจง่ายมากขึ้น"
                ]
            },
            "overall_score": overall,
            "general_suggestions": [
                "ควรเพิ่ม case study จากบริบทท้องถิ่น",
                "เพิ่มกิจกรรมที่ส่งเสริมการมีส่วนร่วมของผู้เรียน",
                "อ้างอิงงานวิจัยที่ทันสมัย (ภายใน 3 ปี)"
            ]
        }
