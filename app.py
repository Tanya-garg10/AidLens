# app.py
import streamlit as st
import os
from PIL import Image
import pdfplumber
import google.generativeai as genai

st.set_page_config(page_title="AidLens", page_icon="🧠", layout="centered")
st.title("🧠 AidLens — Social Good Assistant")

# ---------------- Sidebar ----------------
st.sidebar.header("Settings")
role = st.sidebar.selectbox("Select Role", ["NGO Worker", "Volunteer", "Student"])
language = st.sidebar.selectbox("Output Language", ["English", "Hindi"])

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    value=os.getenv("GEMINI_API_KEY", "")
)

# Default is placeholder; you'll pick from "Show available models"
model_name = st.sidebar.text_input(
    "Model name (use models/...)",
    value=os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
)

st.sidebar.markdown("---")
if st.sidebar.button("🔎 Show available models"):
    if not api_key:
        st.sidebar.error("Enter API key first.")
    else:
        try:
            genai.configure(api_key=api_key)
            models = []
            for m in genai.list_models():
                methods = getattr(m, "supported_generation_methods", [])
                if "generateContent" in methods:
                    models.append(m.name)  # e.g. "models/...."
            if not models:
                st.sidebar.warning("No generateContent models found for this key.")
            else:
                st.sidebar.success("Copy one of these into Model name:")
                st.sidebar.write(models)
        except Exception as e:
            st.sidebar.error(f"Model list error: {e}")

# ---------------- Main UI ----------------
st.write("Paste text, upload an image, or upload a PDF. Then click **Analyze**.")

text = st.text_area(
    "Text input (optional)",
    height=160,
    placeholder="Paste the message / document text here..."
)

col1, col2 = st.columns(2)
with col1:
    img_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg"])
with col2:
    pdf_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])

image = None
if img_file:
    image = Image.open(img_file)
    st.image(image, caption="Uploaded image", use_container_width=True)

def extract_pdf_text(uploaded_pdf, max_pages=8, max_chars=12000):
    """
    Extract text from PDF safely.
    - max_pages limits processing time
    - max_chars limits prompt size
    """
    extracted = []
    with pdfplumber.open(uploaded_pdf) as pdf:
        pages = pdf.pages[:max_pages]
        for p in pages:
            t = p.extract_text() or ""
            if t.strip():
                extracted.append(t.strip())
    joined = "\n\n".join(extracted).strip()
    if len(joined) > max_chars:
        joined = joined[:max_chars] + "\n\n[Truncated]"
    return joined

def build_prompt(role, language, content):
    system = (
        "You are AidLens, an assistant for NGOs & volunteers. "
        "Explain clearly, avoid jargon, be safe and non-medical. "
        "If content is medical/legal, include a short disclaimer and suggest consulting a professional. "
        "Ask 1 follow-up question only if necessary."
    )

    user = f"""
Role: {role}
Language: {language}
Task: Explain and help with next actions.
Content:
{content}

Output format:
1) Summary (2–3 lines)
2) Key points (bullets)
3) Recommended next steps (numbered)
4) Risks / what NOT to do (bullets)
5) One clarifying question (only if necessary)
""".strip()

    return system, user

def run_gemini(api_key, model_name, system, user, image=None):
    genai.configure(api_key=api_key)

    # Auto-fix model name if user didn't include "models/"
    if model_name and not model_name.startswith("models/"):
        model_name = "models/" + model_name

    model = genai.GenerativeModel(model_name, system_instruction=system)

    if image:
        resp = model.generate_content([user, image])
    else:
        resp = model.generate_content(user)

    return resp.text

btn = st.button("Analyze", type="primary", use_container_width=True)

if btn:
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
        st.stop()

    if not model_name:
        st.error("Please enter a valid model name (click 'Show available models').")
        st.stop()

    pdf_text = ""
    if pdf_file:
        try:
            with st.spinner("Extracting text from PDF..."):
                pdf_text = extract_pdf_text(pdf_file)
        except Exception as e:
            st.error(f"PDF read error: {e}")
            st.stop()

    combined_text = (text or "").strip()
    if pdf_text:
        combined_text = (combined_text + "\n\n--- PDF Content ---\n" + pdf_text).strip()

    if not combined_text and not image:
        st.error("Provide text, an image, or a PDF.")
        st.stop()

    content_for_prompt = combined_text if combined_text else "No text provided. Use image only."
    system, user_prompt = build_prompt(role, language, content_for_prompt)

    with st.spinner("Thinking with Gemini..."):
        try:
            out = run_gemini(api_key, model_name, system, user_prompt, image=image)
            st.subheader("Result")
            st.write(out)
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: Click 'Show available models' and copy a model that supports generateContent.")
