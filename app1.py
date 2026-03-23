#@title 👨‍⚕️ Testosterone Clinical Dashboard (v4) { display-mode: "form" }

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="Testosterone Analyzer", layout="wide")

st.title("👨‍⚕️ Testosterone Circadian Analysis Dashboard")
st.markdown("โปรแกรมวิเคราะห์ระดับฮอร์โมนตามช่วงเวลา (อ้างอิง JCEM 2017 & Brambilla 2009)")
st.divider()

# --- 2. ส่วนรับข้อมูล (ย้ายมาหน้าหลักเพื่อให้เห็นง่าย) ---
col_in, col_space, col_out = st.columns([1, 0.1, 2])

with col_in:
    st.subheader("📝 กรอกข้อมูลคนไข้")
    # ใส่ค่าเริ่มต้น (Default) เพื่อให้กราฟขึ้นทันทีที่เปิดเว็บ
    age = st.number_input("อายุคนไข้ (ปี)", min_value=18, max_value=95, value=51)
    test_val = st.number_input("ระดับ Testosterone (ng/mL)", min_value=0.0, max_value=15.0, value=4.34, step=0.01)
    
    # ตัวเลือกเวลา
    times_list = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    test_time = st.selectbox("เวลาที่เจาะเลือด", times_list, index=25) # Default 12:30

# --- 3. ส่วน Logic และการคำนวณ ---
# อ้างอิงเกณฑ์ Mean และ Amplitude ตามอายุ
if age < 40: m, a = 5.31, 0.75
elif age < 50: m, a = 5.05, 0.55
elif age < 60: m, a = 4.85, 0.45
elif age < 70: m, a = 4.45, 0.35
else: m, a = 4.00, 0.25

hours_axis = np.linspace(0, 24, 250)
curve_data = m + a * np.cos((hours_axis - 8) * (2 * np.pi / 24))

hh, mm = map(int, test_time.split(':'))
ph_decimal = hh + (mm / 60)

# --- 4. การแสดงผลกราฟ ---
with col_out:
    st.subheader("📈 ผลการวิเคราะห์")
    
    # สร้างรูปกราฟ
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # พื้นที่ปกติ (Healthy Range)
    ax.fill_between(hours_axis, curve_data-1.8, curve_data+2.5, color='#3498db', alpha=0.1, label='Healthy Range (95% CI)')
    
    # เส้นค่าเฉลี่ยตามวัย
    ax.plot(hours_axis, curve_data, color='#2c3e50', linewidth=2.5, label=f'Avg Curve (Age {age})')
    
    # เส้นขีดจำกัดล่างที่ 2.1 ng/mL
    ax.axhline(2.1, color='#e74c3c', linestyle='--', linewidth=2, label='Lower Limit (2.1 ng/mL)')

    # พล็อตจุดคนไข้ (ถ้าค่ามากกว่า 0)
    if test_val > 0:
        ax.scatter(ph_decimal, test_val, color='red', s=180, edgecolor='black', zorder=5, label='Patient Result')
        ax.annotate(f' {test_val}', (ph_decimal, test_val), xytext=(10, 10), textcoords='offset points', fontweight='bold', fontsize=12)

    # ตกแต่งกราฟ
    ax.set_ylim(0, 11)
    ax.set_xticks(np.arange(0, 25, 4))
    ax.set_xlabel("Time of Day (24h Scale)")
    ax.set_ylabel("Total Testosterone (ng/mL)")
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.2)
    
    # คำสั่งแสดงกราฟบนหน้าเว็บ
    st.pyplot(fig)

# --- 5. สรุปผลด้านล่าง ---
st.divider()
if test_val > 0:
    # คำนวณค่าคาดการณ์ตอนเช้า
    current_expected = m + a * np.cos((ph_decimal - 8) * (2 * np.pi / 24))
    morning_est = (test_val / current_expected) * (m + a)
    
    c1, c2 = st.columns(2)
    with c1:
        if test_val < 2.1:
            st.error(f"**สถานะ:** ต่ำกว่าเกณฑ์มาตรฐาน (2.1 ng/mL)")
        elif test_val < 3.0:
            st.warning(f"**สถานะ:** ค่อนข้างต่ำ (Borderline)")
        else:
            st.success(f"**สถานะ:** ปกติสมวัย")
    with c2:
        st.info(f"🕒 **ค่าคาดการณ์ที่ 08:00 น.:** ประมาณ **{morning_est:.2f} ng/mL**")
