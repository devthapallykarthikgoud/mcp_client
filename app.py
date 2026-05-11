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
# SESSION STATE
# =========================================================

if "symptom_result" not in st.session_state:
    st.session_state.symptom_result = ""

if "photo_result" not in st.session_state:
    st.session_state.photo_result = ""

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
        background: rgba(0,0,0,0.72);
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


def speak_text(text, lang_code):

    try:

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

    except Exception as e:

        st.error(
            f"Speech Error: {str(e)}"
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

    # =========================================
    # ANALYZE BUTTON
    # =========================================

    if st.button(
        "Analyze Symptoms"
    ):

        if symptoms.strip():

            with st.spinner(
                "Analyzing symptoms..."
            ):

                try:

                    result = decide_and_run(
                        f"I have these symptoms: {symptoms}"
                    )

                    st.session_state.symptom_result = result

                except Exception as e:

                    st.error(
                        f"Error: {str(e)}"
                    )

        else:

            st.error(
                "Please enter your symptoms"
            )

    # =========================================
    # SHOW RESULT
    # =========================================

    if st.session_state.symptom_result:

        st.markdown(
            f"""
            <div class="result-box">
            {st.session_state.symptom_result}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =====================================
        # LANGUAGE SELECTOR
        # =====================================

        language1 = st.radio(
            "Voice Language",
            ["English", "Telugu"],
            horizontal=True,
            key="lang1"
        )

        # =====================================
        # SPEAKER BUTTON
        # =====================================

        if st.button(
            "🔊 Speak",
            key="speak_symptom"
        ):

            translated_text = translate_text(
                st.session_state.symptom_result,
                language1
            )

            lang_code = (
                "te"
                if language1 == "Telugu"
                else "en"
            )

            speak_text(
                translated_text,
                lang_code
            )

# =========================================================
# TAB 2 — MEDICINE PHOTO
# =========================================================

with tab2:

    photo = st.file_uploader(
        "Upload medicine photo",
        type=["jpg", "jpeg", "png"]
    )

    # =========================================
    # IMAGE PREVIEW
    # =========================================

    if photo:

        st.image(
            photo,
            width=250
        )

    # =========================================
    # ANALYZE PHOTO
    # =========================================

    if photo and st.button(
        "Analyze Medicine Photo"
    ):

        with st.spinner(
            "Analyzing medicine image..."
        ):

            try:

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

                st.session_state.photo_result = result

            except Exception as e:

                st.error(
                    f"Error: {str(e)}"
                )

    # =========================================
    # SHOW PHOTO RESULT
    # =========================================

    if st.session_state.photo_result:

        st.markdown(
            f"""
            <div class="result-box">
            {st.session_state.photo_result}
            </div>
            """,
            unsafe_allow_html=True
        )

        # =====================================
        # LANGUAGE SELECTOR
        # =====================================

        language2 = st.radio(
            "Voice Language",
            ["English", "Telugu"],
            horizontal=True,
            key="lang2"
        )

        # =====================================
        # SPEAK BUTTON
        # =====================================

        if st.button(
            "🔊 Speak",
            key="speak_photo"
        ):

            translated_text = translate_text(
                st.session_state.photo_result,
                language2
            )

            lang_code = (
                "te"
                if language2 == "Telugu"
                else "en"
            )

            speak_text(
                translated_text,
                lang_code
            )
