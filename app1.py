#@title 👨‍⚕️ Testosterone Clinical Dashboard (v4) { display-mode: "form" }

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. ส่วนกำหนดค่าหน้าจอ (Streamlit Config) ---
st.set_page_config(page_title="Testosterone Clinical Analyzer", layout="centered")

st.title("👨‍⚕️ Testosterone Circadian Analysis")
st.markdown("โปรแกรมวิเคราะห์ระดับฮอร์โมนตามช่วงเวลาและอายุ (อ้างอิง JCEM 2017 & Brambilla 2009)")

# --- 2. ส่วนรับข้อมูลจาก User (Widgets) ---
# บรรทัดเหล่านี้คือการสร้างตัวแปร 'age', 'test_val', 'test_time'
with st.sidebar:
    st.header("📋 ข้อมูลคนไข้")
    age = st.slider("อายุคนไข้ (ปี)", 18, 90, 51)
    test_val = st.number_input("ค่า Testosterone (ng/mL)", 0.0, 15.0, 4.34, step=0.01)
    
    # สร้างตัวเลือกเวลาห่างกัน 30 นาที
    times_list = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    test_time = st.selectbox("เวลาที่เจาะเลือด", times_list, index=25) # Default 12:30

# --- 3. ฟังก์ชันหลักสำหรับคำนวณและวาดกราฟ ---
def plot_final_dashboard(p_age, p_val, p_time_str):
    # กำหนดค่าเฉลี่ยและการสวิงตามทศวรรษ
    if p_age < 40: m, a = 5.31, 0.75
    elif p_age < 50: m, a = 5.05, 0.55
    elif p_age < 60: m, a = 4.85, 0.45
    elif p_age < 70: m, a = 4.45, 0
