import streamlit as st
import pandas as pd
import plotly.express as px
import pymysql
import time
import psutil
from datetime import datetime

st.set_page_config(layout="wide", page_title="ATC Advanced Console")

# [수정포인트] RDS 접속 정보
RDS_HOST = "atc-database.cbi6ewck0l9a.ap-northeast-2.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PW = "miniproject123456789"
RDS_DB = "atc_db"

def load_data(query):
    try:
        conn = pymysql.connect(host=RDS_HOST, user=RDS_USER, password=RDS_PW, db=RDS_DB, charset='utf8mb4')
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def classify_threat(row):
    msg = str(row['msg']).upper()
    if "SCANNING" in msg: return "포트 스캔"
    if "UNAUTHORIZED" in msg: return "미승인 접근"
    if "EXPLOIT" in msg: return "침투 시도"
    return row['status']

# 데이터 준비
df_raw = load_data("SELECT * FROM traffic ORDER BY time DESC")
if not df_raw.empty:
    df_raw['status'] = df_raw.apply(classify_threat, axis=1)
    df_raw['time'] = pd.to_datetime(df_raw['time'])

st.title("🛰️ ATC Cyber Security Advanced Console")

tab1, tab2, tab3 = st.tabs(["📊 분석 통계", "📜 위협 로그", "🛡️ 블랙리스트"])

with tab1:
    if not df_raw.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("총 패킷", f"{len(df_raw)} Pkts")
        col2.metric("탐지 위협", f"{len(df_raw[df_raw['status'] != '정상'])} 건")
        col3.metric("CPU 사용률", f"{psutil.cpu_percent()}%")

        # 트래픽 차트
        df_trend = df_raw.set_index('time').resample('1min').size().reset_index(name='counts')
        st.plotly_chart(px.area(df_trend, x='time', y='counts', title="트래픽 추이"), use_container_width=True)

with tab2:
    st.dataframe(df_raw.head(100), use_container_width=True)

with tab3:
    # 블랙리스트 수동 등록
    with st.expander("➕ 블랙리스트 수동 등록"):
        b_ip = st.text_input("IP 주소")
        if st.button("차단하기"):
            conn = pymysql.connect(host=RDS_HOST, user=RDS_USER, password=RDS_PW, db=RDS_DB, autocommit=True)
            conn.cursor().execute("INSERT IGNORE INTO blacklist VALUES (%s, %s)", (b_ip, "관리자 수동 차단"))
            conn.close()
            st.success("차단 완료")
            st.rerun()

    df_black = load_data("SELECT * FROM blacklist")
    st.table(df_black)

time.sleep(5)
st.rerun()