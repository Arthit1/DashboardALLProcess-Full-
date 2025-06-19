import streamlit as st
import pandas as pd
import plotly.express as px

def show_chart3():
    st.subheader("📧 รายงานสัดส่วนอีเมลบริษัทจากผู้สร้างเอกสาร")

    if 'uploaded_file' not in st.session_state:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์ในหน้า Home ก่อน")
        return

    uploaded_file = st.session_state.get("uploaded_file")
    if uploaded_file is None:
        st.error("No file found in session. Please re-upload.")
        return

    try:
        email_df = pd.read_excel(uploaded_file, sheet_name='Company Email')

        fig = px.pie(email_df, names='Domain', values='Count')
        st.plotly_chart(fig)

        st.markdown("📄 **ตารางสรุปโดเมนอีเมล**")
        st.dataframe(email_df)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
