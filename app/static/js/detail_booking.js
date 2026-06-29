document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('appointmentModal');
    if (!modal) return;
    const closeBtn = modal.querySelector('.close-btn');

    document.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Read data attributes
            const id = btn.dataset.id;
            const packageName = btn.dataset.package;
            const date = btn.dataset.date;
            const time = btn.dataset.time;
            const status = btn.dataset.status;
            const petName = btn.dataset.petName;
            const petBreed = btn.dataset.petBreed;
            const petAge = btn.dataset.petAge;
            const petImage = btn.dataset.petImage;
            const locationName = btn.dataset.locationName;
            const locationAddress = btn.dataset.locationAddress;
            const contact = btn.dataset.contact;
            const featuresStr = btn.dataset.features || '';
            const notes = btn.dataset.notes;

            // Populate text content
            document.getElementById('detail-modal-title').textContent = packageName;
            document.getElementById('detail-modal-subtitle').textContent = `${date} • ${time}`;
            
            const statusBadge = document.getElementById('detail-modal-status');
            statusBadge.textContent = status;
            
            // Adjust badge styles depending on status
            statusBadge.className = ''; // Reset classes
            if (status === 'Selesai') {
                statusBadge.className = 'badge-confirmed';
            } else if (status === 'Dibatalkan') {
                statusBadge.className = 'badge-cancelled';
            } else {
                statusBadge.className = 'badge-upcoming';
            }

            // Pet info
            const petAvatar = document.getElementById('detail-pet-avatar');
            petAvatar.src = petImage;
            petAvatar.alt = petName;
            
            document.getElementById('detail-pet-name').textContent = petName;
            document.getElementById('detail-pet-breed-age').textContent = `${petBreed} • ${petAge}`;

            // Detail fields
            document.getElementById('detail-datetime').textContent = `${date}, ${time}`;
            document.getElementById('detail-package').textContent = packageName;
            document.getElementById('detail-location-name').textContent = locationName;
            document.getElementById('detail-location-address').textContent = locationAddress;
            document.getElementById('detail-partner-name').textContent = locationName;
            document.getElementById('detail-partner-phone').textContent = contact;

            // Features / Checklist
            const checklistContainer = document.getElementById('detail-checklist');
            checklistContainer.innerHTML = '';
            if (featuresStr) {
                const features = featuresStr.split('|');
                features.forEach(feat => {
                    if (feat.trim()) {
                        const li = document.createElement('li');
                        li.innerHTML = `<i class="far fa-check-circle"></i> ${feat}`;
                        checklistContainer.appendChild(li);
                    }
                });
                document.getElementById('detail-checklist-section').style.display = 'block';
            } else {
                document.getElementById('detail-checklist-section').style.display = 'none';
            }

            // Notes
            document.getElementById('detail-notes').textContent = notes;

            // Cancel Form
            const cancelIdInput = document.getElementById('detail-cancel-booking-id');
            const cancelBtn = modal.querySelector('.btn-cancel');
            if (cancelIdInput) {
                cancelIdInput.value = id;
            }
            if (cancelBtn) {
                if (status === 'Dibatalkan' || status === 'Selesai') {
                    cancelBtn.style.display = 'none';
                } else {
                    cancelBtn.style.display = 'block';
                }
            }

            // Show modal
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            document.body.classList.add('modal-active'); // Lock transition for ghosting bug
            modal.querySelector('.detail-modal-container').scrollTop = 0;
        });
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        document.body.classList.remove('modal-active'); // Restore transition
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
            document.body.classList.remove('modal-active'); // Restore transition
        }
    });
});