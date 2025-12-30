# client의 ip 주소를 랜덤으로 나오게 변경
# generate 함수 사용

import socket
import time
import random

SERVER_IP = "receiver 서버의 퍼블릭 ip 주소" # 기존과 동일하게 유지
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 비행기 ID 리스트
planes = ["HL1234", "HL5678", "HL9999(DANGEROUS)", "HL7777", "HL0000(DANGEROUS)"]

print("🚀 랜덤 IP 비행 시뮬레이션 시작...")

def generate_random_ip():
    """가짜 IP 주소를 생성하는 함수"""
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

while True:
    plane = random.choice(planes)
    fake_ip = generate_random_ip() # 루프마다 새로운 가짜 IP 생성

    # 특정 비행기는 공격 메시지를 보냄
    if "DANGEROUS" in plane:
        msg = f"[{fake_ip}] {plane}: [ATTACK] 무단 진입 시도!"
    else:
        msg = f"[{fake_ip}] {plane}: 정상 고도 유지 중"

    sock.sendto(msg.encode(), (SERVER_IP, PORT))
    print(f"전송: {msg}")
    time.sleep(1)