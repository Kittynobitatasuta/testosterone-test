#@title 👨‍⚕️ Testosterone Clinical Dashboard (v4) { display-mode: "form" }

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. Layout Setup ---
st.set_page_config(page_title="Testosterone Analyzer", layout="wide")
st.title("👨‍⚕️ Testosterone Circadian Analysis Dashboard")
st.markdown("วิเคราะห์ตามช่วงเวลาและอายุ (อ้างอิง Endocrine Society & JCEM 2017)")
st.divider()

# --- 2. Inputs ---
col_in, col_space, col_out = st.columns([1, 0.1, 2])
with col_in:
    st.subheader("📝 ข้อมูลคนไข้")
    age = st.number_input("อายุคนไข้ (ปี)", min_value=18, max_value=95, value=18)
    test_val = st.number_input("ระดับ Testosterone (ng/mL)", min_value=0.0, max_value=15.0, value=0.0, step=0.01)
    times_list = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    test_time = st.selectbox("เวลาที่เจาะเลือด", times_list, index=0) 

# --- 3. Logic ---
if age < 40: m, a = 5.31, 0.75
elif age < 50: m, a = 5.05, 0.55
elif age < 60: m, a = 4.85, 0.45
elif age < 70: m, a = 4.45, 0.35
else: m, a = 4.00, 0.25

hours_axis = np.linspace(0, 24, 250)
curve_data = m + a * np.cos((hours_axis - 8) * (2 * np.pi / 24))
hh, mm = map(int, test_time.split(':'))
ph_decimal = hh + (mm / 60)

# --- 4. Plotting ---
with col_out:
    st.subheader("📈 ผลการวิเคราะห์")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.fill_between(hours_axis, curve_data-1.8, curve_data+2.5, color='#3498db', alpha=0.1, label='Healthy Range (95% CI)')
    ax.plot(hours_axis, curve_data, color='#2c3e50', linewidth=2.5, label=f'Avg Curve (Age {age})')
    
    # เส้นแดง 2.1 (Statistical Limit)
    ax.axhline(2.1, color='#e74c3c', linestyle='--', linewidth=1.5, label='Statistical Lower Limit (2.1 ng/mL)')
    
    # --- เพิ่มเส้นประสีเหลือง 3.0 (Endocrine Society Threshold) ---
    ax.axhline(3.0, color='#f1c40f', linestyle='--', linewidth=1.5, alpha=0.7, label='Clinical Threshold (3.0 ng/mL)')

    if test_val > 0:
        ax.scatter(ph_decimal, test_val, color='red', s=180, edgecolor='black', zorder=5)
        ax.annotate(f' {test_val}', (ph_decimal, test_val), xytext=(10, 10), textcoords='offset points', fontweight='bold', fontsize=12)

    ax.set_ylim(0, 11)
    ax.set_xticks(np.arange(0, 25, 4))
    ax.set_xlabel("Time of Day (24h Scale)")
    ax.set_ylabel("Total Testosterone (ng/mL)")
    ax.legend(loc='upper right', prop={'size': 9})
    ax.grid(True, alpha=0.2)
    st.pyplot(fig)

# --- 5. Summary ---
st.divider()
if test_val == 0:
    st.info("💡 กรุณาระบุระดับเทสโทสเตอโรนเพื่อเริ่มการวิเคราะห์")
else:
    current_expected = m + a * np.cos((ph_decimal - 8) * (2 * np.pi / 24))
    morning_est = (test_val / current_expected) * (m + a)
    c1, c2 = st.columns(2)
    with c1:
        if test_val < 2.1: st.error(f"**สถานะ:** ต่ำกว่าเกณฑ์มาตรฐาน (2.1 ng/mL)")
        elif test_val < 3.0: st.warning(f"**สถานะ:** ค่อนข้างต่ำ (Borderline)")
        else: st.success(f"**สถานะ:** ปกติสมวัย")
    with c2:
        st.info(f"🕒 **ค่าคาดการณ์ที่ 08:00 น.:** ประมาณ **{morning_est:.2f} ng/mL**")

with st.expander("📝 หมายเหตุเพิ่มเติมสำหรับการแปลผล (Clinical Notes)"):
    st.write("""
    1. **เกณฑ์ 3.0 ng/mL:** อ้างอิงจาก **Endocrine Society (2018)** และ **AUA** ว่าเป็นจุดตัดที่ควรเริ่มพิจารณาภาวะ Hypogonadism หากมีอาการทางคลินิกร่วมด้วย
    2. **เกณฑ์ 2.1 ng/mL:** คือค่าขอบล่าง (2.5th Percentile) ของประชากรชายสุขภาพดีตามสถิติของ **JCEM 2017**
    3. **Total vs Free T:** ในรายที่ค่าก้ำกึ่ง (2.1-3.0) แนะนำให้ตรวจ SHBG และ Albumin เพิ่มเติมเพื่อหาค่า Free Testosterone
    """)
