import requests
from cryptography.fernet import Fernet
import json

# JSON 데이터
data = [
    {
        "program_key": "검은사자",
        "os": "Windows  10.0.19042",
        "processor": "Intel64 Family 6 Model 140 Stepping 1 GenuineIntel",
        "hostname": "N11196-01",
        "ip_address": "192.168.1.100",
        "mac_address": "84:7b:57:6a:e6:8a",
        "username": "11196"
    },
    {
        "program_key": "노란팔찌",
        "os": "Windows 10.0.22621",
        "processor": "Intel64 Family 6 Model 154 Stepping 4, GenuineInte",
        "hostname": "DESKTOP-I1B5E44",
        "ip_address": "192.168.0.19",
        "mac_address": "04:cf:4b:ab:da:69",
        "username": "dong659"
    },
    {
        "program_key": "급한오리",
        "os": "Darwin  Darwin Kernel Version 23.1.0 Mon Oct  9 212724 PDT 2023; rootxnu-10002.41.9~6/RELEASE_ARM64_T6000",
        "processor": "arm",
        "hostname": "dong659MBPM1Pro16.local",
        "ip_address": "192.168.0.14",
        "mac_address": "c2:9f:4a:e9:10:71",
        "username": "dong659"
    },
    {
        "program_key": "놀랜감자",
        "os": "Windows  10.0.22621",
        "processor": "Intel64 Family 6 Model 58 Stepping 9 GenuineIntel",
        "hostname": "DESKTOP-1UJPS1F",
        "ip_address": "192.168.219.109",
        "mac_address": "e8:03:9a:de:15:4c",
        "username": "suseo"
    },
    {
        "program_key": "숨찬토끼",
        "os": "Windows  10.0.22621",
        "processor": "Intel64 Family 6 Model 142 Stepping 12 GenuineIntel",
        "hostname": "DESKTOP-K2267O1",
        "ip_address": "192.168.219.107",
        "mac_address": "60:e3:2b:d4:03:72",
        "username": "SR"
    },
    {
        "program_key": "초록상자",
        "os": "Windows  10.0.19045",
        "processor": "Intel64 Family 6 Model 165 Stepping 3 GenuineIntel",
        "hostname": "SR-215206",
        "ip_address": "172.17.6.41",
        "mac_address": "88:ae:dd:2a:68:6b",
        "username": "215206"
    },
    {
        "program_key": "파란수박",
        "os": "Windows  10.0.19045",
        "processor": "Intel64 Family 6 Model 158 Stepping 9 GenuineIntel",
        "hostname": "LAPTOP-6LNB5KEK",
        "ip_address": "112.145.225.26",
        "mac_address": "98:22:ef:aa:a0:54",
        "username": "SEC"
    }
]


# JSON 데이터를 문자열로 변환
data_str = json.dumps(data)

# 키 생성
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# 데이터 암호화
encrypted_data = cipher_suite.encrypt(data_str.encode())

# 결과 출력
print(f"data: {encrypted_data}")
print(f"key: {key}")


# JSON 파일의 URL
url = "https://raw.githubusercontent.com/dongqdev/tennisHelperFile/main/user.db"
key = b'XlLg32xNIN5PZB5lEH89ejUSNLQ1k52K-ptQ4LjI_8U='

# Fernet 객체 생성
cipher_suite = Fernet(key)

# URL에서 암호화된 데이터 다운로드
response = requests.get(url)
# encrypted_data = response.content
print(encrypted_data)

decrypted_data = ""

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
for user in data:
    print(user["username"], user['mac_address'])
