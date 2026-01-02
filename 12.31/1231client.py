import socket
import time
import random

SERVER_IP = "127.0.0.1" # 실제 서버 IP로 변경하세요
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 가짜 IP 리스트 생성
normal_ips = [f"192.168.1.{i}" for i in range(10, 30)]
attack_ips = [f"10.0.0.{i}" for i in range(100, 150)]

print("🚀 ATC 비행 시뮬레이션 시작 (멀티 IP 모드)")
print(f"정상 IP: {normal_ips}")
print(f"공격 IP: {attack_ips}")

while True:
    # 1. 정상 트래픽 (3개 IP 사용)
    for v_ip in normal_ips:
        msg = f"{v_ip}|정상 고도 유지 중 (HL{random.randint(1000,9999)})"
        sock.sendto(msg.encode(), (SERVER_IP, PORT))
        print(f"✅ 전송: {v_ip}")
        time.sleep(0.5)

    # 2. 공격 시뮬레이션 (9개 중 하나 선택해서 DDoS)
    target_atk_ip = random.choice(attack_ips)
    print(f"🔥 공격 발생 시뮬레이션: {target_atk_ip}")
    for _ in range(15): # 초당 10회 이상으로 설정하여 차단 유도
        msg = f"{target_atk_ip}|[ATTACK] 무단 진입 시도!"
        sock.sendto(msg.encode(), (SERVER_IP, PORT))
        time.sleep(0.05)

    print("💤 잠시 대기 후 다음 사이클 진행...")
    time.sleep(2)