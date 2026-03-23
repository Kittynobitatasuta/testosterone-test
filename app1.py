#@title 👨‍⚕️ Testosterone Clinical Dashboard (v4) { display-mode: "form" }

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. ตั้งค่าหน้าจอ (Layout) ---
st.set_page_config(page_title="Testosterone Analyzer", layout="wide")

st.title("👨‍⚕️ Testosterone Circadian Analysis Dashboard")
st.markdown("โปรแกรมวิเคราะห์ระดับฮอร์โมนตามช่วงเวลา (อ้างอิง JCEM 2017 & Brambilla 2009)")
st.divider()

# --- 2. ส่วนรับข้อมูล (Inputs) ---
col_in, col_space, col_out = st.columns([1, 0.1, 2])

with col_in:
    st.subheader("📝 กรอกข้อมูลคนไข้")
    # ปรับค่าเริ่มต้นตามที่คุณหมอกำหนด
    age = st.number_input("อายุคนไข้ (ปี)", min_value=18, max_value=95, value=18)
    test_val = st.number_input("ระดับ Testosterone (ng/mL)", min_value=0.0, max_value=15.0, value=0.0, step=0.01)
    
    # สร้างรายการเวลาห่างกัน 30 นาที และตั้งค่าเริ่มต้นที่ 00:00 (index 0)
    times_list = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    test_time = st.selectbox("เวลาที่เจาะเลือด", times_list, index=0) 

# --- 3. ส่วนคำนวณ Logic (Mean & Amplitude) ---
if age < 40: m, a = 5.31, 0.75
elif age < 50: m, a = 5.05, 0.55
elif age < 60: m, a = 4.85, 0.45
elif age < 70: m, a = 4.45, 0.35
else: m, a = 4.00, 0.25

hours_axis = np.linspace(0, 24, 250)
curve_data = m + a * np.cos((hours_axis - 8) * (2 * np.pi / 24))

hh, mm = map(int, test_time.split(':'))
ph_decimal = hh + (mm / 60)

# --- 4. การแสดงผลกราฟ (Plotting) ---
with col_out:
    st.subheader("📈 ผลการวิเคราะห์")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # พื้นที่ปกติ (Healthy Range)
    ax.fill_between(hours_axis, curve_data-1.8, curve_data+2.5, color='#3498db', alpha=0.1, label='Healthy Range (95% CI)')
    
    # เส้นค่าเฉลี่ยตามอายุที่เลือก
    ax.plot(hours_axis, curve_data, color='#2c3e50', linewidth=2.5, label=f'Avg Curve (Age {age})')
    
    # เส้นเกณฑ์ขั้นต่ำ 2.1 ng/mL
    ax.axhline(2.1, color='#e74c3c', linestyle='--', linewidth=2, label='Lower Limit (2.1 ng/mL)')

    # พล็อตจุดคนไข้เฉพาะเมื่อมีค่ามากกว่า 0
    if test_val > 0:
        ax.scatter(ph_decimal, test_val, color='red', s=180, edgecolor='black', zorder=5, label='Patient Result')
        ax.annotate(f' {test_val}', (ph_decimal, test_val), xytext=(10, 10), textcoords='offset points', fontweight='bold', fontsize=12)

    ax.set_ylim(0, 10.5)
    ax.set_xticks(np.arange(0, 25, 4))
    ax.set_xlabel("Time of Day (24h Scale)")
    ax.set_ylabel("Total Testosterone (ng/mL)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.2)
    
    st.pyplot(fig)

# --- 5. สรุปผลการวิเคราะห์ (Summary) ---
st.divider()
if test_val == 0:
    st.info("💡 กรุณาระบุระดับเทสโทสเตอโรนที่ช่องด้านซ้ายเพื่อเริ่มการวิเคราะห์")
else:
    # คำนวณค่าคาดการณ์ตอนเช้า (Morning Projection)
    current_expected = m + a * np.cos((ph_decimal - 8) * (2 * np.pi / 24))
    morning_est = (test_val / current_expected) * (m + a)
    
    c1, c2 =
