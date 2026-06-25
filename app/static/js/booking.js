let currentService = 'Grooming';

// --- FUNGSI MODAL ---
function openModal(serviceType) {
  currentService = serviceType;
  const modal = document.getElementById("bookingModal");
  if (modal) {
    modal.style.display = "flex";
    console.log("Modal dibuka untuk:", serviceType);
    
    // Reset to step 1
    goToStep('step1');
    
    // Update all title spans/titles to reflect service name
    document.querySelectorAll(".service-title-text").forEach(el => {
      el.textContent = serviceType;
    });

    // Reset inputs & selections
    document.querySelectorAll(".selection-card.selected, .time-btn.selected").forEach((el) => {
      el.classList.remove("selected");
    });
    const tglElement = document.getElementById("tanggal_booking");
    if (tglElement) tglElement.value = "";
    const keluhanElement = document.getElementById("keluhan_input");
    if (keluhanElement) keluhanElement.value = "";
  }
}

function closeModal() {
  const modal = document.getElementById("bookingModal");
  if (modal) {
    modal.style.display = "none";
  }
}

// --- FUNGSI NAVIGASI STEP ---
function goToStep(stepId) {
  document.querySelectorAll(".modal-step").forEach((step) => {
    step.style.display = "none";
    step.classList.remove("active");
  });
  const targetStep = document.getElementById(stepId);
  if (targetStep) {
    targetStep.style.display = "block";
    targetStep.classList.add("active");
  }
}

function goToStep2() {
  const selectedPet = document.querySelector("#step1 .selection-card.selected");
  if (!selectedPet) {
    alert("Mohon pilih peliharaan terlebih dahulu!");
    return;
  }
  if (currentService === 'Grooming') {
    goToStep('step2_grooming');
  } else {
    goToStep('step2_vet');
  }
}

function goBackFromStep4() {
  if (currentService === 'Grooming') {
    goToStep('step3_grooming');
  } else {
    goToStep('step3_vet');
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
  // Ambil data pet (step 1)
  const pet = document.querySelector("#step1 .selection-card.selected");
  const tglElement = document.getElementById("tanggal_booking");
  const jam = document.querySelector("#step4 .time-btn.selected");

  if (!pet || !tglElement || !tglElement.value || !jam) {
    alert("Mohon lengkapi pilihan Hewan, Tanggal, dan Jam sebelum konfirmasi!");
    return;
  }

  const formData = new FormData();
  formData.append("id_pet", pet.getAttribute("data-pet-id"));

  let endpoint = "";

  if (currentService === 'Grooming') {
    const paket = document.querySelector("#step2_grooming .selection-card.selected");
    if (!paket) {
      alert("Mohon lengkapi pilihan Paket sebelum konfirmasi!");
      return;
    }
    formData.append("id_paket_grooming", paket.getAttribute("data-paket-id"));
    formData.append("tanggal_booking", tglElement.value);
    formData.append("jam_booking", jam.getAttribute("data-time"));
    endpoint = "/bookings/create";
  } else {
    // Veterinary
    const dokter = document.querySelector("#step2_vet .selection-card.selected");
    const keluhanElement = document.getElementById("keluhan_input");
    if (!dokter) {
      alert("Mohon lengkapi pilihan Dokter sebelum konfirmasi!");
      return;
    }
    const keluhan = keluhanElement ? keluhanElement.value.trim() : "";
    if (!keluhan) {
      alert("Mohon isi keluhan peliharaan Anda!");
      return;
    }
    formData.append("id_dokter", dokter.getAttribute("data-dokter-id"));
    formData.append("keluhan", keluhan);
    formData.append("tanggal_janji", tglElement.value);
    formData.append("jam_janji", jam.getAttribute("data-time"));
    endpoint = "/janji-temu/create";
  }

  try {
    const response = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });

    if (response.redirected) {
      window.location.href = response.url;
    } else if (response.ok) {
      alert("Booking berhasil disimpan!");
      window.location.href = "/booking.html";
    } else {
      const errorText = await response.text();
      alert("Gagal menyimpan booking: " + errorText);
    }
  } catch (error) {
    console.error("Error:", error);
    alert("Terjadi kesalahan pada server!");
  }
}
