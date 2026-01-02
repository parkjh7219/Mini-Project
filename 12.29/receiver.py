import socket
import sqlite3
import time

# 1. DB 초기화
conn = sqlite3.connect('atc_system.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS traffic (time TEXT, ip TEXT, msg TEXT, status TEXT)''')
conn.commit()

# 2. UDP 설정
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 9999))

print("📡 [Server] 관제 무전기 수신 시작...")

while True:
    data, addr = sock.recvfrom(1024)
    msg = data.decode()
    ip = addr[0]
    now = time.strftime('%Y-%m-%d %H:%M:%S')

    # [보안 로직] 'ATTACK'이 포함되면 공격으로 간주
    status = "공격" if "ATTACK" in msg else "정상"

    # 3. DB 저장
    c.execute("INSERT INTO traffic VALUES (?, ?, ?, ?)", (now, ip, msg, status))
    conn.commit()
    print(f"[{status}] {ip} 수신 완료")