# app.py

import streamlit as st
import base64
import asyncio
import tempfile

from gtts import gTTS
from googletrans import Translator

from controller.mcp_client import decide_and_run, call_mcp_tool

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="MediBot MCP",
    page_icon="🩺",
    layout="centered"
)

translator = Translator()

# ---------------------------------------------------
# BACKGROUND CSS
# ---------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-image: url("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

.main-box {
    background: rgba(0,0,0,0.72);
    padding: 30px;
    border-radius: 18px;
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

.stButton button {
    width: 100%;
    border-radius: 10px;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    background-color: #2563eb;
    color: white;
}

.result-box {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    margin-top: 20px;
    color: white;
    border: 1px solid rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# FUNCTIONS
# ---------------------------------------------------

def translate_text(text, language):
    if language == "Telugu":
        translated = translator.translate(text, dest="te")
        return translated.text
    return text


def generate_tts(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    tts.save(temp_file.name)

    return temp_file.name


# ---------------------------------------------------
# HEADER
# ---------------------------------------------------

st.markdown("""
<div class='main-box'>
<h1>🩺 MediBot MCP</h1>
<p>AI Medical Assistant using FastMCP + Groq</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LANGUAGE SELECTOR
# ---------------------------------------------------

language = st.radio(
    "🌍 Select Language",
    ["English", "Telugu"],
    horizontal=True
)

lang_code = "te" if language == "Telugu" else "en"

# ---------------------------------------------------
# TABS
# ---------------------------------------------------

tab1, tab2 = st.tabs([
    "💬 Symptom Checker",
    "💊 Medicine Photo"
])

# ===================================================
# TAB 1 — SYMPTOM CHECKER
# ===================================================

with tab1:

    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="Example: fever, headache, sore throat for 2 days"
    )

    if st.button("Analyze Symptoms"):

        if symptoms.strip():

            with st.spinner("Analyzing symptoms..."):

                result = decide_and_run(
                    f"I have these symptoms: {symptoms}"
                )

                translated_result = translate_text(
                    result,
                    language
                )

                st.markdown(
                    f"""
                    <div class='result-box'>
                    {translated_result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # SPEAK BUTTON
                if st.button("🔊 Speak Response", key="speak1"):

                    audio_file = generate_tts(
                        translated_result,
                        lang_code
                    )

                    audio_bytes = open(audio_file, "rb").read()

                    st.audio(
                        audio_bytes,
                        format="audio/mp3"
                    )

        else:
            st.error("Please enter your symptoms")


# ===================================================
# TAB 2 — MEDICINE PHOTO
# ===================================================

with tab2:

    photo = st.file_uploader(
        "Upload medicine photo",
        type=["jpg", "jpeg", "png"]
    )

    if photo:

        st.image(photo, width=250)

        if st.button("Analyze Medicine Photo"):

            with st.spinner("Analyzing medicine image..."):

                image_b64 = base64.b64encode(
                    photo.read()
                ).decode()

                result = asyncio.run(
                    call_mcp_tool(
                        "medicine_photo_analyzer",
                        {
                            "image_b64": image_b64
                        }
                    )
                )

                translated_result = translate_text(
                    result,
                    language
                )

                st.markdown(
                    f"""
                    <div class='result-box'>
                    {translated_result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # SPEAK BUTTON
                if st.button("🔊 Speak Response", key="speak2"):

                    audio_file = generate_tts(
                        translated_result,
                        lang_code
                    )

                    audio_bytes = open(audio_file, "rb").read()

                    st.audio(
                        audio_bytes,
                        format="audio/mp3"
                    )
