# 플러딩 기능 추가
# 하나의 ip(공격지 주소)에서 패킷 1초에 10번 전송

import socket
import time
import random

# 수신측 정보 설정
SERVER_IP = "receiver 서버의 퍼블릭 ip 주소" # 수신 서버 IP로 확인 후 수정하세요
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 비행기 ID 리스트
planes = ["HL1234", "HL5678", "HL9999(DANGEROUS)"]

# [수정 포인트] 공격에 사용할 고정된 가짜 IP 하나를 미리 정합니다.
attacker_fake_ip = "192.168.0.100"

print("🚀 비행 시뮬레이터 가동...")
print("1: 일반 모드 (랜덤 IP, 초당 1회)")
print("2: 플러딩 모드 (고정 IP 192.168.0.100, 초당 10회)")
mode = input("모드를 선택하세요 (1 or 2): ")

def generate_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"

if mode == "2":
    print(f"🔥 특정 IP({attacker_fake_ip})로 플러딩 공격 시작!")
    delay = 0.1
else:
    print("✈️ 일반 관제 모드 시작!")
    delay = 1

while True:
    if mode == "2":
        # 플러딩 모드일 때는 미리 정해둔 하나의 나쁜 IP만 사용합니다.
        fake_ip = attacker_fake_ip
        plane = "HL9999(DANGEROUS)"
        msg = f"[{fake_ip}] {plane}: [ATTACK] FLOODING!!!"
    else:
        # 일반 모드일 때는 기존처럼 랜덤하게 작동합니다.
        fake_ip = generate_random_ip()
        plane = random.choice(planes)
        status = "[ATTACK] 무단 진입!" if "DANGEROUS" in plane else "정상 고도 유지 중"
        msg = f"[{fake_ip}] {plane}: {status}"

    sock.sendto(msg.encode(), (SERVER_IP, PORT))
    print(f"전송: {msg}")
    time.sleep(delay)
