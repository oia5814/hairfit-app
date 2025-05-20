# hairfit_app_interface.py
"""
Streamlit 앱: 얼굴형, 이마/광대/턱선 중심 디테일, 목 길이/두께, 어깨 형태, 헤어스타일을 선택하면
이미지에 끼치는 영향과 보완 방법을 한눈에 보기 좋게 시각화해주는 전문가용 앱.
비밀번호 보호 없이 누구나 즉시 접속 가능한 버전.
"""

import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import datetime
import openai

# -------------------- 옵션 목록 --------------------
face_shapes = ["둥근형", "달걀형", "각진형", "하트형", "긴형"]
forehead_types = ["이마 넓음", "이마 좁음", "중간"]
cheekbone_types = ["광대 넓음", "광대 낮음", "평균"]
jaw_types = ["턱선 뚜렷", "턱선 둥글", "무턱"]
neck_lengths = ["짧은 목", "보통 목", "긴 목"]
neck_thicknesses = ["가는 목", "보통 두께", "굵은 목"]
shoulder_shapes = ["좁은 어깨", "보통 어깨", "넓은 어깨"]
hair_styles = ["숏컷 (Short Cut)", "단발 (Bob)", "허쉬컷 (Hush Cut)", "미디움 레이어드 (Medium Layered)"]

def evaluate_stability(forehead, cheekbone, jaw):
    score = 3
    if forehead == "이마 넓음": score -= 1
    if cheekbone == "광대 넓음": score -= 1
    if jaw in ["턱선 둥글", "무턱"]: score -= 1

    if score == 3:
        return "🟢 A (매우 안정)", "#d1ffd6"
    elif score == 2:
        return "🟡 B (안정)", "#fff9c4"
    elif score == 1:
        return "🟠 C (보통)", "#ffe0b2"
    elif score == 0:
        return "🔴 D (주의 요망)", "#ffcccb"
    else:
        return "⚠️ F (위험 조합)", "#ffb3b3"

def generate_prompt(face, style):
    face_en = {
        "둥근형": "round face shape",
        "달걀형": "oval face shape",
        "각진형": "square face shape",
        "하트형": "heart-shaped face",
        "긴형": "long face shape"
    }.get(face, "neutral face shape")

    style_en = {
        "숏컷 (Short Cut)": "short haircut",
        "단발 (Bob)": "bob haircut",
        "허쉬컷 (Hush Cut)": "hush cut hairstyle",
        "미디움 레이어드 (Medium Layered)": "medium layered hairstyle"
    }.get(style, "hairstyle")

    return f"A digital illustration of a Korean woman with a {face_en} and a {style_en}. She is facing front with soft lighting and a neutral background. The hairstyle frames her face gently, creating a calm and balanced impression. Modern, natural, beauty consultation style."

st.set_page_config(page_title="헤어핏 구조 분석기", layout="wide")
st.title("💇‍♀️ 헤어핏 구조 분석 + 이미지 예측")

st.sidebar.header("👤 고객 정보")
customer_name = st.sidebar.text_input("고객 이름", value="홍길동")
customer_phone = st.sidebar.text_input("연락처", value="")

st.sidebar.header("📌 골격 선택")
face = st.sidebar.selectbox("얼굴형", face_shapes)
forehead = st.sidebar.selectbox("이마 형태", forehead_types)
cheekbone = st.sidebar.selectbox("광대 형태", cheekbone_types)
jaw = st.sidebar.selectbox("턱선 형태", jaw_types)
neck_len = st.sidebar.selectbox("목 길이", neck_lengths)
neck_thick = st.sidebar.selectbox("목 두께", neck_thicknesses)
shoulder = st.sidebar.selectbox("어깨 형태", shoulder_shapes)
style = st.sidebar.selectbox("헤어스타일", hair_styles)
designer_name = st.sidebar.text_input("✍️ 디자이너 이름", value="디자이너 이아")

# 결과 분석
st.markdown("---")
st.subheader("📊 안정성 분석 결과")
stability_grade, grade_color = evaluate_stability(forehead, cheekbone, jaw)

st.markdown(f"""
<div style='background-color:{grade_color}; padding: 1rem; border-radius: 0.5rem;'>
<b>구조 안정성 등급:</b> {stability_grade}
</div>
""", unsafe_allow_html=True)

# 프롬프트 출력
st.markdown("---")
st.subheader("🎨 이미지 생성 프롬프트")
prompt_text = generate_prompt(face, style)
st.code(prompt_text, language="text")
st.download_button("📋 프롬프트 텍스트 다운로드", prompt_text, file_name="hair_prompt.txt")

# CSV 저장
data = {
    "날짜": datetime.date.today().strftime("%Y-%m-%d"),
    "고객 이름": customer_name,
    "연락처": customer_phone,
    "디자이너": designer_name,
    "얼굴형": face,
    "이마": forehead,
    "광대": cheekbone,
    "턱선": jaw,
    "목 길이": neck_len,
    "목 두께": neck_thick,
    "어깨 형태": shoulder,
    "헤어스타일": style,
    "안정성 등급": stability_grade
}

if st.button("💾 결과 CSV 저장하기"):
    df = pd.DataFrame([data])
    df.to_csv("hairfit_results.csv", mode="a", header=not os.path.exists("hairfit_results.csv"), index=False)
    st.success("CSV 파일 저장 완료!")

# PDF 저장
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "헤어핏 진단 리포트", ln=True, align="C")
        self.ln(5)

    def add_result(self, data_dict, prompt):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"고객 이름: {data_dict['고객 이름']} / 연락처: {data_dict['연락처']}", ln=True)
        self.cell(0, 10, f"디자이너: {data_dict['디자이너']} / 날짜: {data_dict['날짜']}", ln=True)
        self.ln(5)
        self.set_font("Arial", size=11)
        for key, value in data_dict.items():
            self.cell(0, 10, f"{key}: {value}", ln=True)
        self.ln(5)
        self.multi_cell(0, 10, f"[AI 프롬프트]
{prompt}")

if st.button("📄 PDF 리포트 저장하기"):
    pdf = PDF()
    pdf.add_page()
    pdf.add_result(data, prompt_text)
    pdf.output("hairfit_result.pdf")
    st.success("PDF 저장 완료!")

# AI 이미지 생성
st.markdown("---")
st.subheader("🧠 AI 이미지 생성")
api_key = st.text_input("🔐 OpenAI API Key", type="password")

if st.button("🪄 이미지 생성 실행"):
    if not api_key:
        st.warning("API Key를 입력해주세요.")
    else:
        openai.api_key = api_key
        try:
            response = openai.Image.create(prompt=prompt_text, n=1, size="512x512")
            image_url = response['data'][0]['url']
            st.image(image_url, caption="생성된 AI 이미지")
        except Exception as e:
            st.error(f"이미지 생성 실패: {e}")
