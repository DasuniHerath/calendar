import cv2
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QImage
from Screens.calendar_utils import get_google_calendar_events
from Models.face_verification import recognize_face, load_embeddings, match
import os
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class StartAppScreen(QWidget):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu  # Reference to main menu
        self.setWindowTitle("Start App")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        #self.label = QLabel("Loading calendar events and identifying user...")
        #self.event_list_widget = QLabel()
        self.camera_feed = QLabel("Initializing camera feed...")
        self.back_button = QPushButton("Back")  # Back button

        #layout.addWidget(self.label)
        #layout.addWidget(self.event_list_widget)
        layout.addWidget(self.camera_feed)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.back_button.clicked.connect(self.go_back)  # Connect back button

        self.cap = cv2.VideoCapture(0)  # Initialize webcam
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Failed to open webcam.")
        else:
            self.timer = QTimer(self)  # Timer to refresh the feed
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # Update every 30ms for ~30FPS

        # self.load_calendar_events()  # Load events when the screen is initialized

    '''def load_calendar_events(self):
        """Loads Google Calendar events."""
        try:
            events = get_google_calendar_events()
            self.identify_user(events)
        except Exception as e:
            self.event_list_widget.setText(f"Error loading events: {str(e)}")'''

    '''def identify_user(self, events):
        """Simulates user identification and displays calendar events."""
        recognized = True  # Stub, replace with actual recognition logic
        if recognized:
            self.event_list_widget.setText("\n".join(events))
        else:
            self.event_list_widget.setText("User not recognized.")'''

    def update_frame(self):
        #self.fetch_events()
        """Updates the QLabel with the current frame from the webcam."""
        ret, image = self.cap.read()
        if ret:
            # Perform face detection and recognition
            directory = 'facial_recognition'
            weights = os.path.join(directory, "models", "face_detection_yunet_2023mar.onnx")
            face_detector = cv2.FaceDetectorYN_create(weights, "", (0, 0))
            face_detector.setScoreThreshold(0.87)
            weights = os.path.join(directory, "models", "face_recognizer_fast.onnx")
            face_recognizer = cv2.FaceRecognizerSF_create(weights, "")
            embeddings_file = "embeddings.pickle"
            dictionary = load_embeddings(embeddings_file)

            features, faces = recognize_face(image, face_detector, face_recognizer)
            for idx, (face, feature) in enumerate(zip(faces, features)):
                result, user = match(face_recognizer, feature, dictionary)
                box = list(map(int, face[:4]))
                color = (0, 255, 0) if result else (0, 0, 255)
                thickness = 2
                cv2.rectangle(image, box, color, thickness, cv2.LINE_AA)

                id_name, score = user if result else (f"unknown_{idx}", 0.0)
                #text = "Hello {0} ({1:.2f})".format(id_name, score)
                text = "Hello {}".format(id_name)
                position = (box[0], box[1] - 10)
                font = cv2.FONT_HERSHEY_SIMPLEX
                scale = 0.6
                cv2.putText(image, text, position, font, scale, color, thickness, cv2.LINE_AA)

            # Convert the OpenCV frame (BGR) to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

            # Update the QLabel with the frame
            self.camera_feed.setPixmap(QPixmap.fromImage(q_image))
            self.camera_feed.setScaledContents(True)
        else:
            self.camera_feed.setText("Failed to capture frame.")

    def fetch_events(self):
        #email = self.email_input.text().strip()
        email = "malkarath0@gmail.com"
        if not email:
            QMessageBox.warning(self, "Input Error", "Please enter an email address.")
            return
        
        try:
            events = self.get_calendar_events(email)
            if events:
                #self.events_display.setText("\n".join(events))
                print(events)
            else:
                self.events_display.setText("No upcoming events found.")
        except Exception as e:
            QMessageBox.warning(self, "API Error", f"Failed to fetch events: {str(e)}")

    def get_calendar_events(self, email):
        """Fetches calendar events for the given email."""
        creds = None
        token_path = 'token.pickle'

        # Clear the existing token to force re-authentication
        if os.path.exists(token_path):
            os.remove(token_path)

        # Now proceed with OAuth authentication again
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        # Build the Google Calendar service
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = '2024-12-04T00:00:00Z'  # You can replace with the current date or another format
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        event_list = []
        if not events:
            return None

        for event in events:
            event_summary = event.get('summary')
            event_start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
            event_list.append(f"{event_summary} at {event_start}")

        return event_list
    
    def go_back(self):
        """Return to the main menu."""
        self.timer.stop()  # Stop the timer
        self.cap.release()  # Release the webcam
        self.hide()
        self.main_menu.show()

    def closeEvent(self, event):
        """Ensure resources are cleaned up on close."""
        if self.cap.isOpened():
            self.timer.stop()
            self.cap.release()
        event.accept()
