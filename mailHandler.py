import smtplib

from PyQt6.QtCore import QThread, pyqtSignal


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
