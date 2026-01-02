# client의 랜덤 ip 주소를 감지하고 출력

import socket
import sqlite3
import time
import re # 정규표현식을 사용하기 위해 추가

# 1. DB 초기화
conn = sqlite3.connect('atc_system.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS traffic (time TEXT, ip TEXT, msg TEXT, status TEXT)''')
conn.commit()

# 2. UDP 설정
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 9999))

print("📡 [Server] 가짜 IP 인식 모드 가동...")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode()
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    # [가짜 IP 추출 로직]
    # 메시지에서 [1.2.3.4] 형태를 찾아 IP만 뽑아냅니다.
    match = re.search(r"\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]", msg)

    if match:
        display_ip = match.group(1) # 메시지 속 가짜 IP 사용
    else:
        display_ip = addr[0] # 가짜 IP가 없으면 실제 접속 IP 사용

    # [보안 로직] 'ATTACK'이 포함되면 공격으로 간주
    status = "공격" if "ATTACK" in msg else "정상"

    # 3. DB 저장 (추출한 display_ip 저장)
    c.execute("INSERT INTO traffic VALUES (?, ?, ?, ?)", (now, display_ip, msg, status))
    conn.commit()
    print(f"[{status}] {display_ip} 데이터 기록 완료")