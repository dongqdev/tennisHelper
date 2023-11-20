import getpass
import hashlib
import json
import os
import platform
import socket
import urllib
import uuid
from datetime import datetime, timedelta


import mariadb
import requests
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMessageBox
from PySide6.QtCore import QTime
from cryptography.fernet import Fernet

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
        ip_address = socket.gethostbyname(hostname)
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

    def auth_user_info_DB(self, mac_address):
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

            print(result)

            # 데이터베이스 연결 종료
            cursor.close()
            connection.close()

            # 결과에 따라 메시지 출력
            if result:
                auth_Data = {"code": "SUCCESS", "message": "인증된 사용자입니다."}
                return auth_Data
            else:
                auth_Data = {"code": "FAIL", "message": "인증받지 않은 사용자입니다.\n키 등록 후 사용해 주세요"}
                return auth_Data


        except mariadb.Error as e:
            auth_Data = {"code": "ERROR", "message": f"서버와 연결이 원활하지 않습니다.\n{e}"}
            return auth_Data

    def upsert_user_info_DB(self, computer_Info, program_key):
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

            print("[dataHandler-upsert_user_info_DB] 컴퓨터 정보를 등록합니다 : ", computer_Info)
            print("[dataHandler-upsert_user_info_DB] result : ",result)
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
            return "ERROR"

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

    def set_Data_Ui(self, ui_instance):
        global tennisCourtList

        # 시작일,종료일 설정
        # 오늘
        start = datetime.today().strftime("%Y-%m-%d")
        # 20일 뒤
        last = (datetime.today() + timedelta(days=20)).strftime("%Y-%m-%d")

        # 시작일, 종료일 datetime 으로 변환
        start_date = datetime.strptime(start, "%Y-%m-%d")
        last_date = datetime.strptime(last, "%Y-%m-%d")

        # 종료일 까지 반복
        while start_date <= last_date:
            dateName = start_date.strftime("%Y-%m-%d")
            dateValue = start_date.strftime("%Y%m%d,%Y,%m,%d")
            ui_instance.date1Cb.addItem(dateName, dateValue)
            ui_instance.date2Cb.addItem(dateName, dateValue)

            # 하루 더하기
            start_date += timedelta(days=1)

        # 프로그램 실행 시 20일 뒤 날짜를 기본으로 설정
        ui_instance.date1Cb.setCurrentText(last_date.strftime("%Y-%m-%d"))
        ui_instance.date2Cb.setCurrentText(last_date.strftime("%Y-%m-%d"))

        for i in range(20, 6, -2):
            j = i + 2
            if len(str(i)) == 1:
                i = "0" + str(i)
            if len(str(j)) == 1:
                j = "0" + str(j)
            # 20:00 ~ 22:00
            ui_instance.time1Cb.addItem(
                "%s:00 ~ %s:00" % (i, j), "%s:00 ~ %s:00" % (i, j)
            )
            ui_instance.time2Cb.addItem(
                "%s:00 ~ %s:00" % (i, j), "%s:00 ~ %s:00" % (i, j)
            )

        # 전의 생활공원의 경우 시간이 다름
        ui_instance.time1Cb.addItem("===다정동용===", "")
        ui_instance.time1Cb.addItem("09:00 ~ 10:00", "09:00 ~ 10:00")
        ui_instance.time1Cb.addItem("===전의 생활공원용===", "")
        ui_instance.time1Cb.addItem("10:30 ~ 12:30", "10:30 ~ 12:30")
        ui_instance.time1Cb.addItem("13:00 ~ 15:00", "13:00 ~ 15:00")
        ui_instance.time1Cb.addItem("15:30 ~ 17:30", "15:30 ~ 17:30")
        ui_instance.time1Cb.addItem("18:00 ~ 20:00", "18:00 ~ 20:00")
        ui_instance.time2Cb.addItem("===다정동용===", "")
        ui_instance.time2Cb.addItem("09:00 ~ 10:00", "09:00 ~ 10:00")
        ui_instance.time2Cb.addItem("===전의생활공원용===", "")
        ui_instance.time2Cb.addItem("10:30 ~ 12:30", "10:30 ~ 12:30")
        ui_instance.time2Cb.addItem("13:00 ~ 15:00", "13:00 ~ 15:00")
        ui_instance.time2Cb.addItem("15:30 ~ 17:30", "15:30 ~ 17:30")
        ui_instance.time2Cb.addItem("18:00 ~ 20:00", "18:00 ~ 20:00")

        # 테니스장 선택 콤보박스 데이터 삽입
        for name, code in tennisCourtList.items():
            ui_instance.tennisPlace1Cb.addItem(name, code)
            ui_instance.tennisPlace2Cb.addItem(name, code)

        # 초기 계정정보 읽어오기
        if self.get_user_count() != 0:
            for user in self.data["user_info"]:
                ui_instance.idCb.addItem(f"{user['id']}", f"{user['pw']}")
