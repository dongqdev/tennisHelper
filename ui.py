import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from controller import showMessage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 500, 500)

        self.button = QPushButton("Show Computer Info", self)
        self.button.move(200, 250)
        self.button.clicked.connect(showMessage)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec())
