import streamlit as st
import pandas as pd

def home():
    st.title("📂 Upload Your File")

    uploaded_file = st.file_uploader("Choose a file (Excel or CSV)", type=["xlsx", "xls", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success("✅ File uploaded successfully!")
            st.dataframe(df.head())  # Show first few rows

            # ✅ Store both the dataframe and the original file for later use
            st.session_state['uploaded_data'] = df
            st.session_state['uploaded_file'] = uploaded_file  # <-- this line is key!

        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
