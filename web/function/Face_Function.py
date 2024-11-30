"""
    Requirements
    python 3.7.7
    numpy==1.21.6
    opencv-contrib-python==4.1.2.30
    Pillow==9.5.0
"""

import sys
import time
import os
import numpy as np
from PIL import Image
import cv2
from sqlalchemy.orm.exc import NoResultFound
from flask import flash

# Adjust the COM port and baud rate according to your setup
# COM_PORT = 'COM3'  # Replace with your ESP32's COM port
# BAUD_RATE = 115200
# TIMEOUT = 1  # Timeout for reading from the serial port

# esp32_serial = serial.Serial(COM_PORT, BAUD_RATE, timeout=TIMEOUT)

path = "user_image"
name = ""
if not os.path.exists("user_image"):
    os.mkdir("user_image")

# def get_face_id_and_username():
#     try:
#         # Query all users
#         users = User.query.all()

#         # List to store the results
#         result = []
#         for user in users:
#             result.append({"face_id": user.id, "username": user.username})

#         return result
#     except NoResultFound:
#         print("No users found in the database.")
#         return []

# def get_unique_face_id():
#     """
#     Generate a unique face_id by finding the next available ID in the database.
#     """
#     try:
#         # Ambil semua face_id yang ada di database
#         existing_face_ids = [user.id for user in User.query.all()]

#         # Mulai dari ID 1, cari ID yang belum digunakan
#         new_face_id = 1
#         while new_face_id in existing_face_ids:
#             new_face_id += 1

#         return new_face_id
#     except Exception as e:
#         print(f"Error generating unique face_id: {e}")
#         return None


# def read_names_from_database():
#     """
#     Fetch names (usernames) from the database and return them as a list.
#     """
#     try:
#         # Query usernames from the database
#         users = User.query.all()

#         # Extract usernames into a list
#         names = [user.username for user in users]

#         return names
#     except Exception as e:
#         print(f"Error reading names from database: {e}")
#         return []


def training_data(id, username):
    # used to recognize faces in images and videos
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # creates an instance of a face detection classifier using the Haar Cascade classifier
    # pre-trained model for detecting faces in images
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def Images_And_Labels(path):
        imagesPaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []

        for imagePath in imagesPaths:
            gray_image = Image.open(imagePath).convert("L")  # convert to grayscale
            img_arr = np.array(gray_image, "uint8")  # creating array

            # detects faces in the image using the face detection classifier
            faces = detector.detectMultiScale(img_arr)

            for x, y, w, h in faces:
                faceSamples.append(img_arr[y : y + h, x : x + w])
                ids.append(id)
        return faceSamples, ids

    print("Training Data...please wait...!!!")
    faces, ids = Images_And_Labels(path)

    # trains the face recognizer using the loaded face data (faces) and labels (ids).
    recognizer.train(faces, np.array(ids))
    # saves the trained recognizer to a YAML file called 'trained_data.yml'.
    recognizer.write("trained_data.yml")

    flash("Image train completed !!!!.")


def face_generator(user_id, user_username):

    # Folder menyimpan data wajah
    save_dir = "user_image"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    cam = cv2.VideoCapture(0)  # used to create video which is used to capture images
    cam.set(3, 640)
    cam.set(4, 480)
    if not cam.isOpened():
        print("Error: Kamera tidak dapat dibuka!")
        return

    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    if detector.empty():
        print("Error: File Haar Cascade tidak ditemukan!")
        return

    print("taking sample image of user ...please look at camera")
    # this file is used to detect a object in an image
    count = 0

    while True:
        sample = 20
        ret, img = cam.read()  # read the frames using above created objects
        if not ret:
            print("Error: Gagal membaca frame dari kamera.")
            break

        converted_image = cv2.cvtColor(
            img, cv2.COLOR_BGR2GRAY
        )  # converts image to black and white
        faces = detector.detectMultiScale(
            converted_image, 1.3, 5
        )  # detect face in image
        if len(faces) == 0:
            print("Tidak ada wajah yang terdeteksi. Pastikan wajah terlihat di kamera.")
            continue

        for x, y, w, h in faces:

            cv2.rectangle(
                img, (x, y), (x + w, y + h), (255, 0, 0), 2
            )  # creates frame around face
            count += 1
            # print(count)

            # Save the detected face to the list
            face_image = converted_image[y : y + h, x : x + w]
            file_path = os.path.join(save_dir, f"{user_username}.{user_id}.{count}.jpg")
            cv2.imwrite(file_path, face_image)
            print(f"Gambar {count} disimpan di {file_path}")

            # Stop capturing if we have enough samples
            if count >= sample:
                print("Sampel gambar selesai diambil!")
                cam.release()
                cv2.destroyAllWindows()
                break

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

    flash("Image Samples taken succefully !!!!.")

    try:
        # Inisialisasi recognizer
        recognizer = cv2.face.LBPHFaceRecognizer()
        if recognizer.empty():
            raise Exception(
                "Recognizer tidak dapat dibuat. Periksa instalasi OpenCV Anda."
            )

        # Inisialisasi detektor
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        if detector.empty():
            raise Exception("File Haar Cascade tidak ditemukan atau tidak valid.")

        def Images_And_Labels(path):
            try:
                # Mendapatkan semua path gambar di direktori
                imagesPaths = [os.path.join(path, f) for f in os.listdir(path)]
                if not imagesPaths:
                    raise FileNotFoundError(
                        f"Tidak ada file gambar di direktori: {path}"
                    )

                faceSamples = []
                ids = []

                for imagePath in imagesPaths:
                    gray_image = Image.open(imagePath).convert(
                        "L"
                    )  # Konversi ke grayscale
                    img_arr = np.array(gray_image, "uint8")  # Membuat array

                    # Deteksi wajah di gambar
                    faces = detector.detectMultiScale(img_arr)
                    if len(faces) == 0:
                        print(f"Tidak ada wajah yang terdeteksi pada file: {imagePath}")
                        continue

                    # Ekstrak ID dari nama file
                    try:
                        id = int(os.path.split(imagePath)[-1].split(".")[1])
                    except ValueError:
                        print(f"ID tidak valid pada file: {imagePath}")
                        continue

                    # Menambahkan wajah dan ID ke daftar
                    for x, y, w, h in faces:
                        faceSamples.append(img_arr[y : y + h, x : x + w])
                        ids.append(id)

                if not faceSamples or not ids:
                    raise Exception(
                        "Tidak ada wajah yang valid ditemukan untuk training."
                    )

                return faceSamples, ids

            except Exception as e:
                raise Exception(f"Error saat membaca data wajah: {e}")

        # Proses membaca data dan melatih model
        print("Training Data...please wait...!!!")
        faces, ids = Images_And_Labels(path)

        recognizer.train(faces, np.array(ids))
        recognizer.write("trained_data.yml")
        flash("Data train success !!!!.")
        print("Training selesai dan data disimpan sebagai 'trained_data.yml'.")

    except FileNotFoundError as fnfe:
        print(f"File atau direktori tidak ditemukan: {fnfe}")
        flash(f"Error: {fnfe}")

    except Exception as e:
        print(f"Terjadi kesalahan: {e}")
        flash(f"Error: {e}")


def detection(username_name):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("trained_data.yml")  # loaded trained model
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX  # denotes fonts size

    # id = 3  # number of persons your want to recognize
    # Read names from file
    names = username_name
    cam = cv2.VideoCapture(0)  # used to create video which is used to capture images
    cam.set(3, 640)
    cam.set(4, 480)

    # define min window size to be recognize as a face
    minW = 0.1 * cam.get(3)
    maxW = 0.1 * cam.get(4)

    unrecognized_time_start = time.time()  # Start time for unrecognized timer
    recognized = False

    while True:
        if cam is None or not cam.isOpened():
            print("Warning: unable to open video source: ")

        ret, img = cam.read()  # read the frames using above created objects
        if ret == False:
            print("unable to detect img")
        converted_image = cv2.cvtColor(
            img, cv2.COLOR_BGR2GRAY
        )  # converts image to black and white

        faces = faceCascade.detectMultiScale(
            converted_image,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minW)),
        )

        cv2.imshow("Camera", img)
        k = cv2.waitKey(10) & 0xFF
        if k == 27:  # Press 'Esc' to exit
            break

        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            id, accuracy = recognizer.predict(converted_image[y : y + h, x : x + w])
            cv2.imshow("camera", img)
            k = cv2.waitKey(10) & 0xFF
            if k == 27:
                break
            # Check if the id is within the valid range
            # Check if the id is within the valid range
            if 0 <= id < len(names):  # Ensure the id is valid
                name = names[id]  # Get the name corresponding to the id
                accuracy_text = f"{round(100 - accuracy)}%"
                recognized = True

                # Display text on image
                cv2.putText(
                    img, f"Hello, {name}", (x + 5, y - 5), font, 1, (255, 0, 255), 2
                )
                cv2.putText(
                    img,
                    f"{accuracy_text}",
                    (x + 5, y + h - 5),
                    font,
                    1,
                    (255, 255, 0),
                    1,
                )

                # Close after recognizing
                # esp32_serial.write(("Hello, Master").encode('utf-8'))
                time.sleep(10)  # Optional: delay for a couple of seconds before closing
                cam.release()
                cv2.destroyAllWindows()
                return

        # Check if the face remains unrecognized for 10 seconds
        if not recognized and time.time() - unrecognized_time_start >= 10:
            print("Face not recognized for 10 seconds, closing...")
            # esp32_serial.write(("Not recognized").encode('utf-8'))
            time.sleep(10)  # Optional: delay for a couple of seconds before closing
            cam.release()
            cv2.destroyAllWindows()
            return


def main_menu():
    print("\t\t\t ##### Welcome to Face Authentication System #####")
    print("Please choose an option:")
    print("1. Capture images for a new user")
    print("2. Train data for face authentication")
    print("3. Test face authentication")
    print("4. Exit")

    choice = input("Enter the number of your choice: ")

    if choice == "1":
        face_generator()
    elif choice == "2":
        training_data()
    elif choice == "3":
        detection()
    elif choice == "4":
        print("Thank you for using this application! Goodbye!")
        sys.exit()
    else:
        print("Invalid choice, please try again.")
        main_menu()


# Start the application by showing the main menu
# main_menu()

# communicate()
