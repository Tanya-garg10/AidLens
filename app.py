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
                    models.append(m.name)
            if not models:
                st.sidebar.warning("No generateContent models found for this key.")
            else:
                st.sidebar.success("Copy one of these into Model name:")
                st.sidebar.write(models)
        except Exception as e:
            st.sidebar.error(f"Model list error: {e}")

# ---------------- Helpers ----------------
def extract_pdf_text(uploaded_pdf, max_pages=8, max_chars=12000):
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

def normalize_model_name(m):
    if m and not m.startswith("models/"):
        return "models/" + m
    return m

def run_gemini_text(api_key, model_name, system, user, image=None):
    genai.configure(api_key=api_key)
    model_name = normalize_model_name(model_name)
    model = genai.GenerativeModel(model_name, system_instruction=system)

    if image:
        resp = model.generate_content([user, image])
    else:
        resp = model.generate_content(user)
    return resp.text

def transcribe_audio_with_gemini(api_key, model_name, audio_bytes, mime_type):
    """
    Uses Gemini to transcribe audio into text.
    Works as a lightweight voice feature for hackathon demos.
    """
    genai.configure(api_key=api_key)
    model_name = normalize_model_name(model_name)
    model = genai.GenerativeModel(model_name)

    prompt = (
        "Transcribe this audio accurately into plain text. "
        "If Hindi/Hinglish, keep it as spoken. No extra commentary."
    )

    # Gemini accepts multimodal content arrays; audio is passed as inline_data.
    audio_part = {
        "inline_data": {
            "mime_type": mime_type,
            "data": audio_bytes
        }
    }

    resp = model.generate_content([prompt, audio_part])
    return resp.text.strip()

# ---------------- Main UI ----------------
st.write("Paste text, upload an image or PDF, or add voice (audio). Then click **Analyze**.")

text = st.text_area(
    "Text input (optional)",
    height=150,
    placeholder="Paste the message / document text here..."
)

tab1, tab2, tab3 = st.tabs(["🖼️ Image", "📄 PDF", "🎤 Voice"])

image = None
pdf_file = None
audio_file = None

with tab1:
    img_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg"])
    if img_file:
        image = Image.open(img_file)
        st.image(image, caption="Uploaded image", use_container_width=True)

with tab2:
    pdf_file = st.file_uploader("Upload PDF (optional)", type=["pdf"])

with tab3:
    st.caption("Upload an audio file (m4a/mp3/wav). We'll transcribe it using Gemini, then analyze it.")
    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg"])

btn = st.button("Analyze", type="primary", use_container_width=True)

if btn:
    if not api_key:
        st.error("Please enter your Gemini API key in the sidebar.")
        st.stop()

    if not model_name:
        st.error("Please enter a valid model name (click 'Show available models').")
        st.stop()

    # 1) PDF -> text
    pdf_text = ""
    if pdf_file:
        try:
            with st.spinner("Extracting text from PDF..."):
                pdf_text = extract_pdf_text(pdf_file)
        except Exception as e:
            st.error(f"PDF read error: {e}")
            st.stop()

    # 2) Voice -> text
    voice_text = ""
    if audio_file:
        try:
            with st.spinner("Transcribing audio..."):
                audio_bytes = audio_file.read()
                # Streamlit provides file type; fallback to wav
                mime = audio_file.type or "audio/wav"
                voice_text = transcribe_audio_with_gemini(api_key, model_name, audio_bytes, mime)
                st.subheader("Voice Transcription")
                st.write(voice_text)
        except Exception as e:
            st.error(f"Audio transcription error: {e}")
            st.stop()

    # 3) Combine inputs
    combined_text = (text or "").strip()

    if voice_text:
        combined_text = (combined_text + "\n\n--- Voice Transcript ---\n" + voice_text).strip()

    if pdf_text:
        combined_text = (combined_text + "\n\n--- PDF Content ---\n" + pdf_text).strip()

    if not combined_text and not image:
        st.error("Provide text, image, PDF, or voice audio.")
        st.stop()

    content_for_prompt = combined_text if combined_text else "No text provided. Use image only."
    system, user_prompt = build_prompt(role, language, content_for_prompt)

    # 4) Gemini response
    with st.spinner("Thinking with Gemini..."):
        try:
            out = run_gemini_text(api_key, model_name, system, user_prompt, image=image)
            st.subheader("Result")
            st.write(out)
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: Click 'Show available models' and copy a model that supports generateContent.")


