document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("sisiVideo");
    const handButton = document.getElementById("sisiHandButton");

    if (!video || !handButton) {
        console.error("Video atau tombol telapak tangan tidak ditemukan.");
        return;
    }

    // Status animasi
    let greetingFinished = false;
    let isTransitioning = false;


    // ==========================================
    // VIDEO SELESAI
    // ==========================================

    video.addEventListener("ended", () => {

        // Kalau animasi awal selesai
        if (!isTransitioning) {

            greetingFinished = true;

            // Pastikan tetap berada di frame terakhir
            video.pause();

            console.log("SISI selesai melambaikan tangan.");
            console.log("Menunggu user menekan telapak tangan.");

            return;
        }


        // ======================================
        // VIDEO SETELAH TELAPAK DIKLIK
        // ======================================

        console.log("Animasi selesai.");
        console.log("Menuju halaman chat...");

        // Aktifkan efek fade
        document.body.classList.add("page-transition");

        // Tunggu animasi fade selesai
        setTimeout(() => {
            window.location.href = "static/pages/chat.html";
        }, 500);
    });


    // ==========================================
    // TELAPAK TANGAN DIKLIK
    // ==========================================

    handButton.addEventListener("click", () => {

        // Jangan bisa diklik sebelum animasi pertama selesai
        if (!greetingFinished) {
            console.log("Tunggu SISI selesai menyapa.");
            return;
        }

        // Mencegah klik berkali-kali
        if (isTransitioning) {
            return;
        }

        console.log("Telapak tangan diklik.");

        isTransitioning = true;

        video.classList.add("video-resetting");

        setTimeout(() => {

            video.currentTime = 0;

            video.play()
                .then(() => {

                    video.classList.remove("video-resetting");

                    console.log("▶️ Video berhasil diputar ulang.");

                })
                .catch((error) => {

                    console.error("❌ Video gagal diputar:", error);

                    video.classList.remove("video-resetting");

                });

        }, 150);
    });


    // ==========================================
    // AUTOPLAY
    // ==========================================

    video.play().catch((error) => {
        console.warn("Autoplay tidak dapat dijalankan:", error);
    });
});