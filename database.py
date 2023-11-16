import mariadb


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
