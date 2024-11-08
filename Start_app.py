import pickle
import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap 
from calendar_utils import get_google_calendar_events
import face_recognition
import numpy as np

class StartAppScreen(QWidget):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu  # Reference to main menu
        self.setWindowTitle("Start App")
        self.setGeometry(100, 100, 640, 480)

        self.layout = QVBoxLayout()
        self.back_button = QPushButton("Back")  # Back button
        self.back_button.clicked.connect(self.go_back)  # Connect back button

        self.layout.addWidget(self.back_button)
        
        # QLabel to show the webcam feed
        self.video_feed_label = QLabel(self)
        self.layout.addWidget(self.video_feed_label)

        self.setLayout(self.layout)

        self.load_known_encodings()  # Load known encodings

        # Initialize webcam
        self.cap = cv2.VideoCapture(0)  # Start the webcam
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            return

        # Set up a timer for face recognition and video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_feed)
        self.timer.start(100)  # Update the feed every 100 ms

        self.recognized_user = None
        self.events = []
        self.load_calendar_events()  # Load events when the screen initializes

    def load_known_encodings(self):
        """Loads face encodings from the pickle file."""
        try:
            with open("encodings_face_recognition.pickle", "rb") as f:
                self.known_encodings = pickle.load(f)
                print("Encodings loaded successfully.")
        except FileNotFoundError:
            print("Error: Encodings file not found.")
            self.known_encodings = {"encodings": [], "names": []}
        except Exception as e:
            print(f"Error loading encodings: {e}")
            self.known_encodings = {"encodings": [], "names": []}

    def load_calendar_events(self):
        """Loads Google Calendar events and stores them."""
        try:
            self.events = get_google_calendar_events()
            print("Calendar events loaded.")
        except Exception as e:
            print(f"Error loading events: {str(e)}")

    def update_video_feed(self):
        """Updates the video feed and identifies the user."""
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to capture image from webcam.")
            return
        
        # Convert the frame from BGR to RGB for face_recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        recognized = False

        if face_encodings:
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(self.known_encodings["encodings"], face_encoding)
                if True in matches:
                    recognized = True
                    matched_idx = matches.index(True)
                    self.recognized_user = self.known_encodings["names"][matched_idx]
                    break

        # Prepare the overlay text
        overlay_text = ""
        if recognized and self.recognized_user:
            overlay_text = f"Hello, {self.recognized_user}!\nEvents:"
            if self.events:
                overlay_text += "\n" + "\n".join(self.events)
        else:
            overlay_text = "User not recognized."

        # Overlay text on the frame
        self.display_overlay(frame, overlay_text)

    def display_overlay(self, frame, text):
        """Displays overlay text on the captured frame and updates the QLabel."""
        # Convert frame to RGB for displaying in Qt
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.array(frame)

        # Draw the overlay text
        y0, dy = 50, 30  # Initial y position and line height
        for i, line in enumerate(text.split('\n')):
            cv2.putText(frame, line, (10, y0 + i * dy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Convert the frame to QImage and display in the QLabel
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.video_feed_label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        """Override closeEvent to release the webcam when closing the window."""
        if self.cap.isOpened():
            self.cap.release()
        event.accept()

    def go_back(self):
        """Return to the main menu."""
        self.hide()
        self.main_menu.show()

