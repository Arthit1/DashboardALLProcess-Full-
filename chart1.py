import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm, rcParams
import os
import requests

# Function to download and register Sarabun font
def register_sarabun_font(save_dir="fonts"):
    font_name = "Sarabun"
    os.makedirs(save_dir, exist_ok=True)
    font_path = os.path.join(save_dir, f"{font_name}.ttf")

    if not os.path.exists(font_path):
        # Google Fonts URL for Sarabun font
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
    return prop.get_name()

# Register Sarabun font for charts
sarabun_font = register_sarabun_font()

def show_chart1():
    st.title("📦 รายงานจำนวนอุปกรณ์ที่เข้าสู่ขั้นตอนรอหน่วยงานกลางดำเนินการ")

    # Use the registered Sarabun font for Thai text
    if sarabun_font:
        font_path = os.path.join("fonts", "Sarabun.ttf")
        prop = fm.FontProperties(fname=font_path)
        rcParams["font.family"] = prop.get_name()

    # Check if data exists in session_state
    if 'uploaded_data' in st.session_state:
        df = st.session_state['uploaded_data']

        if 'วันที่ Desktop Support ปิดงาน' in df.columns and 'สถานะของเอกสาร' in df.columns:
            # Filter the data where 'สถานะของเอกสาร' is 'รอหน่วยงานกลางดูแลทรัพย์สินดำเนินการ'
            df_filtered = df[df['สถานะของเอกสาร'] == 'รอหน่วยงานกลางดูแลทรัพย์สินดำเนินการ']

            # Check if there is data after filtering
            if not df_filtered.empty:
                df_filtered['วันที่ Desktop Support ปิดงาน'] = pd.to_datetime(df_filtered['วันที่ Desktop Support ปิดงาน'], errors='coerce')
                df_filtered = df_filtered.dropna(subset=['วันที่ Desktop Support ปิดงาน'])

                # Extract month and year for grouping
                df_filtered['Year-Month'] = df_filtered['วันที่ Desktop Support ปิดงาน'].dt.to_period('M')

                # Create a list of unique months for selection
                months = df_filtered['Year-Month'].unique()
                month_options = ['ALL'] + [str(month) for month in months]

                # Allow user to select a month
                selected_month = st.selectbox(
                    "เลือกเดือนที่ต้องการดูข้อมูล",
                    month_options,
                    index=0  # Default to 'ALL'
                )

                # Filter data based on the selected month
                if selected_month != 'ALL':
                    df_filtered = df_filtered[df_filtered['Year-Month'] == pd.Period(selected_month)]

                # Summary data (count per date within the month)
                summary = df_filtered['วันที่ Desktop Support ปิดงาน'].dt.date.value_counts().sort_index()
                summary_df = pd.DataFrame({
                    'วันที่ปิดงานโดย Desktop Support': summary.index,
                    'จำนวนอุปกรณ์': summary.values
                })

                # Bar chart for the selected month
                if not summary_df.empty:
                    fig, ax = plt.subplots(figsize=(10, 5))
                    bars = ax.bar(summary_df['วันที่ปิดงานโดย Desktop Support'].astype(str), summary_df['จำนวนอุปกรณ์'], color='skyblue')
                    ax.set_title(f'จำนวนอุปกรณ์ที่เข้าสู่ขั้นตอนรอหน่วยงานกลางฯ - {selected_month}', fontsize=14)
                    ax.set_xlabel('วันที่ Desktop Support ปิดงาน')
                    ax.set_ylabel('จำนวนอุปกรณ์')
                    plt.xticks(rotation=45)
                    plt.grid(axis='y', linestyle='--', alpha=0.7)

                    # Display count on top of each bar
                    for bar in bars:
                        yval = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=10)

                    # Apply the font to the labels and ticks
                    for label in ax.get_xticklabels():
                        label.set_fontproperties(prop)
                    for label in ax.get_yticklabels():
                        label.set_fontproperties(prop)

                    st.pyplot(fig)

                    # Display the data table below the chart
                    st.subheader(f"ข้อมูลจำนวนอุปกรณ์ที่ปิดงานสำหรับเดือน {selected_month}")
                    st.dataframe(summary_df)
                else:
                    st.warning(f"⚠️ ไม่มีข้อมูลสำหรับเดือน {selected_month}")
            else:
                st.warning("⚠️ ไม่มีข้อมูลที่ตรงกับสถานะ 'รอหน่วยงานกลางดูแลทรัพย์สินดำเนินการ'")
        else:
            st.error("❌ ไม่พบคอลัมน์ 'วันที่ Desktop Support ปิดงาน' หรือ 'สถานะของเอกสาร' ในไฟล์ Excel")
    else:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์ในหน้า Home ก่อน")
