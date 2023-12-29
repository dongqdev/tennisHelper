import getpass
import hashlib
import os
import platform
import socket
import urllib
import uuid
import json
from datetime import datetime, timedelta

from cryptography.fernet import Fernet, InvalidToken
import json
import base64
from hashlib import sha256

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
        # JSON 파일의 URL
        url = "https://raw.githubusercontent.com/dongqdev/tennisHelperFile/main/user.txt"
        key = b'XlLg32xNIN5PZB5lEH89ejUSNLQ1k52K-ptQ4LjI_8U='

        # Fernet 객체 생성
        cipher_suite = Fernet(key)

        # URL에서 암호화된 데이터 다운로드
        response = requests.get(url)
        encrypted_data = response.content
        print(encrypted_data)
        # encrypted_data = b'gAAAAABljrSW0UUUG47yATN5dAP0C37SSMjvFSa0cWFs2_GJ_j7iuM7vqgWWs5eRauedZJ_JiQzYK-Fs2HUMX1OnitOI2mVjRrEU85-eCJvv3JTIKU56EM2meQh4tAGMFlFnEc3T4aDo31eH5bIbpNtDVm7HYRLDDKsSg6t7deWciksSF1rOex0UXwoVzkUAWaUV7b-7Jg78Q-rG1n_gtUq7lDJd_gVASXp3jyqAf9r-VdOSC7AqbHlFl0UpshQkA8BdzBZUy_AifmYSll7lu5-63azum8VGE1-LuuGk3zT26HMDd-LKDOI7u0VK94cpt0NrNRaeyQkdWPk1bdRtzzcAhktRvKXcXKNEdDS8CG-wv65ju3JEiUCbE3uQ1DBzwOowLwQLfIC45kBL1AutSkVMm9UDOncNmOyUx0haUh4PKYowJPQDV27o_nIcBYDyc0h3L9XEvofoKx6NlQdFZrNw9yqiLhsnjtfOYcWbaIb-VPjZoQaKm89B5O6SuprU1j-NygSpZCk6rp93evZNjtXFKQtaSanPi1htocK6fgUDj7TBlcZ7Dn3OAJzRExfx-LJJaKsrHOfnX7KKoTTqHk0z2w__RD22YEGqx0ORSyzQ6Og2mwiPg967txIDP-1HZ7sRcl-0zaH3JsIjFdyPl8mBHtQ2i7Iz7ZrwMZVFmqi9gUN6X6C7uNGs0GkMsAnac0HSMSUxLRMBQa9E3IM2YBmv-ft7iWP3R3P47NLwK4UFZ4jXV1pvySUS5Ixx2UNhfzIFxP74m2gzvXg3-JwfDt5VG2FBtHWMuBbcUGVqodv4BXwDgRSUfdf6qmNHwIJjfyMCWJvLofKGj4R2yZ9wYQkq9ZxDdxg-D8siF4yeRrWCXnK8HNooE6slswJgXd2qtMOf8ZAVwA6tXRDci_Sdvq6aiBVd-y9VlPbDdQaqyGr5S1fMhO-StJCFkRGLhZjuppc5Ev4-mJkelBmt9zSyigHWldpEGLu8lAjKlcvnqDgZfsApaV8I9NCuhI8QsHk3Ow5X2X49uN-M9_cxvzxpm4yFshdDsFakRp0OIoF9_BYywGqfXwgTyH2BVT0SYX0cOACusWb50__LeKvTNThzCuqiBDfl32GIiVQYngyPw0U2t6zeBRXynWr-TfApLk1UD3RR_qxPd0I9_9GbUAnC3o5BbRkQXMzHLcaGHg314tqFsgAR0Hn4xablXCp8zLBrMXgjOS8huRLOgv2ZUOQ25_6n1zmzU3q-Xy_J71dgmM2SW4v_v7JE9TkVkzqx1VghwDrIpMNCliYrh5vTkOi5LHTpq_dp0LdhtxlQb7MLVX5YjISIKCY7thmV0ffq43soLhT8_DoQ7vASbYk0dJSQ8CatOzu8NeEYYggDg5d6J5I3xrWwXJYTRnEMsLMTssEPwEaGpzTr_M8bCO9dmygpi8IPO7eiV8qVJY54miJTPueVI8dP_2waj9yXVUIi6Cc1nyvDJfyJqDaV-L59IVFnTxdJNoVWUpbohp6iwB4SMWTvujAts_9F7xwcE7K0vhWCRSeAG69f3fb-0t1gl09xhsgF5kKjLkHGXVej1P7dsJLJKauM-49wnsLpkGguyUKwa1tytVD6LGfpkVXThdB4GxiIe1o9FBcNLzWzpzeyjG2W_Ze5zfC8QIKI9rcroKyaEah2t9zJh4hsJeXzjLyKxFu_TFWMRflRWwBxJ6xlG29MQFAPWp3C7UfIT_rnzQCtp-bV3TWGK9CSskj0a09tZSng5D-GK6RctI8UswvsWGMYtNdHv7XHMdVo0TLEl3oXaOyfB34QcG-S5BckVrYce7NUBl41sDc67GXcYk74YgjrPlM0H6mmYmdMUDtumWJ8UCrIE5bziSS1fLz8Owp6y28qadjqd8C6ql8RFc0vZjkXZ0oMJRFZpsMkvpExRwSJalsHbiOicMBlhafVKfDzsw3VSxFOn2mUWpGxe300qqiL7AthFmeLsKup0WM12SnfNNtDwfqjDf6iSv4SfpzRwE9xzNXop_9O-A6KTDKHV9MaN-FF_RjWlV9ZlkQVkDaFxsy3D2HpPCovekbioxw2y1anz5QoPrL0zo1giTMG7I1lpoliwswQDgaplb0za_1-yy7P6UBqxB2y3CBH7UQr30-FMqG7yj3FSdZXTzU7-1rN78H6ZTWVrbXN3CPL7kVQegtjI9jnGbS6s6YJd4Ssb-80QYfovTkYxmNGz2n4jI3mwEaPi2eypVwdvj1Lc9X-jzHqBv2ArLi7c5x--RKy2wok0mq-XdcSUDpoWYg0PRNPP3ZFsaB8_u1lSHHaWPC_4LNtxHwegqCdK0sCpmoAKwhsU1Uhsslg4v_Ynojc5cWzDifspb_9cv4yB7pf9cG3EpBRAJeaeMTy4fuItzL6I0i94c5iM-0evvqzxawBOCqz2dBWzMFmHMnPW98Y_PLqaONFKQazMRrYuPB92-hvrlMHlBJqtnukQTl7-ouhEsR2mrkb2WLZf7d8YLjpe4FlRS-utCrFUw0_AtxmiZNQpdLyeS6e9GiU4g=='
        decrypted_data = ""
        data = ""
        # 데이터 복호화
        try:
            decrypted_data = cipher_suite.decrypt(encrypted_data)
            print("복호화된 데이터:", decrypted_data.decode())
        except Exception as e:
            print("복호화하는 동안 오류가 발생했습니다:", e)

        # JSON 데이터를 파이썬 객체로 변환
        try:
            data = json.loads(decrypted_data.decode())
            print("복호화 후 JSON으로 변환된 데이터:", data)
        except Exception as e:
            print("데이터 변환 중 오류가 발생했습니다:", e)

        # 데이터 사용 예시: 모든 사용자의 'os'와 'username' 출력
        result = 0
        for user in data:
            print(user["username"], user['mac_address'])
            if mac_address == user['mac_address']:
                result += 1

        if result > 0:
            auth_Data = {"code": "SUCCESS", "message": "인증된 사용자입니다."}
            return auth_Data
        else:
            auth_Data = {"code": "FAIL", "message": "인증받지 않은 사용자입니다.\n키 등록 후 사용해 주세요"}
            return auth_Data

        # 추가적인 데이터 처리 및 사용...


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
            print("[dataHandler-upsert_user_info_DB] result : ", result)
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
