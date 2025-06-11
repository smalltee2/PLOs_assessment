# เพิ่มฟังก์ชันเหล่านี้ใน class GoogleSheetsManager

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

# เพิ่มฟังก์ชันสำหรับแสดงการแปลผลใน Streamlit

def show_interpretation_history():
    """Show interpretation history from Google Sheets"""
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
