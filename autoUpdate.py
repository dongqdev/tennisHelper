##################################################
import subprocess
import sys

import requests
from PyQt6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QProgressDialog

# 현재 버전
current_version = "2.2.5"

# 원격 버전을 확인하는 URL
# version_url = "http://ns.hakumata.world/tennisHelper/appInfo.txt"
version_url = "https://raw.githubusercontent.com/dongqdev/tennisHelperFile/main/appInfo.txt"

class AutoUpdate:
    def __init__(self):
        self.check_Version()

    def set_Auth_Update_Info(self, messageCode, header, message):
        update_Check_Info = {}
        update_Check_Info["messageCode"] = messageCode
        update_Check_Info["header"] = header
        update_Check_Info["message"] = message

        return update_Check_Info

    def check_Version(self):
        # 원격 버전 확인 및 JSON 파싱
        try:
            response = requests.get(version_url)
            print('[autoUpdate-check_Version] response : ',response)
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
                # driver.quit()
                self.download_and_execute(remote_version)
                return self.set_Auth_Update_Info("UPDATE","업데이트","새로운 버전이 있습니다. 업데이트를 진행합니다.")

            else:
                return self.set_Auth_Update_Info("NOUPDATE", "시작", f"최신 버전입니다. 프로그램을 실행합니다.\n\n[업데이트 내역]\n{updateInfo}")
                # 프로그램 실행
        except requests.RequestException as e:
            return self.set_Auth_Update_Info(
                "ERROR", "업데이트오류", f"원격 버전 정보를 가져오는데 실패했습니다.\n프로그램을 종료합니다.\n{e}"
            )
            # sys.exit(1)  # 오류가 발생하면 애플리케이션을 종료합니다.

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

    # 배치 생성 함수
    def create_temporary_batch_file(self, new_exe):
        with open("update.bat", "w") as bat:
            bat.write(
                f"""@echo off
                timeout /t 2 /nobreak >nul
                start "" "{new_exe}"
                del "%~f0"
                """)