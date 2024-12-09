import cv2
import os
import sqlite3
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox

class NewUserScreen(QWidget):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu  # Reference to main menu
        self.setWindowTitle("New User Registration")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        self.label = QLabel("Enter your details:")

        self.name_input = QLineEdit(self)
        self.name_input.setPlaceholderText("Enter your name")
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("Enter your email")

        self.select_images_button = QPushButton("Select Images")
        self.submit_button = QPushButton("Submit")
        self.back_button = QPushButton("Back")

        layout.addWidget(self.label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.select_images_button)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        
        self.select_images_button.clicked.connect(self.select_images)
        self.submit_button.clicked.connect(self.save_user_data)
        self.back_button.clicked.connect(self.go_back)

        self.selected_images = []

        # Create a connection to the SQLite database
        self.db_connection = sqlite3.connect("users.db")
        self.db_cursor = self.db_connection.cursor()

        # Create table for user data (if not exists)
        self.db_cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   name TEXT NOT NULL,
                                   email TEXT NOT NULL)''')
        self.db_connection.commit()

    def select_images(self):
        """Opens a file dialog to select multiple images."""
        options = QFileDialog.Options()
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)", options=options)
        if file_paths:
            self.selected_images.extend(file_paths)  

    def save_user_data(self):
        """Saves the user details and selected images."""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()

        if not name or not email:
            QMessageBox.warning(self, "Input Error", "Please enter all details (Name and Email).")
            return

        # Insert user details into the database
        try:
            self.db_cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            self.db_connection.commit()
            print(f"User {name} with email {email} saved to the database.")
        except sqlite3.Error as e:
            print(f"Error saving user to database: {e}")
            QMessageBox.warning(self, "Database Error", "Failed to save user data.")
            return

        # Create a folder for the user and save images
        user_folder = os.path.join("facial_recognition/dataset", name)
        os.makedirs(user_folder, exist_ok=True)
        
        for idx, image_path in enumerate(self.selected_images):
            if os.path.exists(image_path):
                _, ext = os.path.splitext(image_path)
                save_path = os.path.join(user_folder, f"{name}_{idx + 1}{ext}")
                image = cv2.imread(image_path)
                cv2.imwrite(save_path, image)
            else:
                print(f"File not found: {image_path}")

        # Fetch and print email for the saved name
        '''retrieved_email = self.get_email_for_name("jhfjghjj")
        if retrieved_email:
            QMessageBox.information(self, "Email Retrieved", f"Email for {name}: {retrieved_email}") '''
        
        self.selected_images.clear()
        self.go_back()

    def get_email_for_name(self, name):
        """Fetches the email address for a given name."""
        try:
            self.db_cursor.execute("SELECT email FROM users WHERE name=?", (name,))
            result = self.db_cursor.fetchone()
            if result:
                return result[0]  # Return the email if found
            else:
                QMessageBox.warning(self, "Not Found", f"No email found for user: {name}")
                return None
        except sqlite3.Error as e:
            print(f"Error fetching email from database: {e}")
            QMessageBox.warning(self, "Database Error", "Failed to retrieve email.")
            return None

    def go_back(self):
        """Return to the main menu."""
        self.hide()
        self.main_menu.show()

    def closeEvent(self, event):
        """Close the database connection when the window is closed."""
        self.db_connection.close()
        event.accept()
