# =========================================================
# app.py — MediBot MCP
# AI Medical Assistant using FastMCP + Groq
# =========================================================

import streamlit as st
import asyncio
import base64
import tempfile

from gtts import gTTS
from deep_translator import GoogleTranslator

from controller.mcp_client import (
    decide_and_run,
    call_mcp_tool
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MediBot MCP",
    page_icon="🩺",
    layout="centered"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background-image: url("https://images.unsplash.com/photo-1576091160399-112ba8d25d1d");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Main container */

.main-card {
    background: rgba(0,0,0,0.72);
    padding: 28px;
    border-radius: 20px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Result box */

.result-box {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    margin-top: 20px;
    color: white;
    border-left: 5px solid #2563eb;
}

/* Headings */

h1, h2, h3, p, label {
    color: white !important;
}

/* Buttons */

.stButton button {
    width: 100%;
    height: 48px;
    border-radius: 10px;
    border: none;
    background-color: #2563eb;
    color: white;
    font-size: 17px;
    font-weight: bold;
}

/* Text area */

textarea {
    border-radius: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNCTIONS
# =========================================================

def translate_text(text, language):
    """
    Translate text to Telugu if selected.
    """

    try:

        if language == "Telugu":

            translated = GoogleTranslator(
                source="auto",
                target="te"
            ).translate(text)

            return translated

        return text

    except Exception:
        return text


def generate_audio(text, lang_code):
    """
    Convert text to speech using gTTS.
    """

    tts = gTTS(
        text=text,
        lang=lang_code
    )

    temp_audio = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    tts.save(temp_audio.name)

    return temp_audio.name


def speak_response(text, lang_code):
    """
    Play AI response as audio.
    """

    audio_file = generate_audio(
        text,
        lang_code
    )

    audio_bytes = open(audio_file, "rb").read()

    st.audio(
        audio_bytes,
        format="audio/mp3"
    )

# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="main-card">

# 🩺 MediBot MCP

### AI Medical Assistant using FastMCP + Groq

✔ Symptom Analysis  
✔ Medicine Photo Recognition  
✔ Telugu Translation  
✔ AI Voice Assistant  

</div>
""")

# =========================================================
# LANGUAGE SELECTOR
# =========================================================

language = st.radio(
    "🌍 Select Language",
    ["English", "Telugu"],
    horizontal=True
)

lang_code = "te" if language == "Telugu" else "en"

# =========================================================
# TABS
# =========================================================

tab1, tab2 = st.tabs([
    "💬 Symptom Checker",
    "💊 Medicine Photo"
])

# =========================================================
# TAB 1 — SYMPTOM CHECKER
# =========================================================

with tab1:

    st.info(
        "⚠ This AI assistant provides informational guidance only. "
        "Consult a doctor for professional medical advice."
    )

    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="Example: fever, headache, sore throat for 2 days",
        height=120
    )

    if st.button("Analyze Symptoms"):

        if symptoms.strip():

            with st.spinner("Analyzing symptoms..."):

                try:

                    # MCP Planner
                    result = decide_and_run(
                        f"I have these symptoms: {symptoms}"
                    )

                    # Translation
                    translated_result = translate_text(
                        result,
                        language
                    )

                    # Display Result
                    st.markdown(
                        f"""
                        <div class="result-box">
                        {translated_result}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Voice Button
                    if st.button(
                        "🔊 Speak Response",
                        key="speak_symptom"
                    ):

                        speak_response(
                            translated_result,
                            lang_code
                        )

                except Exception as e:

                    st.error(
                        f"Error analyzing symptoms: {str(e)}"
                    )

        else:

            st.warning(
                "Please enter your symptoms."
            )

# =========================================================
# TAB 2 — MEDICINE PHOTO
# =========================================================

with tab2:

    st.info(
        "Upload a medicine image to identify medicine details."
    )

    photo = st.file_uploader(
        "Upload medicine photo",
        type=["jpg", "jpeg", "png"]
    )

    if photo:

        st.image(
            photo,
            width=250
        )

        if st.button("Analyze Medicine Photo"):

            with st.spinner(
                "Analyzing medicine image..."
            ):

                try:

                    # Convert image to base64
                    image_b64 = base64.b64encode(
                        photo.read()
                    ).decode()

                    # Call MCP Tool
                    result = asyncio.run(
                        call_mcp_tool(
                            "medicine_photo_analyzer",
                            {
                                "image_b64": image_b64
                            }
                        )
                    )

                    # Translate
                    translated_result = translate_text(
                        result,
                        language
                    )

                    # Display Result
                    st.markdown(
                        f"""
                        <div class="result-box">
                        {translated_result}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # Speak
                    if st.button(
                        "🔊 Speak Response",
                        key="speak_photo"
                    ):

                        speak_response(
                            translated_result,
                            lang_code
                        )

                except Exception as e:

                    st.error(
                        f"Error analyzing image: {str(e)}"
                    )

# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<br>

<center style='color:white'>

MediBot MCP • FastMCP + Groq + Streamlit

</center>
""", unsafe_allow_html=True)
