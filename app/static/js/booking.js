// --- FUNGSI MODAL ---
function openModal(serviceType) {
  const modal = document.getElementById("bookingModal");
  if (modal) {
    modal.style.display = "flex";
    console.log("Modal dibuka untuk:", serviceType);
  }
}

function closeModal() {
  const modal = document.getElementById("bookingModal");
  if (modal) {
    modal.style.display = "none";
  }
}

// --- FUNGSI NAVIGASI STEP ---
function nextStep(stepNumber) {
  document.querySelectorAll(".modal-step").forEach((step) => {
    step.classList.remove("active");
  });
  const targetStep = document.getElementById("step" + stepNumber);
  if (targetStep) {
    targetStep.classList.add("active");
  }
}

// --- FUNGSI SELEKSI UI ---
function selectOption(element) {
  const parent = element.parentElement;
  parent.querySelectorAll(".selected").forEach((el) => {
    el.classList.remove("selected");
  });
  element.classList.add("selected");
}

// --- FUNGSI FINISH BOOKING ---
async function finishBooking() {
  // Ambil data yang dipilih user dari UI
  const pet = document.querySelector("#step1 .selection-card.selected");
  const paket = document.querySelector("#step2 .selection-card.selected");
  const tglElement = document.getElementById("tanggal_booking");
  const jam = document.querySelector("#step4 .time-btn.selected");

  // Validasi
  if (!pet || !paket || !tglElement || !tglElement.value || !jam) {
    alert(
      "Mohon lengkapi pilihan Hewan, Paket, Tanggal, dan Jam sebelum konfirmasi!",
    );
    return;
  }

  // Persiapkan FormData
  const formData = new FormData();
  formData.append("id_pet", pet.getAttribute("data-pet-id"));
  formData.append("id_paket_grooming", paket.getAttribute("data-paket-id"));
  formData.append("tanggal_booking", tglElement.value);
  formData.append("jam_booking", jam.getAttribute("data-time"));

  try {
    const response = await fetch("/bookings/create", {
      method: "POST",
      body: formData,
    });

    if (response.redirected) {
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
