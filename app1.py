import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 1. ตั้งค่าหน้าจอ (Layout Config) ---
st.set_page_config(page_title="Testosterone Analyzer", layout="wide")

st.title("👨‍⚕️ Testosterone Circadian Analysis Dashboard")
st.markdown("โปรแกรมวิเคราะห์ระดับฮอร์โมนตามช่วงเวลา (อ้างอิง Endocrine Society, JCEM 2017 & Brambilla 2009)")
st.divider()

# --- 2. ส่วนรับข้อมูลคนไข้ (Inputs) ---
col_in, col_space, col_out = st.columns([1, 0.1, 2])

with col_in:
    st.subheader("📝 กรอกข้อมูลคนไข้")
    age = st.number_input("อายุคนไข้ (ปี)", min_value=18, max_value=95, value=18)
    test_val = st.number_input("ระดับ Testosterone (ng/mL)", min_value=0.0, max_value=15.0, value=0.0, step=0.01)
    times_list = [f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 30)]
    test_time = st.selectbox("เวลาที่เจาะเลือด", times_list, index=0)

# --- 3. ส่วนคำนวณ Logic (JCEM 2017 & Brambilla 2009) ---

# 3.1 กำหนดค่า Mean (m) จาก JCEM 2017 และ % Drop (D) จาก Brambilla 2009 ตามช่วงอายุ
if age < 40:
    m = 5.31
    D = 0.225  # ช่วง 20-25% เลือกค่ากลางประชากรที่ 22.5%
elif age < 50:
    m = 5.05
    D = 0.185  # ค่าประมาณการช่วงรอยต่อระหว่างทศวรรษ
elif age < 60:
    m = 4.85
    D = 0.15   # ดรอปประมาณ 15%
elif age < 70:
    m = 4.45
    D = 0.12   # ดรอปประมาณ 12%
else:
    m = 4.00
    D = 0.10   # อายุ 70+ ดรอปประมาณ 10% (Blunted Rhythm)

# 3.2 คำนวณค่า Amplitude (a) อัตโนมัติจากสมการความสัมพันธ์ของ Brambilla
a = m * (D / (1.5 - D))

# 3.3 สร้างข้อมูลเส้นโค้ง Cosine Wave 24 ชั่วโมงสำหรับวาดกราฟ
hours_axis = np.linspace(0, 24, 250)
curve_data = m + a * np.cos((hours_axis - 8) * (2 * np.pi / 24))

# 3.4 แปลงเวลาคนไข้เป็นทศนิยม เพื่อหาค่าคาดการณ์ประชากร ณ เวลานั้น
hh, mm = map(int, test_time.split(':'))
ph_decimal = hh + (mm / 60)
current_expected = m + a * np.cos((ph_decimal - 8) * (2 * np.pi / 24))

# 3.5 คำนวณค่าคาดการณ์ตอนเช้า
morning_peak = m + a  # จุดสูงสุดที่เวลา 08:00 น.
morning_est = (test_val / current_expected) * morning_peak if test_val > 0 else 0

# --- 4. การแสดงผลกราฟวิเคราะห์ (Plotting) ---
with col_out:
    st.subheader("📈 ผลการวิเคราะห์")

    fig, ax = plt.subplots(figsize=(10, 6))

    # แถบพื้นที่ปกติของประชากรสุขภาพดี — ปรับ CI ตาม amplitude (Brambilla)
    # ยิ่งอายุมาก a น้อยลง → แถบแคบลงอัตโนมัติ สะท้อน Blunted Rhythm
    ci_lower = curve_data - (a * 1.2)
    ci_upper = curve_data + (a * 1.7)
    ax.fill_between(hours_axis, ci_lower, ci_upper, color='#3498db', alpha=0.1, label='Healthy Reference Range (95% CI)')

    # เส้นโค้งค่าเฉลี่ยตามช่วงอายุ
    ax.plot(hours_axis, curve_data, color='#2c3e50', linewidth=2.5, label=f'Avg Curve (Age {age})')

    # เส้นประสีแดง 2.1 ng/mL: เกณฑ์ต่ำสุดทางสถิติประชากร
    ax.axhline(2.1, color='#e74c3c', linestyle='--', linewidth=1.5, label='Statistical Lower Limit (2.1 ng/mL)')

    # เส้นประสีเหลือง 3.0 ng/mL: เกณฑ์วินิจฉัยทางคลินิกสากล (Endocrine Society)
    ax.axhline(3.0, color='#f1c40f', linestyle='--', linewidth=1.5, alpha=0.7, label='Clinical Threshold (3.0 ng/mL)')

    # พล็อตจุดผลตรวจของคนไข้
    if test_val > 0:
        ax.scatter(ph_decimal, test_val, color='red', s=180, edgecolor='black', zorder=5, label='Patient Result')
        ax.annotate(f' Result: {test_val}', (ph_decimal, test_val), xytext=(10, 10), textcoords='offset points', fontweight='bold', fontsize=12)

    # ตกแต่งรายละเอียดกราฟ
    ax.set_ylim(0, 11)
    ax.set_xticks(np.arange(0, 25, 4))
    ax.set_xlabel("Time of Day (24h Scale)")
    ax.set_ylabel("Total Testosterone (ng/mL)")
    ax.set_title(f"Circadian Model (Brambilla 2009 + JCEM 2017) | Age {age}y", fontsize=10, color='gray')
    ax.legend(loc='upper right', prop={'size': 9})
    ax.grid(True, alpha=0.2)

    st.pyplot(fig)

# --- 5. ส่วนสรุปผลการแปลผลทางคลินิก (Summary) ---
st.divider()
if test_val == 0:
    st.info("💡 กรุณาระบุระดับเทสโทสเตอโรนที่ช่องข้อมูลคนไข้ด้านซ้ายเพื่อเริ่มการวิเคราะห์")
else:
    c1, c2 = st.columns(2)
    with c1:
        if test_val < 2.1:
            st.error("**สถานะ:** ต่ำกว่าเกณฑ์มาตรฐานประชากร (< 2.1 ng/mL)")
        elif test_val < 3.0:
            st.warning("**สถานะ:** ค่อนข้างต่ำ (Borderline 2.1 - 3.0 ng/mL)")
        else:
            st.success("**สถานะ:** อยู่ในเกณฑ์ปกติสมวัย (> 3.0 ng/mL)")
    with c2:
        st.info(f"🕒 **ค่าคาดการณ์ที่จุดสูงสุด (08:00 น.):** ประมาณ **{morning_est:.2f} ng/mL**")

    # Disclaimer แสดงเฉพาะเมื่อมีการคำนวณ morning_est
    st.warning(
        "⚠️ **ข้อควรระวัง:** ค่าคาดการณ์ที่ 08:00 น. คำนวณจากค่าเฉลี่ยประชากร (Population Mean) "
        "ตามโมเดล Brambilla 2009 ซึ่งอาจคลาดเคลื่อนในคนไข้ที่มีภาวะ Obesity, Insulin Resistance, "
        "Sleep Apnea หรือทำงานเป็นกะ (Shift Work) เนื่องจากกลุ่มนี้มักมี Blunted Rhythm "
        "ทำให้ค่าคาดการณ์สูงเกินจริง (Overestimation) — ใช้ประกอบการสื่อสารกับคนไข้เท่านั้น "
        "ไม่ใช่เกณฑ์วินิจฉัยหลัก"
    )

# --- 6. ส่วนหมายเหตุและหลักฐานอ้างอิงทางการแพทย์ (Clinical Notes) ---
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📝 หมายเหตุและเกณฑ์อ้างอิงทางการแพทย์ (Clinical Reference Notes)"):
    st.write("""
    1. **เกณฑ์ทางคลินิก (3.0 ng/mL / 300 ng/dL):** อ้างอิงแนวทางเวชปฏิบัติของ **Endocrine Society (2018)** และ **AUA** ซึ่งเป็นจุดตัดสำคัญในการพิจารณาวินิจฉัยภาวะ Hypogonadism ร่วมกับอาการแสดงทางคลินิก

    2. **เกณฑ์ทางสถิติ (2.1 ng/mL / 210 ng/dL):** อ้างอิงค่าขอบล่าง (2.5th Percentile) ของผู้ชายสุขภาพดีตามมาตรฐาน **Harmonized Reference Ranges (JCEM 2017)**

    3. **ความแปรปรวนตามรอบวัน (Diurnal Variation):** โมเดลกราฟคำนวณและปรับลด Amplitude อัตโนมัติตามสถิติรายช่วงอายุจากงานวิจัยของ **Brambilla et al. 2009** (JCEM 94:907–913) โดยกลุ่มอายุ 30–40 ปีมี diurnal drop ประมาณ 20–25% และลดลงเหลือ ~10% ในกลุ่มอายุ 70+ ปี (Blunted Rhythm)

    4. **แถบ Healthy Reference Range:** ปรับความกว้างอัตโนมัติตาม Amplitude (a) ที่คำนวณจาก Brambilla — คนอายุน้อยจะเห็นแถบกว้างกว่า สะท้อนความแปรปรวนสูงตามธรรมชาติ

    5. **ข้อจำกัดในแนวทางเวชปฏิบัติ:** โปรแกรมนี้คำนวณย้อนกลับจากค่าเฉลี่ยทางสถิติประชากรเพื่อใช้ประกอบการสื่อสารกับคนไข้เท่านั้น ในทางปฏิบัติหากค่าอยู่ใน Grey Zone (2.1–3.0 ng/mL) แนะนำพิจารณาตรวจ SHBG และ Albumin เพิ่มเติมเพื่อประเมิน Free Testosterone หรือนัดเจาะเลือดซ้ำในช่วงเช้าตรู่ (07:00–11:00 น.) ตามดุลยพินิจของแพทย์
    """)
