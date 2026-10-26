from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from groq import Groq
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import threading
import re
import speech_recognition as sr
import os
import requests
import base64
import smtplib

# Memuat variabel dari file .env
load_dotenv()

# Inisialisasi API
app = FastAPI()

# Mengizinkan Frontend (HTML) berkomunikasi dengan Backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- KONFIGURASI API ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "19zQpXlAQKHlcmXgXfLr" # Voice ID 'Zorin'

riwayat_chat = []

class PertanyaanUser(BaseModel):
    text: str

# --- FUNGSI INTERNAL ---
def koreksi_teks(teks):
    koreksi = [
        (r'(?i)\b(sistem\s*kin|sistim\s*kin|sis\s*tekin|sistemkin|sistein|vista\s*king)\b', 'Sistekin'),
        (r'(?i)\b(si\s*ba|cs\s*ba|cis\s*ba)\b', 'CSBA'),
        (r'(?i)\b(es\s*de\s*ef)\b', 'SDF'),
        (r'(?i)\b(un\s*tag|17\s*agustus)\b', 'Untag'),
        (r'(?i)\b(yuyek|yu\s*ai|ui\s*ux|wiyuex)\b', 'UI/UX')
    ]
    teks_koreksi = teks
    for pola, pengganti in koreksi:
        teks_koreksi = re.sub(pola, pengganti, teks_koreksi)
    return teks_koreksi

def load_knowledge_base():
    try:
        with open("sisi1.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Peringatan: File sisi1.md tidak ditemukan."

def putar_suara_background(nama_file):
    def putar():
        if os.path.exists(nama_file):
            os.system(f"mpg123 -q {nama_file}")
            os.remove(nama_file)
    thread = threading.Thread(target=putar)
    thread.daemon = True
    thread.start()

# ==========================================
# ENDPOINT API UNTUK FRONTEND
# ==========================================

@app.get("/api/listen")
def api_mendengar():
    """Menyalakan mikrofon fisik dan merekam suara."""
    r = sr.Recognizer()
    r.energy_threshold = 4000 
    r.dynamic_energy_threshold = False 
    r.pause_threshold = 0.5 
    
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            teks = r.recognize_google(audio, language="id-ID")
            teks_final = koreksi_teks(teks)
            return {"status": "success", "text": teks_final}
        except sr.WaitTimeoutError:
            return {"status": "error", "message": "Waktu habis. Pastikan Anda bicara cukup keras dan dekat."}
        except sr.UnknownValueError:
            return {"status": "error", "message": "Suara tidak jelas atau tertimpa kebisingan ruangan."}
        except Exception as e:
            return {"status": "error", "message": f"Terjadi kesalahan: {str(e)}"}

@app.post("/api/ask")
def api_bertanya(pertanyaan: PertanyaanUser):
    """Memproses teks ke Groq dan memutar suara ElevenLabs."""
    global riwayat_chat
    teks_user = pertanyaan.text
    
    # 1. RAG dengan Groq
    kb_content = load_knowledge_base()
    system_prompt = f"""Anda adalah SISI, asisten AI yang ramah dan cerdas untuk program studi Sistekin.
    Gunakan HANYA informasi berikut untuk menjawab:
    {kb_content}
    Jika informasi tidak ada di atas, beritahu dengan sopan."""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(riwayat_chat)
    messages.append({"role": "user", "content": teks_user})

    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama-3.3-70b-versatile",
        temperature=0.3,
    )
    jawaban_ai = chat_completion.choices[0].message.content
    
    riwayat_chat.append({"role": "user", "content": teks_user})
    riwayat_chat.append({"role": "assistant", "content": jawaban_ai})

    # 2. Buat Suara via ElevenLabs
    nama_file_audio = "suara_sisi.mp3"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": jawaban_ai,
        "model_id": "eleven_multilingual_v2", 
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(nama_file_audio, 'wb') as f:
                f.write(response.content)
            # 3. Putar Suara
            putar_suara_background(nama_file_audio)
    except Exception as e:
        print(f"Gagal TTS: {e}")

    # 4. Kembalikan teks ke web
    return {"status": "success", "response": jawaban_ai}

class ImageData(BaseModel):
    image_base64: str

@app.post("/api/save_photo")
def api_simpan_foto(data: ImageData):
    try:
        # Cek apakah folder 'Pictures' sudah ada, jika belum buat otomatis
        folder_simpan = "Pictures"
        if not os.path.exists(folder_simpan):
            os.makedirs(folder_simpan)

        # Membersihkan kode base64 dari header gambar
        img_data = data.image_base64.split(",")[1]
        
        # Membuat nama file unik berdasarkan tanggal dan jam
        nama_file = f"SISI_Photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        path_simpan = os.path.join(folder_simpan, nama_file)
        
        # Simpan gambar ke folder Pictures
        with open(path_simpan, "wb") as fh:
            fh.write(base64.b64decode(img_data))
            
        return {"status": "success", "message": "Tersimpan"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
    
class EmailData(BaseModel):
    image_base64: str
    email_penerima: str

@app.post("/api/kirim_email")
def api_kirim_email(data: EmailData):
    try:
        # Mengambil kredensial dari environment variables (.env)
        EMAIL_PENGIRIM = os.getenv("EMAIL_PENGIRIM") 
        PASSWORD_PENGIRIM = os.getenv("PASSWORD_PENGIRIM") 

        msg = MIMEMultipart()
        msg['From'] = EMAIL_PENGIRIM
        msg['To'] = data.email_penerima
        msg['Subject'] = "📸 Hasil Photobooth SISI - Sistekin"

        body = "Halo! Terima kasih telah mengunjungi booth Sistekin. Berikut adalah hasil jepretan Anda bersama SISI. Sampai jumpa lagi!"
        msg.attach(MIMEText(body, 'plain'))

        img_data = base64.b64decode(data.image_base64.split(",")[1])
        image = MIMEImage(img_data, name="SISI_Photobooth.jpg")
        msg.attach(image)
    
        # Proses Pengiriman Resmi via Server Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_PENGIRIM, PASSWORD_PENGIRIM)
        server.sendmail(EMAIL_PENGIRIM, data.email_penerima, msg.as_string())
        server.quit()

        return {"status": "success", "message": "Email berhasil meluncur!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
# ==========================================
# API ROUTE UNTUK FRONTEND
# ==========================================

@app.get("/")
async def read_index():
    return FileResponse("home.html")


app.mount("/static", StaticFiles(directory="static"), name="static")