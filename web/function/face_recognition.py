from include.imports import *

# Create a face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Generate a face recognition model
recognizer = cv2.face.LBPHFaceRecognizer_create()
# Function to capture images and store in dataset folder

def capture_images(User):
	# Create a directory to store the captured images
	if not os.path.exists('Faces'):
		os.makedirs('Faces')

	# Open the camera
	cap = cv2.VideoCapture(0)

	# Set the image counter as 0
	count = 0

	while True:
		# Read a frame from the camera
		ret, frame = cap.read()

		# Convert the frame to grayscale
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# Detect faces in the grayscale frame
		faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

		# Draw rectangles around the faces and store the images
		for (x, y, w, h) in faces:
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

			# Store the captured face images in the Faces folder
			cv2.imwrite(f'Faces/{User}_{count}.jpg', gray[y:y + h, x:x + w])

			count += 1

		# Display the frame with face detection
		cv2.imshow('Capture Faces', frame)

		# Break the loop if the 'q' key is pressed
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

		# Break the loop after capturing a certain number of images
		if count >= 1000:
			break

	# Release the camera and close windows
	cap.release()
	cv2.destroyAllWindows()

# Create the dataset of faces
capture_images('Salman')
