from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
import sys


class UI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultimate Shorts Editor")
        self.setGeometry(100, 100, 300, 150)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Enter text:")
        layout.addWidget(self.label)

        self.text_input = QLineEdit()
        layout.addWidget(self.text_input)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.submit_button.clicked.connect(self.on_submit)

    def on_submit(self):
        # Example: print the entered text to the console
        print(self.text_input.text())

    def display(self):
        return self.windowTitle()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())