import streamlit as st
import pandas as pd
from io import BytesIO

def home():
    st.title("📂 Upload Your File")

    uploaded_file = st.file_uploader("Choose a file (Excel or CSV)", type=["xlsx", "xls", "csv"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        st.session_state['file_bytes'] = file_bytes
        st.session_state['uploaded_file'] = uploaded_file

    # Reuse last uploaded file if available
    if 'file_bytes' in st.session_state:
        st.markdown("### 🔀 เลือกชุดข้อมูลที่ต้องการแสดงผล")
        selected_source = st.selectbox(
            "เลือกชุดข้อมูล",
            ["ALL Data", "Tara-Silom Data"],
            index=["ALL Data", "Tara-Silom Data"].index(st.session_state.get('data_source', "ALL Data"))
        )
        st.session_state['data_source'] = selected_source

        try:
            file_like = BytesIO(st.session_state['file_bytes'])
            if uploaded_file and uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(file_like)
            else:
                sheet_name = 'Correct Data' if selected_source == 'ALL Data' else 'Tara-Silom'
                df = pd.read_excel(file_like, sheet_name=sheet_name)

            st.session_state['uploaded_data'] = df
            st.success("✅ File loaded from session memory!")
            st.dataframe(df.head())

        except Exception as e:
            st.error(f"❌ Error reading file from memory: {e}")
