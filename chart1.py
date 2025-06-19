import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm, rcParams
import os
import requests
import re

# Function to download and register Sarabun font
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

    prop = fm.FontProperties(fname=font_path)
    plt.rcParams["font.family"] = prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False
    return prop.get_name()

# Function to clean and strip surrogate characters
def fix_surrogates(text):
    if isinstance(text, str):
        return re.sub(r'[\ud800-\udfff]', '', text)  # remove surrogate pair characters
    return text

def clean_unicode(df):
    return df.applymap(fix_surrogates)

sarabun_font = register_sarabun_font()

def show_chart1():
    st.title("รายงานจำนวนนอุปกรณ์ที่เข้าสู่ขั้นตอนรอหน่วยงานกลางดำเนินการ")

    if sarabun_font:
        font_path = os.path.join("fonts", "Sarabun.ttf")
        prop = fm.FontProperties(fname=font_path)
        rcParams["font.family"] = prop.get_name()

    if 'uploaded_data' in st.session_state:
        df = st.session_state['uploaded_data']
        df = clean_unicode(df)

        if 'วันที่นัดหมาย FM จัดเก็บทรัพย์สิน' in df.columns and 'สถานะของเอกสาร' in df.columns:
            df_filtered = df[df['สถานะของเอกสาร'] == 'รอหน่วยงานกลางดูแลทรัพย์สินดำเนินการ']
            if not df_filtered.empty:
                df_filtered['วันที่นัดหมาย FM จัดเก็บทรัพย์สิน'] = pd.to_datetime(df_filtered['วันที่นัดหมาย FM จัดเก็บทรัพย์สิน'], errors='coerce')
                df_filtered = df_filtered.dropna(subset=['วันที่นัดหมาย FM จัดเก็บทรัพย์สิน'])
                df_filtered['Year-Month'] = df_filtered['วันที่นัดหมาย FM จัดเก็บทรัพย์สิน'].dt.to_period('M')
                months = df_filtered['Year-Month'].unique()
                month_options = ['ALL'] + [str(month) for month in months]

                selected_month = st.selectbox("เลือกเดือนที่ต้องการดูข้อมูล", month_options, index=0)

                if selected_month != 'ALL':
                    df_filtered = df_filtered[df_filtered['Year-Month'] == pd.Period(selected_month)]

                # Original chart
                summary = df_filtered['วันที่นัดหมาย FM จัดเก็บทรัพย์สิน'].dt.date.value_counts().sort_index()
                summary_df = pd.DataFrame({
                    'วันที่นัดหมาย FM จัดเก็บทรัพย์สิน': summary.index,
                    'จำนวนอุปกรณ์': summary.values
                })

                if not summary_df.empty:
                    fig, ax = plt.subplots(figsize=(10, 5))
                    bars = ax.bar(summary_df['วันที่นัดหมาย FM จัดเก็บทรัพย์สิน'].astype(str), summary_df['จำนวนอุปกรณ์'], color='skyblue')
                    ax.set_title(f'Number of devices in the waiting process for central agency action - {selected_month}', fontsize=14)
                    ax.set_xlabel('Date when Desktop Support closed the task')
                    ax.set_ylabel('Number of Devices')
                    plt.xticks(rotation=45, ha='right')
                    plt.grid(axis='y', linestyle='--', alpha=0.7)

                    for bar in bars:
                        yval = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width() / 2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=10)

                    for label in ax.get_xticklabels():
                        label.set_fontproperties(prop)
                    for label in ax.get_yticklabels():
                        label.set_fontproperties(prop)

                    st.pyplot(fig)
                    st.subheader(f"ข้อมูลจำนวนอุปกรณ์ที่ปิดงานสำหรับเดือน {selected_month}")

                else:
                    st.warning(f"⚠️ ไม่มีข้อมูลสำหรับเดือน {selected_month}")

                # Additional table and chart
                device_col = 'ประเภทที่ต้องการให้ตรวจสอบ'
                if device_col in df_filtered.columns:
                    st.subheader("📋 ข้อมูลจำแนกตามประเภทอุปกรณ์")

                    grouped_df = df_filtered.groupby([
                        df_filtered['วันที่นัดหมาย FM จัดเก็บทรัพย์สิน'].dt.date,
                        device_col
                    ]).size().reset_index(name='จำนวนอุปกรณ์')

                    grouped_df.rename(columns={
                        'วันที่นัดหมาย FM จัดเก็บทรัพย์สิน': 'วันที่นัดหมาย',
                        device_col: 'ประเภทที่ต้องการให้ตรวจสอบ'
                    }, inplace=True)

                    st.dataframe(clean_unicode(grouped_df[['วันที่นัดหมาย', 'จำนวนอุปกรณ์', 'ประเภทที่ต้องการให้ตรวจสอบ']]))

                    pivot_df = grouped_df.pivot(index='วันที่นัดหมาย', columns='ประเภทที่ต้องการให้ตรวจสอบ', values='จำนวนอุปกรณ์').fillna(0)

                    st.subheader("📊 กราฟแท่งเปรียบเทียบประเภทอุปกรณ์ตามวันนัดหมาย")
                    fig2, ax2 = plt.subplots(figsize=(12, 6))
                    pie_data = pivot_df.sum()
                    wedges, texts, autotexts = ax2.pie(
                        pie_data,
                        labels=pie_data.index,
                        autopct="%1.1f%%",
                        startangle=140,
                        colors=plt.cm.tab20.colors[:len(pie_data)]
                    )

                    ax2.set_title('สัดส่วนอุปกรณ์แต่ละประเภท (Pie Chart)', fontproperties=prop)
                    plt.tight_layout()

                    if sarabun_font:
                        for label in ax2.get_xticklabels() + ax2.get_yticklabels():
                            label.set_fontproperties(prop)
                        ax2.title.set_fontproperties(prop)
                        ax2.xaxis.label.set_fontproperties(prop)
                        ax2.yaxis.label.set_fontproperties(prop)
                        for text in autotexts:
                            text.set_fontproperties(prop)
                        for text, count in zip(texts, pie_data):
                            text.set_text(f"{text.get_text()} ({int(count)} รายการ)")
                            text.set_fontproperties(prop)

                    st.pyplot(fig2)
                else:
                    st.warning("❌ ไม่พบคอลัมน์ 'ประเภทที่ต้องการให้ตรวจสอบ'")

            else:
                st.warning("⚠️ ไม่มีข้อมูลที่ตรงกับสถานะ 'รอหน่วยงานกลางดูแลทรัพย์สินดำเนินการ'")
        else:
            st.error("❌ ไม่พบคอลัมน์ที่จำเป็นในข้อมูลที่อัปโหลด")
    else:
        st.warning("⚠️ กรุณาอัปโหลดไฟล์ในหน้า Home ก่อน")
