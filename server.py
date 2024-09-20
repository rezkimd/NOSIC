from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64

app = Flask(__name__)
socketio = SocketIO(app)

# Camera stream using OpenCV
def get_frame():
    cap = cv2.VideoCapture(0)  # Change the index if you want another camera
    while True:
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            socketio.emit('camera_frame', {'image': frame_base64})
        socketio.sleep(0.1)  # Control frame rate

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.start_background_task(get_frame)

if __name__ == '__main__':
    socketio.run(app)