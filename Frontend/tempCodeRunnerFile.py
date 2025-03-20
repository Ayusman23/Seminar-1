from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtGui import QScreen

# Ensure ChatSection is defined
class ChatSection(QWidget):  
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: gray;")  # Example styling

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Get screen dimensions using Qt's recommended approach
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()

        # Create layout
        layout = QVBoxLayout()
        
        # Empty label (consider setting some text if needed)
        label = QLabel("")
        layout.addWidget(label)

        # Chat section widget
        chat_section = ChatSection()
        layout.addWidget(chat_section)

        # Set layout
        self.setLayout(layout)

        # Styling
        self.setStyleSheet("background-color: black;")

        # Set window to fullscreen without making it fixed-size
        self.setGeometry(0, 0, screen_width, screen_height)

# Example usage
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MessageScreen()
    window.show()
    sys.exit(app.exec_())
