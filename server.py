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

@app.route("/")
def index():
    # return app.send_static_file("index.html")
    return render_template("index.html")


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


@app.route("/api/update", methods=["POST"])
def update_status():
    data = request.get_json()
    image_url = data.get("image_url")
    status = data.get("status")
    alert = data.get("alert")

    global driver_status
    driver_status = {"image_url": image_url, "status": status, "alert": alert}

    return "", 200  # Respond with 200 OK


# Endpoint to provide the latest status
@app.route("/api/status", methods=["GET"])
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
if __name__ == "__main__":
    app.run(port=3000)
