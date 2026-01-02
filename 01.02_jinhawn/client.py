import socket
import time
import random

SERVER_IP = "43.201.21.61" # 실행 환경에 따라 변경
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

normal_ips = [f"192.168.1.{i}" for i in range(10, 20)]

def send_packet(ip, msg):
    data = f"{ip}|{msg}"
    sock.sendto(data.encode(), (SERVER_IP, PORT))

print("🚀 ATC 고도화 시뮬레이션 시작")
print("1: 정상 통신 (초록)")
print("2: DDoS 공격 (빨강)")
print("3: 포트 스캔/정찰 (주황)")
print("4: 미승인 접근 시도 (노랑)")
print("5: 시스템 침투/SQLi (보라)")

try:
    while True:
        mode = input("\n관제 모드 선택 > ")

        if mode == '1':
            v_ip = random.choice(normal_ips)
            send_packet(v_ip, f"ID:KE{random.randint(100,999)}, ALT:{random.randint(30000,40000)}ft")
            print(f"[-] 정상 데이터 전송: {v_ip}")

        elif mode == '2':
            atk_ip = "10.10.10.10"
            for _ in range(20):
                send_packet(atk_ip, "[ATTACK] FLOODING / OVERLOAD")
            print(f"[!] DDoS 공격 퍼붓는 중: {atk_ip}")

        elif mode == '3':
            scan_ip = f"172.16.{random.randint(0,255)}.{random.randint(0,255)}"
            send_packet(scan_ip, "[WARN] PORT SCANNING DETECTED")
            print(f"[?] 포트 스캔 감지: {scan_ip}")

        elif mode == '4':
            unknown_ip = f"221.{random.randint(0,255)}.1.5"
            send_packet(unknown_ip, "[CAUTION] UNAUTHORIZED ACCESS")
            print(f"[!] 미승인 IP 접근: {unknown_ip}")

        elif mode == '5':
            exploit_ip = "45.12.88.99"
            send_packet(exploit_ip, "[CRITICAL] EXPLOIT / SQL INJECTION")
            print(f"[☠️] 침투 시도 감지: {exploit_ip}")

        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n시뮬레이션 종료")