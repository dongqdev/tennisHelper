import sys

from PyQt6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QInputDialog

from dataHandler import DataHandler

class AuthHandler:
    def __init__(self):
        self.data_handler = DataHandler()

    def authUserCheck(self):
        compute_Info = self.data_handler.get_computer_info()

        if not (self.data_handler.check_user_info(compute_Info["mac_address"])):
            QMessageBox.information(None, "경고", "승인되지 않은 사용자 입니다.\n키 등록 후, 사용해 주세요")
            keyTxt, ok = QInputDialog.getText(self, "프로그램 등록", "KEY:")
            if ok:
                if len(str(keyTxt)) == 0:
                    QMessageBox.information(None, "에러", f"프로그램 키가 입력되지 않았습니다.")
                else:
                    resultText = self.data_handler.upsert_user_info(compute_Info, str(keyTxt))
                    if resultText == "COMPLETE":
                        QMessageBox.information(None, "안내", f"등록이 완료되었습니다.")
                    elif resultText == "EXIST":
                        QMessageBox.information(None, "안내", f"이미 등록된 사용자가 존재합니다.")
                        sys.exit(1)
                    else:
                        QMessageBox.information(None, "안내", f"키가 일치 하지 않습니다.")
                        sys.exit(1)
            else:
                sys.exit(1)
        # if compute_Info["mac_address"] in accessUser_Mac_Adress:
        #    print("접근 허용")
        else:
            # QMessageBox.information(None, "경고", "승인되지 않은 사용자 입니다.")
            # sys.exit(1)
            print("승인된 사용자 입니다.")

    self.authUserCheck();