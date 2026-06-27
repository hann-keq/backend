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

// --- FILTER PACKAGES BY SELECTED PROVIDER ---
const PARTNER_PACKAGES = JSON.parse(
  document.getElementById("partnerPackagesData")?.textContent || "{}"
);

const PARTNER_SCHEDULE = JSON.parse(
  document.getElementById("partnerScheduleData")?.textContent || "{}"
);

const DAY_NAMES = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];

function getDayName(dateString) {
  const d = new Date(dateString + "T00:00:00");
  return DAY_NAMES[d.getDay()];
}

function getSelectedPartnerId() {
  if (currentService === "Grooming") {
    const provider = document.querySelector("#step2_grooming .selection-card.selected");
    return provider ? provider.getAttribute("data-partner-id") : null;
  } else {
    // Veterinary: dokter's partner is embedded via data-partner-id on dokter card
    const dokter = document.querySelector("#step2_vet .selection-card.selected");
    return dokter ? dokter.getAttribute("data-partner-id") : null;
  }
}

function filterTimeSlotsBySchedule(partnerId) {
  if (!partnerId) return;
  const tglElement = document.getElementById("tanggal_booking");
  if (!tglElement || !tglElement.value) return;

  const day = getDayName(tglElement.value);
  const schedule = PARTNER_SCHEDULE[partnerId] || {};
  const todaySchedule = schedule[day];

  document.querySelectorAll("#step4 .time-btn").forEach((btn) => {
    const jam = btn.getAttribute("data-time");
    if (!jam) return;

    if (!todaySchedule) {
      // Closed / libur — hide all times
      btn.style.display = "none";
      return;
    }

    // Check if time is within operating hours
    const jamBuka = todaySchedule.jam_buka;
    const jamTutup = todaySchedule.jam_tutup;

    if (jam >= jamBuka && jam <= jamTutup) {
      btn.style.display = "";
    } else {
      btn.style.display = "none";
    }
  });
}

// Override goToStep to intercept step4 entry and filter time slots
const _originalGoToStep = goToStep;
goToStep = function (stepId) {
  _originalGoToStep(stepId);

  if (stepId === "step4") {
    const partnerId = getSelectedPartnerId();
    if (partnerId) {
      // Set min date to today
      const tglInput = document.getElementById("tanggal_booking");
      if (tglInput) {
        const today = new Date().toISOString().split("T")[0];
        tglInput.setAttribute("min", today);
        tglInput.addEventListener("change", function () {
          filterTimeSlotsBySchedule(partnerId);
          validateDayNotLibur(partnerId);
        });
        tglInput.addEventListener("input", function () {
          filterTimeSlotsBySchedule(partnerId);
          validateDayNotLibur(partnerId);
        });
      }
      filterTimeSlotsBySchedule(partnerId);
    }
  }
};

function validateDayNotLibur(partnerId) {
  const tglInput = document.getElementById("tanggal_booking");
  if (!tglInput || !tglInput.value) return true;

  const day = getDayName(tglInput.value);
  const schedule = PARTNER_SCHEDULE[partnerId] || {};
  const todaySchedule = schedule[day];

  if (!todaySchedule) {
    tglInput.setCustomValidity(`Tutup di hari ${day}. Silakan pilih hari lain.`);
  } else {
    tglInput.setCustomValidity("");
  }
  return !!todaySchedule;
}

function goToStep3Grooming() {
  const selectedProvider = document.querySelector("#step2_grooming .selection-card.selected");
  if (!selectedProvider) {
    alert("Mohon pilih provider terlebih dahulu!");
    return;
  }

  const partnerId = selectedProvider.getAttribute("data-partner-id");
  const packages = PARTNER_PACKAGES[partnerId] || [];
  const container = document.getElementById("packageListContainer");

  if (packages.length === 0) {
    container.innerHTML =
      '<p class="text-muted" style="padding:20px;text-align:center;">No packages available for this provider.</p>';
  } else {
    container.innerHTML = packages
      .map(
        (pkg) => `
      <div class="selection-card" onclick="selectOption(this)" data-paket-id="${pkg.id}">
        <div class="card-content-wrapper align-start">
          <div class="package-icon-circle grooming-bg">
            <i class="fas fa-scissors"></i>
          </div>
          <div class="card-info">
            <span class="package-name">${pkg.nama}</span>
            <span class="package-price">Rp ${Number(pkg.harga).toLocaleString("id-ID")}</span>
          </div>
        </div>
      </div>`
      )
      .join("");
  }

  goToStep("step3_grooming");
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
