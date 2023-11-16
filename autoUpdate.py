##################################################
import sys

import requests
from PyQt6.QtWidgets import QMessageBox

from tennisHelper_BKUP import (driver)


# 원격 버전을 확인하는 URL
version_url = "http://ns.hakumata.world/tennisHelper/appInfo.txt"

# 원격 버전 확인 및 JSON 파싱
try:
    response = requests.get(version_url)
    print(response)
    # response.raise_for_status()  # 오류가 있으면 예외를 발생시킵니다.

    # 인코딩이 utf-8이 아닌 경우 아래와 같이 디코딩을 시도합니다.
    response.encoding = "utf-8"  # 1안
    # remote_info = response.content.decode('utf-8')  # 2안

    remote_info = response.json()
    print("remote_info", remote_info)
    remote_version = remote_info.get(
        "version", "0.0.0"
    )  # 버전 정보가 없으면 '0.0.0'을 사용합니다.
    updateDate = remote_info.get("updateDate", "-")
    updateInfo = remote_info.get("updateInfo", "-")
    print("remote_version", remote_version)
    print("updateDate", updateDate)
    print("updateInfo", updateInfo)
    # QMessageBox.information(None, "업데이트 완료",f"{updateInfo}\n\n{updateDate}");

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