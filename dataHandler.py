import getpass
import hashlib
import json
import os
import platform
import socket
import uuid
import mariadb
from PyQt6.QtWidgets import QMessageBox
from cryptography.fernet import Fernet


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

            print(result)

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
