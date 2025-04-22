import streamlit as st
from home import home
from chart1 import show_chart1
from chart2 import show_chart2
from chart3 import show_chart3

# Sidebar for navigation
st.sidebar.title("📊 Navigation")
page = st.sidebar.radio("Go to", ("Home", "Chart 1", "Chart 2","Chart 3"))

# Page router
if page == "Home":
    home()
elif page == "Chart 1":
    show_chart1()
elif page == "Chart 2":
    show_chart2()
elif page == "Chart 3":
    show_chart3()
