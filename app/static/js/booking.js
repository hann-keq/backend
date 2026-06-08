const modal = document.getElementById("bookingModal");

function openModal(serviceName) {
  modal.style.display = "flex";
  const titleElement = document.getElementById("modalTitle");
  if (titleElement) titleElement.textContent = `${serviceName} Booking`;

  nextStep(1);
}

function closeModal() {
  modal.style.display = "none";
}

function nextStep(step) {
  const steps = document.querySelectorAll(".modal-step");
  steps.forEach((el) => el.classList.remove("active"));

  const target = document.getElementById("step" + step);
  if (target) target.classList.add("active");
}

function selectOption(element) {
  const container = element.parentElement;
  const items = container.querySelectorAll(".selection-card, .time-btn");

  // 2. Hapus class 'selected' dan reset inline style
  items.forEach((el) => {
    el.classList.remove("selected");
    el.style.backgroundColor = "";
  });

  // 3. Tambah class selected
  element.classList.add("selected");

  // 4. Khusus untuk button, gunakan warna highlight
  if (element.tagName === "BUTTON") {
    element.style.backgroundColor = "#f0f7f7";
  }
}

function finishBooking() {
  console.log("Processing booking...");
  alert("Booking Confirmed! Thank you.");
  closeModal();
}

// Tutup modal jika klik di area luar
window.onclick = (event) => {
  if (event.target === modal) closeModal();
};

// efek masuk
window.addEventListener("pageshow", () => {
  document.body.classList.remove("fade-out");
});

// klik navbar
document.querySelectorAll(".main-nav a").forEach((link) => {
  link.addEventListener("click", function (e) {
    const target = this.getAttribute("href");

    if (target && target !== "#") {
      e.preventDefault();

      document.body.classList.add("fade-out");

      // langsung pindah tanpa delay lama
      setTimeout(() => {
        window.location.href = target;
      }, 150); // lebih cepat
    }
  });
});
