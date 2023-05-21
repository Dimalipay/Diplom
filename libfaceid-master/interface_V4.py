import subprocess
from subprocess import Popen, PIPE
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QFrame, QListWidget, QListWidgetItem, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QIcon
import shutil
import os

class GUI(QMainWindow):
    def __init__(self):
        super(GUI, self).__init__()

        self.agegenderemotion_process =

        # Set window icon
        self.setWindowIcon(QIcon('images/logo_1.ico'))

        # Set window size
        self.setGeometry(0, 0, 900, 650)
        self.setWindowTitle("SmartVision")

        # Lock the size of the window
        self.setFixedSize(900, 650)

        # Set directory for images and videos
        self.input_dir = "Input/"
        self.source_dir = "Source/"
        self.index = 1

        # Load and display the background image
        self.bg_label = QLabel(self)
        bg_pixmap = QPixmap("images/geometric-dark-bg.jpg").scaled(self.width(), self.height(), Qt.IgnoreAspectRatio)
        self.bg_label.setPixmap(bg_pixmap)
        self.bg_label.setGeometry(0, 0, 900, 650)  # Ensure the label covers the entire window
        self.bg_label.lower()  # Ensure the background is below all other widgets

        # Load and display the logo image
        self.logo_label = QLabel(self)
        pixmap = QPixmap("images/logo_1.png").scaled(200, 200, Qt.KeepAspectRatio)  # Resize the QPixmap
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setGeometry(370, 10, 200, 200)

        # Create and place the buttons
        self.load_frame = QWidget(self)
        self.load_frame.setGeometry(360, 200, 220, 150)
        layout = QVBoxLayout(self.load_frame)
        layout.setSpacing(10)  # Set equal spacing between widgets

        self.image_button = QPushButton("Загрузить изображение", self.load_frame)
        self.image_button.setFixedHeight(40)  # Set fixed height for the buttons
        self.image_button.setMinimumWidth(150)  # Set minimum width for the buttons
        self.image_button.clicked.connect(self.load_image)
        layout.addWidget(self.image_button)

        self.video_button = QPushButton("Загрузить видео", self.load_frame)
        self.video_button.setFixedHeight(40)  # Set fixed height for the buttons
        self.video_button.setMinimumWidth(150)  # Set minimum width for the buttons
        self.video_button.clicked.connect(self.load_video)
        layout.addWidget(self.video_button)

        # Add buttons for emotion recognition, age recognition, object detection, and object detection (video)
        self.action_frame = QWidget(self)
        self.action_frame.setGeometry(360, 330, 220, 300)
        layout = QVBoxLayout(self.action_frame)
        layout.setSpacing(10)  # Set equal spacing between widgets

        self.emotion_button = QPushButton("Распознование", self.action_frame)
        self.emotion_button.setFixedHeight(40)  # Set fixed height for the buttons
        self.emotion_button.setMinimumWidth(150)  # Set minimum width for the buttons
        self.emotion_button.clicked.connect(self.run_emotion_recognition)
        layout.addWidget(self.emotion_button)

        self.object_button = QPushButton("Распознование объектов", self.action_frame)
        self.object_button.setFixedHeight(40)  # Set fixed height for the buttons
        self.object_button.setMinimumWidth(150)  # Set minimum width for the buttons
        self.object_button.clicked.connect(self.display_image_list)
        layout.addWidget(self.object_button)

        self.object_video_button = QPushButton("Распознование объектов (Видео)", self.action_frame)
        self.object_video_button.setFixedHeight(40)  # Set fixed height for the buttons
        self.object_video_button.setMinimumWidth(150)  # Set minimum width for the buttons
        self.object_video_button.clicked.connect(self.display_video_list)
        layout.addWidget(self.object_video_button)

        # Add new buttons
        self.new_user_button = QPushButton("Проверка пользователя", self.action_frame)
        self.new_user_button.setFixedHeight(40)  # Set fixed height for the buttons
        self.new_user_button.setMinimumWidth(150)  # Set minimum width for the buttons
        self.new_user_button.clicked.connect(self.run_classifier)
        layout.addWidget(self.new_user_button)

        # Create image and video display
        self.image_display = QLabel(self)
        self.image_display.setGeometry(100, 100, 200, 200)

        self.video_display = QLabel(self)
        self.video_display.setGeometry(100, 100, 200, 200)

        self.show()

    def load_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, 'Open file', self.source_dir)
        # Copy image to Input folder and rename
        if image_path:
            filename, ext = os.path.splitext(image_path)
            new_filename = f"test_{self.index}{ext}"
            dest_path = os.path.join(self.input_dir, new_filename)
            shutil.copy(image_path, dest_path)
            # Increment index
            self.index += 1

    def load_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, 'Open file')
        # Copy video to Input folder and rename
        if video_path:
            filename, ext = os.path.splitext(video_path)
            new_filename = f"test_{self.index}{ext}"
            dest_path = os.path.join(self.input_dir, new_filename)
            shutil.copy(video_path, dest_path)
            # Increment index
            self.index += 1

    def display_image_list(self):
        # Get list of images from input directory
        image_list = [f for f in os.listdir(self.input_dir) if
                      f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))]

        # Display list in dialog box
        if image_list:
            self.dialog = QListWidget()  # Keep a reference to the dialog box in the GUI instance
            self.dialog.setWindowTitle("Выберите изображение для распознования")
            self.dialog.addItems(image_list)
            self.dialog.itemClicked.connect(self.run_object_detection)
            self.dialog.show()

        else:
            QMessageBox.warning(self, "No Images Found", "No images found in input directory.")

    def display_video_list(self):
        # Get list of videos from input directory
        video_list = [f for f in os.listdir(self.input_dir) if
                      f.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".flv"))]

        # Display list in dialog box
        if video_list:
            self.dialog = QListWidget()  # Keep a reference to the dialog box in the GUI instance
            self.dialog.setWindowTitle("Выберите видео для распознования")
            self.dialog.addItems(video_list)
            self.dialog.itemClicked.connect(self.run_object_detection_video)
            self.dialog.show()
        else:
            QMessageBox.warning(self, "No Videos Found", "No videos found in input directory.")

    def run_object_detection(self, item):
        try:
            if hasattr(self, 'dialog') and self.dialog.isVisible():
                # Close the image selection window
                self.dialog.close()

            # Get image from the clicked item in the list
            image = item.text()

            # Set input image path from selected image in dropdown list
            input_image_path = os.path.join(self.input_dir, image)

            # Run object detection script with selected image
            output_path = os.path.join(self.input_dir, f"test_{self.index}_{image}")
            cmd = f'python object_detection.py --input "{input_image_path}" --output "{output_path}"'
            os.system(cmd)
            self.index += 1
        except  Exception as e:
            print(f"Error occurred: {e}")

    def run_object_detection_video(self, item):
        if hasattr(self, 'dialog') and self.dialog.isVisible():
            # Close the image selection window
            self.dialog.close()

        # Get video from the clicked item in the list
        video = item.text()

        # Set input video path from selected video in dropdown list
        input_video_path = os.path.join(self.input_dir, video)

        # Run object detection script with selected video
        output_path = os.path.join(self.input_dir, f"test_{self.index}_{video}")
        cmd = f'python object_detection_video.py --input "{input_video_path}" --output "{output_path}"'
        os.system(cmd)
        self.index += 1

    def run_emotion_recognition(self):
        # Try to write to stdin and flush
        try:
            if self.agegenderemotion_process.stdin is not None:
                self.agegenderemotion_process.stdin.write(b'start\n')
                self.agegenderemotion_process.stdin.flush()
            else:
                print("Error: agegenderemotion_process.stdin is None")
        except OSError as e:
            print(f"Error occurred when trying to write to stdin: {e}")

    def closeEvent(self, event):
        # Delete all files in Input folder
        for filename in os.listdir(self.input_dir):
            file_path = os.path.join(self.input_dir, filename)
            os.remove(file_path)

        event.accept()

    def run_classifier(self):
        subprocess.Popen(["python", "app-gui.py"])

app = QApplication([])
gui = GUI()
app.exec()