# 비 정상적인 패킷(dangerous 이름이 붙은 소켓) 이 들어온 경우 해당 ip 를 차단
# iptables 명령어 사용 -> iptables 명령어는 관리자 권한 필요
# sudo python3 receiver.py 명령어로 실행

import socket
import sqlite3
import time
import re
import os # 리눅스 명령어를 실행하기 위해 추가

# 1. DB 초기화
conn = sqlite3.connect('atc_system.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS traffic (time TEXT, ip TEXT, msg TEXT, status TEXT)''')
conn.commit()

# 2. UDP 설정
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 9999))

# 차단된 IP를 기억하기 위한 리스트 (중복 차단 방지)
blocked_ips = []

print("📡 [Server] 보안 감시 및 자동 방화벽 시스템 가동 중...")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode()
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    # [가짜 IP 추출 로직]
    match = re.search(r"\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]", msg)
    if match:
        display_ip = match.group(1)
    else:
        display_ip = addr[0]

    # [보안 로직] 'ATTACK'이 포함되면 공격으로 간주
    if "ATTACK" in msg:
        status = "공격"
        # [방화벽 차단 실행]
        if display_ip not in blocked_ips:
            print(f"🚨 [경고] 공격 감지! IP {display_ip}를 차단합니다.")

            # 리눅스 iptables 명령어로 해당 IP 차단 (DROP)
            # 실제 운영 환경에서는 sudo 권한이 필요합니다.
            os.system(f"sudo iptables -A INPUT -s {display_ip} -j DROP")

            blocked_ips.append(display_ip) # 차단 목록에 추가
    else:
        status = "정상"

    # 3. DB 저장
    c.execute("INSERT INTO traffic VALUES (?, ?, ?, ?)", (now, display_ip, msg, status))
    conn.commit()
    print(f"[{status}] {display_ip} 처리 완료")