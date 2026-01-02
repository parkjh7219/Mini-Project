import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import base64
import time
from datetime import datetime

# =====================================================
# 1. 페이지 설정 및 디자인 (사용자 제공 코드 유지)
# =====================================================
st.set_page_config(layout="wide", page_title="🛰️  ATC 실시간 보안 관제")

def set_bg(image_file):
    # 배경 이미지가 없으면 기본 어두운 색으로 대체
    if not os.path.exists(image_file):
        st.markdown("<style>.stApp {background-color: #050f19;}</style>", unsafe_allow_html=True)
        return
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>    .stApp {{
        background: linear-gradient(rgba(5,15,25,0.6), rgba(5,15,25,0.6)), url("data:image/jpg;base64,{encoded}");
        background-size: cover; background-attachment: fixed;
    }}
    .title-card {{
        background: rgba(10,20,35,0.7); backdrop-filter: blur(10px);
        border-radius: 18px; padding: 20px; margin-bottom: 20px;
        text-align: center; box-shadow: 0 0 30px rgba(0,229,255,0.3);
    }}
    .attack-title {{ font-size: 36px; font-weight: 800; color: #00e5ff; }}
    </style>
    """, unsafe_allow_html=True)

set_bg("background.jpg")
# =====================================================
# 2. 데이터베이스 연동 로직 (추가된 핵심 부분)
# =====================================================
DB_FILE = "atc_system.db"

def load_db_data():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame() # DB가 아직 없으면 빈 데이터 반환

    conn = sqlite3.connect(DB_FILE)
    # 가장 최근 100개의 로그를 읽어옴
    df = pd.read_sql("SELECT * FROM traffic ORDER BY time DESC LIMIT 100", conn)
    conn.close()

    # 시간 컬럼을 시계열 데이터로 변환
    if not df.empty:
        df['time'] = pd.to_datetime(df['time'])
    return df

df = load_db_data()

# =====================================================
# 3. 헤더
# =====================================================
st.markdown('<div class="title-card"><div class="attack-title">🛰️  ATC 실시간 보안 관제 시스템</div></div>',
            unsafe_allow_html=True)

if df.empty:
    st.warning("📡 무전기(receiver.py)를 실행하고 비행기 신호를 기다리는 중입니다...")
    time.sleep(2)
    st.rerun()

# =====================================================
# 4. 상단 대시보드 (메트릭 & 그래프)
# =====================================================
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📊 실시간 트래픽 추이")
    # 시간대별 카운트 (DB 데이터를 기반으로 리샘플링)
    df_count = df.set_index("time").resample("1min").size().reset_index(name="count")

    fig = go.Figure()
    fig.add_scatter(x=df_count["time"], y=df_count["count"], mode="lines+markers", line=dict(color='#00e5ff'))
    fig.update_layout(template="plotly_dark", height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📈 상태 요약")
    total_pkts = len(df)
    attack_pkts = len(df[df['status'] == '공격'])
    st.metric("전체 패킷", f"{total_pkts} PKT")
    st.metric("탐지된 공격", f"{attack_pkts} PKT", delta=f"{attack_pkts}", delta_color="inverse")

# =====================================================
# 5. 중단 분석 (IP별 / 상태별)
# =====================================================
mid1, mid2 = st.columns(2)

with mid1:
    st.subheader("🌐 접속 기체(IP) 분포")
    fig_pie = px.pie(df, names="ip", hole=0.4, color_discrete_sequence=["#00e5ff", "#00fbff", "#0086ff"])
    fig_pie.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_pie, use_container_width=True)

with mid2:
    st.subheader("🛡️  보안 상태 비율")
    fig_status = px.bar(df['status'].value_counts().reset_index(), x='status', y='count', color='status',
                        color_discrete_map={'정상':'#00ff00', '공격':'#ff0000'})
    fig_status.update_layout(template="plotly_dark", height=280, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_status, use_container_width=True)

# =====================================================
# 6. 하단 원본 로그 테이블 (색상 강조 추가)
# =====================================================
st.subheader("📝 실시간 무전 로그 (최근 100건)")

def style_rows(row):
    # 공격인 경우 빨간색 계열, 정상인 경우 녹색 계열 배경
    if row["status"] == "공격":
        return ["background-color: rgba(139, 0, 0, 0.5); color: white"] * len(row)
    return ["background-color: rgba(0, 128, 0, 0.2); color: #00ff00"] * len(row)

styled_df = df.style.apply(style_rows, axis=1)
st.dataframe(styled_df, use_container_width=True, height=400)

# 2초마다 화면 자동 갱신
time.sleep(2)
st.rerun()