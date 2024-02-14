import sys
from dataHandler import DataHandler


class AuthHandler:
    def __init__(self):
        self.data_handler = DataHandler()

    def setAuthUserData(self, messageCode, header, message):
        authUserData = {}
        authUserData["messageCode"] = messageCode
        authUserData["header"] = header
        authUserData["message"] = message

        return authUserData

    def authUserCheck(self):
        compute_Info = self.data_handler.get_computer_info()
        print("Call Function authUserCheck in AuthHandler Class")

        if not (self.data_handler.check_user_info(compute_Info["mac_address"])):
            print("Auth Check Fail")
            return self.setAuthUserData(
                "information", "경고", "승인되지 않은 사용자 입니다.\n키 등록 후, 사용해 주세요"
            )
        else:
            print("Auth Check Success")

#독립구문 테스트
if __name__ == "__main__":
    auth_handler = AuthHandler().authUserCheck()
    print(auth_handler)