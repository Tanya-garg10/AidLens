# 🧠 AidLens – AI for Social Good  
**Powered by Google Gemini**

AidLens is a multimodal AI assistant designed to help NGOs, volunteers, and students understand complex information and take responsible next steps. It supports **text, images, PDFs, and voice input**, making critical information easier to access and act upon in real-world social impact scenarios.

## 🌍 Why AidLens?

In social good and community work, important information often comes in confusing formats—dense text messages, scanned documents, PDFs, images, or even spoken instructions. Misunderstanding such information can cause delays or unsafe decisions.  
AidLens bridges this gap by converting information from multiple formats into **clear, structured, and actionable guidance**.

## ✨ Key Features

- 📝 **Text Input** – Paste messages or notes for instant explanation  
- 🖼️ **Image Upload** – Understand scanned notices or document images  
- 📄 **PDF Support** – Extract and analyze content from multi-page PDFs  
- 🎤 **Voice Input (Mic + Upload)** – Speak directly or upload audio for transcription and analysis  
- 👥 **Role-Based Responses** – Tailored outputs for NGO Workers, Volunteers, and Students  
- 📋 **Structured Output** – Summary, key points, next steps, risks, and clarifying questions  
- ⚠️ **Responsible AI Design** – Safety-aware responses for sensitive topics  

## 🛠️ Built With

- **Python** – Core programming language  
- **Google Gemini API** – Multimodal reasoning, content generation, and audio transcription  
- **Google AI Studio** – API key management and model access  
- **Streamlit** – Web application framework  
- **Streamlit Cloud** – Hosting and public demo deployment  
- **Pillow (PIL)** – Image processing  
- **pdfplumber** – PDF text extraction  
- **streamlit-audiorec** – Microphone-based voice input  
- **Prompt Engineering** – Structured, role-based, and safe AI responses  
- **GitHub** – Version control and open-source collaboration  

## ⚙️ How It Works

1. User provides input via text, image, PDF, or voice  
2. Voice inputs are transcribed using Gemini  
3. PDF text is extracted and combined with other inputs  
4. Gemini processes the content using multimodal reasoning  
5. AidLens returns a structured and role-specific response  

## ▶️ Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/your-username/aidlens.git
cd aidlens
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Gemini API key

```bash
export GEMINI_API_KEY=your_api_key_here
```

*(or enter it in the app sidebar)*

### 4. Run the app

```bash
streamlit run app.py
```

## ⚠️ Disclaimer

AidLens is an informational support tool and does not replace professional medical, legal, or emergency advice. Users should consult qualified professionals when necessary.

## 🚀 Future Roadmap

* Multilingual support for regional languages
* Text-to-speech output for accessibility
* Deeper customization for NGO workflows
* Improved handling of handwritten and large PDFs

## 💙 Impact

AidLens demonstrates how advanced multimodal AI can be applied responsibly beyond chat interfaces—supporting clarity, accessibility, and real-world decision-making for social good.

