import socket
import sqlite3
import time
import subprocess
from datetime import datetime

DB_FILE = "atc_system.db"
WHITELIST = ["127.0.0.1"]
packet_count = {}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # 트래픽 로그 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS traffic
                 (time TEXT, ip TEXT, msg TEXT, status TEXT)''')
    # 수동/자동 차단 리스트 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS blacklist (ip TEXT PRIMARY KEY, reason TEXT)''')
    conn.commit()
    conn.close()

def is_blocked(ip):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT ip FROM blacklist WHERE ip=?", (ip,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def block_os_level(ip):
    """OS 방화벽(iptables)에 실제 등록"""
    try:
        subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"], check=True)
        print(f"🚨 [FIREWALL] OS 레벨 차단 완료: {ip}")
    except:
        print(f"⚠️ OS 차단 권한 없음 (sudo 확인 필요)")

init_db()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 9999))

print("📡 [ATC Receiver] 가동 중... (Port: 9999)")

while True:
    data, addr = sock.recvfrom(1024)
    raw_msg = data.decode()

    if "|" in raw_msg:
        virtual_ip, msg = raw_msg.split("|", 1)
    else:
        virtual_ip, msg = addr[0], raw_msg

    now = time.time()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "정상"

    # 1. 블랙리스트(수동 포함) 확인
    if is_blocked(virtual_ip):
        status = "차단됨"
    else:
        # 2. 실시간 DDoS(Flood) 탐지
        if virtual_ip not in WHITELIST:
            if virtual_ip not in packet_count: packet_count[virtual_ip] = []
            packet_count[virtual_ip].append(now)
            packet_count[virtual_ip] = [t for t in packet_count[virtual_ip] if now - t < 1.0]

            if len(packet_count[virtual_ip]) > 10: # 1초에 10개 이상 패킷
                status = "차단됨"
                conn = sqlite3.connect(DB_FILE)
                conn.execute("INSERT OR IGNORE INTO blacklist VALUES (?, ?)", (virtual_ip, "DDoS 탐지"))
                conn.commit()
                conn.close()
                block_os_level(virtual_ip)
            elif "ATTACK" in msg:
                status = "공격"

    # DB 저장
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO traffic VALUES (?, ?, ?, ?)", (now_str, virtual_ip, msg, status))
    conn.commit()
    conn.close()