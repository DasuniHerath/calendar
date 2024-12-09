import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from Screens.Add_new_user import NewUserScreen
from Screens.Start_app import StartAppScreen
from Screens.Train_model import TrainModelScreen  # Import Train Model Screen
import os
from PyQt5.QtCore import QEvent

class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()

        self.label = QLabel("Choose an option:")
        self.new_user_button = QPushButton("Add New User")
        self.train_model_button = QPushButton("Train The Model")
        self.start_app_button = QPushButton("Start App")

        layout.addWidget(self.label)
        layout.addWidget(self.new_user_button)
        layout.addWidget(self.train_model_button)
        layout.addWidget(self.start_app_button)

        self.setLayout(layout)

        self.new_user_button.clicked.connect(self.open_new_user_screen)
        self.train_model_button.clicked.connect(self.run_train_model)
        self.start_app_button.clicked.connect(self.open_start_app)

    def open_new_user_screen(self):
        self.hide()
        self.new_user_screen = NewUserScreen(self)
        self.new_user_screen.show()

    def open_start_app(self):
        self.hide()
        self.start_app_screen = StartAppScreen(self)
        self.start_app_screen.show()

    def run_train_model(self):
        self.hide()
        self.train_model_screen = TrainModelScreen(self)  # Open Train Model Screen
        self.train_model_screen.show()

    def closeEvent(self, event: QEvent):
        """Handle the close event to sign out the user."""
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')  # Delete the token file to sign out
        event.accept()  # Accept the event to close the window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
