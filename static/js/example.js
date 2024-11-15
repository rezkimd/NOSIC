setInterval(() => {
    // Contoh untuk memperbarui gambar dan status dari server
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('driver-image').src = data.image_url; // URL gambar dari server
            document.getElementById('driver-status').innerText = `Status: ${data.status}`; // Status pengemudi

            // Menambahkan notifikasi baru jika perlu
            if (data.alert) {
                const notificationList = document.getElementById('notification-list');
                const newNotification = document.createElement('li');
                newNotification.innerText = data.alert;
                notificationList.appendChild(newNotification);
            }
        })
        .catch(console.error);
}, 5000); // Update setiap 5 detik
