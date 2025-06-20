import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

def show_chart3():
    st.subheader("📧 รายงานสัดส่วนอีเมลบริษัทจากผู้สร้างเอกสาร")

    if 'file_bytes' not in st.session_state or 'data_source' not in st.session_state:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์และเลือกชุดข้อมูลในหน้า Home ก่อน")
        return

    try:
        uploaded_file = BytesIO(st.session_state['file_bytes'])
        sheet_name = 'Company Email' if st.session_state['data_source'] == 'ALL Data' else 'Tara-Silom Email Summary'
        email_df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

        fig = px.pie(email_df, names='Domain', values='Count')
        st.plotly_chart(fig)

        st.markdown("📄 **ตารางสรุปโดเมนอีเมล**")
        st.dataframe(email_df)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
