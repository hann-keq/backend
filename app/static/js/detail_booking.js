document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('appointmentModal');
    if (!modal) return;
    const closeBtn = modal.querySelector('.close-btn');
    const cancelBtn = modal.querySelector('.btn-cancel');

    document.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            modal.querySelector('.detail-modal-container').scrollTop = 0;
        });
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    });

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    });
});