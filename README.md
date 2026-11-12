# SISI — Sistem AI (Local Voice & Chat Assistant)

**SISI** is a local, privacy-first AI assistant engineered specifically for the **Systems & Information Technology (Sistekin)** department at Universitas 17 Agustus 1945 Surabaya.

Built to run on a dedicated Ubuntu mini PC server, SISI combines local Large Language Model (LLM) inference via **Ollama** with a **Python/Flask** backend and **Text-to-Speech (TTS)** synthesis to deliver natural, low-latency voice and text interactions.

---

### ✨ Key Features
- **Local LLM Inference:** Powered by Ollama for offline-capable, zero-API-cost, and privacy-preserving AI responses.
- **Voice Synthesis (TTS):** Generates natural Indonesian speech output (`suara_sisi`) alongside text responses.
- **Custom Web OS Interface:** Interactive frontend interfaces (`hima_os.html` & `home.html`) designed for campus kiosks and departmental showcases.
- **Lightweight Backend Architecture:** Built with Python (`app.py` & `server.py`) for fast request routing and audio streaming.

---

### 🛠️ Tech Stack
- **Backend:** Python, Flask
- **AI & Speech:** Ollama (Local LLM), Text-to-Speech Synthesis
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Deployment & Infrastructure:** Ubuntu Linux Server (Self-Hosted)

---

### 🚀 Local Setup & Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/andreasivan636/SISI-Sistekin.git](https://github.com/andreasivan636/SISI-Sistekin.git)
   cd SISI-Sistekin
