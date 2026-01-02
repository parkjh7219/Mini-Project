import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
import psutil
import time
from datetime import datetime

# 페이지 설정
st.set_page_config(layout="wide", page_title="🚀 ATC 실시간 보안 관제")

DB_FILE = "atc_system.db"

# --- 기능 함수 ---
def load_db_data():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM traffic ORDER BY time DESC", conn)
    conn.close()
    if not df.empty: df['time'] = pd.to_datetime(df['time'])
    return df

def reset_logs():
    if os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("DELETE FROM traffic")
        conn.commit()
        conn.close()
        return True
    return False

# --- 밝은 테마 스타일 적용 ---
st.markdown("""
<style>
    /* 전체 배경을 밝게 */
    .stApp {
        background-color: #f8f9fa;
    }
    /* 상단 타이틀 카드 */
    .title-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: 1px solid #e9ecef;
    }
    /* 메트릭 박스 글자색 조정 */
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# 메인 타이틀
st.markdown("""
<div class="title-card">
    <h1 style='text-align: center; color: #007bff; margin:0;'>🛰️ ATC Cyber Security Dashboard</h1>
    <p style='text-align: center; color: #666;'>실시간 항공 무전 보안 관제 시스템</p>
</div>
""", unsafe_allow_html=True)

df_all = load_db_data()

# 사이드바 (밝은 느낌 유지)
with st.sidebar:
    st.header("🔍 시스템 제어")
    if st.button("🗑️ 로그 초기화 (Clear DB)"):
        if reset_logs():
            st.success("로그가 초기화되었습니다.")
            time.sleep(1)
            st.rerun()

    st.divider()
    st.subheader("🖥️ 서버 자원")
    # RAM 오류 수정 완료
    st.metric("CPU 사용률", f"{psutil.cpu_percent()}%")
    st.metric("메모리 사용률", f"{psutil.virtual_memory().percent}%")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📊 실시간 현황", "📜 상세 로그 분석", "🛡️ 차단 관리"])

with tab1:
    if df_all.empty:
        st.info("수신된 데이터가 없습니다. 서버 IP 설정을 확인하세요.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("전체 트래픽", f"{len(df_all)} 건")
        with c2:
            atk_cnt = len(df_all[df_all['status'].isin(['공격', '차단됨'])])
            st.metric("위협 탐지", f"{atk_cnt} 건", delta=atk_cnt, delta_color="inverse")
        with c3:
            unique_ips = df_all['ip'].nunique()
            st.metric("접속 IP 수", f"{unique_ips} 개")

        # 그래프 디자인 변경
        df_chart = df_all.copy()
        df_chart = df_chart.set_index('time').resample('1min').size().reset_index(name='count')

        fig = px.line(df_chart, x='time', y='count', title="트래픽 동향")
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#333",
            xaxis=dict(showgrid=True, gridcolor='#eee'),
            yaxis=dict(showgrid=True, gridcolor='#eee')
        )
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("📝 최근 접속 로그 (최신 100건)")

    # 상태별 배경색
    def highlight_status(row):
        if row["status"] == "차단됨":
            return ["background-color: #ffebee; color: #c62828"] * len(row) # 연빨강
        if row["status"] == "공격":
            return ["background-color: #fff3e0; color: #ef6c00"] * len(row) # 연주황
        return [""] * len(row)

    if not df_all.empty:
        st.dataframe(df_all.head(100).style.apply(highlight_status, axis=1), use_container_width=True)

with tab3:
    st.subheader("🚫 실시간 차단 리스트")
    blocked_ips = df_all[df_all['status'] == "차단됨"]['ip'].unique()
    if len(blocked_ips) > 0:
        for ip in blocked_ips:
            st.error(f"보안 차단됨: {ip}")
    else:
        st.success("현재 위협이 감지되지 않았습니다.")

# 2초마다 자동 갱신
time.sleep(2)
st.rerun()