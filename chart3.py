import streamlit as st
import pandas as pd
import plotly.express as px

def show_chart3():
    st.subheader("📊 Comparison: Correct Data vs Duplicate & Wrong Data")

    if 'uploaded_data' not in st.session_state:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์ในหน้า Home ก่อน")
        return

    # Read from uploaded Excel file
    uploaded_file = st.session_state.get("uploaded_file")
    if uploaded_file is None:
        st.error("No file found in session. Please re-upload.")
        return

    try:
        # Load both sheets
        correct_df = pd.read_excel(uploaded_file, sheet_name='Correct Data')
        wrong_df = pd.read_excel(uploaded_file, sheet_name='Duplicate & Wrong Data')

        # Count rows
        correct_count = len(correct_df)
        wrong_count = len(wrong_df)

        # Create pie chart
        pie_data = pd.DataFrame({
            'Data Type': ['Correct Data', 'Duplicate & Wrong Data'],
            'Count': [correct_count, wrong_count]
        })

        fig = px.pie(pie_data, names='Data Type', values='Count', title="Data Distribution")

        st.plotly_chart(fig)
        st.markdown(f"✅ **Correct Data:** {correct_count} records  \n❌ **Duplicate & Wrong Data:** {wrong_count} records  \n📦 **Total:** {correct_count + wrong_count} records")

    except Exception as e:
        st.error(f"An error occurred: {e}")
