document.addEventListener('DOMContentLoaded', () => {
    window.addEventListener('pageshow', () => {
        document.body.classList.remove('fade-out');
    });

    document.querySelectorAll('.main-nav a').forEach((link) => {
        link.addEventListener('click', function (e) {
            const target = this.getAttribute('href');

            if (target && target !== '#') {
                e.preventDefault();
                document.body.classList.add('fade-out');

                setTimeout(() => {
                    window.location.href = target;
                }, 150);
            }
        });
    });

    const confirmLogoutBtn = document.getElementById('confirmLogout');
    if (confirmLogoutBtn) {
        confirmLogoutBtn.addEventListener('click', async function () {
            document.body.classList.add('fade-out');

            try {
                await fetch('/logout', { method: 'POST' });
            } catch (_) {
                // ignore network errors
            }

            setTimeout(() => {
                window.location.href = '/';
            }, 200);
        });
    }

    const openEditProfileBtn = document.getElementById('openEditProfile');
    if (openEditProfileBtn) {
        openEditProfileBtn.addEventListener('click', function () {
            window.location.href = openEditProfileBtn.dataset.editUrl;
        });
    }

    const editPetModal = document.getElementById('editPetModal');
    if (editPetModal) {
        editPetModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;

            document.getElementById('modal-pet-id').value = button.getAttribute('data-id');
            document.getElementById('modal-pet-name').value = button.getAttribute('data-nama');
            document.getElementById('modal-pet-jenis').value = button.getAttribute('data-ras');
            document.getElementById('modal-pet-umur').value = button.getAttribute('data-umur');
            document.getElementById('modal-pet-berat').value = button.getAttribute('data-berat');
            document.getElementById('modal-pet-gender').value = button.getAttribute('data-gender');
        });
    }
});