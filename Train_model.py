import os
import pickle
import cv2
import face_recognition
from imutils import paths
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox

class TrainModelScreen(QWidget):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu  # Reference to main menu
        self.setWindowTitle("Train Model")
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()
        
        # Label and buttons
        self.label = QLabel("Train Model - Generate Encodings")
        self.start_encoding_button = QPushButton("Start Encoding")
        self.back_button = QPushButton("Back")

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.start_encoding_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        # Connect buttons to their functions
        self.start_encoding_button.clicked.connect(self.generate_encodings)
        self.back_button.clicked.connect(self.go_back)

    def generate_encodings(self):
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
        QMessageBox.information(self, "Encoding Complete", "Face encoding generation is complete!")


    def go_back(self):
        """Return to the main menu."""
        self.hide()
        self.main_menu.show()
