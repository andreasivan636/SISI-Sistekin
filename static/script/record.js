// Tangkap elemen teks tempat jawaban SISI akan ditampilkan
const sisiAnswerText = document.querySelector('.sisi__answer-text');

// Jadikan startRecording sebagai fungsi utama yang memicu seluruh proses
async function startRecording() {
    // 1. Pindah ke tampilan merekam (Muncul mic besar)
    hide('state-default');
    hide('state-result');
    show('state-recording');

    try {
        // 2. Panggil API Python untuk mulai mendengarkan suara user
        const listenRes = await fetch('http://localhost:8000/api/listen');
        const listenData = await listenRes.json();

        // Begitu suara selesai ditangkap, pindah ke state result (Munculkan bubble AI)
        stopRecording();

        // Jika gagal mendengarkan/error dari mikrofon
        if (listenData.status !== 'success') {
            sisiAnswerText.innerHTML = '⚠️ ' + listenData.message;
            return;
        }

        // 3. Ubah isi bubble sementara AI sedang "memikirkan" jawaban
        sisiAnswerText.innerHTML = '<i>SISI sedang merangkai jawaban...</i>';

        // 4. Kirim teks hasil suara ke otak AI (Groq/ElevenLabs)
        const askRes = await fetch('http://localhost:8000/api/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: listenData.text })
        });
        const askData = await askRes.json();

        // 5. Timpa teks di dalam bubble dengan jawaban asli dari SISI
        if (askData.status === 'success') {
            sisiAnswerText.innerHTML = askData.response;
        } else {
            sisiAnswerText.innerHTML = '⚠️ Maaf, SISI mengalami gangguan saat menjawab.';
        }

    } catch (error) {
        // Jika server mati atau ada error jaringan
        stopRecording();
        sisiAnswerText.innerHTML = '⚠️ Gagal terhubung ke server. Pastikan uvicorn menyala.';
        console.error(error);
    }
}

// Fungsi stopRecording akan otomatis dipanggil dari dalam startRecording 
// saat AI selesai mendengarkan, untuk memunculkan bubble hasil.
function stopRecording() {
    hide('state-recording');
    show('state-result');
}

// Fungsi utilitas untuk menyembunyikan dan menampilkan elemen
function show(className) {
    const el = document.querySelector('.' + className);
    if(el) el.classList.remove('hidden');
}

function hide(className) {
    const el = document.querySelector('.' + className);
    if(el) el.classList.add('hidden');
}