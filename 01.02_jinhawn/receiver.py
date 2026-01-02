import socket
import pymysql
import time
from datetime import datetime

# [설정] RDS 접속 정보
RDS_HOST = "atc-database.cbi6ewck0l9a.ap-northeast-2.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PW = "miniproject123456789"
RDS_DB = "atc_db"

def get_db_connection():
    return pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PW,
        db=RDS_DB,
        charset='utf8mb4', # 한글 처리를 위해 필수
        autocommit=True
    )

#def get_db_connection(include_db=True):
#    """안정적인 DB 연결을 위한 함수"""
#    return pymysql.connect(
#        host=RDS_HOST,
#        user=RDS_USER,
#        password=RDS_PW,
#        db=RDS_DB if include_db else None,
#        charset='utf8mb4',
#        autocommit=True,
#        use_unicode=True
#    )

# 1. 초기화: DB 및 테이블 생성 + 한글 인코딩 강제 설정
try:
    # (1) DB 방 생성
    conn = get_db_connection(include_db=False)
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {RDS_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.close()

    # (2) 테이블 생성 및 인코딩 변경
    conn = get_db_connection(include_db=True)
    with conn.cursor() as cursor:
        # 트래픽 로그 테이블
        cursor.execute('''CREATE TABLE IF NOT EXISTS traffic
        (time DATETIME, ip VARCHAR(50), msg TEXT, status VARCHAR(20))''')
        # 블랙리스트 테이블
        cursor.execute('''CREATE TABLE IF NOT EXISTS blacklist
        (ip VARCHAR(50) PRIMARY KEY, reason TEXT)''')

        # [중요] 한글 저장을 위해 테이블 인코딩 강제 변환
        cursor.execute("ALTER TABLE traffic CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute("ALTER TABLE blacklist CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.close()
    print("✅ AWS RDS 초기화 및 한글 인코딩 설정 완료!")
except Exception as e:
    print(f"❌ DB 설정 오류: {e}")

# 2. UDP 수신 설정
PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", PORT))

packet_count = {}
WHITELIST = ["127.0.0.1"]

print("📡 [ATC Receiver] 가동 중... (Port: 9999)")

while True:
    data, addr = sock.recvfrom(1024)
    raw_msg = data.decode()

    # 데이터 파싱
    if "|" in raw_msg:
        virtual_ip, msg = raw_msg.split("|", 1)
    else:
        virtual_ip, msg = addr[0], raw_msg

    now = time.time()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "정상"

    # 3. 비즈니스 로직 및 DB 저장
    try:
        # 매번 연결을 새로 열어 InterfaceError를 방지합니다.
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # (1) 블랙리스트 확인
            cursor.execute("SELECT ip FROM blacklist WHERE ip=%s", (virtual_ip,))
            if cursor.fetchone():
                status = "차단됨"
            else:
                # (2) DDoS 탐지
                if virtual_ip not in WHITELIST:
                    if virtual_ip not in packet_count: packet_count[virtual_ip] = []
                    packet_count[virtual_ip].append(now)
                    packet_count[virtual_ip] = [t for t in packet_count[virtual_ip] if now - t < 1.0]

                    if len(packet_count[virtual_ip]) > 10:
                        status = "차단됨"
                        cursor.execute("INSERT IGNORE INTO blacklist VALUES (%s, %s)", (virtual_ip, "DDoS 탐지"))
                    elif "ATTACK" in msg:
                        status = "공격"

            # (3) 로그 저장
            cursor.execute("INSERT INTO traffic (time, ip, msg, status) VALUES (%s, %s, %s, %s)",
                           (now_str, virtual_ip, msg, status))
        conn.close() # 작업 후 즉시 닫기
        print(f"[{status}] {virtual_ip} -> RDS 저장 성공")

    except Exception as e:
        print(f"⚠️ 데이터 처리 중 오류 발생: {e}")