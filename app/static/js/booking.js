async function finishBooking() {
    // Ambil data yang dipilih user dari UI
    const pet = document.querySelector('#step1 .selection-card.selected');
    const paket = document.querySelector('#step2 .selection-card.selected');
    const tgl = document.getElementById('tanggal_booking').value;
    const jam = document.querySelector('#step4 .time-btn.selected');

    // Validasi sederhana
    if (!pet || !paket || !tgl || !jam) {
        alert("Mohon lengkapi pilihan Hewan, Paket, Tanggal, dan Jam sebelum konfirmasi!");
        return;
    }

    // Persiapkan FormData untuk dikirim ke Python
    const formData = new FormData();
    formData.append("id_pet", pet.getAttribute('data-pet-id'));
    formData.append("id_paket_grooming", paket.getAttribute('data-paket-id'));
    formData.append("tanggal_booking", tgl);
    formData.append("jam_booking", jam.getAttribute('data-time'));

    try {
        // Kirim ke route Python /bookings/create
        const response = await fetch('/bookings/create', {
            method: 'POST',
            body: formData
        });

        // Tangani hasil respon dari Python
        if (response.redirected) {
            // Jika Python berhasil redirect ke /appointments.html
            window.location.href = response.url;
        } else if (response.ok) {
            alert("Booking berhasil disimpan!");
            window.location.href = "/appointments.html";
        } else {
            const errorText = await response.text();
            alert("Gagal menyimpan booking: " + errorText);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Terjadi kesalahan pada server!");
    }
}