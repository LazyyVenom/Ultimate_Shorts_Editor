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
        self.label_video1 = QLabel("Video 1 Path:")
        layout.addWidget(self.label_video1)
        self.input_video1 = QLineEdit()
        layout.addWidget(self.input_video1)

        self.label_video2 = QLabel("Video 2 Path:")
        layout.addWidget(self.label_video2)
        self.input_video2 = QLineEdit()
        layout.addWidget(self.input_video2)

        self.label_audio = QLabel("Audio Path:")
        layout.addWidget(self.label_audio)
        self.input_audio = QLineEdit()
        layout.addWidget(self.input_audio)

        # Images section
        self.images_layout = QVBoxLayout()
        self.images = []  # List to store (image_path_input, timestamp_input, h_layout, remove_button)
        self.images_label = QLabel("Images (Path + Timestamp):")
        layout.addWidget(self.images_label)
        layout.addLayout(self.images_layout)

        btns_layout = QHBoxLayout()
        self.add_image_button = QPushButton("+")
        self.add_image_button.clicked.connect(self.add_image_input)
        btns_layout.addWidget(self.add_image_button)
        self.remove_image_button = QPushButton("-")
        self.remove_image_button.clicked.connect(self.remove_last_image_input)
        btns_layout.addWidget(self.remove_image_button)
        layout.addLayout(btns_layout)

        self.submit_button = QPushButton("Submit")
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.submit_button.clicked.connect(self.on_submit)

    def add_image_input(self):
        h_layout = QHBoxLayout()
        image_path_input = QLineEdit()
        image_path_input.setPlaceholderText("Image Path")
        timestamp_input = QLineEdit()
        timestamp_input.setPlaceholderText("Timestamp (s)")
        h_layout.addWidget(image_path_input)
        h_layout.addWidget(timestamp_input)
        self.images_layout.addLayout(h_layout)
        self.images.append((image_path_input, timestamp_input, h_layout))

    def remove_last_image_input(self):
        if self.images:
            _, _, h_layout = self.images.pop()
            # Remove all widgets from the layout
            while h_layout.count():
                item = h_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            self.images_layout.removeItem(h_layout)

    def on_submit(self):
        print("Video 1 Path:", self.input_video1.text())
        print("Video 2 Path:", self.input_video2.text())
        print("Audio Path:", self.input_audio.text())
        for idx, (img_input, ts_input, _) in enumerate(self.images):
            print(f"Image {idx+1} Path:", img_input.text(), "Timestamp:", ts_input.text())

    def display(self):
        return self.windowTitle()
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec_())