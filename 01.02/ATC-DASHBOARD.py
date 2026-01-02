import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import time
from datetime import datetime

# 1. 페이지 설정 및 디자인 테마
st.set_page_config(layout="wide", page_title="ATC Advanced Command Center", page_icon="🛰️")

# 커스텀 CSS: 대시보드 가독성 향상
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)

DB_FILE = "atc_system.db"

# 2. 데이터 유틸리티 함수
def get_data(query):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            return pd.read_sql(query, conn)
    except:
        return pd.DataFrame()

def classify_threat(row):
    """메시지 내용을 기반으로 위협 수준 재분류"""
    msg = str(row['msg']).upper()
    if "SCANNING" in msg: return "포트 스캔"
    if "UNAUTHORIZED" in msg: return "미승인 접근"
    if "EXPLOIT" in msg: return "침투 시도"
    if row['status'] == "차단됨": return "차단됨"
    if row['status'] == "공격": return "공격"
    return "정상"

def style_status(val):
    """상태별 색상 지정 (배경색, 검정 글씨)"""
    colors = {
        '정상': 'background-color: #00FF88; color: black;',
        '공격': 'background-color: #FF4B4B; color: white;',
        '차단됨': 'background-color: #FF4B4B; color: white;',
        '포트 스캔': 'background-color: #E67E22; color: white;',
        '미승인 접근': 'background-color: #F1C40F; color: black;',
        '침투 시도': 'background-color: #9B59B6; color: white;'
    }
    return f'{colors.get(val, "")} font-weight: bold;'

# 3. 데이터 준비 (모든 탭에서 공유)
df_raw = get_data("SELECT * FROM traffic ORDER BY time DESC")
if not df_raw.empty:
    df_raw['status'] = df_raw.apply(classify_threat, axis=1)
    df_raw['time'] = pd.to_datetime(df_raw['time'])

# 4. 헤더 영역
st.title("🛰️ ATC Cyber Security Advanced Console")
st.caption(f"최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 시스템 가동 중")

# 스마트 팝업 알림 (가장 최근 위협)
if 'last_alert_ip' not in st.session_state: st.session_state.last_alert_ip = None
df_atk_latest = df_raw[df_raw['status'] != '정상'].head(1)

if not df_atk_latest.empty:
    current_ip = df_atk_latest.iloc[0]['ip']
    if st.session_state.last_alert_ip != current_ip:
        st.error(f"🚨 [긴급 위협 탐지] IP: {current_ip} | 유형: {df_atk_latest.iloc[0]['status']}")
        if st.button("위협 확인 완료 (닫기)"):
            st.session_state.last_alert_ip = current_ip
            st.rerun()

# 5. 메인 탭 구성
tab1, tab2, tab3 = st.tabs(["📊 실시간 분석 통계", "📜 고도화 위협 로그", "🛡️ 블랙리스트 관리"])

# --- TAB 1: 실시간 분석 통계 ---
with tab1:
    if not df_raw.empty:
        # 지표 상단 레이아웃
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("총 수신 패킷", f"{len(df_raw)} Pkts")
        m2.metric("고유 접근 IP", f"{df_raw['ip'].nunique()} IPs")
        m3.metric("탐지된 공격", f"{len(df_raw[df_raw['status'] != '정상'])} 건", delta_color="inverse")
        m4.metric("보안 위협 수준", "Critical" if len(df_raw[df_raw['status'] != '정상']) > 50 else "Stable")

        st.divider()

        # 차트 레이아웃
        c1, c2 = st.columns([0.6, 0.4])
        with c1:
            # 트래픽 추이 그래프 (1분 단위)
            df_trend = df_raw.set_index('time').resample('1min').size().reset_index(name='counts')
            fig_trend = px.area(df_trend, x='time', y='counts', title="📈 실시간 트래픽 밀도",
                                color_discrete_sequence=['#007bff'])
            st.plotly_chart(fig_trend, use_container_width=True)

        with c2:
            # 위협 유형 분포 파이 차트
            type_counts = df_raw['status'].value_counts().reset_index()
            fig_pie = px.pie(type_counts, values='count', names='status', title="🛡️ 보안 상태 분포",
                             color='status', color_discrete_map={
                    '정상':'#00FF88', '공격':'#FF4B4B', '차단됨':'#FF4B4B',
                    '포트 스캔':'#E67E22', '미승인 접근':'#F1C40F', '침투 시도':'#9B59B6'
                })
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("데이터를 수신 중입니다. 잠시만 기다려 주세요...")

# --- TAB 2: 고도화 위협 로그 ---
with tab2:
    st.subheader("📝 실시간 위협 탐지 로그 (위험도별 시각화)")
    if not df_raw.empty:
        # 스타일 적용 및 테이블 표시
        styled_df = df_raw.head(100).style.applymap(style_status, subset=['status'])
        st.dataframe(styled_df, use_container_width=True, height=600)
    else:
        st.write("로그가 비어 있습니다.")

# --- TAB 3: 블랙리스트 관리 ---
with tab3:
    st.subheader("🚫 영구 차단 블랙리스트")

    # 입력 폼
    with st.expander("➕ 블랙리스트 수동 등록", expanded=False):
        col_ip, col_reason, col_btn = st.columns([0.4, 0.4, 0.2])
        with col_ip: b_ip = st.text_input("차단할 IP")
        with col_reason: b_reason = st.text_input("차단 사유", value="관리자 수동 차단")
        with col_btn:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("즉시 차단"):
                if b_ip:
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("INSERT OR IGNORE INTO blacklist (ip, reason) VALUES (?, ?)", (b_ip, b_reason))
                        conn.commit()
                    st.success(f"{b_ip}가 차단되었습니다.")
                    st.rerun()

    st.divider()

    # 블랙리스트 테이블 표시
    df_black = get_data("SELECT * FROM blacklist")
    if not df_black.empty:
        st.table(df_black)
    else:
        st.write("현재 차단된 IP가 없습니다.")

# 6. 실시간 갱신 (5초 단위)
time.sleep(5)
st.rerun()