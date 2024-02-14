# -*- coding: utf-8 -*-
# UI 변환 명령어 : pyside6-uic ./tennisHelper.ui -p tennisHelper_UI.py > UI2PY.py
# EXE 변환 명령어(Window) :  pyinstaller -w -F --icon=sejong_chn.ico -n tennisHelper tennisHelper.py
# EXE 변환 명령어(Window) :  pyinstaller -w -F --icon=sejong_eng.ico --onefile -n tennisHelper tennisHelper_ui.py
# python -m pyinstallerui
import uuid
from datetime import datetime
import time

from PyQt6.QtWidgets import QMessageBox, QTimeEdit, QDialog

# 다크테마 사용법 : pip install pyqtdarktheme
import qdarktheme

from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QRect,
    QTime,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
)
from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer

import sys

# 셀레니엄
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#
from divided_app.dataHandler import DataHandler
from divided_app.autoUpdate import AutoUpdate
from reserve_fnc import Reservation


##################################################
# 크롬 드라이버 시작
##################################################
options = Options()
options.add_argument("--incognito")
options.add_experimental_option("detach", True)  # 브라우저 바로 닫힘 방지
options.add_experimental_option("excludeSwitches", ["enable-logging"])  # 불필요한 메시지 제거

# 페이지 로드 전략을 'eager'로 설정
options.page_load_strategy = "eager"

# WebDriver 초기화
driver = webdriver.Chrome(options=options)

# 세종시 통합예약시스템 접속
driver.get("https://onestop.sejong.go.kr/Usr/main/main.do")
# 페이지 로딩을 기다려 주자!
driver.implicitly_wait(time_to_wait=1)
# 브라우저 창 크기 설정 (너비 x 높이)
driver.set_window_size(1200, 800)

# 팝업창 닫기
# driver.execute_script("$('#mb-row').css('display','none')")

# 쿠키 설정 팝업창(의미없음 - 쿠키설정 테스트)
# driver.add_cookie({"name": "main_layerPopOneDayCk", "value": "Y"})
##################################################
# 크롬 드라이버 종료
##################################################

# 액션 후 지연시간 : 돔생성 후 버튼 동작하기 위해
actionTime = 0.7
actionTime2 = 0.7


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
    def __init__(self) -> None:
        # 프로그램 실행
        super().__init__()

        # UI 설정 및 초기화
        self.init_Ui()

        # 창위치 변경
        self.move(1350, 200)

        # dataHandler 로드
        self.data_handler = DataHandler()
        # reserve_fnc 로드
        # self.reserve_fnc = Reservation()
        self.reserve_fnc = Reservation(lambda: self.do_reserve(1))  # 콜백 함수 전달

        # autoUpdate 로드
        self.autoUpdate = AutoUpdate()
        # 콤보 박스 업데이트
        self.data_handler.set_Data_Ui(self)

        # 현재시간 설정, 타이머 설정 (1초마다 업데이트)가
        timer = QTimer(self.centralwidget)
        timer.timeout.connect(self.updateTime)
        timer.start(1000)

        # 업데이트 확인
        update_Check_Info = self.autoUpdate.check_Version()
        print("[tennisHelper_ui-__init__] update_Check_Info : ", update_Check_Info)
        if update_Check_Info["messageCode"] == "UPDATE":
            self.show_information_message(
                update_Check_Info["header"], update_Check_Info["message"]
            )
            driver.quit()
            # self.autoUpdate.download_and_execute()
        elif update_Check_Info["messageCode"] == "NOUPDATE":
            self.show_information_message(
                update_Check_Info["header"], update_Check_Info["message"]
            )
        else:
            self.show_information_message(
                update_Check_Info["header"], update_Check_Info["message"]
            )
            driver.quit()
            sys.exit()

        # 사용자 인증(키체크)
        self.auth_User_Info()

        # 아이디 등록 안내 메시지 표출 : QMessageBox
        if self.data_handler.get_user_count() == 0:
            QMessageBox.information(self, "계정등록 안내", "등록된 계정이 없습니다.\n계정정보 등록 후 사용해 주세요")

    def init_Ui(self):
        # 앱 타이틀
        # self.setWindowTitle(f"세종시 통합예약 시스템 도우미 v{current_version}")
        self.setWindowModality(Qt.NonModal)

        ##################################################
        # UI 시작
        ##################################################
        self.resize(485, 861)
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.titleLbl = QLabel(self.centralwidget)
        self.titleLbl.setObjectName("titleLbl")
        self.titleLbl.setGeometry(QRect(20, 10, 351, 41))
        font = QFont()
        font.setPointSize(18)
        self.titleLbl.setFont(font)
        self.accountGb = QGroupBox(self.centralwidget)
        self.accountGb.setObjectName("accountGb")
        self.accountGb.setGeometry(QRect(30, 60, 431, 71))
        font1 = QFont()
        font1.setPointSize(13)
        self.accountGb.setFont(font1)
        self.idLbl = QLabel(self.accountGb)
        self.idLbl.setObjectName("idLbl")
        self.idLbl.setGeometry(QRect(30, 30, 60, 31))
        self.idLbl.setFont(font1)
        self.idCb = QComboBox(self.accountGb)
        self.idCb.setObjectName("idCb")
        self.idCb.setGeometry(QRect(110, 30, 171, 31))
        self.addAccountBtn = QPushButton(self.accountGb)
        self.addAccountBtn.setObjectName("addAccountBtn")
        self.addAccountBtn.setGeometry(QRect(290, 30, 61, 31))
        font2 = QFont()
        font2.setPointSize(8)
        self.addAccountBtn.setFont(font2)
        self.deleteAccountBtn = QPushButton(self.accountGb)
        self.deleteAccountBtn.setObjectName("deleteAccountBtn")
        self.deleteAccountBtn.setGeometry(QRect(360, 30, 61, 31))
        self.deleteAccountBtn.setFont(font2)
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(260, 150, 60, 16))
        self.reserve1Gb = QGroupBox(self.centralwidget)
        self.reserve1Gb.setObjectName("reserve1Gb")
        self.reserve1Gb.setGeometry(QRect(30, 130, 431, 181))
        self.reserve1Gb.setFont(font1)
        self.date1Lbl = QLabel(self.reserve1Gb)
        self.date1Lbl.setObjectName("date1Lbl")
        self.date1Lbl.setGeometry(QRect(30, 55, 60, 30))
        self.date1Lbl.setFont(font1)
        self.time1Lbl = QLabel(self.reserve1Gb)
        self.time1Lbl.setObjectName("time1Lbl")
        self.time1Lbl.setGeometry(QRect(30, 85, 60, 30))
        self.time1Lbl.setFont(font1)
        self.tennisPlace1Lbl = QLabel(self.reserve1Gb)
        self.tennisPlace1Lbl.setObjectName("tennisPlace1Lbl")
        self.tennisPlace1Lbl.setGeometry(QRect(30, 120, 81, 20))
        self.tennisPlace1Lbl.setFont(font1)
        self.date1Cb = QComboBox(self.reserve1Gb)
        self.date1Cb.setObjectName("date1Cb")
        self.date1Cb.setGeometry(QRect(160, 60, 231, 26))
        self.time1Cb = QComboBox(self.reserve1Gb)
        self.time1Cb.setObjectName("time1Cb")
        self.time1Cb.setGeometry(QRect(160, 90, 231, 26))
        self.tennisPlace1Cb = QComboBox(self.reserve1Gb)
        self.tennisPlace1Cb.setObjectName("tennisPlace1Cb")
        self.tennisPlace1Cb.setGeometry(QRect(160, 120, 231, 26))
        self.reserveYNLbl1 = QLabel(self.reserve1Gb)
        self.reserveYNLbl1.setObjectName("reserveYNLbl1")
        self.reserveYNLbl1.setGeometry(QRect(30, 150, 141, 21))
        self.reserveChkBtn1 = QPushButton(self.reserve1Gb)
        self.reserveChkBtn1.setObjectName("reserveChkBtn1")
        self.reserveChkBtn1.setGeometry(QRect(30, 28, 361, 23))
        font3 = QFont()
        font3.setPointSize(9)
        self.reserveChkBtn1.setFont(font3)
        self.reserveMsgLbl1 = QLabel(self.reserve1Gb)
        self.reserveMsgLbl1.setObjectName("reserveMsgLbl1")
        self.reserveMsgLbl1.setGeometry(QRect(160, 150, 221, 16))
        self.reserve2Gb = QGroupBox(self.centralwidget)
        self.reserve2Gb.setObjectName("reserve2Gb")
        self.reserve2Gb.setGeometry(QRect(30, 320, 431, 181))
        self.reserve2Gb.setFont(font1)
        self.date2Lbl = QLabel(self.reserve2Gb)
        self.date2Lbl.setObjectName("date2Lbl")
        self.date2Lbl.setGeometry(QRect(30, 60, 60, 20))
        self.date2Lbl.setFont(font1)
        self.time2Lbl = QLabel(self.reserve2Gb)
        self.time2Lbl.setObjectName("time2Lbl")
        self.time2Lbl.setGeometry(QRect(30, 90, 60, 20))
        self.time2Lbl.setFont(font1)
        self.tennisPlace2Lbl = QLabel(self.reserve2Gb)
        self.tennisPlace2Lbl.setObjectName("tennisPlace2Lbl")
        self.tennisPlace2Lbl.setGeometry(QRect(30, 120, 81, 20))
        self.tennisPlace2Lbl.setFont(font1)
        self.date2Cb = QComboBox(self.reserve2Gb)
        self.date2Cb.setObjectName("date2Cb")
        self.date2Cb.setGeometry(QRect(160, 60, 231, 26))
        self.time2Cb = QComboBox(self.reserve2Gb)
        self.time2Cb.setObjectName("time2Cb")
        self.time2Cb.setGeometry(QRect(160, 90, 231, 26))
        self.tennisPlace2Cb = QComboBox(self.reserve2Gb)
        self.tennisPlace2Cb.setObjectName("tennisPlace2Cb")
        self.tennisPlace2Cb.setGeometry(QRect(160, 120, 231, 26))
        self.reserveChbox2 = QCheckBox(self.reserve2Gb)
        self.reserveChbox2.setObjectName("reserveChbox2")
        self.reserveChbox2.setGeometry(QRect(100, 2, 21, 16))
        self.reserveYNLbl2 = QLabel(self.reserve2Gb)
        self.reserveYNLbl2.setObjectName("reserveYNLbl2")
        self.reserveYNLbl2.setGeometry(QRect(30, 150, 141, 21))
        self.reserveChkBtn2 = QPushButton(self.reserve2Gb)
        self.reserveChkBtn2.setObjectName("reserveChkBtn2")
        self.reserveChkBtn2.setGeometry(QRect(30, 30, 361, 23))
        self.reserveChkBtn2.setFont(font3)
        self.reserveMsgLbl2 = QLabel(self.reserve2Gb)
        self.reserveMsgLbl2.setObjectName("reserveMsgLbl2")
        self.reserveMsgLbl2.setGeometry(QRect(170, 152, 221, 16))
        self.noticeGb = QGroupBox(self.centralwidget)
        self.noticeGb.setObjectName("noticeGb")
        self.noticeGb.setGeometry(QRect(30, 530, 431, 161))
        self.noticeGb.setFont(font1)
        self.noticeLbl4 = QLabel(self.noticeGb)
        self.noticeLbl4.setObjectName("noticeLbl4")
        self.noticeLbl4.setGeometry(QRect(10, 50, 411, 16))
        self.noticeLbl4.setFont(font3)
        self.noticeLbl1 = QLabel(self.noticeGb)
        self.noticeLbl1.setObjectName("noticeLbl1")
        self.noticeLbl1.setGeometry(QRect(10, 27, 391, 20))
        self.noticeLbl1.setFont(font3)
        self.noticeLbl5 = QLabel(self.noticeGb)
        self.noticeLbl5.setObjectName("noticeLbl5")
        self.noticeLbl5.setGeometry(QRect(10, 70, 411, 16))
        self.noticeLbl5.setFont(font3)
        self.noticeLbl6 = QLabel(self.noticeGb)
        self.noticeLbl6.setObjectName("noticeLbl6")
        self.noticeLbl6.setGeometry(QRect(10, 90, 411, 16))
        self.noticeLbl6.setFont(font3)
        self.noticeLbl8_2 = QLabel(self.noticeGb)
        self.noticeLbl8_2.setObjectName("noticeLbl8_2")
        self.noticeLbl8_2.setGeometry(QRect(10, 110, 411, 16))
        self.noticeLbl8_2.setFont(font3)
        self.noticeLbl8_3 = QLabel(self.noticeGb)
        self.noticeLbl8_3.setObjectName("noticeLbl8_3")
        self.noticeLbl8_3.setGeometry(QRect(10, 130, 411, 16))
        self.noticeLbl8_3.setFont(font3)
        self.coutionLbl = QLabel(self.centralwidget)
        self.coutionLbl.setObjectName("coutionLbl")
        self.coutionLbl.setGeometry(QRect(190, 815, 261, 20))
        font4 = QFont()
        font4.setPointSize(7)
        font4.setBold(False)
        font4.setItalic(True)
        font4.setKerning(True)
        self.coutionLbl.setFont(font4)
        self.line2 = QFrame(self.centralwidget)
        self.line2.setObjectName("line2")
        self.line2.setGeometry(QRect(30, 795, 421, 20))
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.loginBtn = QPushButton(self.centralwidget)
        self.loginBtn.setObjectName("loginBtn")
        self.loginBtn.setGeometry(QRect(40, 705, 181, 41))
        self.loginBtn.setFont(font1)
        self.autoReserveBtn = QPushButton(self.centralwidget)
        self.autoReserveBtn.setObjectName("autoReserveBtn")
        self.autoReserveBtn.setGeometry(QRect(250, 750, 91, 41))
        self.autoReserveBtn.setFont(font3)
        self.selfReserveBtn = QPushButton(self.centralwidget)
        self.selfReserveBtn.setObjectName("selfReserveBtn")
        self.selfReserveBtn.setGeometry(QRect(250, 705, 181, 41))
        self.selfReserveBtn.setFont(font1)
        self.timeEdit = QTimeEdit(self.centralwidget)
        self.timeEdit.setObjectName("timeEdit")
        self.timeEdit.setGeometry(QRect(100, 760, 118, 24))
        self.timeSetLbl = QLabel(self.centralwidget)
        self.timeSetLbl.setObjectName("timeSetLbl")
        self.timeSetLbl.setGeometry(QRect(30, 763, 71, 16))
        self.currentTimeLbl = QLabel(self.centralwidget)
        self.currentTimeLbl.setObjectName("currentTimeLbl")
        self.currentTimeLbl.setGeometry(QRect(30, 815, 131, 16))
        self.stopAutoReserveBtn = QPushButton(self.centralwidget)
        self.stopAutoReserveBtn.setObjectName("stopAutoReserveBtn")
        self.stopAutoReserveBtn.setGeometry(QRect(340, 750, 91, 41))
        self.stopAutoReserveBtn.setFont(font3)
        self.darkModeChBox = QCheckBox(self.centralwidget)
        self.darkModeChBox.setObjectName("darkModeChBox")
        self.darkModeChBox.setGeometry(QRect(380, 25, 81, 16))
        self.devLogLW = QListWidget(self.centralwidget)
        self.devLogLW.setObjectName("devLogLW")
        self.devLogLW.setGeometry(QRect(505, 80, 271, 751))
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)

        QMetaObject.connectSlotsByName(self)
        # setupUi

    def retranslateUi(self, MainWindow):
        self.setWindowTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\uc138\uc885\uc2dc \ud1b5\ud569 \uc608\uc57d \uc2dc\uc2a4\ud15c \ub3c4\uc6b0\ubbf8 ",
                None,
            )
        )
        self.titleLbl.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\uc138\uc885\uc2dc \ud1b5\ud569 \uc608\uc57d \uc2dc\uc2a4\ud15c \ub3c4\uc6b0\ubbf8",
                None,
            )
        )
        self.accountGb.setTitle(
            QCoreApplication.translate("MainWindow", "\uacc4\uc815\uc815\ubcf4", None)
        )
        self.idLbl.setText(
            QCoreApplication.translate("MainWindow", "\uc544\uc774\ub514 : ", None)
        )
        self.addAccountBtn.setText(
            QCoreApplication.translate("MainWindow", "\uacc4\uc815\ub4f1\ub85d", None)
        )
        self.deleteAccountBtn.setText(
            QCoreApplication.translate("MainWindow", "\uacc4\uc815\uc0ad\uc81c", None)
        )
        self.label_3.setText("")
        self.reserve1Gb.setTitle(
            QCoreApplication.translate("MainWindow", "\uc608\uc57d\uc815\ubcf4 1", None)
        )
        self.date1Lbl.setText(
            QCoreApplication.translate("MainWindow", "\ub0a0 \uc9dc : ", None)
        )
        self.time1Lbl.setText(
            QCoreApplication.translate("MainWindow", "\uc2dc \uac04 : ", None)
        )
        self.tennisPlace1Lbl.setText(
            QCoreApplication.translate(
                "MainWindow", "\ud14c\ub2c8\uc2a4\uc7a5 : ", None
            )
        )
        self.reserveYNLbl1.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uac00\ub2a5 \uc5ec\ubd80  : ", None
            )
        )
        self.reserveChkBtn1.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uac00\ub2a5 \uc5ec\ubd80 \ud655\uc778", None
            )
        )
        self.reserveMsgLbl1.setText("")
        self.reserve2Gb.setTitle(
            QCoreApplication.translate("MainWindow", "\uc608\uc57d\uc815\ubcf4 2", None)
        )
        self.date2Lbl.setText(
            QCoreApplication.translate("MainWindow", "\ub0a0 \uc9dc : ", None)
        )
        self.time2Lbl.setText(
            QCoreApplication.translate("MainWindow", "\uc2dc \uac04 : ", None)
        )
        self.tennisPlace2Lbl.setText(
            QCoreApplication.translate(
                "MainWindow", "\ud14c\ub2c8\uc2a4\uc7a5 : ", None
            )
        )
        self.reserveChbox2.setText("")
        self.reserveYNLbl2.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uac00\ub2a5 \uc5ec\ubd80  : ", None
            )
        )
        self.reserveChkBtn2.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uac00\ub2a5 \uc5ec\ubd80 \ud655\uc778", None
            )
        )
        self.reserveMsgLbl2.setText("")
        self.noticeGb.setTitle(
            QCoreApplication.translate("MainWindow", "\uc774\uc6a9\uc548\ub0b4", None)
        )
        self.noticeLbl4.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \ud55c\uac1c \uc608\uc57d\uc2dc, \uc608\uc57d\uc815\ubcf4 1\ub9cc \uc124\uc815,\ub450\uac1c \uc608\uc57d\uc2dc, \uc608\uc57d\uc815\ubcf41,2 \ubaa8\ub450 \uc791\uc131",
                None,
            )
        )
        self.noticeLbl1.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \ucd08\uae30 \ud504\ub85c\uadf8\ub7a8 \uc2e4\ud589 \uc2dc, \uacc4\uc815\ub4f1\ub85d \ud6c4 \ub85c\uadf8\uc778 \ubc0f \uc608\uc57d\ud558\uae30 \uc9c4\ud589",
                None,
            )
        )
        self.noticeLbl5.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \ub85c\uadf8\uc778 \ubc84\ud2bc\uc744 \ud074\ub9ad\ud558\uc5ec \ub85c\uadf8\uc778 \ud6c4, \uc608\uc57d\ud558\uae30 \ubc84\ud2bc\uc744 \ub20c\ub7ec\uc11c \uc608\uc57d",
                None,
            )
        )
        self.noticeLbl6.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \uc608\uc57d\uc2dc\uac04 \uc124\uc815 \ud6c4, \uc790\ub3d9\uc608\uc57d\ud558\uae30 \ud074\ub9ad\uc2dc \uc124\uc815\ub41c \uc2dc\uac04\uc5d0 \uc790\ub3d9\uc73c\ub85c \uc608\uc57d",
                None,
            )
        )
        self.noticeLbl8_2.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- data.dat, data.dat.hash, key.key \ud30c\uc77c \ubcc0\uacbd \ubc0f  \uc0ad\uc81c \uc2dc \uacc4\uc815 \uc7ac\ub4f1\ub85d \ud544\uc694",
                None,
            )
        )
        self.noticeLbl8_3.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \ub2e4\uc815\ub3d9\uacfc \uc804\uc758\uc0dd\ud65c\uacf5\uc6d0\uc758 \uacbd\uc6b0, \uc2dc\uac04\uc774 \ub2e4\ub978 \uad6c\uc7a5\uacfc \ub2e4\ub984 \uc608\uc57d\uc2dc \uc720\uc758",
                None,
            )
        )
        self.coutionLbl.setText(
            QCoreApplication.translate(
                "MainWindow",
                "* \ubd80\uc815 \uc608\uc57d(\ub9e4\ud06c\ub85c)\uc73c\ub85c \uc778\ud55c \ubd88\uc774\uc775 \ubc1c\uc0dd\uc2dc \ucc45\uc784\uc9c0\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.",
                None,
            )
        )
        self.loginBtn.setText(
            QCoreApplication.translate("MainWindow", "\ub85c\uadf8\uc778", None)
        )
        self.autoReserveBtn.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc790\ub3d9\uc608\uc57d\uc2dc\uc791", None
            )
        )
        self.selfReserveBtn.setText(
            QCoreApplication.translate("MainWindow", "\uc608\uc57d\ud558\uae30", None)
        )
        self.timeSetLbl.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uc2dc\uac04 : ", None
            )
        )
        self.currentTimeLbl.setText(
            QCoreApplication.translate(
                "MainWindow", "\ud604\uc7ac\uc2dc\uac04 : ", None
            )
        )
        self.stopAutoReserveBtn.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc790\ub3d9\uc608\uc57d\uc911\uc9c0", None
            )
        )
        self.darkModeChBox.setText(
            QCoreApplication.translate("MainWindow", "\ub2e4\ud06c\ubaa8\ub4dc", None)
        )
        # retranslateUi

        self.dialog = QDialog()
        self.addAccountBtn.clicked.connect(self.addAcount_dialog_open)
        self.deleteAccountBtn.clicked.connect(self.deleteAccount_dialog_open)

        # 예약정보 2 기본 비활성화
        self.reserveChbox2.setChecked(False)
        self.date2Cb.setEnabled(False)
        self.time2Cb.setEnabled(False)
        self.tennisPlace2Cb.setEnabled(False)

        # 버튼 클릭 이벤트
        self.selfReserveBtn.clicked.connect(lambda: self.do_reserve(1))
        self.autoReserveBtn.clicked.connect(self.auto_reserve_check_time)
        self.stopAutoReserveBtn.clicked.connect(self.stop_auto_reserve)
        self.loginBtn.clicked.connect(self.login)
        self.darkModeChBox.stateChanged.connect(self.toggleTheme)
        self.reserveChkBtn1.clicked.connect(self.reserveCheck1)
        self.reserveChkBtn2.clicked.connect(self.reserveCheck2)
        self.reserveChbox2.stateChanged.connect(self.reserveYN2)

        # 자동예약 기본 시간 설정
        self.timeEdit.setDisplayFormat("HH:mm:ss")
        new_time = QTime(8, 59, 58)  # 새로운 시간을 설정합니다.
        self.timeEdit.setTime(new_time)
        selectedTime = self.timeEdit.time().toString()

        # 다크모드 기본 활성화
        self.darkModeChBox.setChecked(True)

    def show_information_message(self, title, message):
        # 기존의 QMessageBox 생성 부분
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        # WindowStaysOnTopHint 설정
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # 모달 대화 상자로 실행
        msg.exec()

    def reserveYN2(self, state):
        # 두번째 예약 활성화/비활성화
        if self.reserveChbox2.isChecked():
            self.date2Cb.setEnabled(True)
            self.time2Cb.setEnabled(True)
            self.tennisPlace2Cb.setEnabled(True)
        else:
            self.date2Cb.setEnabled(False)
            self.time2Cb.setEnabled(False)
            self.tennisPlace2Cb.setEnabled(False)

    def pass_alert(self):
        # Chrome alert() 무시
        try:
            result = driver.switch_to.alert
            result.accept()
        except:
            pass

    def deleteAccount_dialog_open(self):
        idTxt, ok = QInputDialog.getText(self, "계정삭제", "아이디:")
        if ok:
            if len(str(idTxt)) == 0:
                QMessageBox.information(self, "에러", f"아이디가 입력되지 않았습니다.")
            else:
                QMessageBox.information(
                    self, "안내", f"{self.data_handler.delete_user(str(idTxt))}"
                )

                self.idCb.clear()
                # 계정 삭제 후 selectbox 리로드
                if self.data_handler.get_user_count() != 0:
                    for user in self.data_handler.data["user_info"]:
                        self.idCb.addItem(f"{user['id']}", f"{user['pw']}")

    def addAcount_dialog_open(self):
        idTxt, ok1 = QInputDialog.getText(self, "계정등록", "아이디:")
        if ok1:
            if len(str(idTxt)) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("[tennisHelper_ui-addAcount_dialog_open] 아이디가 입력되지 않았습니다.")
                msg.setWindowTitle("Error")
                msg.exec()
            else:
                pwTxt, ok2 = QInputDialog.getText(self, "계정등록", "비밀번호:")
                if ok2:
                    if len(str(pwTxt)) == 0:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Icon.Critical)
                        msg.setText("[tennisHelper_ui-addAcount_dialog_open] 비밀번호가 입력되지 않았습니다.")
                        msg.setWindowTitle("Error")
                        msg.exec()
                    else:
                        print(f"[tennisHelper_ui-addAcount_dialog_open] 등록예정 계정 : {str(idTxt)} / {str(pwTxt)}")
                        DataHandler().add_user(str(idTxt), str(pwTxt))
                        print(f"[tennisHelper_ui-addAcount_dialog_open] 계정추가 테스트 성공 1 {self.idCb.count()}")
                        # 계정정보 모두 삭제
                        self.idCb.clear()
                        # 계정 등록 후 selectbox 리로드
                        data_handler = DataHandler()
                        if data_handler.get_user_count() != 0:
                            for user in data_handler.data["user_info"]:
                                self.idCb.addItem(f"{user['id']}", f"{user['pw']}")

                        print(f"[tennisHelper_ui-addAcount_dialog_open] 계정추가 테스트 성공 2 {self.idCb.count()}")
                        '''
                        if isinstance(self.idCb, QComboBox):
                            print(f"[tennisHelper_ui-addAcount_dialog_open] 계정추가 테스트 성공 ")
                            self.idCb.addItem(str(idTxt), str(pwTxt))
                            # self.idCb는 QComboBox의 인스턴스입니다.
                            # 여기에 원하는 작업을 수행하세요.
                        else:
                            print(f"[tennisHelper_ui-addAcount_dialog_open] 계정추가 테스트 오류발생 ")
                            # self.idCb는 QComboBox의 인스턴스가 아닙니다.
                            # 다른 처리 방식이 필요할 수 있습니다.


                        
                        self.dataHandler = DataHandler()
                        if self.dataHandler.get_user_count() != 0:
                            for user in self.dataHandler.data["user_info"]:
                                print(f"[tennisHelper_ui-addAcountComplete] ID : {user['id']}, PW : {user['pw']}")
                                self.idCb.addItem(f"{user['id']}", f"{user['pw']}")
                            print(
                                f"[tennisHelper_ui-addAcount_dialog_open] 계정등록 완료-계정 갯수 : {self.data_handler.get_user_count()}"
                            )
                        '''

    def updateTime(self):
        # 현재 시간 가져오기
        current_time = QTime.currentTime()

        # 시간을 LCD에 표시
        display_text = current_time.toString("hh:mm:ss")
        # print(display_text)
        self.currentTimeLbl.setText("현재시간: {}".format(display_text))

    # reserve_fnc.py
    def auto_reserve_check_time(self):
        # QTimeEdit에서 시간 가져오기
        setting_Time = self.timeEdit.time()

        # 현재 시간 가져오기
        current_time = QTime.currentTime()

        print(f"현재시간 : {current_time} /설정시간 : {setting_Time}")
        """
        # 현재 시간과 비교
        if current_time > setting_Time:
            QMessageBox.information(self, "자동예약오류",f"설정 된 시간이 주어진 시간보다 이전입니다.")
            return
        """

        # 자동 예약 시간
        auto_Time_Value = self.timeEdit.time().toString("hh:mm:ss")
        self.reserve_fnc.auto_reserve_start_timer(auto_Time_Value)

    def stop_auto_reserve(self):
        QMessageBox.information(self, "자동예약안내", f"자동예약이 중지되었습니다.")
        self.reserve_fnc.auto_reserve_stop_timer()

    def toggleTheme(self):
        # 현재 다크 테마인지 확인
        if self.darkModeChBox.isChecked():
            # 다크 테마로 전환
            self.setStyleSheet(qdarktheme.load_stylesheet())
        else:
            self.setStyleSheet("")

    def reserveCheck1(self):
        oprtnPlanNo = str(self.tennisPlace1Cb.currentData()).split(",")[0]
        sYear = str(self.date1Cb.currentText()).split("-")[0]
        sMonth = str(self.date1Cb.currentText()).split("-")[1]
        sDay = str(self.date1Cb.currentText()).split("-")[2]
        tennis_schedule = self.data_handler.fcltList(oprtnPlanNo, sYear, sMonth, sDay)

        self.tennis_window = TennisScheduleWindow(tennis_schedule)
        self.tennis_window.show()

    def reserveCheck2(self):
        oprtnPlanNo = str(self.tennisPlace2Cb.currentData()).split(",")[0]
        sYear = str(self.date2Cb.currentText()).split("-")[0]
        sMonth = str(self.date2Cb.currentText()).split("-")[1]
        sDay = str(self.date2Cb.currentText()).split("-")[2]
        tennis_schedule = self.data_handler.fcltList(oprtnPlanNo, sYear, sMonth, sDay)

        self.tennis_window = TennisScheduleWindow(tennis_schedule)
        self.tennis_window.show()

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
            print("[tennisHelper-login]] 로그인 버튼 클릭")
            # driver.execute_script("sjCombineLogin()")
            # WebDriverWait를 사용하여 원하는 요소가 나타날 때까지 기다립니다.
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//a[text()='로그인']"))
            )
            driver.execute_script("sjCombineLogin()")
            # driver.find_element(By.XPATH, f"//a[text()='로그인']").click()

            # alert 메시지 제거
            # 지원종료 : driver.switchTo().alert().accept();
            self.pass_alert()

            # 아이디/비밀번호 입력(셀레니엄 라이브러리 느려서 스크립트 대체)
            print("[tennisHelper-login]] 아이디/비밀번호 입력")
            # 셀리니움으로 정보입력
            driver.find_element(By.ID, "id").send_keys(id)
            driver.find_element(By.ID, "password").send_keys(pw)
            # 스크립트로 정보입력
            # driver.execute_script("document.querySelector('#id').value = arguments[0]",str(id))
            # driver.execute_script( "document.querySelector('#password').value = arguments[0]",str(pw))

            print("[tennisHelper-login]] 로그인 시도")
            driver.find_element(By.ID, "login_btn").click()
            # driver.execute_script("document.querySelector('#formLogin').submit()")
            self.pass_alert()
            print("[tennisHelper-login]] 로그인 성공")

    def auth_User_Info(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        mac_address = ":".join([mac[e : e + 2] for e in range(0, 11, 2)])
        auth_result = self.data_handler.auth_user_info_DB(mac_address)
        print(
            f"[tennisHelper_ui-auth_User_Info] mac_address : {mac_address}, auth_result : {auth_result}"
        )

        if auth_result["code"] == "FAIL":
            QMessageBox.information(self, "경고", f"{auth_result['message']}")
            keyTxt, ok = QInputDialog.getText(self, "프로그램 등록", "KEY:")
            if ok:
                if len(str(keyTxt)) == 0:
                    QMessageBox.information(self, "에러", f"프로그램 키가 입력되지 않았습니다.")
                    sys.exit(1)
                else:
                    resultText = self.data_handler.upsert_user_info_DB(
                        self.data_handler.get_computer_info, str(keyTxt)
                    )

                    if resultText == "COMPLETE":
                        QMessageBox.information(self, "안내", f"등록이 완료되었습니다.")
                    elif resultText == "EXIST":
                        QMessageBox.information(self, "안내", f"이미 등록된 사용자가 존재합니다.")
                        sys.exit(1)
                    elif resultText == "FAIL":
                        QMessageBox.information(self, "안내", f"키가 일치 하지 않습니다.")
                        sys.exit(1)
                    else:
                        QMessageBox.information(self, "안내", f"서버와 연결이 원활하지 않습니다.")
                        sys.exit(1)
            else:
                sys.exit(1)
        elif auth_result["code"] == "ERROR":
            QMessageBox.information(self, "경고", f"{auth_result['message']}")
            sys.exit(1)
        else:
            print(f"[tennisHelper_ui-auth_User_Info] 승인된 사용자 입니다.")

    ####################################################
    # 예약하기
    ####################################################
    def do_reserve(self, reserve_Info_Num):
        # 예약정보 설정
        reservationData = {}
        if reserve_Info_Num == 1:
            reservationData["date"] = str(self.date1Cb.currentData()).split(",")
            reservationData["time"] = str(self.time1Cb.currentData())
            reservationData["tennisPlace"] = str(
                self.tennisPlace1Cb.currentData()
            ).split(",")[0]
            reservationData["tennisCourt"] = str(
                self.tennisPlace1Cb.currentData()
            ).split(",")[1]
        elif reserve_Info_Num == 2:
            reservationData["date"] = str(self.date2Cb.currentData()).split(",")
            reservationData["time"] = str(self.time2Cb.currentData())
            reservationData["tennisPlace"] = str(
                self.tennisPlace2Cb.currentData()
            ).split(",")[0]
            reservationData["tennisCourt"] = str(
                self.tennisPlace2Cb.currentData()
            ).split(",")[1]

        print(
            f"[tennisHelper_ui.py-do_reserve({reserve_Info_Num})] 예약정보 설정완료 reservationData : {reservationData}"
        )

        # 예약화면으로 이동
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예약화면으로 이동 시작")
        basicUrl = "https://onestop.sejong.go.kr/Usr/resve/instDetail.do?fcltClCode=FC_TENNIS&oprtnPlanNo="
        driver.get(
            basicUrl + reservationData["tennisPlace"] + "&fcltType=SPT&menuName=테니스장"
        )
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예약화면으로 이동 완료")
        if actionTime2 > 0:
            time.sleep(actionTime2)

        # 날짜 선택
        # scrpit로 실행
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 날짜 선택 화면 이동 시작")
        # 예시 : fn_selectCalDate('2023', '09', '22', 'OP21695037103696738', 'F17025807221180634', 'Y', '20230919', 'Y');
        driver.execute_script(
            "fn_selectCalDate(arguments[0],arguments[1],arguments[2],arguments[3],arguments[4],arguments[5],arguments[6],arguments[7])",
            reservationData["date"][1],
            reservationData["date"][2],
            reservationData["date"][3],
            reservationData["tennisPlace"],
            "",
            "Y",
            str(datetime.today().strftime("%Y-%m-%d")),
            "Y",
        )
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 날짜 선택 화면 이동 완료")
        if actionTime2 > 0:
            time.sleep(actionTime2)

        calendatDateBtn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "instDetail_resveDate_btn"))
        )
        calendatDateBtn.click()

        # driver.execute_script("document.querySelector('#instDetail_resveDate_btn').click()")
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 날짜 선택 성공  =====")
        if actionTime2 > 0:
            time.sleep(actionTime2)

        # 테니스장/테니스 코트 선택
        # 테니스장 시간 순서 변경으로 실제 시간 READ
        # document.querySelector("span").parentElement.parentElement.onclick()
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 테니스 코트/시간 선택 시작")
        # driver.execute_script("document.querySelectorAll('#timeSection_' + " + time1 + ")[parseInt(" + tennisCourt1 + ")].click()")
        """
        driver.execute_script(
            
            var tempTimeEl = new Array();
            document.querySelectorAll('span').forEach(function(arg,idx){
                if(arg.innerText == reservationData['time']){
                    tempTimeEl.push(arg); 
                }
            });
            tempTimeEl[reservationData['tennisCourt']].parentElement.parentElement.onclick();
            
        )
        
        # 원하는 텍스트를 가진 span 태그들을 찾기
        matching_spans = []
        spans = driver.find_elements(By.TAG_NAME, "span")
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] {reservationData['time']} 선택")
        for span in spans:
            if span.text == reservationData['time']:
                matching_spans.append(span)

        # 시간 선택
        time_Button = matching_spans[int(reservationData['tennisCourt'])]
        time_Button.click()
        """

        # WebDriverWait를 사용하여 원하는 요소가 나타날 때까지 기다립니다.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//span[text()='{reservationData['time']}']")
            )
        )
        if actionTime2 > 0:
            time.sleep(actionTime)

        # 더 구체적인 선택자 사용
        matching_spans = driver.find_elements(
            By.XPATH, f"//span[text()='{reservationData['time']}']"
        )

        # 코트/시간 선택 및 클릭
        matching_spans[int(reservationData["tennisCourt"])].click()
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 테니스 코트/시간 선택 완료")
        time.sleep(actionTime)

        try:
            print(
                f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 오른쪽 하단 다음버튼 클릭하여 메시지 박스(매크로 안내문구) 활성화 시작"
            )
            instDetail_resveTime_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "instDetail_resveTime_btn"))
            )
            instDetail_resveTime_btn.click()
            if actionTime2 > 0:
                time.sleep(actionTime2)
            print(
                f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 오른쪽 하단 다음버튼 클릭하여 메시지 박스(매크로 안내문구) 활성화 완료"
            )
        except Exception as e:
            print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예약실패")
            if self.reserveChbox2.isChecked():
                if (reserve_Info_Num == 1) and (self.reserveChbox2.isChecked()):
                    time.sleep(actionTime)
                    self.do_reserve(2)
            print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예외 발생 : {e}")
            return

        try:
            print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 동의 및 예약 ")
            agree1 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "agree1"))
            )
            agree1.click()
            if actionTime2 > 0:
                time.sleep(actionTime2)
            agree2 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "agree2"))
            )
            agree2.click()
            if actionTime2 > 0:
                time.sleep(actionTime2)
            btnWrap01 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "btnWrap01"))
            )
            btnWrap01.click()
            if actionTime2 > 0:
                time.sleep(actionTime2)
            print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예약가능")
        except Exception as e:
            print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예약실패")
            if (reserve_Info_Num == 1) and (self.reserveChbox2.isChecked()):
                time.sleep(actionTime)
                self.do_reserve(2)
            print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예외 발생 : {e}")
            return

        # 이용안내 동의 및 예약 사유 화면이동
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 매크로 알림창 동의 체크 시작")
        agreeCheck = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "agreeCheck"))
        )
        agreeCheck.click()
        if actionTime2 > 0:
            time.sleep(actionTime2)
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 매크로 알림창 동의 체크 완료")

        macro_alert = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="mb-row"]/div/div/div/div/button')
            )
        )
        macro_alert.click()
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 매크로 알림창 동의 확인 완료")
        if actionTime2 > 0:
            time.sleep(actionTime2)

        # 예약사유 입력
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 이용안내 동의 및 예약 사유 화면이동")
        # driver.find_element(By.ID, "infoYn").send_keys('pass')
        macro_final = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="content"]/div[3]/div[4]/div/div[1]/a/div')
            )
        )
        macro_final.click()

        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 이용안내 동의 확인 완료")
        if actionTime2 > 0:
            time.sleep(actionTime2)

        driver.find_element(By.ID, "resveResn").send_keys("개인운동")
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예약사유 입력 완료")
        if actionTime2 > 0:
            time.sleep(actionTime2)

        # 유의사항 동의 및 예약
        goReservation = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "goReservation"))
        )
        goReservation.click()
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예약버튼 클릭 완료")
        # time.sleep(actionTime)
        # driver.find_element(By.CLASS_NAME, "mb-control-yes").click()
        # print("===== 16. 안내창 체크 완료 =====")
        if actionTime2 > 0:
            time.sleep(actionTime2)
        finl_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="mb-row"]/div/div/div/div/button[1]')
            )
        )
        finl_btn.click()

        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 결제 안내창 확인 완료")
        if actionTime2 > 0:
            time.sleep(actionTime2)
        print(f"[tennisHelper_ui-do_reserve({reserve_Info_Num})] 예약완료")
        if (reserve_Info_Num == 1) and (self.reserveChbox2.isChecked()):
            time.sleep(actionTime)
            self.do_reserve(2)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

# 이벤트 루프 시작
app.exec()
