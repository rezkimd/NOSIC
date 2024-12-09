import sys

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from function.Face_Function import face_generator
import requests
import sqlite3
import cv2

app = Flask(__name__)

# Konfigurasi database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your_secret_key"  # Ganti dengan kunci rahasia yang kuat

db = SQLAlchemy(app)


# Model untuk pengguna
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)  # Waktu otomatis terisi
    date = db.Column(db.Date, default=date.today)  # Tanggal otomatis terisi
    count = db.Column(db.Integer, default=1)  # Default count adalah 1
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )  # Foreign key

    user = db.relationship("User", backref=db.backref("data", lazy=True))


# ====================================================#
# Batas suci fungsi
# ====================================================#

def send_buzzer_alert_to_esp32():
    """
    Fungsi untuk mengirimkan peringatan ke ESP32 melalui HTTP POST.
    """
    
    esp32_url = "http://127.0.0.1:5000/api/getAlert"

    # Payload yang dikirim ke ESP32
    payload = {
        "alert": "Drowsiness detected",
        "timestamp": datetime.now().isoformat(),  # Mengirimkan waktu kejadian
    }

    try:
        # Kirim data ke ESP32
        response = requests.post(esp32_url, json=payload, timeout=5)
        response.raise_for_status()  # Periksa jika ada error
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"Error sending alert to ESP32: {e}")
        return None

def read_usernames_from_db():
    try:
        # Ambil semua username dari tabel User
        users = User.query.all()
        usernames = [user.username for user in users]  # Menyimpan username dalam list
        return usernames
    except Exception as e:
        print(f"Error reading usernames from database: {e}")
        return []


# ====================================================#
# Batas suci
# ====================================================#

# Fungsi untuk mendapatkan data akun dari database
def get_accounts():
    conn = sqlite3.connect('instance/users.db')  # Ganti dengan nama file database Anda
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM user")
    accounts = cursor.fetchall()
    conn.close()
    return [{"username": row[0]} for row in accounts]

@app.route('/accounts')
def accounts_list():
    accounts = get_accounts()
    print(accounts)  # Debugging: cetak akun yang diambil dari database
    return render_template('accounts.html', accounts=accounts)


@app.route('/monitor/<username>')
def monitor(username):
    # Logika untuk mengambil data monitoring berdasarkan username
    return render_template('monitor.html', username=username)

# Buat database jika belum ada
with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return redirect(url_for("login"))


# Rute Sign Up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        # Hash password untuk keamanan, hapus method='sha256'
        hashed_password = generate_password_hash(password)  # Tanpa menentukan metode

        # Cek jika username sudah ada
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose a different one.", "danger")
            return redirect(url_for("signup"))

        # Menjalankan pendaftaran wajah
        try:
            # Buat user baru
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash("Capturing face data. Please look at the camera.", "info")
            face_generator(
                user_id=new_user.id, user_username=new_user.username, detector=detector
            )  # Fungsi untuk menangkap gambar wajah
            flash("Face data successfully registered!", "success")

        except Exception as e:
            flash(f"An error occurred while processing face data: {e}", "danger")
            db.session.rollback()

        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


# Rute Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        # Validasi kredensial (ganti dengan logika autentikasi yang sesuai)
        if (username == "admin" and password == "password") or (
            user and check_password_hash(user.password, password)
        ):
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Username or password is incorrect", "danger")

    return render_template("login.html")


# Halaman Dashboard
@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("index.html")
    return redirect(url_for("login"))


# Halaman Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


# Endpoint untuk menerima data kecepatan dari web form
@app.route("/set_speed", methods=["POST"])
def set_speed():
    if "username" in session:  # Pastikan user login
        speed = request.form.get("speed")

        if not speed.isdigit() or int(speed) < 0 or int(speed) > 255:
            flash(
                "Invalid speed value. Please enter a value between 0 and 255.", "danger"
            )
            return redirect(url_for("dashboard"))

        # Simpan data kecepatan ke database (opsional, bisa juga langsung dikirim ke ESP32)
        db.session.execute(
            "INSERT INTO motor_speed (speed) VALUES (:speed)", {"speed": int(speed)}
        )
        db.session.commit()

        flash("Speed successfully updated!", "success")
        return redirect(url_for("dashboard"))
    else:
        return redirect(url_for("login"))


# Endpoint untuk ESP32 mengambil data kecepatan terbaru
@app.route("/api/get_speed", methods=["GET"])
def get_speed():
    # Ambil nilai kecepatan terbaru dari database
    result = db.session.execute(
        "SELECT speed FROM motor_speed ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if result:
        return {"speed": result["speed"]}
    else:
        return {"error": "No speed data available"}, 404


# @app.route('/upload_image/<int:user_id>', methods=['POST'])
# def upload_image(user_id):
#     # Cek apakah user_id valid
#     user = User.query.get(user_id)
#     if not user:
#         return jsonify({"error": "Invalid user ID"}), 400

#     # Simpan gambar
#     if 'file' not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files['file']
#     if file:
#         filename = secure_filename(f"face.{user_id}.{len(os.listdir(UPLOAD_FOLDER)) + 1}.jpg")
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(filepath)
#         return jsonify({"message": "Image uploaded successfully!", "file": filename})
#     else:
#         return jsonify({"error": "Invalid file"}), 400

if __name__ == "__main__":
    app.run(debug=True)
