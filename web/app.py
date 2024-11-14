from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan kunci rahasia yang kuat

# Rute Default
@app.route('/')
def home():
    return redirect(url_for('login'))

# Halaman Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validasi kredensial (ganti dengan logika autentikasi yang sesuai)
        if username == 'admin' and password == 'password':
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Username or password is incorrect', 'danger')

    return render_template('login.html')

# Halaman Dashboard
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('index.html')  # Pastikan nama file sesuai
    return redirect(url_for('login'))

# Halaman Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
