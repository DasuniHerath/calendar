from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from calendar_utils import get_google_calendar_events

class StartAppScreen(QWidget):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu  # Reference to main menu
        self.setWindowTitle("Start App")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        self.label = QLabel("Loading calendar events and identifying user...")
        self.event_list_widget = QLabel()
        self.back_button = QPushButton("Back")  # Back button

        layout.addWidget(self.label)
        layout.addWidget(self.event_list_widget)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.back_button.clicked.connect(self.go_back)  # Connect back button
        self.load_calendar_events()  # Load events when the screen is initialized
        
    def load_calendar_events(self):
        """Loads Google Calendar events."""
        try:
            events = get_google_calendar_events()
            self.identify_user(events)
        except Exception as e:
            self.event_list_widget.setText(f"Error loading events: {str(e)}")

    def identify_user(self, events):
        """Simulates user identification and displays calendar events."""
        recognized = True  # Stub, replace with actual recognition logic
        if recognized:
            self.event_list_widget.setText("\n".join(events))
        else:
            self.event_list_widget.setText("User not recognized.")

    def go_back(self):
        """Return to the main menu."""
        self.hide()
        self.main_menu.show()
