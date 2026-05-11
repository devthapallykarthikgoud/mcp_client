# =========================================================
# app.py
# MediBot MCP — Enhanced with Professional TTS
# =========================================================

import streamlit as st
import base64
import asyncio
import tempfile
import re

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
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================

for key in ["symptom_result", "photo_result", "speak_target", "show_lang_modal"]:
    if key not in st.session_state:
        st.session_state[key] = "" if "result" in key else False

# =========================================================
# BACKGROUND + GLOBAL STYLES
# =========================================================

with open("background.png", "rb") as file:
    bg_image = base64.b64encode(file.read()).decode()

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Sora:wght@600;700&display=swap');

    * {{ box-sizing: border-box; }}

    .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        font-family: 'DM Sans', sans-serif;
    }}

    h1, h2, h3 {{
        font-family: 'Sora', sans-serif !important;
    }}

    /* ── Card / Result Box ── */
    .result-box {{
        background: rgba(8, 12, 24, 0.82);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        padding: 24px 28px;
        border-radius: 18px;
        color: #e8f0fe;
        margin-top: 20px;
        border: 1px solid rgba(99, 179, 237, 0.18);
        line-height: 1.75;
        font-size: 15px;
        position: relative;
    }}

    /* ── Speaker FAB (Floating Action Button) ── */
    .speak-fab {{
        position: fixed;
        bottom: 36px;
        right: 36px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
    }}

    .fab-btn {{
        width: 62px;
        height: 62px;
        border-radius: 50%;
        background: linear-gradient(135deg, #1a73e8, #0d47a1);
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 26px;
        box-shadow: 0 6px 24px rgba(26,115,232,0.5);
        transition: transform 0.2s, box-shadow 0.2s;
        animation: pulse-glow 2.8s ease-in-out infinite;
    }}

    .fab-btn:hover {{
        transform: scale(1.1);
        box-shadow: 0 10px 32px rgba(26,115,232,0.7);
    }}

    @keyframes pulse-glow {{
        0%, 100% {{ box-shadow: 0 6px 24px rgba(26,115,232,0.45); }}
        50%        {{ box-shadow: 0 6px 36px rgba(26,115,232,0.85); }}
    }}

    /* ── Language Modal ── */
    .lang-modal-overlay {{
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.65);
        backdrop-filter: blur(6px);
        z-index: 10000;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .lang-modal {{
        background: linear-gradient(160deg, #0d1b2a, #112240);
        border: 1px solid rgba(99,179,237,0.25);
        border-radius: 22px;
        padding: 36px 40px 32px;
        width: 340px;
        text-align: center;
        box-shadow: 0 24px 80px rgba(0,0,0,0.6);
        animation: modal-in 0.25s ease;
    }}

    @keyframes modal-in {{
        from {{ opacity:0; transform: scale(0.88) translateY(20px); }}
        to   {{ opacity:1; transform: scale(1)    translateY(0);    }}
    }}

    .lang-modal h3 {{
        color: #e8f0fe;
        margin: 0 0 8px;
        font-size: 20px;
    }}

    .lang-modal p {{
        color: #90caf9;
        font-size: 13px;
        margin: 0 0 24px;
    }}

    .lang-choices {{
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-bottom: 18px;
    }}

    .lang-pill {{
        flex: 1;
        padding: 14px 10px;
        border-radius: 14px;
        border: 1px solid rgba(99,179,237,0.3);
        background: rgba(255,255,255,0.05);
        color: #e8f0fe;
        font-size: 15px;
        cursor: pointer;
        transition: background 0.18s, transform 0.15s, border-color 0.18s;
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
    }}

    .lang-pill:hover {{
        background: rgba(26,115,232,0.35);
        border-color: #1a73e8;
        transform: translateY(-2px);
    }}

    .lang-cancel {{
        background: transparent;
        border: none;
        color: #64b5f6;
        font-size: 13px;
        cursor: pointer;
        text-decoration: underline;
        font-family: 'DM Sans', sans-serif;
    }}

    /* ── Audio Player Styling ── */
    .audio-wrapper {{
        background: rgba(8,12,24,0.85);
        border-radius: 14px;
        padding: 16px 20px;
        margin-top: 12px;
        border: 1px solid rgba(99,179,237,0.15);
    }}

    .audio-label {{
        color: #90caf9;
        font-size: 12px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}

    /* ── Tab Styling ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: rgba(8,12,24,0.6);
        border-radius: 14px;
        padding: 6px;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        color: #90caf9;
        font-weight: 500;
    }}

    .stTabs [aria-selected="true"] {{
        background: rgba(26,115,232,0.35) !important;
        color: #e8f0fe !important;
    }}

    /* ── Input / TextArea ── */
    .stTextArea textarea {{
        background: rgba(8,12,24,0.75) !important;
        border: 1px solid rgba(99,179,237,0.25) !important;
        border-radius: 12px !important;
        color: #e8f0fe !important;
        font-family: 'DM Sans', sans-serif !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: linear-gradient(135deg, #1a73e8, #0d47a1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
        transition: opacity 0.18s, transform 0.15s !important;
    }}

    .stButton > button:hover {{
        opacity: 0.88;
        transform: translateY(-1px);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HELPER FUNCTIONS
# =========================================================

def clean_text_for_tts(text: str) -> str:
    """
    Strip HTML tags, markdown, extra symbols and
    normalise whitespace so gTTS gets clean prose.
    """
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove markdown bold/italic/headers
    text = re.sub(r"[*_#`~]", "", text)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove non-alphanumeric except basic punctuation
    text = re.sub(r"[^\w\s,.!?;:()\-]", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def translate_to_telugu(text: str) -> str:
    try:
        return GoogleTranslator(source="auto", target="te").translate(text)
    except Exception:
        return text


def generate_and_play_audio(raw_text: str, language: str):
    """
    Clean → (optionally translate) → synthesise → render audio player.
    language: 'English' | 'Telugu'
    """
    clean = clean_text_for_tts(raw_text)

    if not clean:
        st.warning("Nothing to speak — the result appears to be empty.")
        return

    if language == "Telugu":
        with st.spinner("Translating to Telugu…"):
            clean = translate_to_telugu(clean)
        lang_code = "te"
        flag = "🇮🇳"
        label = "Telugu Audio"
    else:
        lang_code = "en"
        flag = "🇬🇧"
        label = "English Audio"

    with st.spinner(f"Generating {flag} audio…"):
        try:
            tts = gTTS(text=clean, lang=lang_code, slow=False)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tmp.name)
            audio_bytes = open(tmp.name, "rb").read()

            st.markdown(
                f'<div class="audio-wrapper">'
                f'<div class="audio-label">{flag} {label}</div>',
                unsafe_allow_html=True
            )
            st.audio(audio_bytes, format="audio/mp3")
            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Speech generation failed: {e}")


# =========================================================
# HEADER
# =========================================================

st.title("🩺 MediBot MCP")
st.caption("AI Medical Assistant · FastMCP + Groq · Voice in English & Telugu")

st.divider()

# =========================================================
# TABS
# =========================================================

tab1, tab2 = st.tabs(["🔬 Symptom Checker", "💊 Medicine Photo"])

# =========================================================
# TAB 1 — SYMPTOM CHECKER
# =========================================================

with tab1:

    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="Example: fever, headache, sore throat for 2 days…",
        height=120
    )

    col_btn, col_speak = st.columns([3, 1])

    with col_btn:
        analyze_clicked = st.button("🔍 Analyze Symptoms", use_container_width=True)

    with col_speak:
        speak1_clicked = st.button("🔊 Speak", use_container_width=True, key="speak_tab1",
                                   disabled=not bool(st.session_state.symptom_result))

    # ── Analyze ──
    if analyze_clicked:
        if symptoms.strip():
            with st.spinner("Analyzing symptoms…"):
                try:
                    result = decide_and_run(f"I have these symptoms: {symptoms}")
                    st.session_state.symptom_result = result
                except Exception as e:
                    st.error(f"Analysis error: {e}")
        else:
            st.warning("Please describe your symptoms before analyzing.")

    # ── Result display ──
    if st.session_state.symptom_result:
        st.markdown(
            f'<div class="result-box">{st.session_state.symptom_result}</div>',
            unsafe_allow_html=True
        )

    # ── Language selector + audio (appears after Speak is clicked) ──
    if speak1_clicked and st.session_state.symptom_result:
        st.session_state.speak_target = "symptom"

    if st.session_state.get("speak_target") == "symptom" and st.session_state.symptom_result:
        st.markdown("---")
        st.markdown("**🌐 Select Voice Language**")
        lang_col1, lang_col2, lang_col3 = st.columns([1, 1, 2])

        with lang_col1:
            if st.button("🇬🇧 English", use_container_width=True, key="eng_sym"):
                generate_and_play_audio(st.session_state.symptom_result, "English")
                st.session_state.speak_target = ""

        with lang_col2:
            if st.button("🇮🇳 Telugu", use_container_width=True, key="tel_sym"):
                generate_and_play_audio(st.session_state.symptom_result, "Telugu")
                st.session_state.speak_target = ""

        with lang_col3:
            if st.button("✖ Cancel", key="cancel_sym"):
                st.session_state.speak_target = ""


# =========================================================
# TAB 2 — MEDICINE PHOTO
# =========================================================

with tab2:

    photo = st.file_uploader(
        "Upload a medicine photo",
        type=["jpg", "jpeg", "png"],
        help="Clear, well-lit photos give the best results."
    )

    if photo:
        col_img, col_meta = st.columns([1, 2])
        with col_img:
            st.image(photo, width=220, caption="Uploaded medicine")
        with col_meta:
            st.markdown(
                f"""
                <div style='color:#90caf9; font-size:13px; margin-top:10px;'>
                📁 <b>{photo.name}</b><br>
                📦 {round(photo.size/1024, 1)} KB · {photo.type}
                </div>
                """,
                unsafe_allow_html=True
            )

    col_btn2, col_speak2 = st.columns([3, 1])

    with col_btn2:
        analyze2_clicked = st.button(
            "🔍 Analyze Medicine Photo",
            use_container_width=True,
            disabled=not bool(photo)
        )

    with col_speak2:
        speak2_clicked = st.button(
            "🔊 Speak",
            use_container_width=True,
            key="speak_tab2",
            disabled=not bool(st.session_state.photo_result)
        )

    # ── Analyze photo ──
    if analyze2_clicked and photo:
        with st.spinner("Analyzing medicine image…"):
            try:
                photo.seek(0)
                image_b64 = base64.b64encode(photo.read()).decode()
                result = asyncio.run(
                    call_mcp_tool("medicine_photo_analyzer", {"image_b64": image_b64})
                )
                st.session_state.photo_result = result
            except Exception as e:
                st.error(f"Analysis error: {e}")

    # ── Result display ──
    if st.session_state.photo_result:
        st.markdown(
            f'<div class="result-box">{st.session_state.photo_result}</div>',
            unsafe_allow_html=True
        )

    # ── Language selector + audio ──
    if speak2_clicked and st.session_state.photo_result:
        st.session_state.speak_target = "photo"

    if st.session_state.get("speak_target") == "photo" and st.session_state.photo_result:
        st.markdown("---")
        st.markdown("**🌐 Select Voice Language**")
        lang_col4, lang_col5, lang_col6 = st.columns([1, 1, 2])

        with lang_col4:
            if st.button("🇬🇧 English", use_container_width=True, key="eng_photo"):
                generate_and_play_audio(st.session_state.photo_result, "English")
                st.session_state.speak_target = ""

        with lang_col5:
            if st.button("🇮🇳 Telugu", use_container_width=True, key="tel_photo"):
                generate_and_play_audio(st.session_state.photo_result, "Telugu")
                st.session_state.speak_target = ""

        with lang_col6:
            if st.button("✖ Cancel", key="cancel_photo"):
                st.session_state.speak_target = ""


# =========================================================
# FLOATING SPEAKER FAB (always visible, opens modal logic)
# =========================================================

st.markdown(
    """
    <div class="speak-fab">
        <div style="
            background: rgba(8,12,24,0.82);
            border: 1px solid rgba(99,179,237,0.25);
            border-radius: 10px;
            padding: 6px 12px;
            color: #90caf9;
            font-size: 11px;
            letter-spacing: 0.05em;
            text-align: center;
        ">🔊 SPEAK</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div style="
        text-align: center;
        margin-top: 48px;
        color: rgba(144,202,249,0.45);
        font-size: 12px;
        letter-spacing: 0.04em;
    ">
        MediBot MCP · FastMCP + Groq · Voice powered by gTTS &amp; Google Translate
    </div>
    """,
    unsafe_allow_html=True
)
