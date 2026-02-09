# app.py
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai

st.set_page_config(page_title="AidLens", page_icon="🧠", layout="centered")
st.title("🧠 AidLens — Social Good Assistant")

# --- Sidebar ---
st.sidebar.header("Settings")
role = st.sidebar.selectbox("Select Role", ["NGO Worker", "Volunteer", "Student"])
language = st.sidebar.selectbox("Output Language", ["English", "Hindi"])

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    value=os.getenv("GEMINI_API_KEY", "")
)

# Default is just a placeholder; you'll pick from the "Show available models" list.
model_name = st.sidebar.text_input(
    "Model name (use models/...)",
    value=os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
)

# --- Show available models button ---
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
                    models.append(m.name)  # e.g., "models/...."
            if not models:
                st.sidebar.warning("No generateContent models found for this key.")
            else:
                st.sidebar.success("Copy one of these into Model name:")
                st.sidebar.write(models)
        except Exception as e:
            st.sidebar.error(f"Model list error: {e}")

st.write("Paste text or upload an image (optional). Then click **Analyze**.")

text = st.text_area(
    "Text input",
    height=180,
    placeholder="Paste the message / document text here..."
)

img_file = st.file_uploader("Upload image (optional)", type=["png", "jpg", "jpeg"])

image = None
if img_file:
    image = Image.open(img_file)
    st.image(image, caption="Uploaded image", use_container_width=True)

def build_prompt(role, language, text):
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
Content: {text}

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

    # Auto-fix model name
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

    if not text and not image:
        st.error("Provide text or an image.")
        st.stop()

    system, user_prompt = build_prompt(role, language, text if text else "No text provided. Use image only.")
    with st.spinner("Thinking with Gemini..."):
        try:
            out = run_gemini(api_key, model_name, system, user_prompt, image=image)
            st.subheader("Result")
            st.write(out)
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Tip: Click 'Show available models' and copy a model that supports generateContent.")
