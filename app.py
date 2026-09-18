import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

st.set_page_config(
    page_title="FLOW",
    page_icon="🌊",
    layout="wide"
)

# -----------------------------
# REAL ANALYSIS DATA
# -----------------------------
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def _find_csv(*names):
    """GitHub/Streamlit Cloud와 로컬에서 파일명을 유연하게 찾습니다."""
    for name in names:
        p = BASE_DIR / name
        if p.exists():
            return p
    raise FileNotFoundError(
        f"필요한 CSV 파일을 찾지 못했습니다: {', '.join(names)}"
    )

AREA_FILE = _find_csv("area_summary.csv", "area_summary(1).csv")
TIME_FILE = _find_csv("time_result.csv", "time_result(1).csv")
TWIN_FILE = _find_csv("twin_difference.csv", "twin_difference(1).csv")
MAP_FILE = _find_csv("flow_area_map.csv")

@st.cache_data
def load_analysis_data():
    area_df = pd.read_csv(AREA_FILE)
    time_df = pd.read_csv(TIME_FILE)
    twin_df = pd.read_csv(TWIN_FILE)

    # key 타입을 통일해 필터링 오류 방지
    for df in (area_df, time_df):
        df["area_code"] = df["area_code"].astype(str).str.strip()
        df["category"] = df["category"].astype(str).str.strip()
        df["area"] = df["area"].astype(str).str.strip()

    twin_df["area"] = twin_df["area"].astype(str).str.strip()
    twin_df["category"] = twin_df["category"].astype(str).str.strip()

    # TRUE/FALSE가 문자열로 읽혀도 정상 처리
    area_df["analysis_available_bool"] = (
        area_df["analysis_available"]
        .astype(str).str.strip().str.lower()
        .isin(["true", "1", "yes"])
    )
    return area_df, time_df, twin_df

area_df, time_df_all, twin_df_all = load_analysis_data()

@st.cache_data
def load_map_data():
    df = pd.read_csv(MAP_FILE, dtype={"area_code": str})
    df["area_code"] = df["area_code"].astype(str).str.strip()
    return df

map_df = load_map_data()

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #f6f9fc;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}

.hero {
    background: linear-gradient(135deg, #123f6d 0%, #2376aa 100%);
    padding: 50px 54px;
    border-radius: 26px;
    color: white;
    margin-bottom: 32px;
}

.hero-title {
    font-size: 56px;
    font-weight: 800;
    margin-bottom: 4px;
}

.hero-sub {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 16px;
}

.hero-desc {
    font-size: 16px;
    line-height: 1.8;
    opacity: 0.95;
}

.section-title {
    font-size: 27px;
    font-weight: 800;
    margin-top: 42px;
    margin-bottom: 16px;
    color: #18324a;
}

.card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    border: 1px solid #e9eef3;
    min-height: 145px;
}

.label {
    font-size: 13px;
    color: #71808f;
    font-weight: 700;
    margin-bottom: 8px;
}

.big {
    font-size: 42px;
    font-weight: 800;
    color: #183f6c;
    line-height: 1.1;
}

.subtext {
    margin-top: 10px;
    font-size: 14px;
    line-height: 1.6;
    color: #5d6a76;
}

.diagnosis-box {
    background: white;
    border: 1px solid #e5ebf1;
    border-radius: 18px;
    padding: 22px 24px;
    margin-bottom: 18px;
}

.warning {
    background: #fff2f2;
    border-left: 5px solid #ef6461;
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 14px;
}

.dead-box {
    background: #fff7e8;
    border: 1px solid #f1d19b;
    border-radius: 18px;
    padding: 24px;
    margin-top: 10px;
}

.twin-box {
    background: #edf5ff;
    border: 1px solid #d3e4f8;
    border-radius: 18px;
    padding: 24px;
}

.compare-box {
    margin-top: 16px;
    padding: 18px 20px;
    background: white;
    border: 1px solid #e5ebf1;
    border-radius: 14px;
}

.why-card {
    background: white;
    border: 1px solid #e7ecf1;
    border-radius: 16px;
    padding: 20px;
    min-height: 165px;
}

.demo-badge {
    display: inline-block;
    padding: 6px 12px;
    background: #edf2f7;
    color: #536273;
    font-size: 12px;
    border-radius: 999px;
    font-weight: 700;
    margin-bottom: 10px;
}

div.stButton > button {
    width: 100%;
    height: 50px;
    border-radius: 13px;
    background-color: #174f82;
    color: white;
    font-weight: 700;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HERO
# -----------------------------
st.markdown(
    '<div class="hero">'
    '<div class="hero-title">FLOW</div>'
    '<div class="hero-sub">사람은 많은데, 손님은 없는 이유</div>'
    '<div class="hero-desc">'
    '유동인구의 숫자만 보는 것이 아니라,<br>'
    '실제 소비와 얼마나 연결되는지를 분석합니다.<br>'
    '서울 골목상권의 숨은 소비 기회를 찾아보세요.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# -----------------------------
# INPUT + STATE
# -----------------------------
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "selected_key" not in st.session_state:
    st.session_state.selected_key = None

st.markdown("""
<style>
.flow-step-card{background:#fff;border:1px solid #dfe8e3;border-radius:18px;padding:20px 22px;box-shadow:0 8px 24px rgba(21,55,43,.055);margin:8px 0 16px}
.flow-step-no{display:inline-flex;width:29px;height:29px;border-radius:50%;align-items:center;justify-content:center;background:#087443;color:white;font-weight:900;margin-right:8px}
.flow-breadcrumb{color:#65766f;font-size:13px;font-weight:700;margin:3px 0 12px}
.flow-selected{background:#eef8f2;border:1px solid #cfe7d8;border-left:5px solid #087443;border-radius:14px;padding:13px 16px;margin:10px 0 15px}
.flow-help{background:#f1f8f4;border-radius:12px;padding:11px 14px;color:#486259;font-size:13px;margin:8px 0 14px}
div[data-testid="stButton"] > button[kind="primary"]{background:#087443;border-color:#087443;border-radius:10px;font-weight:800}
</style>
""", unsafe_allow_html=True)


st.markdown('''
<style>
/* FLOW schematic maps: reference-image-like clean white cards */
div[data-testid="stIFrame"] { border-radius:16px; }
.flow-step-card iframe { background:#ffffff !important; }
</style>
''', unsafe_allow_html=True)

st.markdown('<div class="section-title">1. 분석할 지역을 선택해주세요</div>', unsafe_allow_html=True)
st.caption("서울시 자치구 → 행정동 → 골목상권 순서로 좁혀가며 내 상권을 찾습니다.")
st.markdown("""
<div style="display:flex;gap:8px;align-items:center;margin:10px 0 20px;font-size:13px;font-weight:800;color:#5f7169">
<span style="background:#eaf6ef;color:#087443;padding:7px 12px;border-radius:999px">① 서울 자치구</span>
<span>→</span><span style="background:#f2f5f3;padding:7px 12px;border-radius:999px">② 행정동</span>
<span>→</span><span style="background:#f2f5f3;padding:7px 12px;border-radius:999px">③ 골목상권</span>
<span>→</span><span style="background:#f2f5f3;padding:7px 12px;border-radius:999px">④ 업종</span>
</div>
""", unsafe_allow_html=True)

available_codes = set(area_df["area_code"].astype(str).unique())
explore_df = map_df[map_df["area_code"].astype(str).isin(available_codes)].copy()
SEOUL_GU_GEOJSON = "https://raw.githubusercontent.com/southkorea/seoul-maps/master/juso/2015/json/seoul_municipalities_geo_simple.json"

for k, v in {"selected_district":None,"selected_dong":None,"map_selected_area_code":None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown('<div class="flow-step-card">', unsafe_allow_html=True)
st.markdown('<span class="flow-step-no">1</span><b style="font-size:20px">서울시 자치구 선택</b>', unsafe_allow_html=True)
st.caption("서울 약도에서 원하는 자치구를 눌러주세요.")

gu_map = folium.Map(location=[37.5665,126.9780], zoom_start=10.65, tiles=None, zoom_control=False, dragging=False, scrollWheelZoom=False, doubleClickZoom=False, attributionControl=False, prefer_canvas=True)
folium.Rectangle(
    bounds=[[37.40,126.72],[37.72,127.20]],
    color="#ffffff", fill=True, fill_color="#ffffff", fill_opacity=1, weight=0
).add_to(gu_map)
folium.GeoJson(
    SEOUL_GU_GEOJSON,
    style_function=lambda f: {"fillColor":"#dcefe4" if f["properties"].get("SIG_KOR_NM")==st.session_state.selected_district else "#fbfcfb","color":"#9aa8a1","weight":2.4 if f["properties"].get("SIG_KOR_NM")==st.session_state.selected_district else 1.15,"fillOpacity":1},
    highlight_function=lambda f: {"fillColor":"#cce9d8","color":"#087443","weight":2.5,"fillOpacity":1},
    tooltip=folium.GeoJsonTooltip(fields=["SIG_KOR_NM"],aliases=[""],labels=False,sticky=True,style="background:white;color:#173c67;font-size:14px;font-weight:800;padding:6px 9px;border:1px solid #d8e4de;border-radius:7px;")
).add_to(gu_map)

gu_event=st_folium(gu_map,height=390,use_container_width=True,returned_objects=["last_active_drawing"],key="seoul_diagram_picker")
clicked=gu_event.get("last_active_drawing") if gu_event else None
if clicked:
    picked_gu=(clicked.get("properties") or {}).get("SIG_KOR_NM")
    if picked_gu in set(explore_df["district"].dropna()) and picked_gu != st.session_state.selected_district:
        st.session_state.selected_district=picked_gu
        st.session_state.selected_dong=None
        st.session_state.map_selected_area_code=None
        st.rerun()

with st.expander("지도로 선택하기 어렵다면 목록으로 선택"):
    gus=sorted(explore_df["district"].dropna().unique())
    gu_fb=st.selectbox("자치구",gus,key="gu_fb")
    if st.button("이 자치구 선택",key="gu_fb_btn"):
        st.session_state.selected_district=gu_fb
        st.session_state.selected_dong=None
        st.session_state.map_selected_area_code=None
        st.rerun()
st.markdown('</div>',unsafe_allow_html=True)

gu=st.session_state.selected_district
if gu:
    gu_df=explore_df[explore_df["district"]==gu].copy()
    st.markdown(f'<div class="flow-breadcrumb">선택 지역 &nbsp;›&nbsp; <b>{gu}</b></div>',unsafe_allow_html=True)

    st.markdown('<div class="flow-step-card">',unsafe_allow_html=True)
    st.markdown(f'<span class="flow-step-no">2</span><b style="font-size:20px">{gu} 행정동 선택</b>',unsafe_allow_html=True)
    st.caption("상권이 너무 많지 않도록 행정동을 먼저 선택합니다.")

    dong_summary=(gu_df.dropna(subset=["dong"]).groupby("dong",as_index=False).agg(lat=("lat","mean"),lon=("lon","mean"),n=("area_code","nunique")))
    dongs=sorted(dong_summary["dong"].tolist())

    st.markdown("""
    <div style="background:#fbfcfb;border:1px solid #e2e8e5;border-radius:16px;
                padding:16px 18px;margin:10px 0 14px">
      <div style="font-size:13px;color:#66766f;margin-bottom:4px">행정동을 선택하면 해당 동의 분석 가능 상권만 표시됩니다.</div>
    </div>
    """, unsafe_allow_html=True)

    cols=st.columns(4)
    for i,dname in enumerate(dongs):
        count=int(dong_summary.loc[dong_summary["dong"]==dname,"n"].iloc[0])
        with cols[i%4]:
            if st.button(f"{dname} · 상권 {count}곳", key=f"dong_btn_{gu}_{dname}", use_container_width=True):
                st.session_state.selected_dong=dname
                st.session_state.map_selected_area_code=None
                st.rerun()

    with st.expander("목록으로 행정동 선택"):
        dong_pick=st.selectbox("행정동",["행정동을 선택해주세요"]+dongs,key=f"dong_select_{gu}")
        if dong_pick!="행정동을 선택해주세요" and dong_pick!=st.session_state.selected_dong:
            st.session_state.selected_dong=dong_pick
            st.session_state.map_selected_area_code=None
            st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

dong=st.session_state.selected_dong
if gu and dong:
    dong_df=explore_df[(explore_df["district"]==gu)&(explore_df["dong"]==dong)].copy()
    st.markdown(f'<div class="flow-breadcrumb">선택 지역 &nbsp;›&nbsp; <b>{gu}</b> &nbsp;›&nbsp; <b style="color:#087443">{dong}</b></div>',unsafe_allow_html=True)

    st.markdown('<div class="flow-step-card">',unsafe_allow_html=True)
    st.markdown(f'<span class="flow-step-no">3</span><b style="font-size:20px">{dong}의 분석 가능한 상권</b>',unsafe_allow_html=True)
    st.caption(f"상권 {dong_df.area_code.nunique()}곳만 표시합니다. 파란 점을 누르면 바로 선택됩니다.")

    am=folium.Map(location=[float(dong_df.lat.mean()),float(dong_df.lon.mean())],zoom_start=15,tiles=None,control_scale=False)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="© OpenStreetMap contributors",
        name="거리 지도",
        opacity=0.58
    ).add_to(am)
    for r in dong_df.itertuples(index=False):
        code=str(r.area_code); sel=code==str(st.session_state.map_selected_area_code)
        folium.CircleMarker([r.lat,r.lon],radius=10 if sel else 7,color="#087443" if sel else "#1769aa",weight=3 if sel else 2,fill=True,fill_color="#0b8b53" if sel else "#3c86bd",fill_opacity=.92,tooltip=f"{r.area_name} 〔{code}〕").add_to(am)
    evt=st_folium(am,height=350,use_container_width=True,returned_objects=["last_object_clicked_tooltip"],key=f"area_map_{gu}_{dong}")
    tip=evt.get("last_object_clicked_tooltip") if evt else None
    if tip:
        mm=re.search(r"〔([^〕]+)〕",str(tip))
        if mm and mm.group(1).strip()!=str(st.session_state.map_selected_area_code):
            st.session_state.map_selected_area_code=mm.group(1).strip()
            st.rerun()

    with st.expander("지도에서 찾기 어렵다면 상권 목록으로 선택"):
        labels={str(r.area_name):str(r.area_code) for r in dong_df.itertuples(index=False)}
        area_fb=st.selectbox("상권",list(labels),key=f"area_fb_{gu}_{dong}")
        if st.button("이 상권 선택",key=f"area_fb_btn_{gu}_{dong}"):
            st.session_state.map_selected_area_code=labels[area_fb]
            st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

selected_code=st.session_state.map_selected_area_code
if selected_code:
    selected_area_rows=area_df[area_df["area_code"].astype(str)==str(selected_code)].copy()
    if not selected_area_rows.empty:
        selected_area_name=selected_area_rows["area"].iloc[0]
        st.markdown(f'<div class="flow-selected"><div style="font-size:12px;font-weight:800;color:#6b7c8f">선택한 상권</div><div style="font-size:20px;font-weight:900;color:#075b38">{selected_area_name}</div><div style="margin-top:4px;color:#64766e">{gu} · {dong}</div></div>',unsafe_allow_html=True)
        st.markdown('<span class="flow-step-no">4</span><b style="font-size:20px">업종을 선택해주세요</b>',unsafe_allow_html=True)
        categories=sorted(selected_area_rows["category"].dropna().unique())
        selected_category=st.selectbox("업종 선택",categories,key=f"cat_{selected_code}")
        st.markdown('<div class="flow-help">선택한 상권에서 현재 FLOW 분석 결과가 존재하는 업종만 표시합니다.</div>',unsafe_allow_html=True)
        if st.button("FLOW 진단하기 →",type="primary"):
            st.session_state.selected_key=(str(selected_code),selected_category)
            st.session_state.show_result=True
            st.rerun()

if st.session_state.show_result and st.session_state.selected_key:
    selected_code, category = st.session_state.selected_key

    row_df = area_df[
        (area_df["area_code"] == str(selected_code)) &
        (area_df["category"] == str(category))
    ].copy()

    if row_df.empty:
        st.error("선택한 상권·업종의 분석 결과를 찾지 못했습니다.")
        st.stop()

    row = row_df.iloc[0]
    area = str(row["area"])

    if not bool(row["analysis_available_bool"]):
        st.markdown(f'<div class="section-title">2. {area} · {category}</div>', unsafe_allow_html=True)
        st.warning("최근 4개 분기의 활동 또는 관측 근거가 부족하여 분석할 수 없습니다.")
        st.stop()

    # 해당 상권·업종의 시간대 결과
    time_rows = time_df_all[
        (time_df_all["area_code"] == str(selected_code)) &
        (time_df_all["category"] == str(category))
    ].copy()

    # 00~06 및 activity_eligible == FALSE는 DEAD TIME 후보에서 제외
    if "activity_eligible" in time_rows.columns:
        eligible = (
            time_rows["activity_eligible"].astype(str).str.strip().str.lower()
            .isin(["true", "1", "yes"])
        )
    else:
        eligible = pd.Series(True, index=time_rows.index)

    dead_candidates = time_rows[
        (time_rows["time"].astype(str) != "00~06") & eligible
    ].copy()

    # area_summary의 dead_time을 우선 사용하고, 없으면 eligible gap 최대값
    dead_time = str(row.get("dead_time", "")).strip()
    if (not dead_time) or dead_time.lower() == "nan" or dead_time == "뚜렷한 DEAD TIME 없음":
        if not dead_candidates.empty:
            dead_time = str(dead_candidates.loc[dead_candidates["gap"].idxmax(), "time"])
        else:
            dead_time = "뚜렷한 DEAD TIME 없음"

    # 차트용 시간대: 기존 서비스와 동일하게 06~24 중심
    chart_rows = time_rows[time_rows["time"].astype(str) != "00~06"].copy()
    time_order = ["06~11", "11~14", "14~17", "17~21", "21~24"]
    chart_rows["time"] = pd.Categorical(chart_rows["time"], categories=time_order, ordered=True)
    chart_rows = chart_rows.sort_values("time")

    if chart_rows.empty:
        st.warning("이 상권·업종의 시간대 분석 결과가 없습니다.")
        st.stop()

    times = chart_rows["time"].astype(str).tolist()
    potential = chart_rows["potential"].astype(float).to_numpy()
    actual = chart_rows["actual"].astype(float).to_numpy()

    if dead_time in times:
        dead_index = times.index(dead_time)
    else:
        valid_gap = (potential - actual)
        dead_index = int(np.nanargmax(valid_gap))
        dead_time = times[dead_index]

    dead_gap = float(potential[dead_index] - actual[dead_index])

    # BEST TWIN 차이 TOP3
    twin_name_raw = row.get("twin_name", np.nan)
    twin_name = "" if pd.isna(twin_name_raw) else str(twin_name_raw).strip()
    twin_rows = twin_df_all[
        (twin_df_all["area"] == area) &
        (twin_df_all["category"] == str(category))
    ].copy()
    if twin_name:
        twin_rows = twin_rows[twin_rows["twin_name"].astype(str).str.strip() == twin_name]
    if "rank" in twin_rows.columns:
        twin_rows = twin_rows.sort_values("rank")
    twin_rows = twin_rows.head(3)

    why = []
    for r in twin_rows.itertuples(index=False):
        why.append((str(r.feature), float(r.difference), str(r.unit)))

    data = {
        "flow_score": float(row["flow_score"]),
        "traffic_score": float(row["traffic_score"]),
        "consumer_score": float(row["consumer_score"]),
        "times": times,
        "potential": potential.tolist(),
        "actual": actual.tolist(),
        "twin": twin_name,
        "similarity": float(row["similarity"]) if pd.notna(row["similarity"]) else np.nan,
        "twin_conversion": float(row["twin_conversion"]) if pd.notna(row["twin_conversion"]) else np.nan,
        "why": why,
    }

    twin_diff = (
        float(data["twin_conversion"] - actual[dead_index])
        if pd.notna(data["twin_conversion"]) else np.nan
    )

    if data["consumer_score"] < 50:
        flow_type = "전환 개선형"
        hero_line = "사람은 충분한데, 실제 소비로 이어지는 힘은 약한 편입니다."
        traffic_label = "충분한 편"
        conversion_label = "낮은 편"
        hero_sub = "새로운 사람을 더 모으는 것보다, 이미 존재하는 유동이 왜 소비로 이어지지 않는지 먼저 볼 필요가 있습니다."
    elif data["consumer_score"] < 70:
        flow_type = "균형 점검형"
        hero_line = "사람의 흐름과 소비 연결은 보통 수준이지만, 놓치는 구간이 있습니다."
        traffic_label = "보통 이상"
        conversion_label = "보통 수준"
        hero_sub = "전체 평균보다 시간대별 차이를 중심으로 소비 기회를 확인해볼 상권입니다."
    else:
        flow_type = "연결 우수형"
        hero_line = "사람의 흐름이 실제 소비로 비교적 잘 이어지는 편입니다."
        traffic_label = "충분한 편"
        conversion_label = "높은 편"
        hero_sub = "전체 수준보다 특정 시간대의 추가 기회와 유사상권의 차이를 확인해볼 수 있습니다."

    # 2. ONE-LINE DIAGNOSIS
    st.markdown(f'<div class="section-title">2. {area} · {category}는 어떤 상권일까요?</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="diagnosis-box">
            <div class="label">FLOW 진단 · {flow_type}</div>
            <div style="font-size:30px;font-weight:850;color:#173c67;line-height:1.35;margin:8px 0 10px;">
                {hero_line}
            </div>
            <div class="subtext">{hero_sub}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="card">
                <div class="label">사람의 흐름</div>
                <div style="font-size:27px;font-weight:850;color:#173c67;margin:7px 0;">{traffic_label}</div>
                <div class="subtext">같은 업종의 비교 상권 가운데 유동이 어느 정도인지 보여줍니다.</div>
            </div>
            """, unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="card">
                <div class="label">소비로 이어지는 정도</div>
                <div style="font-size:27px;font-weight:850;color:#a55c00;margin:7px 0;">{conversion_label}</div>
                <div class="subtext">상권 여건에 비해 실제 소비가 얼마나 연결되는지를 비교한 결과입니다.</div>
            </div>
            """, unsafe_allow_html=True
        )

    with st.expander("ⓘ 분석지수도 확인하고 싶어요"):
        st.write(
            f"분석지수 기준으로 유동 수준은 {data['traffic_score']}, FLOW SCORE는 {data['flow_score']}입니다. "
            "두 값은 매출액이나 미래 매출 예측값이 아니라 상권 간 상대 비교를 위한 분석지표입니다."
        )

    # -----------------------------
    # QUICK SUMMARY
    # -----------------------------
    eligible_rank = dead_candidates.copy()
    eligible_rank["gap"] = pd.to_numeric(eligible_rank["gap"], errors="coerce")
    eligible_rank = eligible_rank.dropna(subset=["gap"]).sort_values("gap", ascending=False)

    if data["consumer_score"] < 50:
        quick_type = "유동은 충분하지만 소비 연결은 약한 편"
    elif data["consumer_score"] < 70:
        quick_type = "유동과 소비 연결은 보통 수준"
    else:
        quick_type = "유동이 소비로 비교적 잘 이어지는 편"

    quick_twin = data["twin"] if data["twin"] else "성과가 더 높은 유사상권 없음"

    st.markdown("#### 한눈에 보는 FLOW 진단")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown(
            f"""<div class="card" style="min-height:145px;">
            <div class="label">상권 유형</div>
            <div style="font-size:20px;font-weight:850;color:#173c67;margin-top:9px;">{quick_type}</div>
            </div>""", unsafe_allow_html=True
        )
    with q2:
        st.markdown(
            f"""<div class="card" style="min-height:145px;">
            <div class="label">가장 먼저 볼 시간</div>
            <div style="font-size:27px;font-weight:850;color:#a55c00;margin-top:9px;">{dead_time}</div>
            <div class="subtext">소비 연결 격차가 가장 큰 시간</div>
            </div>""", unsafe_allow_html=True
        )
    with q3:
        st.markdown(
            f"""<div class="card" style="min-height:145px;">
            <div class="label">비교해볼 상권</div>
            <div style="font-size:21px;font-weight:850;color:#173c67;margin-top:9px;">{quick_twin}</div>
            <div class="subtext">구조가 비슷한 비교 기준</div>
            </div>""", unsafe_allow_html=True
        )


    # 3. TIME
    st.markdown('<div class="section-title">3. 사람이 소비로 가장 덜 이어지는 시간은?</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="action-box">
            <div class="label">가장 큰 소비공백이 나타난 시간</div>
            <div style="font-size:34px;font-weight:850;color:#a55c00;margin:5px 0 7px;">{dead_time}</div>
            <div style="font-size:17px;font-weight:750;color:#18324a;line-height:1.65;">
                이 시간대는 주변 유동과 상권 조건에 비해 실제 소비가 상대적으로 낮게 나타났습니다.
            </div>
            <div class="subtext">
                즉, 사람이 전혀 없는 시간이 아니라 <b>사람의 활동이 소비로 충분히 이어지지 않는 시간</b>에 가깝습니다.
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    time_df = pd.DataFrame({
        "시간대": data["times"],
        "소비가 일어날 여건": data["potential"],
        "실제 소비 수준": data["actual"]
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=time_df["시간대"], y=time_df["소비가 일어날 여건"],
        name="소비가 일어날 여건", marker_color="#A8C7E8"
    ))
    fig.add_trace(go.Bar(
        x=time_df["시간대"], y=time_df["실제 소비 수준"],
        name="실제 소비 수준", marker_color="#245B91"
    ))
    fig.update_layout(
        barmode="group", height=390,
        margin=dict(l=15, r=15, t=50, b=15),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(gridcolor="#e9eef3", title="상대 지수", showticklabels=False),
        xaxis=dict(showgrid=False, title=""),
        bargap=0.28
    )
    fig.add_vrect(
        x0=dead_index - 0.45, x1=dead_index + 0.45,
        fillcolor="rgba(255,177,85,0.14)", line_width=0, layer="below"
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(
        f"""
        <div style="background:#eef6ff;border-left:4px solid #245B91;border-radius:8px;padding:14px 16px;margin-top:2px;">
            <b>{dead_time}을 먼저 보세요.</b><br>
            다른 시간대보다 소비가 일어날 여건과 실제 소비 사이의 격차가 가장 크게 나타납니다.
            FLOW는 이를 '매출이 오를 시간'이 아니라 <b>우선 점검할 시간</b>으로 해석합니다.
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown("#### 시간대 점검 우선순위")
    if not eligible_rank.empty:
        first_rr = eligible_rank.iloc[0]
        st.markdown(
            f"""<div class="card" style="border-left:4px solid #a55c00;">
            <div class="label">우선 확인</div>
            <div style="font-size:24px;font-weight:850;color:#a55c00;margin:7px 0;">{first_rr["time"]}</div>
            <div style="font-size:15px;line-height:1.65;">
            상권 여건 대비 실제 소비의 상대적 격차가 가장 크게 나타난 시간대입니다.
            </div></div>""",
            unsafe_allow_html=True
        )
        rest = eligible_rank.iloc[1:].copy()
        rest = rest[pd.to_numeric(rest["gap"], errors="coerce") > 0]
        if rest.empty:
            st.caption("나머지 시간대에서는 추가로 크게 두드러지는 소비공백 신호가 확인되지 않았습니다.")
        else:
            st.caption("다음으로 참고할 시간대: " + " · ".join(rest["time"].astype(str).head(2).tolist()))
        st.caption("※ 00~06 및 활동 관측 근거가 부족한 시간대는 DEAD TIME 우선순위에서 제외합니다.")

    with st.expander("ⓘ 그래프는 어떻게 계산됐나요?"):
        st.write(
            f"분석 내부 지수에서는 {dead_time}의 상권 조건을 고려한 상대적 소비 기대수준이 "
            f"{potential[dead_index]:.0f}, 실제 소비 수준이 {actual[dead_index]:.0f}로 계산되었습니다. "
            f"차이는 {dead_gap:.0f}입니다. 이 값은 원화 매출이나 미래 매출 예측치가 아닙니다."
        )

    # 4. TWIN
    st.markdown('<div class="section-title">4. 비슷한 조건인데 더 잘되는 곳은?</div>', unsafe_allow_html=True)

    if not data["twin"]:
        st.info("현재 조건에서 성과가 더 높은 유사상권을 찾지 못했습니다.")
    else:
        similarity_text = f"{data['similarity']:.1f}" if pd.notna(data["similarity"]) else "—"
        twin_conversion_text = f"{data['twin_conversion']:.1f}" if pd.notna(data["twin_conversion"]) else "—"
        twin_diff_text = f"+{twin_diff:.1f}" if pd.notna(twin_diff) else "—"

        st.markdown(
            f"""
            <div class="twin-box">
                <div class="label">왜 {data["twin"]}을 보여주나요?</div>
                <div style="font-size:25px;font-weight:850;color:#173c67;margin:8px 0;">
                    우리와 구조는 비슷하지만, 소비 연결은 더 활발하기 때문입니다.
                </div>
                <div class="subtext">
                    유사도 지수 {similarity_text} · 실제 특성의 일치율이 아니라 구조적 비교를 위한 지수입니다.
                </div>
            </div>
            """, unsafe_allow_html=True
        )

        v1, vm, v2 = st.columns([1, .25, 1])
        with v1:
            st.markdown(
                f"""<div class="card" style="min-height:175px;text-align:center;">
                <div class="label">우리 상권</div>
                <div style="font-size:22px;font-weight:850;color:#173c67;margin:9px 0;">{area}</div>
                <div style="font-size:15px;">{dead_time} 소비 연결</div>
                <div style="font-size:22px;font-weight:850;color:#a55c00;margin-top:6px;">상대적으로 낮음</div>
                </div>""", unsafe_allow_html=True
            )
        with vm:
            st.markdown("<div style='text-align:center;font-size:24px;font-weight:800;padding-top:70px;'>VS</div>", unsafe_allow_html=True)
        with v2:
            st.markdown(
                f"""<div class="card" style="min-height:175px;text-align:center;">
                <div class="label">BEST TWIN</div>
                <div style="font-size:22px;font-weight:850;color:#173c67;margin:9px 0;">{data["twin"]}</div>
                <div style="font-size:15px;">같은 비교 기준</div>
                <div style="font-size:22px;font-weight:850;color:#245B91;margin-top:6px;">소비 연결 더 활발</div>
                </div>""", unsafe_allow_html=True
            )

        with st.expander("ⓘ 분석값으로 비교하기"):
            st.write(
                f"내부 분석지수 기준 우리 상권 {dead_time} 소비 수준은 {actual[dead_index]:.1f}, "
                f"BEST TWIN 비교값은 {twin_conversion_text}, 차이는 {twin_diff_text}입니다. "
                "이 값은 원화 매출이나 실제 매출 증가율이 아닙니다."
            )

        if data["why"]:
            st.markdown("#### 결과가 다른 이유를 살펴볼 비교 단서")
            why_cols = st.columns(len(data["why"]))
            positive_features = []
            for i, (feature, diff, unit) in enumerate(data["why"]):
                if diff > 0:
                    positive_features.append((feature, diff, unit))
                with why_cols[i]:
                    direction = "우리 상권이 낮음" if diff < 0 else "우리 상권이 높음"
                    value = f"{abs(diff):.1f}" if abs(diff) < 100 else f"{abs(diff):,.0f}"
                    st.markdown(
                        f"""<div class="card" style="min-height:155px;">
                        <div class="label">비교 단서 {i+1}</div>
                        <div style="font-size:18px;font-weight:800;color:#183f6c;margin:7px 0;">{feature}</div>
                        <div style="font-size:14px;line-height:1.6;"><b>{direction}</b><br>{value}{unit} 차이</div>
                        </div>""", unsafe_allow_html=True
                    )

            meaningful_positive = [(f, d, u) for f, d, u in positive_features if abs(d) >= 0.05]
            if meaningful_positive:
                pf, pdiff, punit = meaningful_positive[0]
                st.success(
                    f"**우리 상권이 이미 가진 특징:** BEST TWIN과 비교하면 `{pf}`은 우리 상권이 더 높게 나타납니다. "
                    "이는 매출 성과의 원인이라는 뜻이 아니라, 현재 상권이 가진 구조적 특징입니다."
                )

            st.caption("※ 위 차이는 소비성과 차이의 원인으로 확정한 결과가 아니라, 추가로 확인할 비교 단서입니다.")

        with st.expander("ⓘ BEST TWIN과 유사도는 어떻게 해석하나요?"):
            st.write(
                "BEST TWIN은 구조가 유사한 후보 중 소비 연결 성과가 더 높은 비교 상권입니다. "
                "유사도는 실제 특성 일치율이 아니라 16개 상권특성에서 두 상권의 평균 백분위 차이를 이용한 구조적 유사도입니다."
            )

    # 5. STORE DIAGNOSIS
    st.markdown('<div class="section-title">5. 우리 가게에서는 무엇부터 확인해야 할까요?</div>', unsafe_allow_html=True)
    st.write(
        "여기부터는 **상권 분석 결과와 사장님의 응답을 함께 비교**합니다. "
        "FLOW가 현재 보유한 것은 상권 단위 데이터이며, 개별 점포의 POS·입점 데이터는 아직 연결되어 있지 않습니다. "
        "따라서 아래 결과는 원인을 확정하는 처방이 아니라 **내 가게에서 다음으로 무엇을 확인할지 정하는 점검 가이드**입니다."
    )

    compare_store = st.checkbox("내 가게 맞춤 점검 시작하기", key="compare_store")

    if compare_store:
        store_weak = st.selectbox(
            "① 평소 주문이나 매출이 가장 약한 시간대는 언제인가요?",
            ["선택해주세요"] + list(data["times"]),
            key="store_weak_time"
        )

        store_stage = st.radio(
            "② 그 시간대에 가장 가까운 상황은 무엇인가요?",
            [
                "잘 모르겠어요",
                "주변에 사람 자체가 적어요",
                "사람은 지나가지만 가게로 잘 들어오지 않아요",
                "손님은 들어오지만 주문·구매가 기대보다 적어요"
            ],
            key="store_stage"
        )

        store_channel = st.radio(
            "③ 평소 매출이 가장 많이 발생하는 방식은 무엇인가요?",
            ["매장 중심", "포장 중심", "배달 중심", "혼합형", "잘 모르겠어요"],
            key="store_channel",
            horizontal=True
        )

        if store_weak != "선택해주세요":
            same_time = store_weak == dead_time

            if same_time:
                result_title = "상권과 내 가게가 같은 시간대에서 약합니다."
                result_desc = (
                    f"상권에서도 {dead_time}의 소비공백이 가장 크고, 사장님이 입력한 가게의 취약시간도 {store_weak}입니다. "
                    "점포만의 문제로 단정하기보다 상권 공통 패턴과 점포 운영을 함께 비교해볼 필요가 있습니다."
                )
                badge = "상권 공통 패턴 가능성도 함께 확인"
            else:
                result_title = "상권보다 내 가게의 개별 문제를 먼저 확인해보세요."
                result_desc = (
                    f"상권 전체에서는 {dead_time}의 소비공백이 가장 크지만, 사장님 가게는 {store_weak}이 가장 약하다고 응답했습니다. "
                    "상권 평균과 다른 패턴이므로 먼저 점포 내부의 운영·입점·구매 과정을 비교해보는 편이 타당합니다."
                )
                badge = "점포 개별 패턴 우선 점검"

            st.markdown("### 맞춤 점검 결과")
            st.markdown(
                f"""
                <div class="diagnosis-box">
                    <div class="label">MY STORE × FLOW · {badge}</div>
                    <div style="font-size:25px;font-weight:850;color:#173c67;margin:7px 0;">{result_title}</div>
                    <div class="subtext">{result_desc}</div>
                </div>
                """, unsafe_allow_html=True
            )

            # Priority 1: stage-based check
            if store_stage == "사람은 지나가지만 가게로 잘 들어오지 않아요":
                p1_title = f"{store_weak} 입점률을 비교해보세요"
                p1_text = (
                    f"{store_weak}의 '매장 앞 통행 인원 대비 실제 입점 인원'을 기록하고, "
                    "평소 잘되는 시간대의 입점률과 비교해보세요. 취약시간에만 입점률이 크게 낮다면 "
                    "상권 전체보다 점포 앞 접점에서 문제가 생기는지 확인할 단서가 됩니다."
                )
                p1_how = "직접 기록: 매장 앞 통행 인원 ÷ 실제 입점 인원"
            elif store_stage == "손님은 들어오지만 주문·구매가 기대보다 적어요":
                p1_title = f"{store_weak} 구매전환을 비교해보세요"
                p1_text = (
                    f"{store_weak}의 방문자 수와 실제 주문건수를 기록하고 평소 잘되는 시간대와 비교해보세요. "
                    "방문은 비슷한데 주문 비율만 낮다면 방문 이후 주문 단계에서 문제가 생기는지 살펴볼 수 있습니다."
                )
                p1_how = "직접 기록: 방문자 수 · 주문건수 · 가능하면 객단가"
            elif store_stage == "주변에 사람 자체가 적어요":
                p1_title = f"{store_weak} 매장 앞 유동을 비교해보세요"
                p1_text = (
                    f"상권 전체 유동과 실제 매장 앞 유동은 다를 수 있습니다. {store_weak}의 매장 앞 통행 인원을 "
                    "평소 잘되는 시간대와 같은 방식으로 세어 비교해보세요."
                )
                p1_how = "직접 기록: 동일 시간 간격의 매장 앞 통행 인원"
            else:
                p1_title = f"{store_weak} 기본 흐름부터 기록해보세요"
                p1_text = (
                    "현재 응답만으로 어느 단계에서 막히는지 특정하기 어렵습니다. "
                    "통행 → 입점 → 주문의 세 단계를 같은 시간대에 기록하면 다음 점검 대상을 좁힐 수 있습니다."
                )
                p1_how = "직접 기록: 통행 인원 · 입점 인원 · 주문건수"

            # Priority 2: channel-based check
            if store_channel == "포장 중심":
                p2_title = "포장 주문 흐름을 따로 보세요"
                p2_text = (
                    "포장 중심 매장은 매장 방문 전체와 포장 주문을 섞어 보면 문제가 가려질 수 있습니다. "
                    "취약시간과 정상시간의 포장 주문건수와 대기시간을 같은 기준으로 비교해보세요."
                )
                p2_how = "POS/직접 확인: 포장 주문건수 · 평균 대기시간"
            elif store_channel == "배달 중심":
                p2_title = "배달 주문 흐름을 따로 보세요"
                p2_text = (
                    "배달 중심 매장은 거리 유동만으로 설명하기 어렵습니다. "
                    "취약시간과 정상시간의 배달 주문건수·취소건수를 분리해 비교해보세요."
                )
                p2_how = "배달앱/POS 확인: 주문건수 · 취소건수"
            elif store_channel == "매장 중심":
                p2_title = "입점 이후 주문까지 비교하세요"
                p2_text = (
                    "매장 중심이라면 취약시간과 정상시간에서 입점 인원 대비 주문건수가 달라지는지 확인하세요. "
                    "입점은 비슷한데 주문만 줄어드는지 구분하는 것이 핵심입니다."
                )
                p2_how = "직접/POS 확인: 입점 인원 · 주문건수"
            elif store_channel == "혼합형":
                p2_title = "판매 채널을 나눠 비교하세요"
                p2_text = (
                    "매장·포장·배달을 합산하면 어느 채널에서 약해지는지 보이지 않습니다. "
                    "취약시간과 정상시간의 주문건수를 채널별로 나눠 비교해보세요."
                )
                p2_how = "POS 확인: 매장 · 포장 · 배달 주문건수"
            else:
                p2_title = "매출이 생기는 채널부터 구분하세요"
                p2_text = (
                    "매장·포장·배달 중 어느 방식이 매출의 중심인지 먼저 나누어 보면 "
                    "취약시간의 원인을 더 구체적으로 좁힐 수 있습니다."
                )
                p2_how = "POS 확인: 채널별 주문건수 또는 매출 비중"

            # Priority 3: relation to area pattern
            if same_time:
                p3_title = f"{dead_time}을 비교상권과 함께 보세요"
                p3_text = (
                    f"내 가게와 상권의 취약시간이 모두 {dead_time}입니다. "
                    f"FLOW의 상권 데이터와 유사상권 비교 결과를 함께 참고할 수 있습니다. "
                    "점포 기록을 확보한 뒤 이 시간대의 차이를 우선 비교해볼 가치가 있습니다."
                )
                p3_how = "FLOW 보유: 상권 시간대 결과 · BEST TWIN 비교"
            else:
                p3_title = f"상권의 {dead_time} 소비공백은 다음으로 확인하세요"
                p3_text = (
                    f"현재 사장님 가게는 {store_weak}이 더 약하다고 응답했습니다. "
                    f"먼저 점포 기록으로 {store_weak}의 문제를 확인하고, 이후 상권 공통 취약시간인 {dead_time} 대응을 검토하세요."
                )
                p3_how = "FLOW 보유: 상권 취약시간 / 점포 데이터: 사장님 확인 필요"

            st.markdown("### FLOW ACTION · 확인 순서")
            ac1, ac2, ac3 = st.columns(3)
            actions = [
                ("1순위", p1_title, p1_text, p1_how),
                ("2순위", p2_title, p2_text, p2_how),
                ("3순위", p3_title, p3_text, p3_how),
            ]
            for col, (rank, title, desc, how) in zip([ac1, ac2, ac3], actions):
                with col:
                    st.markdown(
                        f"""
                        <div class="card" style="min-height:285px;">
                            <div class="label">{rank}</div>
                            <div style="font-size:19px;font-weight:850;color:#183f6c;margin:8px 0 10px;">{title}</div>
                            <div style="font-size:14px;line-height:1.72;margin-bottom:16px;">{desc}</div>
                            <div style="font-size:12px;font-weight:850;color:#71808f;">어떻게 확인하나요?</div>
                            <div style="font-size:13px;line-height:1.55;margin-top:5px;">{how}</div>
                        </div>
                        """, unsafe_allow_html=True
                    )

            st.markdown(
                """
                <div style="background:#eef6ff;border-left:4px solid #245B91;border-radius:8px;padding:14px 16px;margin-top:12px;">
                    <b>현재 FLOW가 직접 분석한 데이터와 사장님이 추가로 확인할 데이터는 다릅니다.</b><br>
                    FLOW는 현재 상권 단위의 유동·소비·시간대·비교상권 데이터를 분석합니다.
                    입점자 수, 입점률, 주문건수, 객단가 같은 개별 점포 데이터는 현재 연결되어 있지 않아
                    위 ACTION에서는 <b>사장님이 다음으로 확인할 항목과 비교 방법</b>을 안내합니다.
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### 직접 점검 체크리스트")
            st.caption("아래 항목은 FLOW가 이미 보유한 값이 아니라, 사장님이 점포에서 직접 확인할 수 있는 다음 단계입니다.")

            st.checkbox(f"{store_weak} 매장 앞 통행 인원을 같은 시간 간격으로 기록했다", key="check_traffic")
            st.checkbox(f"{store_weak} 실제 입점 인원 또는 방문자 수를 기록했다", key="check_entry")
            st.checkbox("평소 잘되는 시간대도 같은 방식으로 기록했다", key="check_normal")
            st.checkbox("두 시간대의 주문건수 또는 POS 기록을 확인했다", key="check_orders")

            with st.expander("간단 비교 계산기"):
                st.write("직접 기록한 값이 있다면 취약시간과 평소 잘되는 시간의 입점률을 간단히 비교할 수 있습니다.")
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.markdown(f"**취약시간 · {store_weak}**")
                    weak_pass = st.number_input("통행 인원", min_value=0, value=0, step=1, key="weak_pass")
                    weak_enter = st.number_input("입점 인원", min_value=0, value=0, step=1, key="weak_enter")
                with cc2:
                    st.markdown("**평소 잘되는 시간대**")
                    normal_pass = st.number_input("통행 인원 ", min_value=0, value=0, step=1, key="normal_pass")
                    normal_enter = st.number_input("입점 인원 ", min_value=0, value=0, step=1, key="normal_enter")

                if weak_pass > 0 and normal_pass > 0:
                    weak_rate = weak_enter / weak_pass * 100
                    normal_rate = normal_enter / normal_pass * 100
                    diff_rate = weak_rate - normal_rate
                    r1, r2, r3 = st.columns(3)
                    r1.metric("취약시간 입점률", f"{weak_rate:.1f}%")
                    r2.metric("평소시간 입점률", f"{normal_rate:.1f}%")
                    r3.metric("차이", f"{diff_rate:+.1f}%p")
                    if diff_rate < 0:
                        st.info(
                            f"취약시간의 입점률이 평소시간보다 {abs(diff_rate):.1f}%p 낮습니다. "
                            "이 결과는 사용자가 직접 입력한 점포 기록의 단순 비교이며, FLOW의 상권 분석값이나 인과분석 결과는 아닙니다."
                        )
                    else:
                        st.info(
                            "입점률만 보면 취약시간이 더 낮지 않습니다. 주문 전환이나 객단가 등 다른 단계를 추가로 확인해볼 수 있습니다. "
                            "이 결과는 사용자가 입력한 점포 기록의 단순 비교입니다."
                        )

            with st.expander("ⓘ 점포 데이터가 연결되면 무엇이 달라지나요?"):
                st.write(
                    "향후 POS·주문·입점 데이터가 연결되면 사용자가 직접 기록하지 않아도 "
                    "시간대별 입점률, 구매전환, 채널별 주문 흐름 등을 상권 패턴과 자동 비교하는 방식으로 확장할 수 있습니다. "
                    "현재 프로토타입은 그 이전 단계인 '어디를 먼저 확인해야 하는지'를 좁혀주는 기능입니다."
                )

        with st.expander("ⓘ 고객 연령대는 왜 묻지 않나요?"):
            st.write(
                "현재 DEMO 결과에는 상권·업종·시간대별 고객 연령대 소비를 직접 비교할 수 있는 데이터가 없습니다. "
                "근거가 없는 맞춤진단을 피하기 위해 현재 버전에서는 연령대를 사용하지 않습니다."
            )

    st.divider()
    st.markdown("### FLOW는 무엇이 다른가요?")
    st.markdown(
        "**유동인구가 많은지를 보여주는 데서 끝나지 않습니다. "
        "사람의 활동이 소비로 충분히 이어지지 않는 시간대를 찾고, "
        "비슷한 상권과 비교한 뒤 내 가게에서 무엇부터 확인해야 하는지 좁혀줍니다.**"
    )
    st.caption(
        "현재 버전은 DEMO 데이터 기반 프로토타입입니다. 분석지수는 상권 간 상대 비교를 위한 값이며 "
        "개별 점포의 미래 매출이나 특정 요인의 인과효과를 예측하지 않습니다."
    )
