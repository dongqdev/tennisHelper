from PyQt6.QtWidgets import QMessageBox
from data import dataprint

def showMessage():
    info = dataprint()
    msg = "\n".join([f"{key}: {value}" for key, value in info.items()])
    QMessageBox.information(None, "Computer Information", msg)
