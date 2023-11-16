# -*- coding: utf-8 -*-
# UI 변환 명령어 : pyside6-uic ./tennisHelper.ui -p tennisHelper_UI.py >> UI2PY1.py
# UI 변환 명령어 : pyside6-uic ./addAccountDialog.ui -p addAccountDialog.py >> UI2PY2.py
# EXE 변환 명령어(MAC) : pyinstaller -w -F --icon=sejong_eng.ico -n tennisHelper tennisHelper.py
# EXE 변환 명령어(Window) :  pyinstaller -w -F --icon=sejong_eng.ico -n tennisHelper_v tennisHelper.py

import mariadb
import getpass
import hashlib
import subprocess
import urllib

import requests
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QProcess
from PyQt6.QtWidgets import QMessageBox, QTimeEdit, QDialog
from cryptography.fernet import Fernet

# 다크테마 사용법 : pip install pyqtdarktheme
import qdarktheme


import json
import uuid
import platform
import smtplib
from email.message import EmailMessage
import socket

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import *

from PySide6.QtCore import QTimer

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

# 팝업창 닫기
# driver.execute_script("$('#mb-row').css('display','none')")

# 쿠키 설정 팝업창(의미없음 - 쿠키설정 테스트)
# driver.add_cookie({"name": "main_layerPopOneDayCk", "value": "Y"})
##################################################
# 크롬 드라이버 종료
##################################################

# 동작 하나당 시간 간격(느린 컴퓨터 및 브라우저에서 돔생성 이전에 클릭 방지)
actionTime = 0.4

# 현재 애플리케이션 버전
current_version = "2.1.0"

accessUser_Mac_Adress = [
    "84:7b:57:6a:e6:8a",
    "98:22:ef:aa:a0:54",
    "60:e3:2b:d4:03:72",
    "e8:03:9a:de:15:4c",
    "e4:02:9b:58:88:e6",
    "88:ae:dd:2a:68:6b",
    "88:ae:dd:2a:6b:b5",
]


        ##################################################
        # UI 종료
        ##################################################

        ##################################################
        # 기능 개발 시작
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
        self.time1Cb.addItem("===다정동용===", "")
        self.time1Cb.addItem("09:00 ~ 10:00", "09:00 ~ 10:00")
        self.time1Cb.addItem("===전의 생활공원용===", "")
        self.time1Cb.addItem("10:30 ~ 12:30", "10:30 ~ 12:30")
        self.time1Cb.addItem("13:00 ~ 15:00", "13:00 ~ 15:00")
        self.time1Cb.addItem("15:30 ~ 17:30", "15:30 ~ 17:30")
        self.time1Cb.addItem("18:00 ~ 20:00", "18:00 ~ 20:00")
        self.time2Cb.addItem("===다정동용===", "")
        self.time2Cb.addItem("09:00 ~ 10:00", "09:00 ~ 10:00")
        self.time2Cb.addItem("===전의생활공원용===", "")
        self.time2Cb.addItem("10:30 ~ 12:30", "10:30 ~ 12:30")
        self.time2Cb.addItem("13:00 ~ 15:00", "13:00 ~ 15:00")
        self.time2Cb.addItem("15:30 ~ 17:30", "15:30 ~ 17:30")
        self.time2Cb.addItem("18:00 ~ 20:00", "18:00 ~ 20:00")

        ##################################################
        # 시간 설정 종료
        ##################################################
        ##################################################
        # 테니스장 설정 시작
        ##################################################
        tennisCourtList = {
            "중앙공원1": "OP48220697364086712,0",
            "중앙공원2": "OP48220697364086712,1",
            "중앙공원3": "OP48220697364086712,2",
            "중앙공원4": "OP48220697364086712,3",
            "중앙공원5": "OP48220697364086712,4",
            "중앙공원6": "OP48220697364086712,5",
            "중앙공원7": "OP48220697364086712,6",
            "중앙공원8": "OP48220697364086712,7",
            "중앙공원9": "OP48220697364086712,8",
            "중앙공원10": "OP48220697364086712,9",
            "수질복원센터A 테니스장1": "OP17028520651712824,0",
            "수질복원센터A 테니스장2": "OP21695037103696738,0",
            "수질복원센터A 테니스장3": "OP21166946437826537,0",
            "수질복원센터A 테니스장4": "OP21695037103696738,1",
            "수질복원센터A 테니스장5": "OP21703893297820968,0",
            "수질복원센터A 테니스장6": "OP21695037103696738,2",
            "수질복원센터A 테니스장7": "OP17028232109098739,0",
            "수질복원센터A 테니스장8": "OP21695037103696738,3",
            "수질복원센터A 테니스장9": "OP17028232109098739,1",
            "금남 생활체육공원1": "OP17271926690114529,0",
            "금남 생활체육공원2": "OP17271926690114529,1",
            "금남 생활체육공원3": "OP17271926690114529,2",
            "다정동 저류지 체육시설1 ": "OP17273881146249546,0",
            "다정동 저류지 체육시설2 ": "OP17273881146249546,1",
            "다정동 저류지 체육시설3 ": "OP17273881146249546,2",
            "소정 테니스장 A": "OP46996723757808552,0",
            "소정 테니스장 B": "OP46996723757808552,1",
            "소정 테니스장 C": "OP46996723757808552,2",
            "수질복원센터B 1": "OP17028743154983862,0",
            "수질복원센터B 2": "OP21696357966701005,0",
            "수질복원센터B 3": "OP17028743154983862,1",
            "전의생활체육공원1": "OP15716320733942054,0",
            "전의생활체육공원2": "OP15716320733942054,1",
            "전의생활체육공원3": "OP15716320733942054,2",
            "전의공공하수처리시설1": "OP10900259200163999,0",
            "조치원 체육공원1": "OP16682360410452683,0",
            "조치원 체육공원2": "OP16682360410452683,1",
            "조치원 체육공원3": "OP16682360410452683,2",
            "조치원 체육공원4": "OP16682360410452683,3",
            "조치원 체육공원5": "OP16682360410452683,4",
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

    # 배치 생성 함수
    def create_temporary_batch_file(self, new_exe):
        with open("update.bat", "w") as bat:
            bat.write(
                f"""@echo off
    timeout /t 2 /nobreak >nul
    start "" "{new_exe}"
    del "%~f0"
    """
            )

    # 다운로드 및 실행 함수
    def download_and_execute(self, remote_version):
        """# 원격 .exe 파일 URL
        remote_exe_url = 'http://ns.hakumata.world/tennisHelper/tennisHelper.exe'

        # 다운로드할 파일 경로
        local_exe_path = f'tennisHelper_v{remote_version}.exe'

        # 파일 다운로드
        response = requests.get(remote_exe_url)
        with open(local_exe_path, 'wb') as file:
            file.write(response.content)

        # 현재 실행 중인 애플리케이션 종료 및 새 버전 실행
        QCoreApplication.quit()
        # QProcess.startDetached(local_exe_path)"""

        # 원격 .exe 파일 URL
        url = "http://ns.hakumata.world/tennisHelper/tennisHelper.exe"
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
        idTxt, ok = QInputDialog.getText(self, "계정삭제", "아이디:")
        if ok:
            if len(str(idTxt)) == 0:
                QMessageBox.information(None, "에러", f"아이디가 입력되지 않았습니다.")
            else:
                QMessageBox.information(
                    None, "안내", f"{data_handler.delete_user(str(idTxt))}"
                )

                self.idCb.clear()
                # 계정 삭제 후 selectbox 리로드

                if data_handler.get_user_count() != 0:
                    for user in data_handler.data["user_info"]:
                        self.idCb.addItem(f"{user['id']}", f"{user['pw']}")

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
                        self.idCb.clear()
                        # 계정 등록 후 selectbox 리로드
                        data_handler = DataHandler()
                        if data_handler.get_user_count() != 0:
                            for user in data_handler.data["user_info"]:
                                self.idCb.addItem(f"{user['id']}", f"{user['pw']}")

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
        tennisPlace1 = tennisPlaceInfo1.split(",")[0]
        tennisCourt1 = tennisPlaceInfo1.split(",")[1]
        tennisPlaceInfo2 = self.tennisPlace2Cb.currentData()
        tennisPlace2 = tennisPlaceInfo2.split(",")[0]
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
        # driver.execute_script("document.querySelectorAll('#timeSection_' + " + time1 + ")[parseInt(" + tennisCourt1 + ")].click()")
        driver.execute_script(
            "var tempTimeEl = new Array(); document.querySelectorAll('span').forEach(function(arg,idx){ "
            "if(arg.innerText == '" + time1 + "'){ "
            "tempTimeEl.push(arg); }"
            "}); tempTimeEl["
            + tennisCourt1
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
        time.sleep(0.5)
        driver.find_element(
            By.XPATH, '//*[@id="mb-row"]/div/div/div/div/button'
        ).click()
        print("===== 11. 매크로 알림창 동의 확인 완료 =====")
        time.sleep(0.5)

        # 예약사유 입력
        print("===== 12. 이용안내 동의 및 예약 사유 화면이동 =====")
        # driver.find_element(By.ID, "infoYn").send_keys('pass')
        driver.find_element(
            By.XPATH, '//*[@id="content"]/div[3]/div[4]/div/div[1]/a/div'
        ).click()
        print("===== 13. 이용안내 동의 확인 완료 =====")
        time.sleep(0.5)
        driver.find_element(By.ID, "resveResn").send_keys("개인운동")
        print("===== 14. 예약사유 입력 완료 =====")
        time.sleep(0.5)

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
        tennisPlace1 = tennisPlaceInfo1.split(",")[0]
        tennisCourt1 = tennisPlaceInfo1.split(",")[1]
        tennisPlaceInfo2 = self.tennisPlace2Cb.currentData()
        tennisPlace2 = tennisPlaceInfo2.split(",")[0]
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
        driver.execute_script(
            "var tempTimeEl = new Array(); document.querySelectorAll('span').forEach(function(arg,idx){ "
            "if(arg.innerText == '" + time2 + "'){ "
            "tempTimeEl.push(arg); }"
            "}); tempTimeEl["
            + tennisCourt2
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
        time.sleep(0.5)
        driver.find_element(
            By.XPATH, '//*[@id="mb-row"]/div/div/div/div/button'
        ).click()
        print("===== 11. 매크로 알림창 동의 확인 완료 =====")
        time.sleep(0.5)

        # 예약사유 입력
        print("===== 12. 이용안내 동의 및 예약 사유 화면이동 =====")
        # driver.find_element(By.ID, "infoYn").send_keys('pass')
        driver.find_element(
            By.XPATH, '//*[@id="content"]/div[3]/div[4]/div/div[1]/a/div'
        ).click()
        print("===== 13. 이용안내 동의 확인 완료 =====")
        time.sleep(0.5)
        driver.find_element(By.ID, "resveResn").send_keys("개인운동")
        print("===== 14. 예약사유 입력 완료 =====")
        time.sleep(0.5)

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



