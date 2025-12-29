import socket
import time
import random

SERVER_IP = "43.203.170.17" # 수정 필수
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 비행기 ID 리스트
planes = ["HL1234", "HL5678", "HL9999(DANGEROUS)"]

print("🚀 비행 시뮬레이션 시작...")

while True:
    plane = random.choice(planes)
    # 특정 비행기는 공격 메시지를 보냄
    if "DANGEROUS" in plane:
        msg = f"{plane}: [ATTACK] 무단 진입 시도!"
    else:
        msg = f"{plane}: 정상 고도 유지 중"

    sock.sendto(msg.encode(), (SERVER_IP, PORT))
    print(f"전송: {msg}")
    time.sleep(1) # 1초 간격