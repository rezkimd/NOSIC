from flask import Flask, Response, jsonify, render_template, request
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import dlib
import cv2
import os
import time

from webcamvideostream import WebcamVideoStream

app = Flask(__name__)

# Load the facial landmark predictor and the face detector
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

def gen(camera):
    while True:
        if camera.stopped:
            break
        frame = camera.read()
        ret, jpeg = cv2.imencode(".jpg", frame)
        if jpeg is not None:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n\r\n"
            )
        else:
            print("frame is none")

# def eye_aspect_ratio(eye):
#     A = dist.euclidean(eye[1], eye[5])
#     B = dist.euclidean(eye[2], eye[4])
#     C = dist.euclidean(eye[0], eye[3])
#     ear = (A + B) / (2.0 * C)
#     return ear

# def lip_distance(shape):
#     top_lip = shape[50:53]
#     top_lip = np.concatenate((top_lip, shape[61:64]))
#     low_lip = shape[56:59]
#     low_lip = np.concatenate((low_lip, shape[65:68]))
#     top_mean = np.mean(top_lip, axis=0)
#     low_mean = np.mean(low_lip, axis=0)
#     distance = abs(top_mean[1] - low_mean[1])
#     return distance

# def generate_frames():
#     vs = VideoStream(src=0).start()  # Change '0' to your webcam index, if needed
#     time.sleep(1.0)  # Allow camera sensor to warm up
#     COUNTER = 0
#     EYE_AR_THRESH = 0.3
#     EYE_AR_CONSEC_FRAMES = 30
#     YAWN_THRESH = 20

#     while True:
#         frame = vs.read()
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         rects = detector.detectMultiScale(
#             frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
#         )

#         for x, y, w, h in rects:
#             rect = dlib.rectangle(int(x), int(y), int(x + w), int(y + h))
#             shape = predictor(frame, rect)
#             shape = face_utils.shape_to_np(shape)
#             ear = eye_aspect_ratio(
#                 shape[face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]]
#                 + shape[face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]]
#             )
#             distance = lip_distance(shape)

#             # Draw indicators based on analysis (optional visual feedback)
#             if ear < EYE_AR_THRESH:
#                 COUNTER += 1
#                 cv2.putText(
#                     frame,
#                     "DROWSINESS ALERT!",
#                     (10, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7,
#                     (0, 0, 255),
#                     2,
#                 )
#             else:
#                 COUNTER = 0

#             if distance > YAWN_THRESH:
#                 cv2.putText(
#                     frame,
#                     "Yawn Alert",
#                     (10, 60),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.7,
#                     (0, 0, 255),
#                     2,
#                 )

#             # Draw eyes and lips (optional)
#             cv2.drawContours(
#                 frame,
#                 [shape[face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]]],
#                 -1,
#                 (0, 255, 0),
#                 1,
#             )
#             cv2.drawContours(
#                 frame,
#                 [shape[face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]]],
#                 -1,
#                 (0, 255, 0),
#                 1,
#             )

#         # Encode the frame in JPEG format
#         ret, buffer = cv2.imencode(".jpg", frame)
#         frame = buffer.tobytes()

#         yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


# Sample data for user data
users_data = [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
]


@app.route("/")
def index():
    return app.send_static_file("index.html")


# feeding the frame with picture from camera
@app.route("/video_feed")
def video_feed():
    return Response(
        gen(WebcamVideoStream().start()),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    
# def video_feed():
#     return Response(
#         generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
#     )

@app.route('/api/update', methods=['POST'])
def update_status():
    data = request.get_json()
    image_url = data.get('image_url')
    status = data.get('status')
    alert = data.get('alert')
    
    global driver_status
    driver_status = {'image_url': image_url, 'status': status, 'alert': alert}
    
    return '', 200  # Respond with 200 OK

# Endpoint to provide the latest status
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify(driver_status)


@app.route("/api/userdata")
def get_user_data():
    return jsonify(users_data)


@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.json
    # Handle settings update logic here (save to a database, etc.)
    print("Settings received:", data)
    return jsonify({"status": "success", "message": "Settings updated!"})

# Run the server on port 3000
if __name__ == '__main__':
    app.run(port=3000)