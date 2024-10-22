import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QEvent
import cv2  # OpenCV for webcam functionality
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from calendar_utils import get_google_calendar_events

# Define SCOPES for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setGeometry(100, 100, 400, 200)
        
        layout = QVBoxLayout()

        self.label = QLabel("Choose an option:")
        self.new_user_button = QPushButton("New User")
        self.start_app_button = QPushButton("Start App")

        layout.addWidget(self.label)
        layout.addWidget(self.new_user_button)
        layout.addWidget(self.start_app_button)

        self.setLayout(layout)

        self.new_user_button.clicked.connect(self.open_new_user_screen)
        self.start_app_button.clicked.connect(self.open_start_app)

    def open_new_user_screen(self):
        self.hide()
        self.new_user_screen = NewUserScreen()
        self.new_user_screen.show()

    def open_start_app(self):
        self.hide()
        self.start_app_screen = StartAppScreen()
        self.start_app_screen.show()

    def closeEvent(self, event: QEvent):
        """Handle the close event to sign out the user."""
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')  # Delete the token file to sign out
        event.accept()  # Accept the event to close the window

class NewUserScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New User Registration")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        self.label = QLabel("Enter your details:")

        # Input fields for email and password
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter your email")
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)  # Hides the password input

        self.capture_button = QPushButton("Capture Image")
        self.submit_button = QPushButton("Submit")

        layout.addWidget(self.label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.capture_button)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

        self.capture_button.clicked.connect(self.capture_image)
        self.submit_button.clicked.connect(self.save_user_data)

    def capture_image(self):
        """Captures an image using the webcam and saves it."""
        cap = cv2.VideoCapture(0)  # Open webcam

        if not cap.isOpened():
            print("Cannot open camera")
            return
        
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture image")
        else:
            # Save the captured image
            cv2.imwrite('captured_image.jpg', frame)
            print("Image saved as captured_image.jpg")

        # Release the camera and close windows
        cap.release()
        cv2.destroyAllWindows()

    def save_user_data(self):
        """Saves the user email, password, and captured image to the user table, and returns to the main menu."""
        email = self.email_input.text()
        password = self.password_input.text()

        if email and password:
            # Here you would save the data to your database
            print(f"User registered with email: {email} and password: {password}")
            # Assuming captured_image.jpg is saved
            print("Image saved for user.")
            
            # Redirect to Main Menu after saving user data
            self.close()  # Close current window
            self.main_menu = MainMenu()  # Reopen main menu
            self.main_menu.show()  # Show the main menu window

        else:
            print("Please enter both email and password.")


class StartAppScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Start App")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        self.label = QLabel("Loading calendar events and identifying user...")
        self.event_list_widget = QLabel()
       
        layout.addWidget(self.label)
        layout.addWidget(self.event_list_widget)
        

        self.setLayout(layout)

        self.load_calendar_events()  # Load events when the screen is initialized
        
    def load_calendar_events(self):
        """Loads Google Calendar events."""
        try:
            # Re-authenticate the user and get calendar events
            events = get_google_calendar_events()  # Ensure this function is defined
            self.identify_user(events)
        except Exception as e:
            self.event_list_widget.setText(f"Error loading events: {str(e)}")

    def identify_user(self, events):
        """Simulates user identification and displays calendar events."""
        # You would add webcam-based user recognition here
        recognized = True  # Stub, replace with actual recognition logic
        if recognized:
            self.event_list_widget.setText("\n".join(events))
        else:
            self.event_list_widget.setText("User not recognized.")

    def authorize_new_account(self):
        """Force the user to log in with a new account by deleting the token and re-authenticating."""
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
        self.status_label.setText("Authorizing a new account...")
        get_google_calendar_events()
        self.status_label.setText("New account authorized!")

    def sign_out(self):
        """Sign out by deleting the stored token file."""
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
            self.event_list_widget.clear()
            self.status_label.setText("Signed out successfully! Please authorize a new account.")
        else:
            self.status_label.setText("No account is currently signed in.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())