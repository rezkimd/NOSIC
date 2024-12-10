# Core Python Libraries
import sys               # Mengelola input/output dan manipulasi sistem
import time              # Untuk operasi terkait waktu
import os                # Mengelola operasi sistem file
from datetime import datetime, date  # Mengelola waktu dan tanggal

# Flask Libraries (Web Framework)
from flask import (
    Flask,              # Membuat aplikasi Flask
    Response,           # Membuat respons HTTP
    render_template,    # Merender template HTML
    request,            # Mendapatkan data dari HTTP request
    redirect,           # Redirect ke URL lain
    url_for,            # Membuat URL dinamis
    flash,              # Menampilkan pesan sementara kepada pengguna
    session,            # Mengelola sesi pengguna
    jsonify             # Mengembalikan data dalam format JSON
)
from flask_sqlalchemy import SQLAlchemy  # ORM untuk berinteraksi dengan database

# Flask Security
from werkzeug.security import (
    generate_password_hash,  # Hash password untuk keamanan
    check_password_hash      # Memeriksa kecocokan hash password
)

# OpenCV (Computer Vision)
import cv2                   # Framework utama untuk operasi computer vision
import cv2.data              # Akses data bawaan OpenCV (seperti file xml untuk haarcascade)
import cv2.face              # Ekstensi OpenCV untuk operasi pengenalan wajah (seperti LBPH)

# Image Processing
from PIL import Image         # Pemrosesan gambar

# NumPy (Numerical Operations)
import numpy as np            # Operasi numerik berbasis array

# Dlib (Machine Learning and Computer Vision)
import dlib                  # Deteksi wajah dan landmarks

# Imutils (Image Utilities)
import imutils
from imutils import face_utils  # Utilitas untuk pengolahan wajah
from imutils.video import VideoStream  # Streaming video secara efisien

# Scipy (Scientific Computation)
from scipy.spatial import distance as dist  # Penghitungan jarak spasial (digunakan untuk EAR)

# Threading
from threading import Thread  # Menjalankan proses paralel

# Argument Parsing
import argparse               # Parsing argumen dari command line

# HTTP Requests
import requests               # Mengirim HTTP request (GET, POST, dll.)

# Database Interaction
import sqlite3                # Berinteraksi dengan database SQLite
from sqlalchemy.orm.exc import NoResultFound  # Exception handling untuk query SQLAlchemy

# Application-Specific Modules
from function.face_function import face_generator  # Fungsi khusus untuk face generation
from function.drowsiness_yawn import VideoStreamManager # Fungsi untuk deteksi kantuk/menguap
