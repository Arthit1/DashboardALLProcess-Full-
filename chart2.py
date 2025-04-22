import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm, rcParams
import os
import requests

# Register Sarabun font
def register_sarabun_font(save_dir="fonts"):
    font_name = "Sarabun"
    os.makedirs(save_dir, exist_ok=True)
    font_path = os.path.join(save_dir, f"{font_name}.ttf")

    if not os.path.exists(font_path):
        css_url = f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}&display=swap"
        response = requests.get(css_url)
        if response.status_code == 200:
            ttf_url = response.text.split("url(")[1].split(")")[0].replace('"', '')
            font_data = requests.get(ttf_url).content
            with open(font_path, "wb") as f:
                f.write(font_data)
        else:
            st.warning("Could not download Sarabun font.")
            return None

    prop = fm.FontProperties(fname=font_path)
    rcParams["font.family"] = prop.get_name()
    return font_path

sarabun_path = register_sarabun_font()

def show_chart2():
    st.subheader("📊 Pie Chart of สถานะของเอกสาร")

    if "uploaded_data" not in st.session_state:
        st.warning("⚠️ Please upload a file on the Home page first.")
        return

    df = st.session_state["uploaded_data"]

    status_column = "สถานะของเอกสาร"
    if status_column not in df.columns:
        st.error(f"❌ Column '{status_column}' not found in the uploaded data.")
        return

    unique_statuses = df[status_column].astype(str).unique()
    selected_statuses = st.multiselect(
        "เลือกสถานะที่จะแสดงในกราฟ (Select statuses to include)",
        options=unique_statuses,
        default=[]
    )

    if not selected_statuses:
        st.info("ℹ️ กรุณาเลือกสถานะเพื่อแสดงกราฟ (Please select at least one status).")
        return

    filtered_df = df[df[status_column].isin(selected_statuses)]
    status_counts = filtered_df[status_column].value_counts()

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        status_counts,
        labels=status_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=plt.cm.Paired.colors[:len(status_counts)],
        wedgeprops=dict(width=0.4, edgecolor='w')
    )
    ax.axis("equal")

    if sarabun_path:
        prop = fm.FontProperties(fname=sarabun_path)
        for text in texts + autotexts:
            text.set_fontproperties(prop)

        # Custom labels with record count
        for text, count in zip(texts, status_counts):
            text.set_text(f"{text.get_text()} ({count} รายการ)")

    st.pyplot(fig)

    st.markdown(f"📦 **รวมทั้งหมด:** {status_counts.sum()} รายการ")
