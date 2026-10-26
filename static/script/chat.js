const chatContainer = document.getElementById('chat-container');
const micBtn = document.getElementById('mic-btn');

// Fungsi pembantu untuk membuat bubble chat baru
function tambahBubble(pengirim, teks, id_elemen = null) {
    const div = document.createElement('div');
    // Jika pengirimnya 'user' pakai class Kanan, jika 'ai' pakai class Kiri
    div.className = (pengirim === 'user') ? 'bubble-user' : 'bubble-ai';
    if (id_elemen) div.id = id_elemen;
    div.innerHTML = teks;
    
    chatContainer.appendChild(div);
    // Otomatis scroll ke chat paling bawah
    chatContainer.scrollTop = chatContainer.scrollHeight; 
}

function hapusBubble(id_elemen) {
    const elemen = document.getElementById(id_elemen);
    if (elemen) elemen.remove();
}

// Fungsi Utama saat tombol Mic diklik
async function mulaiObrolan() {
    // 1. Ubah tombol jadi merah berdenyut
    micBtn.classList.add('recording');
    
    // 2. Munculkan bubble status SISI mendengarkan
    const statusDengarId = "status-" + Date.now();
    tambahBubble('ai', '<i>SISI sedang mendengarkan suaramu...</i>', statusDengarId);

    try {
        // Panggil mesin pendengar di Python
        const listenRes = await fetch('http://localhost:8000/api/listen');
        const listenData = await listenRes.json();

        // Hapus tulisan mendengarkan & matikan warna merah tombol
        hapusBubble(statusDengarId);
        micBtn.classList.remove('recording');

        if (listenData.status !== 'success') {
            tambahBubble('ai', '⚠️ ' + listenData.message);
            return;
        }

        // 3. Tampilkan ucapan User di KANAN
        const teksUser = listenData.text;
        tambahBubble('user', teksUser);

        // 4. Tampilkan status SISI memikirkan di KIRI
        const statusMikirId = "mikir-" + Date.now();
        tambahBubble('ai', '<i>Sedang merangkai jawaban...</i>', statusMikirId);

        // Panggil otak Groq & ElevenLabs di Python
        const askRes = await fetch('http://localhost:8000/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: teksUser })
        });
        const askData = await askRes.json();

        // Hapus tulisan memikirkan
        hapusBubble(statusMikirId);

        if (askData.status === 'success') {
            // 5. Tampilkan jawaban SISI yang sebenarnya di KIRI!
            tambahBubble('ai', askData.response);
        }

    } catch (error) {
        micBtn.classList.remove('recording');
        hapusBubble(statusDengarId);
        tambahBubble('ai', '⚠️ Gagal terhubung ke server. Pastikan uvicorn menyala.');
        console.error(error);
    }
}