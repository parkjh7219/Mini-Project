# 화이트 리스트 추가
# 화이트 리스트 : 절대 차단하면 안되는 ip 목록 추가
# 127.0.0.1 = 로컬호스트 주소 , receiver 서버의 퍼블릭 ip 주소

import socket
import sqlite3
import time
import re
import os

# 1. DB 초기화
conn = sqlite3.connect('atc_system.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS traffic (time TEXT, ip TEXT, msg TEXT, status TEXT)''')
conn.commit()

# 2. UDP 설정
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 9999))

# 화이트리스트 설정
whitelist = ["127.0.0.1", "receiver 서버의 퍼블릭 ip 주소"]

blocked_ips = []

print("📡 [Server] 안전 장치가 포함된 보안 시스템 가동 중...")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode()
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    # 실제 패킷을 보낸 사람의 주소 (터미널 연결 보호용)
    real_sender_ip = addr[0]

    # 메시지 내 가짜 IP 추출
    match = re.search(r"\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]", msg)
    display_ip = match.group(1) if match else real_sender_ip

    if "ATTACK" in msg:
        status = "공격"

        # 차단 로직 실행 전 화이트리스트 체크
        # 1. 메시지 속 IP가 화이트리스트인지 확인
        # 2. 실제로 패킷을 던진 IP가 화이트리스트인지 확인 (터미널 튕김 방지)
        if display_ip in whitelist or real_sender_ip in whitelist:
            print(f"⚠️ [주의] 공격이 감지되었으나 화이트리스트 IP({display_ip})이므로 차단을 제외합니다.")
        elif display_ip not in blocked_ips:
            print(f"🚨 [차단] IP {display_ip}를 방화벽에 등록합니다.")
            os.system(f"sudo iptables -A INPUT -s {display_ip} -j DROP")
            blocked_ips.append(display_ip)
    else:
        status = "정상"

    c.execute("INSERT INTO traffic VALUES (?, ?, ?, ?)", (now, display_ip, msg, status))
    conn.commit()
    print(f"[{status}] {display_ip} 처리 완료")