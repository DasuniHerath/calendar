import os
import pickle
import cv2
import face_recognition
from imutils import paths
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
from Models.face_verification import save_embeddings, load_embeddings, recognize_face

class TrainModelScreen(QWidget):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu  # Reference to main menu
        self.setWindowTitle("Train Model")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        # Label and buttons
        self.label = QLabel("Train Model - Generate Embeddings")
        self.start_encoding_button = QPushButton("Start Train")
        self.back_button = QPushButton("Back")

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.start_encoding_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        # Connect buttons to their functions
        self.start_encoding_button.clicked.connect(self.generate_encodings)
        self.back_button.clicked.connect(self.go_back)

    '''def generate_encodings(self):
        """Generates face encodings from images in the dataset."""
        dataset_path = "facial_recognition/dataset"
        image_paths = list(paths.list_images(dataset_path))
        known_encodings = []
        known_names = []

        # Process each image in the dataset
        for (i, image_path) in enumerate(image_paths):
            print(f"[INFO] Processing image {i + 1}/{len(image_paths)}")
            name = image_path.split(os.path.sep)[-2]

            # Load image and check if it's valid
            image = cv2.imread(image_path)
            if image is None:
                print(f"[WARNING] Could not read image {image_path}. Skipping...")
                continue

            # Verify the image is 8-bit and has 3 color channels (RGB)
            if image.dtype != "uint8" or len(image.shape) != 3 or image.shape[2] != 3:
                print(f"[WARNING] Image {image_path} is not a valid 8-bit RGB image. Skipping...")
                continue

            # Convert to RGB
            try:
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            except Exception as e:
                print(f"[ERROR] Could not process image {image_path}: {e}")
                continue

            # Detect face locations and generate encodings
            try:
                boxes = face_recognition.face_locations(rgb, model="hog")
                encodings = face_recognition.face_encodings(rgb, boxes)
            except Exception as e:
                print(f"[ERROR] Failed to generate encoding for {image_path}: {e}")
                continue

            # Save each encoding with the corresponding name
            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(name)

        # Save encodings and names to a file
        print("[INFO] Serializing encodings...")
        data = {"encodings": known_encodings, "names": known_names}
        with open("encodings_face_recognition.pickle", "wb") as f:
            f.write(pickle.dumps(data))

        # Show completion message
        QMessageBox.information(self, "Encoding Complete", "Face encoding generation is complete!") '''
    
    def generate_encodings(self):
        directory = 'facial_recognition'
        weights = os.path.join(directory, "models",
                            "face_detection_yunet_2023mar.onnx")
        face_detector = cv2.FaceDetectorYN_create(weights, "", (0, 0))
        face_detector.setScoreThreshold(0.87)

        weights = os.path.join(directory, "models", "face_recognizer_fast.onnx")
        face_recognizer = cv2.FaceRecognizerSF_create(weights, "")

        embeddings_file = "embeddings.pickle"
        # Load existing embeddings or create new ones
        dictionary = load_embeddings(embeddings_file)
        if not dictionary:
            # Traverse subdirectories to get images with user IDs from subfolder names
            for subdir, _, files_in_subdir in os.walk(os.path.join(directory, 'dataset')):
                user_id = os.path.basename(subdir)
                if not files_in_subdir:
                    continue

                for file_name in files_in_subdir:
                    if file_name.lower().endswith(('.jpg', '.png', '.jpeg')):
                        file_path = os.path.join(subdir, file_name)
                        image = cv2.imread(file_path)
                        feats, faces = recognize_face(image, face_detector, face_recognizer, file_path)
                        if faces is None:
                            continue

                        # Store features for the user ID
                        if user_id not in dictionary:
                            dictionary[user_id] = feats[0]
                        else:
                            # You can average features if there are multiple images per ID
                            dictionary[user_id] = np.mean([dictionary[user_id], feats[0]], axis=0)

            print(f'There are {len(dictionary)} IDs.')
            save_embeddings(dictionary, embeddings_file)

    def go_back(self):
        """Return to the main menu."""
        self.hide()
        self.main_menu.show()
