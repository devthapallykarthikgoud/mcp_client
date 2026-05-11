# app.py

import streamlit as st
import base64
import asyncio

from controller.mcp_client import decide_and_run, call_mcp_tool

st.set_page_config(
    page_title="MediBot MCP",
    page_icon="🩺"
)

st.title("🩺 MediBot MCP")
st.caption("AI Medical Assistant using FastMCP + Groq")

tab1, tab2 = st.tabs([
    "Symptom Checker",
    "Medicine Photo"
])


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
                st.write(result)
        else:
            st.error("Please enter your symptoms")


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

                st.write(result)
