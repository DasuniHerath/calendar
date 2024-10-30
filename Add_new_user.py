import cv2
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox

class NewUserScreen(QWidget):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu  # Reference to main menu
        self.setWindowTitle("New User Registration")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        self.label = QLabel("Enter your details:")

        # Input fields for name, email, and password
        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter your name")
        #self.email_input = QLineEdit(self)
        #self.email_input.setPlaceholderText("Enter your email")
        #self.password_input = QLineEdit(self)
        #self.password_input.setPlaceholderText("Enter your password")
        #self.password_input.setEchoMode(QLineEdit.Password)  # Hides the password input

        # Buttons
        self.select_images_button = QPushButton("Select Images")
        #self.capture_button = QPushButton("Capture Image")
        self.submit_button = QPushButton("Submit")
        self.back_button = QPushButton("Back")  # Back button

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.name_input)
        #layout.addWidget(self.email_input)
        #layout.addWidget(self.password_input)
        layout.addWidget(self.select_images_button)
        #layout.addWidget(self.capture_button)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        # Connect buttons to their functions
        self.select_images_button.clicked.connect(self.select_images)
        #self.capture_button.clicked.connect(self.capture_image)
        self.submit_button.clicked.connect(self.save_user_data)
        self.back_button.clicked.connect(self.go_back)

        # List to hold selected image paths
        self.selected_images = []

    def select_images(self):
        """Opens a file dialog to select multiple images."""
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)", options=options)
        if file_paths:
            self.selected_images.extend(file_paths)  # Add selected images to the list
            #print(f"Selected images: {self.selected_images}")

    '''def capture_image(self):
        """Captures an image using the webcam and saves it temporarily."""
        cap = cv2.VideoCapture(0)  # Open webcam

        if not cap.isOpened():
            print("Cannot open camera")
            return
        
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture image")
        else:
            cv2.imwrite('captured_image.jpg', frame)
            self.selected_images.append('captured_image.jpg')  # Add captured image to selected images list
            print("Image saved as captured_image.jpg")

        cap.release()
        cv2.destroyAllWindows()'''

    def save_user_data(self):
        """Saves the user details and selected images."""
        name = self.name_input.text().strip()
        #email = self.email_input.text().strip()
        #password = self.password_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Input Error", "Please enter all details (Name).")
            return

        # Define the folder path based on the user's name
        user_folder = os.path.join("facial_recognition/dataset", name)

        # Create the folder if it doesn't exist
        os.makedirs(user_folder, exist_ok=True)

        # Save each selected image to the user's folder
        for idx, image_path in enumerate(self.selected_images):
            # Check if image exists
            if os.path.exists(image_path):
                # Save the image with a unique name in the user's folder
                _, ext = os.path.splitext(image_path)
                save_path = os.path.join(user_folder, f"{name}_{idx + 1}{ext}")
                image = cv2.imread(image_path)
                cv2.imwrite(save_path, image)
                #print(f"Saved image to: {save_path}")
            else:
                print(f"File not found: {image_path}")

        QMessageBox.information(self, "Success", f"User {name} registered successfully with images saved.")
        
        # Clear the selected images list after saving
        self.selected_images.clear()
        
        # Return to main menu
        self.go_back()

    def go_back(self):
        """Return to the main menu."""
        self.hide()
        self.main_menu.show()
