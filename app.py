# =========================================================
# app.py
# MediBot MCP
# =========================================================

import streamlit as st
import base64
import asyncio
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
    page_icon="🩺"
)

# =========================================================
# BACKGROUND IMAGE
# =========================================================

with open("background.png", "rb") as file:
    bg_image = base64.b64encode(
        file.read()
    ).decode()

st.markdown(
    f"""
    <style>

    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}

    .result-box {{
        background: rgba(0,0,0,0.70);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-top: 20px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FUNCTIONS
# =========================================================

def translate_text(text, language):

    if language == "Telugu":

        translated = GoogleTranslator(
            source="auto",
            target="te"
        ).translate(text)

        return translated

    return text


def speak_text(text, lang_code):

    tts = gTTS(
        text=text,
        lang=lang_code
    )

    temp_audio = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    tts.save(temp_audio.name)

    audio_bytes = open(
        temp_audio.name,
        "rb"
    ).read()

    st.audio(
        audio_bytes,
        format="audio/mp3"
    )

# =========================================================
# HEADER
# =========================================================

st.title("🩺 MediBot MCP")
st.caption("AI Medical Assistant using FastMCP + Groq")

# =========================================================
# TABS
# =========================================================

tab1, tab2 = st.tabs([
    "Symptom Checker",
    "Medicine Photo"
])

# =========================================================
# TAB 1 — SYMPTOM CHECKER
# =========================================================

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

                st.markdown(
                    f"""
                    <div class="result-box">
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # =========================================
                # SPEAKER BUTTON
                # =========================================

                if st.button(
                    "🔊",
                    key="speak_symptoms"
                ):

                    language = st.radio(
                        "Select Voice Language",
                        ["English", "Telugu"],
                        horizontal=True,
                        key="lang1"
                    )

                    translated_text = translate_text(
                        result,
                        language
                    )

                    lang_code = (
                        "te"
                        if language == "Telugu"
                        else "en"
                    )

                    speak_text(
                        translated_text,
                        lang_code
                    )

        else:

            st.error(
                "Please enter your symptoms"
            )

# =========================================================
# TAB 2 — MEDICINE PHOTO
# =========================================================

with tab2:

    photo = st.file_uploader(
        "Upload medicine photo",
        type=["jpg", "jpeg", "png"]
    )

    if photo:

        st.image(
            photo,
            width=250
        )

        if st.button(
            "Analyze Medicine Photo"
        ):

            with st.spinner(
                "Analyzing medicine image..."
            ):

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

                st.markdown(
                    f"""
                    <div class="result-box">
                    {result}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # =========================================
                # SPEAKER BUTTON
                # =========================================

                if st.button(
                    "🔊",
                    key="speak_photo"
                ):

                    language = st.radio(
                        "Select Voice Language",
                        ["English", "Telugu"],
                        horizontal=True,
                        key="lang2"
                    )

                    translated_text = translate_text(
                        result,
                        language
                    )

                    lang_code = (
                        "te"
                        if language == "Telugu"
                        else "en"
                    )

                    speak_text(
                        translated_text,
                        lang_code
                    )
