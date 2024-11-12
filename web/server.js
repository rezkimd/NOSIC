const express = require('express');
const app = express();
const cors = require('cors');

app.use(cors());
app.use(express.json()); // Untuk parsing JSON

let driverStatus = { image_url: 'default.jpg', status: 'Normal', alert: null };

// Endpoint untuk menerima gambar dan status dari ESP32-CAM
app.post('/api/update', (req, res) => {
    const { image_url, status, alert } = req.body;
    driverStatus = { image_url, status, alert };
    res.sendStatus(200);
});

// Endpoint untuk memberikan status terkini
app.get('/api/status', (req, res) => {
    res.json(driverStatus);
});

// Menjalankan server pada port 3000
app.listen(3000, () => {
    console.log('Server berjalan di http://localhost:3000');
});
