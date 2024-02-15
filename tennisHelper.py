# -*- coding: utf-8 -*-
# EXE 변환 명령어(MAC) : pyinstaller -w -F --icon=sejong_chn.ico -n tennisHelper tennisHelper.py
# EXE 변환 명령어(Window) :  pyinstaller -w -F --icon=sejong_eng.ico -n 세종시_통합예약시스템_도우미 tennisHelper.py
# UI 변환 명령어 : pyuic6 -o output.py tennisHelper.ui
# 아래 문구 추가
# 상단 :
'''
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi()  # UI 설정 함수 호출

    def setupUi(self):
'''
# 하단
'''
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 앱 객체 생성
    mainWin = MainWindow()  # 메인 윈도우 객체 생성
    mainWin.show()  # 메인 윈도우 보여주기
    sys.exit(app.exec())  # 이벤트 루프 시작
'''
# parent=MainWindow >>> 찾아 바꾸기 >>> parent=self


import mariadb
import getpass
import hashlib
import subprocess
import urllib

import requests

# PYQT6
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QMainWindow,QWidget,QMessageBox,QDialog,QInputDialog,QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QProgressDialog
from PyQt6.QtCore import QThread,pyqtSignal,QTimer,QTime,Qt
from PyQt6.QtGui import QFont, QBrush, QColor


from cryptography.fernet import Fernet

# 다크테마 사용법 : pip install pyqtdarktheme
import qdarktheme


import json
import uuid
import platform
import smtplib
from email.message import EmailMessage
import socket


import os
import sys
import time

from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


##################################################
# 크롬 드라이버 시작
##################################################
options = Options()
options.add_argument("--incognito")
options.add_experimental_option("detach", True)  # 브라우저 바로 닫힘 방지
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 불필요한 메시지 제거

driver = webdriver.Chrome(options=options)
# 세종시 통합예약시스템 접속
driver.get("https://onestop.sejong.go.kr/Usr/main/main.do")
# 페이지 로딩을 기다려 주자!
driver.implicitly_wait(time_to_wait=1)
driver.set_window_size(800, 800)

# 팝업창 닫기
# driver.execute_script("$('#mb-row').css('display','none')")

# 쿠키 설정 팝업창(의미없음 - 쿠키설정 테스트)
# driver.add_cookie({"name": "main_layerPopOneDayCk", "value": "Y"})
##################################################
# 크롬 드라이버 종료
##################################################

# 동작 하나당 시간 간격(느린 컴퓨터 및 브라우저에서 돔생성 이전에 클릭 방지)
actionTime = 0.5
inputTime = 0.7
# 사용자인증 체크
userAuthCheck = False

# 현재 애플리케이션 버전
current_version = "2.3.0"

accessUser_Mac_Adress = [
    "84:7b:57:6a:e6:8a",
    "98:22:ef:aa:a0:54",
    "60:e3:2b:d4:03:72",
    "e8:03:9a:de:15:4c",
    "e4:02:9b:58:88:e6",
    "88:ae:dd:2a:68:6b",
    "88:ae:dd:2a:6b:b5",
]


class DataHandler:
    def __init__(self, key_path="key.key", data_path="data.dat"):
        self.key_path = key_path
        self.data_path = data_path
        self.load_key()
        # 파일이 존재할 때만 데이터를 불러옴
        if os.path.exists(self.data_path):
            self.load_data()
            print(self.data)
        else:
            # 파일이 존재하지 않으면 빈 데이터를 생성
            self.data = {"user_info": [], "computer_info": []}

    def load_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as key_file:
                self.key = key_file.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(self.key)

    def calculate_file_hash(self, file_path):
        hasher = hashlib.sha256()
        with open(file_path, "rb") as file:
            while True:
                data = file.read(65536)  # Read in 64k chunks
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()

    def save_data(self):
        encrypted_data = Fernet(self.key).encrypt(json.dumps(self.data).encode())
        with open(self.data_path, "wb") as data_file:
            data_file.write(encrypted_data)
        # Calculate and save the hash of the data file
        hash_value = self.calculate_file_hash(self.data_path)
        with open(self.data_path + ".hash", "w") as hash_file:
            hash_file.write(hash_value)

    def load_data(self):
        if os.path.exists(self.data_path):
            # Verify the integrity of the data file
            expected_hash = ""
            if os.path.exists(self.data_path + ".hash"):
                with open(self.data_path + ".hash", "r") as hash_file:
                    expected_hash = hash_file.read().strip()

            actual_hash = self.calculate_file_hash(self.data_path)
            if expected_hash != actual_hash:
                raise ValueError(
                    "Data file integrity check failed. File may have been tampered with."
                )

            with open(self.data_path, "rb") as data_file:
                encrypted_data = data_file.read()
                decrypted_data = Fernet(self.key).decrypt(encrypted_data)
                self.data = json.loads(decrypted_data.decode())
        else:
            self.data = []
            # Create an empty hash file
            with open(self.data_path + ".hash", "w") as hash_file:
                hash_file.write("")

    def add_user(self, user_id, password):
        for user in self.data["user_info"]:
            if user["id"] == user_id:
                print("이미 존재하는 아이디입니다.")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("이미 존재하는 아이디입니다.\n계정정보 삭제 후 재등록해주세요")
                msg.setWindowTitle("Error")
                msg.exec()
                return
        self.data["user_info"].append({"id": user_id, "pw": password})
        self.save_data()
        print(f"사용자 {user_id}가 추가되었습니다.")

    def update_user(self, user_id, new_password):
        for user in self.data["user_info"]:
            if user["id"] == user_id:
                user["pw"] = new_password
                self.save_data()
                print(f"사용자 {user_id}의 비밀번호가 수정되었습니다.")
                return
        print("존재하지 않는 아이디입니다.")

    def delete_user(self, user_id):
        user_found = False
        for user in self.data["user_info"]:
            if user["id"] == user_id:
                self.data["user_info"].remove(user)
                self.save_data()
                user_found = True
                break

        if not user_found:
            print(f"사용자 {user_id} 계정을 찾을 수 없습니다.")
            return f"사용자 {user_id} 계정을 찾을 수 없습니다."
        else:
            print(f"사용자 {user_id} 계정이 삭제되었습니다.")
            return f"사용자 {user_id} 계정이 삭제되었습니다."

    def print_users(self):
        for user in self.data["user_info"]:
            print(f"아이디: {user['id']}, 비밀번호: {user['pw']}")

    """def get_users(self):
        for user in self.data["user_info"]:
            self.idCb.addItem(f"{user['id']}", f"{user['pw']}")"""

    def get_user_count(self):
        return len(self.data["user_info"])

    def add_computer_info(self, computer_info):
        self.data["computer_info"] = []  # 컴퓨터 정보 초기화

        # 새로운 컴퓨터 정보 추가
        self.data["computer_info"].append(computer_info)
        self.save_data()
        print("컴퓨터 정보가 추가되었습니다.")

    # 컴퓨터 정보 수집 (예시)
    def get_computer_info(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        os_name = platform.system()
        os_version = platform.version()
        cptName = platform.node()
        processor = platform.processor()
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            print(f"Hostname {hostname} could not be resolved. Check the hostname and network connection.")
            # 적절한 오류 처리나 대체 로직을 여기에 구현합니다.

        userName = getpass.getuser()

        computer_info = {
            "cptName": f"{cptName}",
            "os": f"{os_name} : {os_version}",
            "processor": f"{processor}",
            "hostname": f"{hostname}",
            "ip_address": f"{ip_address}",
            "mac_address": ":".join([mac[e : e + 2] for e in range(0, 11, 2)]),
            "username": f"{userName}",
        }

        # JSON 인코딩
        json_data = json.dumps(computer_info)

        # 반환된 JSON 문자열을 파이썬 딕셔너리로 변환합니다.
        computer_info = json.loads(json_data)

        return computer_info


    def check_user_info(self, mac_address):
        try:
            connection = mariadb.connect(
                host="222.99.18.182",
                database="tennis_helper",
                user="tennishelper",
                password="pu(H_CwbGc4kFtv.",
            )
            # 커서 생성
            cursor = connection.cursor()

            # mac_address로 user 테이블 검색
            cursor.execute("SELECT * FROM user WHERE mac_address = ?", (mac_address,))
            result = cursor.fetchone()

            # 결과에 따라 메시지 출력
            if result:
                return True
            else:
                return False

            # 데이터베이스 연결 종료
            cursor.close()
            connection.close()

        except mariadb.Error as e:
            print(f"서버와 연결이 원활하지 않습니다 : {e}")
            sys.exit(1)

    def upsert_user_info(self, computer_Info, program_key):
        try:
            connection = mariadb.connect(
                host="222.99.18.182",
                database="tennis_helper",
                user="tennishelper",
                password="pu(H_CwbGc4kFtv.",
            )
            cursor = connection.cursor()

            computer_Info = self.get_computer_info()

            # 먼저 program_key에 해당하는 행이 있는지 확인합니다.
            cursor.execute(
                "SELECT mac_address FROM user WHERE program_key = ?", (program_key,)
            )
            result = cursor.fetchone()

            print("컴퓨터 정보를 등록합니다 : ", computer_Info)

            if result:
                if result[0] and result[0] != computer_Info["mac_address"]:
                    print("program_key가 존재하고 mac_address 존재하지만 입력된 mac_address 다른 경우")
                    return "EXIST"
                else:
                    print("program_key가 존재하고 mac_address 없거나 입력된 mac_address 일치하는 경우")
                    query = """
                        UPDATE user 
                        SET os = ?, processor = ?, hostname = ?, ip_address = ?, mac_address = ?, username = ? 
                        WHERE program_key = ?
                    """
                    cursor.execute(
                        query,
                        (
                            computer_Info["os"],
                            computer_Info["processor"],
                            computer_Info["hostname"],
                            computer_Info["ip_address"],
                            computer_Info["mac_address"],
                            computer_Info["username"],
                            program_key,
                        ),
                    )
                    connection.commit()
                    return "COMPLETE"
            else:
                # program_key가 존재하지 않으면
                return "FAIL"

        except mariadb.Error as e:
            return f"서버와 연결이 원활하지 않습니다\n{e}"


def send_Email(mailData):
    # 사용자에게 전송할 이메일 메시지 작성
    message = EmailMessage()
    # message.set_content(f"{get_userInfo()}")  # 이메일 내용을 설정합니다.
    computer_info = (
        DataHandler().get_computer_info()
    )  # 이 함수는 컴퓨터 정보를 담은 딕셔너리를 반환한다고 가정합니다.

    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
        </head>
        <body style="height:100vh; background-color: #4158D0; background-image: linear-gradient(43deg, #4158D0 0%, #C850C0 46%, #FFCC70 100%);">
            <center style="background-color:#fff; padding:10px; width:600px; margin:20px auto; border-radius:20px; box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);">
                <h1 style="font-family: sans-serif; color: #333;">컴퓨터 정보</h1>
                <table style="border-collapse: collapse; margin: 25px 0; font-size: 0.9em; font-family: sans-serif; min-width: 400px; width: 100%;">
                    <thead>
                        <tr style="background-color: #2e3bf7; color: #ffffff; text-align: left;">
                            <th style="padding: 12px 15px;">항목</th>
                            <th style="padding: 12px 15px;">정보</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid #dddddd;">
                            <td style="padding: 12px 15px;">컴퓨터 이름</td>
                            <td style="padding: 12px 15px;">{computer_info["cptName"]}</td>
                        </tr>
                        <tr style="background-color: #f3f3f3; border-bottom: 1px solid #dddddd;">
                            <td style="padding: 12px 15px;">운영 체제</td>
                            <td style="padding: 12px 15px;">{computer_info["os"]}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #dddddd;">
                            <td style="padding: 12px 15px;">프로세서</td>
                            <td style="padding: 12px 15px;">{computer_info["processor"]}</td>
                        </tr>
                        <tr style="background-color: #f3f3f3; border-bottom: 1px solid #dddddd;">
                            <td style="padding: 12px 15px;">호스트 이름</td>
                            <td style="padding: 12px 15px;">{computer_info["hostname"]}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #dddddd;">
                            <td style="padding: 12px 15px;">IP 주소</td>
                            <td style="padding: 12px 15px;">{computer_info["ip_address"]}</td>
                        </tr>
                        <tr style="background-color: #f3f3f3; border-bottom: 2px solid #2e3bf7;">
                            <td style="padding: 12px 15px;">MAC 주소</td>
                            <td style="padding: 12px 15px;">{computer_info["mac_address"]}</td>
                        </tr>
                        <tr style="background-color: #f3f3f3; border-bottom: 2px solid #2e3bf7;">
                            <td style="padding: 12px 15px;">유저명</td>
                            <td style="padding: 12px 15px;">{computer_info["userName"]}</td>
                        </tr>
                    </tbody>
                </table>
            </center>
        </body>
        </html>
        """

    # 이제 html_content 변수는 이메일 본문으로 사용할 준비가 되었습니다.

    message.add_alternative(html_content, subtype="html")
    message["Subject"] = f"세종시 통합 시스템 도우미({computer_info['cptName']})"  # 이메일 제목을 설정합니다.
    message["From"] = "noReply@gmail.com"  # 보내는 이메일 주소를 설정합니다.
    message["To"] = ""  # 받는 이메일 주소를 설정합니다.

    # SMTP 서버 설정
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Gmail의 경우 보통 587 포트를 사용합니다.

    # SMTP 서버에 연결하여 이메일 전송

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # TLS 암호화 연결을 시작합니다.
        server.login("", "")  # 이메일 계정 로그인
        server.send_message(message)  # 이메일 전송
        server.quit()  # SMTP 서버 연결 종료
        print("이메일 전송 성공!")
    except Exception as e:
        print("이메일 전송 실패:", e)


class EmailThread(QThread):
    finished = pyqtSignal()

    def __init__(self, mailData):
        QThread.__init__(self)
        self.mailData = mailData

    def run(self):
        send_Email(self.mailData)
        self.finished.emit()


class TennisScheduleWindow(QWidget):
    def __init__(self, tennis_schedule):
        super().__init__()
        self.tennis_schedule = tennis_schedule
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.table.horizontalHeader().setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.load_data_into_table()
        self.layout.addWidget(self.table)
        self.adjust_frame_size(len(self.tennis_schedule))

    def adjust_frame_size(self, size):
        self.table.adjustSize()
        self.adjustSize()
        self.resize(18 * size, 300)

    def load_data_into_table(self):
        # 테이블 사이즈 조절

        # 코트별로 데이터 분리
        courts = {}
        for key, value in self.tennis_schedule.items():
            court_name = value["fcltNm"]
            if court_name not in courts:
                courts[court_name] = []
            courts[court_name].append(
                (value["useBeginHm"] + "-" + value["useEndHm"], value["reserveYn"])
            )

        # 각 코트별로 시간대 정렬
        for court in courts:
            courts[court].sort()

        # 테이블 구성
        self.table.setColumnCount(len(courts))
        self.table.setRowCount(len(courts[list(courts.keys())[0]]))
        self.table.setHorizontalHeaderLabels(list(courts.keys()))

        # 데이터 삽입
        for col, court in enumerate(courts.keys()):
            for row, (time, status) in enumerate(courts[court]):
                item = QTableWidgetItem(time)
                if status == "Y":
                    item.setBackground(QColor(0, 0, 255))  # 파란색
                    item.setForeground(QBrush(Qt.GlobalColor.white))
                else:
                    item.setBackground(QColor(255, 0, 0))  # 빨간색
                    item.setForeground(QBrush(Qt.GlobalColor.white))
                self.table.setItem(row, col, item)

        # 테이블 헤더 크기 조절
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # 프레임 크기 조절
        self.adjustSize()


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi()  # UI 설정 함수 호출
        # 창위치 변경
        self.move(1350, 200)
    '''
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('tennisHelper.ui', self)
        # 이벤트 연결
        self.setupUi()
        # 창위치 변경
        self.move(1350, 200)
    '''

    def setupUi(self):
        # 앱 타이틀
        self.setWindowTitle(f"세종시 통합예약 시스템 도우미 v{current_version}")
        # self.setWindowModality(Qt.NonModal)

        ##################################################
        # UI 시작
        ##################################################

        self.setObjectName("MainWindow")
        self.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        self.resize(568, 853)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.titleLbl = QtWidgets.QLabel(parent=self.centralwidget)
        self.titleLbl.setGeometry(QtCore.QRect(40, 10, 351, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.titleLbl.setFont(font)
        self.titleLbl.setObjectName("titleLbl")
        self.accountGb = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.accountGb.setGeometry(QtCore.QRect(30, 60, 501, 71))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.accountGb.setFont(font)
        self.accountGb.setObjectName("accountGb")
        self.idLbl = QtWidgets.QLabel(parent=self.accountGb)
        self.idLbl.setGeometry(QtCore.QRect(30, 30, 60, 31))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.idLbl.setFont(font)
        self.idLbl.setObjectName("idLbl")
        self.idCb = QtWidgets.QComboBox(parent=self.accountGb)
        self.idCb.setGeometry(QtCore.QRect(110, 30, 171, 31))
        self.idCb.setObjectName("idCb")
        self.addAccountBtn = QtWidgets.QPushButton(parent=self.accountGb)
        self.addAccountBtn.setGeometry(QtCore.QRect(360, 30, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.addAccountBtn.setFont(font)
        self.addAccountBtn.setObjectName("addAccountBtn")
        self.deleteAccountBtn = QtWidgets.QPushButton(parent=self.accountGb)
        self.deleteAccountBtn.setGeometry(QtCore.QRect(430, 30, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.deleteAccountBtn.setFont(font)
        self.deleteAccountBtn.setObjectName("deleteAccountBtn")
        self.loginBtn = QtWidgets.QPushButton(parent=self.accountGb)
        self.loginBtn.setGeometry(QtCore.QRect(290, 30, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(8)
        self.loginBtn.setFont(font)
        self.loginBtn.setObjectName("loginBtn")
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(260, 150, 60, 16))
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")
        self.reserve1Gb = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.reserve1Gb.setGeometry(QtCore.QRect(30, 130, 501, 181))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.reserve1Gb.setFont(font)
        self.reserve1Gb.setObjectName("reserve1Gb")
        self.date1Lbl = QtWidgets.QLabel(parent=self.reserve1Gb)
        self.date1Lbl.setGeometry(QtCore.QRect(30, 55, 60, 30))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.date1Lbl.setFont(font)
        self.date1Lbl.setObjectName("date1Lbl")
        self.time1Lbl = QtWidgets.QLabel(parent=self.reserve1Gb)
        self.time1Lbl.setGeometry(QtCore.QRect(30, 85, 60, 30))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.time1Lbl.setFont(font)
        self.time1Lbl.setObjectName("time1Lbl")
        self.tennisPlace1Lbl = QtWidgets.QLabel(parent=self.reserve1Gb)
        self.tennisPlace1Lbl.setGeometry(QtCore.QRect(30, 120, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.tennisPlace1Lbl.setFont(font)
        self.tennisPlace1Lbl.setObjectName("tennisPlace1Lbl")
        self.date1Cb = QtWidgets.QComboBox(parent=self.reserve1Gb)
        self.date1Cb.setGeometry(QtCore.QRect(160, 60, 311, 26))
        self.date1Cb.setObjectName("date1Cb")
        self.time1Cb = QtWidgets.QComboBox(parent=self.reserve1Gb)
        self.time1Cb.setGeometry(QtCore.QRect(160, 90, 311, 26))
        self.time1Cb.setObjectName("time1Cb")
        self.tennisPlace1Cb = QtWidgets.QComboBox(parent=self.reserve1Gb)
        self.tennisPlace1Cb.setGeometry(QtCore.QRect(160, 120, 311, 26))
        self.tennisPlace1Cb.setObjectName("tennisPlace1Cb")
        self.reserveYNLbl1 = QtWidgets.QLabel(parent=self.reserve1Gb)
        self.reserveYNLbl1.setGeometry(QtCore.QRect(30, 150, 141, 21))
        self.reserveYNLbl1.setObjectName("reserveYNLbl1")
        self.reserveChkBtn1 = QtWidgets.QPushButton(parent=self.reserve1Gb)
        self.reserveChkBtn1.setGeometry(QtCore.QRect(30, 28, 441, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.reserveChkBtn1.setFont(font)
        self.reserveChkBtn1.setObjectName("reserveChkBtn1")
        self.reserveMsgLbl1 = QtWidgets.QLabel(parent=self.reserve1Gb)
        self.reserveMsgLbl1.setGeometry(QtCore.QRect(160, 150, 221, 16))
        self.reserveMsgLbl1.setText("")
        self.reserveMsgLbl1.setObjectName("reserveMsgLbl1")
        self.reserve2Gb = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.reserve2Gb.setGeometry(QtCore.QRect(30, 320, 501, 181))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.reserve2Gb.setFont(font)
        self.reserve2Gb.setObjectName("reserve2Gb")
        self.date2Lbl = QtWidgets.QLabel(parent=self.reserve2Gb)
        self.date2Lbl.setGeometry(QtCore.QRect(30, 60, 60, 20))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.date2Lbl.setFont(font)
        self.date2Lbl.setObjectName("date2Lbl")
        self.time2Lbl = QtWidgets.QLabel(parent=self.reserve2Gb)
        self.time2Lbl.setGeometry(QtCore.QRect(30, 90, 60, 20))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.time2Lbl.setFont(font)
        self.time2Lbl.setObjectName("time2Lbl")
        self.tennisPlace2Lbl = QtWidgets.QLabel(parent=self.reserve2Gb)
        self.tennisPlace2Lbl.setGeometry(QtCore.QRect(30, 120, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.tennisPlace2Lbl.setFont(font)
        self.tennisPlace2Lbl.setObjectName("tennisPlace2Lbl")
        self.date2Cb = QtWidgets.QComboBox(parent=self.reserve2Gb)
        self.date2Cb.setGeometry(QtCore.QRect(160, 60, 311, 26))
        self.date2Cb.setObjectName("date2Cb")
        self.time2Cb = QtWidgets.QComboBox(parent=self.reserve2Gb)
        self.time2Cb.setGeometry(QtCore.QRect(160, 90, 311, 26))
        self.time2Cb.setObjectName("time2Cb")
        self.tennisPlace2Cb = QtWidgets.QComboBox(parent=self.reserve2Gb)
        self.tennisPlace2Cb.setGeometry(QtCore.QRect(160, 120, 311, 26))
        self.tennisPlace2Cb.setObjectName("tennisPlace2Cb")
        self.reserveChbox2 = QtWidgets.QCheckBox(parent=self.reserve2Gb)
        self.reserveChbox2.setGeometry(QtCore.QRect(100, 2, 21, 16))
        self.reserveChbox2.setText("")
        self.reserveChbox2.setObjectName("reserveChbox2")
        self.reserveYNLbl2 = QtWidgets.QLabel(parent=self.reserve2Gb)
        self.reserveYNLbl2.setGeometry(QtCore.QRect(30, 150, 141, 21))
        self.reserveYNLbl2.setObjectName("reserveYNLbl2")
        self.reserveChkBtn2 = QtWidgets.QPushButton(parent=self.reserve2Gb)
        self.reserveChkBtn2.setGeometry(QtCore.QRect(30, 30, 441, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.reserveChkBtn2.setFont(font)
        self.reserveChkBtn2.setObjectName("reserveChkBtn2")
        self.reserveMsgLbl2 = QtWidgets.QLabel(parent=self.reserve2Gb)
        self.reserveMsgLbl2.setGeometry(QtCore.QRect(170, 152, 221, 16))
        self.reserveMsgLbl2.setText("")
        self.reserveMsgLbl2.setObjectName("reserveMsgLbl2")
        self.noticeGb = QtWidgets.QGroupBox(parent=self.centralwidget)
        self.noticeGb.setGeometry(QtCore.QRect(0, 520, 531, 161))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.noticeGb.setFont(font)
        self.noticeGb.setObjectName("noticeGb")
        self.noticeLbl4 = QtWidgets.QLabel(parent=self.noticeGb)
        self.noticeLbl4.setGeometry(QtCore.QRect(10, 50, 411, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.noticeLbl4.setFont(font)
        self.noticeLbl4.setObjectName("noticeLbl4")
        self.noticeLbl1 = QtWidgets.QLabel(parent=self.noticeGb)
        self.noticeLbl1.setGeometry(QtCore.QRect(10, 27, 391, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.noticeLbl1.setFont(font)
        self.noticeLbl1.setObjectName("noticeLbl1")
        self.noticeLbl5 = QtWidgets.QLabel(parent=self.noticeGb)
        self.noticeLbl5.setGeometry(QtCore.QRect(10, 70, 411, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.noticeLbl5.setFont(font)
        self.noticeLbl5.setObjectName("noticeLbl5")
        self.noticeLbl6 = QtWidgets.QLabel(parent=self.noticeGb)
        self.noticeLbl6.setGeometry(QtCore.QRect(10, 90, 411, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.noticeLbl6.setFont(font)
        self.noticeLbl6.setObjectName("noticeLbl6")
        self.noticeLbl8_2 = QtWidgets.QLabel(parent=self.noticeGb)
        self.noticeLbl8_2.setGeometry(QtCore.QRect(10, 110, 411, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.noticeLbl8_2.setFont(font)
        self.noticeLbl8_2.setObjectName("noticeLbl8_2")
        self.noticeLbl8_3 = QtWidgets.QLabel(parent=self.noticeGb)
        self.noticeLbl8_3.setGeometry(QtCore.QRect(10, 130, 411, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.noticeLbl8_3.setFont(font)
        self.noticeLbl8_3.setObjectName("noticeLbl8_3")
        self.coutionLbl = QtWidgets.QLabel(parent=self.centralwidget)
        self.coutionLbl.setGeometry(QtCore.QRect(260, 810, 271, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        font.setKerning(True)
        self.coutionLbl.setFont(font)
        self.coutionLbl.setObjectName("coutionLbl")
        self.line2 = QtWidgets.QFrame(parent=self.centralwidget)
        self.line2.setGeometry(QtCore.QRect(30, 790, 501, 20))
        self.line2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line2.setObjectName("line2")
        self.autoReserveBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.autoReserveBtn.setGeometry(QtCore.QRect(250, 700, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.autoReserveBtn.setFont(font)
        self.autoReserveBtn.setObjectName("autoReserveBtn")
        self.selfReserveBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.selfReserveBtn.setGeometry(QtCore.QRect(20, 700, 201, 41))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.selfReserveBtn.setFont(font)
        self.selfReserveBtn.setObjectName("selfReserveBtn")
        self.timeEdit = QtWidgets.QTimeEdit(parent=self.centralwidget)
        self.timeEdit.setGeometry(QtCore.QRect(100, 760, 118, 24))
        self.timeEdit.setObjectName("timeEdit")
        self.timeSetLbl = QtWidgets.QLabel(parent=self.centralwidget)
        self.timeSetLbl.setGeometry(QtCore.QRect(30, 763, 71, 16))
        self.timeSetLbl.setObjectName("timeSetLbl")
        self.currentTimeLbl = QtWidgets.QLabel(parent=self.centralwidget)
        self.currentTimeLbl.setGeometry(QtCore.QRect(30, 810, 131, 16))
        self.currentTimeLbl.setObjectName("currentTimeLbl")
        self.stopAutoReserveBtn = QtWidgets.QPushButton(parent=self.centralwidget)
        self.stopAutoReserveBtn.setGeometry(QtCore.QRect(400, 700, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.stopAutoReserveBtn.setFont(font)
        self.stopAutoReserveBtn.setObjectName("stopAutoReserveBtn")
        self.darkModeChBox = QtWidgets.QCheckBox(parent=self.centralwidget)
        self.darkModeChBox.setGeometry(QtCore.QRect(450, 30, 81, 16))
        self.darkModeChBox.setObjectName("darkModeChBox")
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        # retranslateUi

        ##################################################
        # UI 종료
        ##################################################

        ##################################################
        # 기능 개발 시작
        ##################################################
        # 데이터 핸들러 초기화
        data_Handler = DataHandler()

        ##################################################
        # 자동업데이트 시작
        ##################################################

        # 원격 버전을 확인하는 URL
        version_url = "https://raw.githubusercontent.com/dongqdev/tennisHelperFile/main/appInfo.txt"

        # 원격 버전 확인 및 JSON 파싱
        try:
            response = requests.get(version_url)
            print('[autoUpdate-check_Version] response : ', response)
            # response.raise_for_status()  # 오류가 있으면 예외를 발생시킵니다.

            # 인코딩이 utf-8이 아닌 경우 아래와 같이 디코딩을 시도합니다.
            response.encoding = "utf-8"  # 1안
            # remote_info = response.content.decode('utf-8')  # 2안

            remote_info = response.json()
            print("[autoUpdate-check_Version remote_info", remote_info)
            remote_version = remote_info.get("version", "0.0.0")
            # 버전 정보가 없으면 '0.0.0'을 사용합니다.
            updateDate = remote_info.get("updateDate", "-")
            updateInfo = remote_info.get("updateInfo", "-")
            # QMessageBox.information(None, "업데이트 완료",f"{updateInfo}\n\n{updateDate}");

            update_Check_Info = {}

            # 버전 비교
            if current_version < remote_version:
                QMessageBox.information(None, "업데이트", "새로운 버전이 있습니다. 업데이트를 진행합니다.")
                # user_reply = QMessageBox.question(None, "업데이트", "새로운 버전이 있습니다. 업데이트를 진행할까요?", QMessageBox.Yes | QMessageBox.No,QMessageBox.Yes)
                driver.quit()
                # if user_reply == QMessageBox.Yes:

                local_exe_path = self.download_and_execute(remote_version)
            else:
                QMessageBox.information(
                    None, "시작", f"최신 버전입니다. 프로그램을 실행합니다.\n\n[업데이트 내역]\n{updateInfo}"
                )
                # 프로그램 실행
        except requests.RequestException as e:
            QMessageBox.critical(
                None, "업데이트 오류", f"원격 버전 정보를 가져오는데 실패했습니다.\n프로그램을 종료합니다."
            )
            sys.exit(1)  # 오류가 발생하면 애플리케이션을 종료합니다.

        ##################################################
        # 자동업데이트 종료
        ##################################################
        ##################################################
        # 사용자 인증 시작
        ##################################################

        compute_Info = data_Handler.get_computer_info()

        if(userAuthCheck == True):
            if not (data_Handler.check_user_info(compute_Info["mac_address"])):
                QMessageBox.information(None, "경고", "승인되지 않은 사용자 입니다.\n키 등록 후, 사용해 주세요")
                keyTxt, ok = QInputDialog.getText(self, "프로그램 등록", "KEY:")
                if ok:
                    if len(str(keyTxt)) == 0:
                        QMessageBox.information(None, "에러", f"프로그램 키가 입력되지 않았습니다")
                    else:
                        resultText = data_Handler.upsert_user_info(
                            compute_Info, str(keyTxt)
                        )
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

        ##################################################
        # 사용자 인증 종료
        ##################################################

        # get_computer_info() 메서드 호출 시 self 인자 전달
        computer_info = data_Handler.get_computer_info()

        print(computer_info)
        print(data_Handler.get_user_count())
        if data_Handler.get_user_count() == 0:
            # 아이디 등록 안내 메시지 표출 : QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("계정정보 등록 후 사용해주세요")
            msg.setWindowTitle("Error")
            msg.exec()

        # 이후에 send_Email() 함수에서 computer_info 변수를 사용할 수 있음
        # send_Email(computer_info)

        # 이메일 전송 스레드를 생성하고 시작합니다.
        # self.email_thread = EmailThread(computer_info)
        # self.email_thread.finished.connect(self.on_email_sent)
        # self.email_thread.start()
        # print(data_Handler.data)
        ##################################################
        # 현재시간 보여주기 시작
        ##################################################
        # 타이머 설정 (1초마다 업데이트)가
        timer = QTimer(self.centralwidget)
        timer.timeout.connect(self.updateTime)
        timer.start(1000)

        # 자동예약 기본 시간 설정
        self.timeEdit.setDisplayFormat("HH:mm:ss")
        new_time = QTime(8, 59, 58)  # 새로운 시간을 설정합니다.
        self.timeEdit.setTime(new_time)
        selectedTime = self.timeEdit.time().toString()

        print("자동예약 설정시간 : ", selectedTime)
        ##################################################
        # 현재시간 보여주기 종료
        ##################################################

        # 버튼 클릭 이벤트
        self.selfReserveBtn.clicked.connect(self.btn_reserve_self)
        self.autoReserveBtn.clicked.connect(self.btn_reserve_auto)
        self.stopAutoReserveBtn.clicked.connect(self.btn_reserve_auto_stop)
        self.loginBtn.clicked.connect(self.login)
        self.darkModeChBox.stateChanged.connect(self.toggleTheme)
        self.reserveChkBtn1.clicked.connect(self.reserveCheck1)
        self.reserveChbox2.stateChanged.connect(self.reserveYN2)
        self.reserveChkBtn2.clicked.connect(self.reserveCheck2)

        ##################################################
        # 계정 읽어오기 시작
        ##################################################

        # 초기 계정정보 읽어오기
        if data_Handler.get_user_count() != 0:
            for user in data_Handler.data["user_info"]:
                self.idCb.addItem(f"{user['id']}", f"{user['pw']}")

        ##################################################
        # 계정 읽어오기 종료
        ##################################################
        ##################################################
        # 날짜 설정 시작
        ##################################################
        # 시작일,종료일 설정
        start = datetime.today().strftime("%Y-%m-%d")
        last = (datetime.today() + timedelta(20)).strftime("%Y-%m-%d")

        # 시작일, 종료일 datetime 으로 변환
        start_date = datetime.strptime(start, "%Y-%m-%d")
        last_date = datetime.strptime(last, "%Y-%m-%d")

        # 종료일 까지 반복
        while start_date <= last_date:
            dateName = start_date.strftime("%Y-%m-%d")
            dateValue = start_date.strftime("%Y%m%d,%Y,%m,%d")
            self.date1Cb.addItem(dateName, dateValue)
            self.date2Cb.addItem(dateName, dateValue)

            # 하루 더하기
            start_date += timedelta(days=1)
        # 프로그램 실행 시 20일 뒤 날짜를 기본으로 설정
        print(last_date.strftime("%Y-%m-%d"))
        self.date1Cb.setCurrentText(last_date.strftime("%Y-%m-%d"))
        self.date2Cb.setCurrentText(last_date.strftime("%Y-%m-%d"))
        ##################################################
        # 날짜 설정 종료
        ##################################################
        ##################################################
        # 시간 설정 시작
        ##################################################
        for i in range(20, 6, -2):
            j = i + 2
            if len(str(i)) == 1:
                i = "0" + str(i)
            if len(str(j)) == 1:
                j = "0" + str(j)
            # 20:00 ~ 22:00
            self.time1Cb.addItem("%s:00 ~ %s:00" % (i, j), "%s:00 ~ %s:00" % (i, j))
            self.time2Cb.addItem("%s:00 ~ %s:00" % (i, j), "%s:00 ~ %s:00" % (i, j))

        # 전의 생활공원의 경우 시간이 다름
        self.time1Cb.addItem("===다정동===", "")
        self.time1Cb.addItem("09:00 ~ 10:00", "09:00 ~ 10:00")
        self.time1Cb.addItem("===금남생활체육공원===", "")
        self.time1Cb.addItem("06:00 ~ 08:00", "06:00 ~ 08:00")
        self.time1Cb.addItem("===전의 생활공원===", "")
        self.time1Cb.addItem("09:00 ~ 11:00", "09:00 ~ 11:00")
        self.time1Cb.addItem("11:30 ~ 13:30", "11:30 ~ 13:30")
        self.time1Cb.addItem("14:00 ~ 16:00", "14:00 ~ 16:00")
        self.time1Cb.addItem("16:30 ~ 18:30", "16:30 ~ 18:30")
        self.time1Cb.addItem("19:00 ~ 21:00", "19:00 ~ 21:00")
        self.time2Cb.addItem("===다정동===", "")
        self.time2Cb.addItem("09:00 ~ 10:00", "09:00 ~ 10:00")
        self.time2Cb.addItem("===금남생활체육공원===", "")
        self.time2Cb.addItem("06:00 ~ 08:00", "06:00 ~ 08:00")
        self.time2Cb.addItem("===전의생활공원===", "")
        self.time2Cb.addItem("09:00 ~ 11:00", "09:00 ~ 11:00")
        self.time2Cb.addItem("11:30 ~ 13:30", "11:30 ~ 13:30")
        self.time2Cb.addItem("14:00 ~ 16:00", "14:00 ~ 16:00")
        self.time2Cb.addItem("16:30 ~ 18:30", "16:30 ~ 18:30")
        self.time2Cb.addItem("19:00 ~ 21:00", "19:00 ~ 21:00")

        ##################################################
        # 시간 설정 종료
        ##################################################
        ##################################################
        # 테니스장 설정 시작
        ##################################################
        tennisCourtList = {
            "중앙공원 테니스장 1": "OP8374580375538171,0",
            "중앙공원 테니스장 2": "OP8374580375538171,1",
            "중앙공원 테니스장 3": "OP8374580375538171,2",
            "중앙공원 테니스장 4": "OP8374580375538171,3",
            "중앙공원 테니스장 5": "OP8374580375538171,4",
            "중앙공원 테니스장 6": "OP8374580375538171,5",
            "중앙공원 테니스장 7": "OP8374580375538171,6",
            "중앙공원 테니스장 8": "OP8374580375538171,7",
            "중앙공원 테니스장 9": "OP8374580375538171,8",
            "중앙공원 테니스장 10": "OP8374580375538171,9",
            "수질복원센터A 테니스장 코트1": "OP17028520651712824,0",
            "수질복원센터A 테니스장 코트2": "OP21695037103696738,0",
            "수질복원센터A 테니스장 코트3": "OP21166946437826537,0",
            "수질복원센터A 테니스장 코트4": "OP21695037103696738,1",
            "수질복원센터A 테니스장 코트5": "OP21703893297820968,0",
            "수질복원센터A 테니스장 코트6": "OP21695037103696738,2",
            "수질복원센터A 테니스장 코트7": "OP17028232109098739,0",
            "수질복원센터A 테니스장 코트8": "OP21695037103696738,3",
            "수질복원센터A 테니스장 코트9": "OP17028232109098739,1",
            "금남 생활체육공원 테니스장 1번코트": "OP8789086424809791,0",
            "금남 생활체육공원 테니스장 2번코트": "OP8789086424809791,1",
            "금남 생활체육공원 테니스장 3번코트": "OP8789086424809791,2",
            "다정동 저류지 체육시설 테니스장 1번코트": "OP8789473875350117,0",
            "다정동 저류지 체육시설 테니스장 2번코트": "OP8789473875350117,1",
            "다정동 저류지 체육시설 테니스장 3번코트 ": "OP8789473875350117,2",
            "소정 테니스장 A코트": "OP9396378582681599,0",
            "소정 테니스장 B코트": "OP9396378582681599,1",
            "소정 테니스장 C코트": "OP9396378582681599,2",
            "수질복원센터B 테니스장 코트1": "OP17028743154983862,0",
            "수질복원센터B 테니스장 코트2": "OP21696357966701005,0",
            "수질복원센터B 테니스장 코트3": "OP17028743154983862,1",
            "전의생활체육공원 테니스장 1번코트": "OP7750036806725368,0",
            "전의생활체육공원 테니스장 2번코트": "OP7750036806725368,1",
            "전의생활체육공원 테니스장 3번코트": "OP7750036806725368,2",
            "전의공공하수처리시설 테니스장 1코트": "OP10900259200163999,0",
            "조치원 체육공원 테니스장 1번코트": "OP8791200602627801,0",
            "조치원 체육공원 테니스장 2번코트": "OP8791200602627801,1",
            "조치원 체육공원 테니스장 3번코트": "OP8791200602627801,2",
            "조치원 체육공원 테니스장 4번코트": "OP8791200602627801,3",
            "조치원 체육공원 테니스장 5번코트": "OP8791200602627801,4",
        }
        for name, code in tennisCourtList.items():
            self.tennisPlace1Cb.addItem(name, code)
            self.tennisPlace2Cb.addItem(name, code)

        self.dialog = QDialog()
        self.addAccountBtn.clicked.connect(self.addAcount_dialog_open)
        self.deleteAccountBtn.clicked.connect(self.deleteAccount_dialog_open)

        # 예약정보 2 기본 비활성화
        self.reserveChbox2.setChecked(False)
        self.date2Cb.setEnabled(False)
        self.time2Cb.setEnabled(False)
        self.tennisPlace2Cb.setEnabled(False)

        # 다크모드 기본 활성화
        self.darkModeChBox.setChecked(True)
        ##################################################
        # 테니스장 설정 종료
        ##################################################

    def fcltList(self, oprtnPlanNo, sYear, sMonth, sDay):
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Host": "onestop.sejong.go.kr",
            "Origin": "https://onestop.sejong.go.kr",
            "Referer": "https://onestop.sejong.go.kr/Usr/resve/instDetail.do",
        }
        params = {
            "oprtnPlanNo": oprtnPlanNo,
            "sYear": sYear,
            "sMonth": sMonth,
            "sDay": sDay,
            "fcltNo": "",
        }

        params = urllib.parse.urlencode(params)

        url = "https://onestop.sejong.go.kr/Usr/resve/rest/timeCheck.do"
        res = requests.post(url=url, params=params)
        data = json.loads(res.text)

        # 응답 내용 확인
        # print("reserve 응답 상태 코드:", res.status_code)
        # print(f"응답 텍스트({name}):", res.text)

        reserveList = data

        # print("reserveList : ",reserveList)

        #############################################################
        # 예약자 명단 종료
        #############################################################

        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Host": "onestop.sejong.go.kr",
            "Origin": "https://onestop.sejong.go.kr",
            "Referer": "https://onestop.sejong.go.kr/Usr/resve/instDetail.do",
        }
        params = {
            "oprtnPlanNo": oprtnPlanNo,
            "sYear": sYear,
            "sMonth": sMonth,
            "sDay": sDay,
            "fcltNo": "",
        }

        params = urllib.parse.urlencode(params)

        url = "https://onestop.sejong.go.kr/Usr/resve/rest/fcltList.do"
        res = requests.post(url=url, params=params)
        # print(f"params : {params}")
        # print(f'url : {url}')
        # print(res)
        # 요청 보내기

        # 응답 내용 확인
        # print("fclt 응답 상태 코드:", res.status_code)
        # print(f"응답 텍스트({name}):", res.text)
        # JSON 데이터 파싱
        data = json.loads(res.text)
        # 새로운 딕셔너리 생성
        fcltList = data["fcltList"]
        timeList = data["timeList"]

        tennisCountCheckList = {}
        for data in fcltList:
            for time in timeList:
                fcltNo = data["fcltNo"]
                fcltNm = data["fcltNm"]
                oprtnPlanUseTimeNo = time["oprtnPlanUseTimeNo"]
                tennisCountCheckList[f"{fcltNo}-{oprtnPlanUseTimeNo}"] = {
                    "fcltNm": fcltNm,
                    "fcltNo": fcltNo,
                    "oprtnPlanUseTimeNo": time["oprtnPlanUseTimeNo"],
                    "oprtnPlanNo": time["oprtnPlanNo"],
                    "strUseBeginHm": time["strUseBeginHm"],
                    "strUseEndHm": time["strUseEndHm"],
                    "useBeginHm": time["useBeginHm"],
                    "useEndHm": time["useEndHm"],
                }
        # print('tennisCountCheckList1 : ',tennisCountCheckList)

        # print(f"기예약 갯수 : {len(reserveList['checkList'])}")

        # tennisCountCheckList reserveYn : Y 으로 초기화
        for key in tennisCountCheckList:
            tennisCountCheckList[key]["reserveYn"] = "Y"

        for reservation in reserveList["checkList"]:
            # fcltNo와 oprtnPlanUseTimeNo를 결합하여 키 생성
            key = f"{reservation['fcltNo']}-{reservation['oprtnPlanUseTimeNo']}"
            # print(key)

            # tennisCountCheckList1 해당 키가 존재하는지 확인
            if key in tennisCountCheckList:
                # 존재하면 reserveYn: 'N' 추가
                tennisCountCheckList[key]["reserveYn"] = "N"

        return tennisCountCheckList

    ##################################################
    # 자동 업데이트 함수 정의 시작
    ##################################################
    # 배치 생성 함수
    def create_temporary_batch_file(self, new_exe):
        with open("update.bat", "w") as bat:
            bat.write(
                f"""@echo off
                timeout /t 2 /nobreak >nul
                start "" "{new_exe}"
                del "%~f0"
                """)

    # 다운로드 및 실행 함수
    def download_and_execute(self, remote_version):
        # 원격 .exe 파일 URL
        # url = "http://ns.hakumata.world/tennisHelper/tennisHelper.exe"
        url = "https://github.com/dongqdev/tennisHelperFile/raw/main/tennisHelper.exe"
        # 다운로드할 파일 경로
        local_exe_path = f"tennisHelper_v{remote_version}.exe"

        response = requests.get(url, stream=True)
        total_length = response.headers.get("content-length")
        if total_length is None:  # 서버가 콘텐츠 길이를 제공하지 않는 경우
            with open(local_exe_path, "wb") as f:
                f.write(response.content)
        else:
            dlg = QProgressDialog("업데이트 다운로드 중...", "취소", 0, int(total_length))
            dlg.setWindowTitle("업데이트")
            dlg.setModal(True)
            dlg.show()

            with open(local_exe_path, "wb") as f:
                for data in response.iter_content(chunk_size=4096):
                    f.write(data)
                    dlg.setValue(f.tell())

            dlg.close()
            self.create_temporary_batch_file(local_exe_path)
            QMessageBox.information(
                None,
                "업데이트 완료",
                f"업데이트가 완료되었습니다.\ntenisHelper_v{remote_version}이 잠시 후 실행됩니다.",
            )
            subprocess.call(["update.bat"], shell=True)
            sys.exit(1)

    ##################################################
    # 자동 업데이트 함수 정의 종료
    ##################################################

    def on_email_sent(self):
        # 이메일 전송이 완료되었을 때 수행할 작업
        pass

    def reserveYN2(self, state):
        # 체크박스 상태 변경 시 호출
        if self.reserveChbox2.isChecked():
            self.date2Cb.setEnabled(True)
            self.time2Cb.setEnabled(True)
            self.tennisPlace2Cb.setEnabled(True)
        else:
            self.date2Cb.setEnabled(False)
            self.time2Cb.setEnabled(False)
            self.tennisPlace2Cb.setEnabled(False)

    def reserveCheck1(self):
        oprtnPlanNo = str(self.tennisPlace1Cb.currentData()).split(",")[0]
        sYear = str(self.date1Cb.currentText()).split("-")[0]
        sMonth = str(self.date1Cb.currentText()).split("-")[1]
        sDay = str(self.date1Cb.currentText()).split("-")[2]
        tennis_schedule = self.fcltList(oprtnPlanNo, sYear, sMonth, sDay)

        self.tennis_window = TennisScheduleWindow(tennis_schedule)
        self.tennis_window.show()

    def reserveCheck2(self):
        oprtnPlanNo = str(self.tennisPlace2Cb.currentData()).split(",")[0]
        sYear = str(self.date2Cb.currentText()).split("-")[0]
        sMonth = str(self.date2Cb.currentText()).split("-")[1]
        sDay = str(self.date2Cb.currentText()).split("-")[2]
        tennis_schedule = self.fcltList(oprtnPlanNo, sYear, sMonth, sDay)

        self.tennis_window = TennisScheduleWindow(tennis_schedule)
        self.tennis_window.show()

    def deleteAccount_dialog_open(self):
        data_handler = DataHandler()

        # 현재 선택된 콤보박스 인덱스 확인
        selected_index = self.idCb.currentIndex()

        # 선택된 인덱스에 해당하는 아이디 가져오기
        selected_id = self.idCb.itemText(selected_index)

        # 예/아니오 대화상자를 표시하여 삭제 여부 확인
        confirm = QMessageBox.question(
            self,
            "계정 삭제",
            f"{selected_id}를 삭제하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            # 아이디 삭제
            result = data_handler.delete_user(selected_id)
            QMessageBox.information(None, "안내", result)

            # 계정 삭제 후 selectbox 내 계정 삭제
            self.idCb.removeItem(selected_index)


    def addAcount_dialog_open(self):
        idTxt, ok1 = QInputDialog.getText(self, "계정등록", "아이디:")
        if ok1:
            if len(str(idTxt)) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("아이디가 입력되지 않았습니다.")
                msg.setWindowTitle("Error")
                msg.exec()
            else:
                pwTxt, ok2 = QInputDialog.getText(self, "계정등록", "비밀번호:")
                if ok2:
                    if len(str(pwTxt)) == 0:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.setText("비밀번호가 입력되지 않았습니다.")
                        msg.setWindowTitle("Error")
                        msg.exec()
                    else:
                        print(f"등록예정 계정 : {str(idTxt)} / {str(pwTxt)}")
                        DataHandler().add_user(str(idTxt), str(pwTxt))
                        # self.idCb.clear()

                        # 계정정보 재등록
                        data_handler = DataHandler()
                        user_count = data_handler.get_user_count()
                        print(f"사용자 수: {user_count}")
                        # self.idCb.addItem(f"{str(idTxt)}", f"{str(pwTxt)}")
                        if user_count != 0:
                            for user in data_handler.data["user_info"]:
                                print(f"{user['id']}", f"{user['pw']}")
                            self.idCb.addItem(str(idTxt), str(pwTxt))


    def updateTime(self):
        # 현재 시간 가져오기
        current_time = QTime.currentTime()

        # 시간을 LCD에 표시
        display_text = current_time.toString("h:mm:ss")
        # print(display_text)
        self.currentTimeLbl.setText("현재시간: {}".format(display_text))

    def pass_alert(self):
        try:
            result = driver.switch_to.alert
            result.accept()
        except:
            pass

    def login(self):
        data_handler = DataHandler()

        if data_handler.get_user_count() == 0:
            # 아이디 등록 안내 메시지 표출 : QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("계정정보 등록 후 사용해주세요")
            msg.setWindowTitle("Error")
            msg.exec()
        else:
            id = str(self.idCb.currentText())
            pw = str(self.idCb.currentData())

            logoutUrl = "https://onestop.sejong.go.kr/exsignon/sso/logout.jsp"
            driver.get(logoutUrl)

            # 로그인 버튼 클릭
            print("===== 로그인 버튼 클릭 =====")
            driver.execute_script("sjCombineLogin()")
            # Message: unexpected alert open: {Alert text:
            # 세종 통합예약 시스템은 세종시청과 통합 로그인을 사용합니다.
            # 세종시청 통합 로그인 화면으로 이동합니다.}
            # alert 메시지 제거
            # 지원종료 : driver.switchTo().alert().accept();
            self.pass_alert()

            # 아이디/비밀번호 입력(셀레니엄 라이브러리 느려서 스크립트 대체)
            print("===== 아이디/비밀번호 입력 =====")
            # 셀리니움으로 정보입력
            driver.find_element(By.ID, "id").send_keys(id)
            driver.find_element(By.ID, "password").send_keys(pw)
            # 스크립트로 정보입력
            # driver.execute_script("document.querySelector('#id').value = arguments[0]",str(id))
            # driver.execute_script( "document.querySelector('#password').value = arguments[0]",str(pw))

            print("===== 로그인 시도 =====")
            driver.find_element(By.ID, "login_btn").click()
            # driver.execute_script("document.querySelector('#formLogin').submit()")
            self.pass_alert()
            print("===== 로그인 성공 =====")

    def do_reserve1(self):
        # 예약정보 설정
        date1 = str(self.date1Cb.currentData()).split(",")
        time1 = str(self.time1Cb.currentData())
        date2 = str(self.date2Cb.currentData()).split(",")
        time2 = str(self.time2Cb.currentData())
        tennisPlaceInfo1 = str(self.tennisPlace1Cb.currentData())
        tennisPlaceInfo2 = str(self.tennisPlace2Cb.currentData())
        tennisCourtName1 = str(self.tennisPlace1Cb.currentText())
        tennisCourtName2 = str(self.tennisPlace2Cb.currentText())
        tennisPlace1 = tennisPlaceInfo1.split(",")[0]
        tennisPlace2 = tennisPlaceInfo2.split(",")[0]
        tennisCourt1 = tennisPlaceInfo1.split(",")[1]
        tennisCourt2 = tennisPlaceInfo2.split(",")[1]

        # 예약화면으로 이동
        print("===== 1. 예약화면 이동 =====")
        basicUrl = "https://onestop.sejong.go.kr/Usr/resve/instDetail.do?fcltClCode=FC_TENNIS&oprtnPlanNo="
        driver.get(basicUrl + tennisPlace1 + "&fcltType=SPT&menuName=테니스장")
        print("===== 2. 예약화면 이동 완료 =====")
        time.sleep(actionTime)

        # 날짜 선택
        # scrpit로 실행
        print("===== 3. 날짜 선택 화면 이동=====")
        # fn_selectCalDate('2023', '09', '22', 'OP21695037103696738', 'F17025807221180634', 'Y', '20230919', 'Y');
        driver.execute_script(
            "fn_selectCalDate(arguments[0],arguments[1],arguments[2],arguments[3],arguments[4],arguments[5],arguments[6],arguments[7])",
            date1[1],
            date1[2],
            date1[3],
            tennisPlace1,
            "",
            "Y",
            str(datetime.today().strftime("%Y-%m-%d")),
            "Y",
        )
        print("===== 4. 날짜 선택 화면 이동 완료=====")
        driver.find_element(By.ID, "instDetail_resveDate_btn").click()
        # driver.execute_script("document.querySelector('#instDetail_resveDate_btn').click()")
        print("===== 5. 날짜 선택 성공  =====")
        time.sleep(actionTime)

        # 테니스장/테니스 코트 선택
        # 테니스장 시간 순서 변경으로 실제 시간 READ
        # document.querySelector("span").parentElement.parentElement.onclick()
        print("===== 6. 테니스 코트/시간 선택 시작 =====")

        # "mtitle" 클래스를 가진 모든 span 태그 찾기
        spans = driver.find_elements(By.CLASS_NAME, "mTitle")
        span_texts = [span.text for span in spans]  # span의 텍스트를 리스트로 추출

        print("span_texts : ",span_texts)

        try:
            tennisCourtIndex1 = span_texts.index(tennisCourtName1)  # 배열에서 tennisCourt 변수와 일치하는 요소의 인덱스 찾기
            print(f"'{tennisCourtName1}'의 배열 내 순서: {tennisCourtIndex1}")
        except ValueError:
            print(f"'{tennisCourtName1}'을(를) 찾을 수 없습니다.")

        # driver.execute_script("document.querySelectorAll('#timeSection_' + " + time1 + ")[parseInt(" + tennisCourt1 + ")].click()")
        driver.execute_script(
            "var tempTimeEl = new Array(); document.querySelectorAll('span').forEach(function(arg,idx){ "
            "if(arg.innerText == '" + time1 + "'){ "
            "tempTimeEl.push(arg); }"
            "}); tempTimeEl["
            + str(tennisCourtIndex1)
            + "].parentElement.parentElement.onclick();"
        )
        print("===== 6. 테니스 코트/시간 선택 완료 =====")
        time.sleep(actionTime)

        try:
            print("===== 6.1. 테니스 코트/시간 선택 시작 =====")
            driver.find_element(By.ID, "instDetail_resveTime_btn").click()
            time.sleep(actionTime)
            print("===== 6.1. 테니스 코트/시간 선택 완료 =====")
        except Exception as e:
            print("===== 8. 예약실패(1/2) > 2차 예약 실시1 =====")
            if self.reserveChbox2.isChecked():
                self.do_reserve2()
            print("8. 예외 발생(1/2) ", e)
            return

        try:
            print("===== 7. 동의 및 예약시도(1/2) =====")
            driver.find_element(By.ID, "agree1").click()
            time.sleep(0.2)
            driver.find_element(By.ID, "agree2").click()
            time.sleep(0.2)
            driver.find_element(By.NAME, "btnWrap01").click()
            time.sleep(actionTime)
            print("===== 8. 예약가능(1/2) =====")
        except Exception as e:
            print("===== 8. 예약실패(1/2) > 2차 예약 실시2 =====")
            if self.reserveChbox2.isChecked():
                self.do_reserve2()
            print("8. 예외 발생(1/2) ", e)
            return

        # 이용안내 동의 및 예약 사유 화면이동
        print("===== 9. 매크로 알림창 동의 체크 시작 =====")
        driver.find_element(By.ID, "agreeCheck").click()
        print("===== 10. 매크로 알림창 동의 체크 완료 =====")
        time.sleep(inputTime)
        driver.find_element(
            By.XPATH, '//*[@id="mb-row"]/div/div/div/div/button'
        ).click()
        print("===== 11. 매크로 알림창 동의 확인 완료 =====")
        time.sleep(inputTime)

        # 예약사유 입력
        print("===== 12. 이용안내 동의 및 예약 사유 화면이동 =====")
        # driver.find_element(By.ID, "infoYn").send_keys('pass')
        driver.find_element(
            By.XPATH, '//*[@id="content"]/div[3]/div[4]/div/div[1]/a/div'
        ).click()
        print("===== 13. 이용안내 동의 확인 완료 =====")
        time.sleep(inputTime)
        driver.find_element(By.ID, "resveResn").send_keys("개인운동")
        print("===== 14. 예약사유 입력 완료 =====")
        time.sleep(inputTime)

        # 유의사항 동의 및 예약
        driver.find_element(By.ID, "goReservation").click()
        print("===== 15. 예약버튼 클릭 완료 =====")
        time.sleep(actionTime)
        # driver.find_element(By.CLASS_NAME, "mb-control-yes").click()
        # print("===== 16. 안내창 체크 완료 =====")
        time.sleep(actionTime)
        driver.find_element(
            By.XPATH, '//*[@id="mb-row"]/div/div/div/div/button[1]'
        ).click()
        print("===== 17. 결제 안내창 확인 완료 =====")
        time.sleep(actionTime)
        print("===== 18. 예약완료 =====")
        if self.reserveChbox2.isChecked():
            self.do_reserve2()

    def do_reserve2(self):
        # 예약정보 설정
        date1 = str(self.date1Cb.currentData()).split(",")
        time1 = str(self.time1Cb.currentData())
        date2 = str(self.date2Cb.currentData()).split(",")
        time2 = str(self.time2Cb.currentData())
        tennisPlaceInfo1 = str(self.tennisPlace1Cb.currentData())
        tennisPlaceInfo2 = str(self.tennisPlace2Cb.currentData())
        tennisCourtName1 = str(self.tennisPlace1Cb.currentText())
        tennisCourtName2 = str(self.tennisPlace2Cb.currentText())
        tennisPlace1 = tennisPlaceInfo1.split(",")[0]
        tennisPlace2 = tennisPlaceInfo2.split(",")[0]
        tennisCourt1 = tennisPlaceInfo1.split(",")[1]
        tennisCourt2 = tennisPlaceInfo2.split(",")[1]

        # 예약화면으로 이동
        print("===== 1. 예약화면 이동 =====")
        basicUrl = "https://onestop.sejong.go.kr/Usr/resve/instDetail.do?fcltClCode=FC_TENNIS&oprtnPlanNo="
        driver.get(basicUrl + tennisPlace2 + "&fcltType=SPT&menuName=테니스장")
        print("===== 2. 예약화면 이동 완료 =====")
        time.sleep(actionTime)

        # 날짜 선택
        # scrpit로 실행
        print("===== 3. 날짜 선택 화면 이동=====")
        # fn_selectCalDate('2023', '09', '22', 'OP21695037103696738', 'F17025807221180634', 'Y', '20230919', 'Y');
        driver.execute_script(
            "fn_selectCalDate(arguments[0],arguments[1],arguments[2],arguments[3],arguments[4],arguments[5],arguments[6],arguments[7])",
            date2[1],
            date2[2],
            date2[3],
            tennisPlace2,
            "",
            "Y",
            str(datetime.today().strftime("%Y-%m-%d")),
            "Y",
        )
        print("===== 4. 날짜 선택 화면 이동 완료=====")
        driver.find_element(By.ID, "instDetail_resveDate_btn").click()
        # driver.execute_script("document.querySelector('#instDetail_resveDate_btn').click()")
        print("===== 5. 날짜 선택 성공  =====")
        time.sleep(actionTime)

        # 테니스장/테니스 코트 선택
        # 테니스장 시간 순서 변경으로 실제 시간 READ
        # document.querySelector("span").parentElement.parentElement.onclick()
        print("===== 6. 테니스 코트/시간 선택 시작 =====")
        # driver.execute_script("document.querySelectorAll('#timeSection_' + " + time1 + ")[parseInt(" + tennisCourt1 + ")].click()")

        # "mtitle" 클래스를 가진 모든 span 태그 찾기
        spans = driver.find_elements(By.CLASS_NAME, "mTitle")
        span_texts = [span.text for span in spans]  # span의 텍스트를 리스트로 추출

        try:
            tennisCourtIndex2 = span_texts.index(tennisCourtName2)  # 배열에서 tennisCourt 변수와 일치하는 요소의 인덱스 찾기
            print(f"'{tennisCourtName2}'의 배열 내 순서: {tennisCourtIndex2}")
        except ValueError:
            print(f"'{tennisCourtName2}'을(를) 찾을 수 없습니다.")

        # driver.execute_script("document.querySelectorAll('#timeSection_' + " + time1 + ")[parseInt(" + tennisCourt1 + ")].click()")
        driver.execute_script(
            "var tempTimeEl = new Array(); document.querySelectorAll('span').forEach(function(arg,idx){ "
            "if(arg.innerText == '" + time1 + "'){ "
                                              "tempTimeEl.push(arg); }"
                                              "}); tempTimeEl["
            + str(tennisCourtIndex2)
            + "].parentElement.parentElement.onclick();"
        )
        print("===== 6. 테니스 코트/시간 선택 완료 =====")
        time.sleep(actionTime)

        try:
            print("===== 6.1. 테니스 코트/시간 선택 시작 =====")
            driver.find_element(By.ID, "instDetail_resveTime_btn").click()
            time.sleep(actionTime)
            print("===== 6.1. 테니스 코트/시간 선택 완료 =====")
        except Exception as e:
            print("===== 8. 예약실패(2/2) > 2차 예약 실시1 =====")
            # self.do_reserve2()
            print("8. 예외 발생(2/2) ", e)
            return

        try:
            print("===== 7. 동의 및 예약시도(2/2) =====")
            driver.find_element(By.ID, "agree1").click()
            time.sleep(actionTime)
            driver.find_element(By.ID, "agree2").click()
            time.sleep(actionTime)
            driver.find_element(By.NAME, "btnWrap01").click()
            time.sleep(actionTime)
            print("===== 8. 예약가능(2/2) =====")
        except Exception as e:
            print("===== 8. 예약실패(2/2) > 2차 예약 실시2 =====")
            # self.do_reserve2()
            print("8. 예외 발생(1/2) ", e)
            return

        # 이용안내 동의 및 예약 사유 화면이동
        print("===== 9. 매크로 알림창 동의 체크 시작 =====")
        driver.find_element(By.ID, "agreeCheck").click()
        print("===== 10. 매크로 알림창 동의 체크 완료 =====")
        time.sleep(inputTime)
        driver.find_element(
            By.XPATH, '//*[@id="mb-row"]/div/div/div/div/button'
        ).click()
        print("===== 11. 매크로 알림창 동의 확인 완료 =====")
        time.sleep(inputTime)

        # 예약사유 입력
        print("===== 12. 이용안내 동의 및 예약 사유 화면이동 =====")
        # driver.find_element(By.ID, "infoYn").send_keys('pass')
        driver.find_element(
            By.XPATH, '//*[@id="content"]/div[3]/div[4]/div/div[1]/a/div'
        ).click()
        print("===== 13. 이용안내 동의 확인 완료 =====")
        time.sleep(inputTime)
        driver.find_element(By.ID, "resveResn").send_keys("개인운동")
        print("===== 14. 예약사유 입력 완료 =====")
        time.sleep(inputTime)

        # 유의사항 동의 및 예약
        driver.find_element(By.ID, "goReservation").click()
        print("===== 15. 예약버튼 클릭 완료 =====")
        time.sleep(actionTime)
        # driver.find_element(By.CLASS_NAME, "mb-control-yes").click()
        # print("===== 16. 안내창 체크 완료 =====")
        time.sleep(actionTime)
        driver.find_element(
            By.XPATH, '//*[@id="mb-row"]/div/div/div/div/button[1]'
        ).click()
        print("===== 17. 결제 안내창 확인 완료 =====")
        time.sleep(actionTime)
        print("===== 18. 예약완료 =====")

        # 예약목록
        driver.execute_script("fn_goMyPage('/Usr/resve/myPage.do')")

    def btn_reserve_self(self):
        print("===== 예약정보 =====")
        print(
            "1. 날짜1 - input3 : " + self.date1Cb.currentText(),
            self.date1Cb.currentData(),
        )
        print(
            "2. 시간1 - input4 : " + self.time1Cb.currentText(),
            self.time1Cb.currentData(),
        )
        print(
            "3. 날짜2 - input5 : " + self.date2Cb.currentText(),
            self.date2Cb.currentData(),
        )
        print(
            "4. 시간2 - input6 : " + self.time2Cb.currentText(),
            self.time2Cb.currentData(),
        )
        print(
            "5. 테니스장1 - input7 : " + self.tennisPlace1Cb.currentText(),
            self.tennisPlace1Cb.currentData(),
        )
        print(
            "6. 테니스장2 - input8 : " + self.tennisPlace2Cb.currentText(),
            self.tennisPlace2Cb.currentData(),
        )

        """  콤보박스 값
        if self.input3.currentText() == '':
            one_text = self.input3.currentText()
            self.stat.setText('One : ' + one_text)
        """

        try:
            print("===== 수동 예약을 시작 =====")
            self.do_reserve1()

        except Exception as e:
            print("예외 발생. ", e)
            # self.stat.setText('오류 발생. 종료 후 다시 시도해주세요.')

    def btn_reserve_auto(self):
        print("===== 예약정보 =====")
        print(
            "1. 날짜1 - input3 : " + self.date1Cb.currentText(),
            self.date1Cb.currentData(),
        )
        print(
            "2. 시간1 - input4 : " + self.time1Cb.currentText(),
            self.time1Cb.currentData(),
        )
        print(
            "3. 날짜2 - input5 : " + self.date2Cb.currentText(),
            self.date2Cb.currentData(),
        )
        print(
            "4. 시간2 - input6 : " + self.time2Cb.currentText(),
            self.time2Cb.currentData(),
        )
        print(
            "5. 테니스장1 - input7 : " + self.tennisPlace1Cb.currentText(),
            self.tennisPlace1Cb.currentData(),
        )
        print(
            "6. 테니스장2 - input8 : " + self.tennisPlace2Cb.currentText(),
            self.tennisPlace2Cb.currentData(),
        )

        set_reserve_time = self.timeEdit.time().toString(
            "HH:mm:ss"
        )  # 예약 시간을 설정하세요 (HH:MM:SS 형식)
        now_time = datetime.today().strftime("%H:%M:%S")
        print("예약 설정 시간:", set_reserve_time)
        print("현재 시간:", now_time)
        if set_reserve_time < now_time:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("자동 예약 설정시간이 현재시간보다 이전입니다.")
            msg.setWindowTitle("Error")
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("자동 예약이 시작되었습니다.")
            msg.setWindowTitle("Error")
            msg.exec()
            # 타이머 객체를 생성하고 1초마다 타이머가 만료될 때 check_reservation_time 함수를 호출합니다.
            self.timer = QTimer()
            self.timer.timeout.connect(self.check_reservation_time)

            # 타이머를 시작합니다.
            self.timer.start(1000)  # 1초마다 타이머가 만료되도록 설정합니다.

    def check_reservation_time(self):
        print("===== 자동 예약을 시작 =====")
        set_reserve_time = self.timeEdit.time().toString(
            "HH:mm:ss"
        )  # 예약 시간을 설정하세요 (HH:MM:SS 형식)
        now_time = datetime.today().strftime("%H:%M:%S")
        print("예약 설정 시간:", set_reserve_time)
        print("현재 시간:", now_time)

        if set_reserve_time == now_time:
            self.timer.stop()  # 예약이 시작되면 타이머를 중지합니다.
            self.do_reserve1()

    def btn_reserve_auto_stop(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("자동 예약이 중지되었습니다.")
        msg.setWindowTitle("Error")
        msg.exec()
        self.autoReservationRunning = False
        self.timer.stop()  # 타이머를 중지합니다.

    # 다크테마 적용
    # qdarktheme.setup_theme()
    def toggleTheme(self):
        # 현재 다크 테마인지 확인
        if self.darkModeChBox.isChecked():
            # 다크 테마로 전환
            self.setStyleSheet(qdarktheme.load_stylesheet())
        else:
            self.setStyleSheet("")


app = QApplication(sys.argv)


window = MainWindow()
window.show()

# 이벤트 루프 시작
app.exec()
