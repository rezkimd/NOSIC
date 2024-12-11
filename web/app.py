from include.imports import *

app = Flask(__name__)

# Konfigurasi database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "your_secret_key"  # Ganti dengan kunci rahasia yang kuat

db = SQLAlchemy(app)

# Inisiasi Model
detector = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)  # Faster but less accurate
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Membuat object video stream
ap = argparse.ArgumentParser()
ap.add_argument("-w", "--webcam", type=int, default=0, help="index of webcam on system")
args = vars(ap.parse_args())
# vs = VideoStream(src=args["webcam"])

# Inisialisasi VideoStreamManager
video_stream_manager = VideoStreamManager(src=0, detector=detector, predictor=predictor)


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


@app.route("/speed/<int:speed>", methods=["POST", "GET"])
def set_speed(speed):
    """
    Endpoint untuk mengatur nilai kecepatan motor.
    """
    global current_speed
    current_speed = speed  # Set nilai kecepatan
    return (
        jsonify({"status": "success", "message": f"Speed updated to {current_speed}"}),
        200,
    )


@app.route("/api/getAlert", methods=["GET"])
def get_alert():
    """
    Endpoint untuk mengambil nilai speed dan alert.
    """
    alert_message = "Speed dikurangi" if current_speed > 150 else "Speed normal"
    response_data = {"speed": current_speed, "alert": alert_message}
    return jsonify(response_data), 200


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
    conn = sqlite3.connect("instance/users.db")  # Ganti dengan nama file database Anda
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM user")
    accounts = cursor.fetchall()
    conn.close()
    return [{"username": row[0]} for row in accounts]


@app.route("/accounts")
def accounts_list():
    conn = sqlite3.connect("instance/users.db")  # Ganti dengan nama file database Anda
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM user")
    accounts = [{"username": row[0]} for row in cursor.fetchall()]
    conn.close()
    print(accounts)  # Debugging: cetak akun yang diambil dari database

    return render_template("accounts.html", accounts=accounts)



@app.route("/monitor")
def monitor():
    username = session.get('username')  # Ambil username dari session
    if not username:
        # Jika pengguna tidak login, arahkan ke halaman login
        return redirect(url_for('login'))
    # Logika untuk mengambil data monitoring berdasarkan username
    return render_template("monitor.html", username=username)


@app.route("/start_video_feed", methods=["POST"])
def start_video_feed():
    if not video_stream_manager.is_running():
        video_stream_manager.start()
        # Mulai thread untuk drowsiness detection
        Thread(target=video_stream_manager.drowsiness_detector, daemon=True).start()
    return "", 204  # No Content


@app.route("/stop_video_feed", methods=["POST"])
def stop_video_feed():
    video_stream_manager.stop()
    return "", 204  # No Content


@app.route("/video_feed")
def video_feed():
    if not video_stream_manager.is_running():
        return "Video stream is not running", 400  # Bad Request
    return Response(
        start_video_feed(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


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
        session['username'] = username

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


@app.route('/logout')
def logout():
    session.pop('username', None)  # Hapus username dari session
    return redirect(url_for('login'))


# # Endpoint untuk menerima data kecepatan dari web form
# @app.route("/set_speed", methods=["POST"])
# def set_speed():
#     if "username" in session:  # Pastikan user login
#         speed = request.form.get("speed")

#         if not speed.isdigit() or int(speed) < 0 or int(speed) > 255:
#             flash(
#                 "Invalid speed value. Please enter a value between 0 and 255.", "danger"
#             )
#             return redirect(url_for("dashboard"))

#         # Simpan data kecepatan ke database (opsional, bisa juga langsung dikirim ke ESP32)
#         db.session.execute(
#             "INSERT INTO motor_speed (speed) VALUES (:speed)", {"speed": int(speed)}
#         )
#         db.session.commit()

#         flash("Speed successfully updated!", "success")
#         return redirect(url_for("dashboard"))
#     else:
#         return redirect(url_for("login"))


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
