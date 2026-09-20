import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
AGE_FILE = _find_csv("age_comparison.csv")

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
def load_age_comparison():
    df = pd.read_csv(AGE_FILE, encoding="utf-8-sig")
    df["area_code"] = df["area_code"].astype(str).str.strip()
    df["category"] = df["category"].astype(str).str.strip()
    return df

age_df = load_age_comparison()

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

/* ===== FLOW sidebar polish ===== */
section[data-testid="stSidebar"] {
    width: 310px !important;
    min-width: 310px !important;
    background: linear-gradient(180deg, #123f6d 0%, #174f82 100%);
    border-right: none;
}
section[data-testid="stSidebar"] > div {
    width: 310px !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 34px 22px 28px 22px !important;
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.94);
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.18);
}
section[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: 8px;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 12px;
    padding: 10px 12px;
    margin-bottom: 3px;
    transition: all 0.15s ease;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255,255,255,0.13);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: white;
    border-color: white;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #174f82 !important;
    font-weight: 800 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] p {
    font-size: 15px !important;
}
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: rgba(255,255,255,0.68) !important;
    font-size: 12px !important;
}


/* ===== final navigation + hero polish ===== */

/* Sidebar menu: full, consistent width */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    width: 100% !important;
    min-height: 48px;
    display: flex !important;
    align-items: center !important;
    box-sizing: border-box !important;
    padding: 11px 14px !important;
}

/* Hide Streamlit's native radio circles */
section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
    display: none !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    margin: 0 !important;
    width: 100%;
}

/* Selected / unselected menu styling */
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
    background: #ffffff !important;
    border-color: #ffffff !important;
    box-shadow: 0 5px 14px rgba(0,0,0,0.10);
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) p {
    color: #174f82 !important;
    font-weight: 850 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:not(:has(input:checked)) {
    background: rgba(255,255,255,0.065) !important;
    border-color: rgba(255,255,255,0.13) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label:not(:has(input:checked)) p {
    color: rgba(255,255,255,0.94) !important;
}

/* Compact hero so the actual service starts higher */
.hero {
    padding: 34px 40px !important;
    min-height: 0 !important;
    margin-bottom: 18px !important;
}
.hero-title {
    font-size: 42px !important;
    line-height: 1.05 !important;
    margin-bottom: 14px !important;
}
.hero-sub {
    font-size: 24px !important;
    line-height: 1.3 !important;
    margin-bottom: 13px !important;
}
.hero-desc {
    font-size: 14px !important;
    line-height: 1.55 !important;
}

/* Reduce first-section vertical gap */
.section-title {
    margin-top: 30px !important;
}

/* Smaller screens / high browser zoom */
@media (max-width: 1100px) {
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        width: 260px !important;
        min-width: 260px !important;
    }
    .hero {
        padding: 28px 30px !important;
    }
    .hero-title {
        font-size: 36px !important;
    }
    .hero-sub {
        font-size: 21px !important;
    }
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


# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.sidebar.markdown(
    """
    <div style="padding:4px 2px 22px 2px;">
        <div style="font-size:30px;font-weight:900;letter-spacing:-0.5px;color:white;">FLOW</div>
        <div style="font-size:13px;font-weight:650;color:rgba(255,255,255,.76);margin-top:5px;">
            사람의 흐름을 소비의 흐름으로
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
page = st.sidebar.radio(
    "메뉴",
    ["01  상권 진단", "02  시간대 진단", "03  비교 TWIN", "04  가게 점검", "05  Action Point"],
    label_visibility="collapsed"
)
page = {
    "01  상권 진단": "상권 진단",
    "02  시간대 진단": "시간대 진단",
    "03  비교 TWIN": "비교 TWIN",
    "04  가게 점검": "가게 점검",
    "05  Action Point": "Action Point",
}.get(page, page)
st.sidebar.markdown("---")
if st.session_state.get("selected_key"):
    _nav_code, _nav_cat = st.session_state.selected_key
    _nav_row = area_df[(area_df["area_code"] == str(_nav_code)) & (area_df["category"] == str(_nav_cat))]
    if not _nav_row.empty:
        st.sidebar.caption("현재 분석")
        st.sidebar.markdown(f"**{_nav_row.iloc[0]['area']}**")
        st.sidebar.caption(str(_nav_cat))
else:
    st.sidebar.caption("먼저 상권과 업종을 선택해주세요.")

if page == "상권 진단":
    st.markdown('<div class="section-title">1. 내 상권 찾아보기</div>', unsafe_allow_html=True)
    st.caption("분석할 상권과 업종을 선택하세요.")
    
    # -----------------------------
    # 지역 탐색용 메타데이터
    # GitHub에 이미 올라가 있는 flow_area_map.csv를 사용합니다.
    # 이 파일의 실제 컬럼:
    # area_code, area_name, district, dong, lat, lon, area_size
    # -----------------------------
    MAP_FILE = _find_csv("flow_area_map.csv")
    
    @st.cache_data
    def load_region_data():
        region = pd.read_csv(MAP_FILE, encoding="utf-8-sig")
    
        region = region.rename(columns={
            "area_name": "area",
            "district": "gu",
        })
    
        region["area_code"] = region["area_code"].astype(str).str.strip()
        for col in ["area", "gu", "dong"]:
            region[col] = region[col].astype(str).str.strip()
    
        return region[["area_code", "area", "gu", "dong"]].drop_duplicates()
    
    region_df = load_region_data()
    
    # area_summary.csv에서 실제 분석 가능한 상권만 남깁니다.
    available_codes = set(area_df["area_code"].astype(str).str.strip())
    region_flow = region_df[region_df["area_code"].isin(available_codes)].copy()
    
    
    # ─────────────────────────────────────────────
    # 상권 선택 UI — 두 경로를 탭으로 분리
    # ─────────────────────────────────────────────
    st.markdown("""
    <style>
    .finder-head{
        margin:4px 0 16px;
        padding:18px 20px;
        border:1px solid #dfe8f1;
        border-radius:16px;
        background:#ffffff;
    }
    .finder-head .title{font-size:18px;font-weight:900;color:#18324a;margin-bottom:5px}
    .finder-head .sub{font-size:13px;color:#7b8996}
    .choice-summary{
        background:#eef6ff;
        border:1px solid #d5e7fa;
        border-left:4px solid #1f5f99;
        border-radius:12px;
        padding:13px 16px;
        margin:14px 0 12px;
    }
    .choice-summary .eyebrow{font-size:11px;font-weight:800;color:#71859a;margin-bottom:4px}
    .choice-summary .main{font-size:17px;font-weight:900;color:#173c67}
    .choice-summary .meta{font-size:12px;color:#687b8e;margin-top:4px}
    .step-hint{
        font-size:12px;color:#83909b;margin:4px 0 10px;
    }
    div[data-baseweb="tab-list"]{
        gap:8px;
        background:#edf2f6;
        padding:5px;
        border-radius:12px;
    }
    button[data-baseweb="tab"]{
        border-radius:9px;
        font-weight:800;
        padding-top:10px;
        padding-bottom:10px;
    }
    </style>
    
    <div class="finder-head">
      <div class="title">내 상권은 어떻게 찾을까요?</div>
      <div class="sub">지역을 차례로 좁히거나, 알고 있는 상권명을 바로 검색할 수 있습니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    selected_code = None
    selected_area_label = None
    selected_gu_final = None
    selected_dong_final = None
    
    tab_region, tab_search = st.tabs(["📍 지역으로 찾기", "⌕ 상권명 검색"])
    
    with tab_region:
        st.markdown('<div class="step-hint">① 자치구 → ② 행정동 → ③ 상권</div>', unsafe_allow_html=True)
    
        gu_options = sorted(region_flow["gu"].dropna().unique().tolist())
        selected_gu = st.selectbox(
            "① 자치구",
            ["자치구를 선택해주세요"] + gu_options,
            key="region_gu"
        )
    
        if selected_gu != "자치구를 선택해주세요":
            gu_region = region_flow[region_flow["gu"] == selected_gu].copy()
            dong_options = sorted(gu_region["dong"].dropna().unique().tolist())
    
            selected_dong = st.selectbox(
                "② 행정동",
                ["행정동을 선택해주세요"] + dong_options,
                key="region_dong"
            )
    
            if selected_dong != "행정동을 선택해주세요":
                dong_region = (
                    gu_region[gu_region["dong"] == selected_dong][["area", "area_code"]]
                    .drop_duplicates()
                    .sort_values(["area", "area_code"])
                )
    
                dong_labels = {}
                for row in dong_region.itertuples(index=False):
                    label = row.area
                    if (dong_region["area"] == row.area).sum() > 1:
                        label = f"{row.area} · {row.area_code}"
                    dong_labels[label] = str(row.area_code)
    
                if dong_labels:
                    area_choice = st.selectbox(
                        "③ 상권",
                        ["상권을 선택해주세요"] + list(dong_labels.keys()),
                        key="region_area"
                    )
                    if area_choice != "상권을 선택해주세요":
                        selected_area_label = area_choice
                        selected_code = dong_labels[area_choice]
                        selected_gu_final = selected_gu
                        selected_dong_final = selected_dong
                else:
                    st.info("이 행정동에는 현재 FLOW 분석 결과와 연결되는 상권이 없습니다.")
    
    with tab_search:
        st.markdown('<div class="step-hint">상권명 일부만 입력해도 검색됩니다.</div>', unsafe_allow_html=True)
        search_query = st.text_input(
            "상권명 검색",
            placeholder="예: 광흥창, 신촌, 건대, 백산초등학교",
            key="area_search_query"
        ).strip()
    
        if search_query:
            search_pool = (
                region_flow[region_flow["area"].str.contains(search_query, case=False, na=False)]
                [["area", "area_code", "gu", "dong"]]
                .drop_duplicates()
                .sort_values(["area", "gu", "dong"])
            )
    
            if search_pool.empty:
                st.warning("검색어와 일치하는 FLOW 분석 상권을 찾지 못했습니다.")
            else:
                search_labels = {}
                search_meta = {}
                for row in search_pool.itertuples(index=False):
                    label = f"{row.area} · {row.gu} {row.dong}"
                    if label in search_labels:
                        label = f"{label} · {row.area_code}"
                    search_labels[label] = str(row.area_code)
                    search_meta[label] = (row.area, row.gu, row.dong)
    
                searched_label = st.selectbox(
                    f"검색 결과 {len(search_labels)}곳",
                    ["검색 결과를 선택해주세요"] + list(search_labels.keys()),
                    key="searched_area"
                )
    
                if searched_label != "검색 결과를 선택해주세요":
                    selected_code = search_labels[searched_label]
                    selected_area_label, selected_gu_final, selected_dong_final = search_meta[searched_label]
    
    # 탭은 Streamlit rerun 때 양쪽 위젯이 모두 존재할 수 있으므로,
    # 실제 선택 완료된 값이 있으면 세션에 저장하여 공통 업종 단계에서 사용합니다.
    if selected_code is not None:
        st.session_state["finder_selected_code"] = str(selected_code)
        st.session_state["finder_selected_area"] = selected_area_label
        st.session_state["finder_selected_gu"] = selected_gu_final
        st.session_state["finder_selected_dong"] = selected_dong_final
    
    selected_code = st.session_state.get("finder_selected_code")
    selected_area_label = st.session_state.get("finder_selected_area")
    selected_gu_final = st.session_state.get("finder_selected_gu")
    selected_dong_final = st.session_state.get("finder_selected_dong")
    
    if selected_code:
        selected_area_rows = area_df[
            area_df["area_code"].astype(str).str.strip() == str(selected_code)
        ].copy()
    
        if not selected_area_rows.empty:
            selected_area_name = selected_area_rows["area"].iloc[0]
            category_options = sorted(
                selected_area_rows["category"].dropna().astype(str).unique().tolist()
            )
    
            st.markdown("---")
            st.markdown("##### 분석 업종")
            selected_category = st.selectbox(
                "업종 선택",
                category_options,
                key=f"category_{selected_code}",
                label_visibility="collapsed"
            )
    
            st.markdown(
                f"""
                <div class="choice-summary">
                  <div class="eyebrow">선택 완료</div>
                  <div class="main">{selected_area_name} · {selected_category}</div>
                  <div class="meta">{selected_gu_final or ''} {selected_dong_final or ''}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            selected_category = None
            st.warning("선택한 상권의 분석 데이터를 찾지 못했습니다.")
    else:
        selected_category = None
    
    with st.expander("ⓘ 내가 어느 상권인지 잘 모르겠어요"):
        st.write(
            "FLOW의 상권명은 서울시 상권분석서비스에서 제공하는 상권 단위를 기준으로 합니다. "
            "익숙한 동네 이름과 다를 수 있으므로, 자치구·행정동으로 찾아보거나 상권명을 검색해 확인할 수 있습니다."
        )
    
    if st.button(
        "FLOW 진단하기 →",
        type="primary",
        use_container_width=True,
        disabled=(selected_code is None or selected_category is None)
    ):
        st.session_state.selected_key = (selected_code, selected_category)
        st.session_state.show_result = True
    

if page != "상권 진단" and not (st.session_state.show_result and st.session_state.selected_key):
    st.info("먼저 **상권 진단** 메뉴에서 상권과 업종을 선택하고 FLOW 진단을 실행해주세요.")

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

    # DEAD TIME은 R 핵심분석의 최종 판정 결과(area_summary)를 그대로 사용
    dead_time = str(row.get("dead_time", "")).strip()
    has_dead_time = bool(
        dead_time and dead_time.lower() != "nan"
        and dead_time != "뚜렷한 DEAD TIME 없음"
    )
    if not has_dead_time:
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

    if has_dead_time and dead_time in times:
        dead_index = times.index(dead_time)
        dead_gap = float(potential[dead_index] - actual[dead_index])
    else:
        dead_index = None
        dead_gap = np.nan

    # 비교 TWIN 차이 TOP3
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
        if has_dead_time and dead_index is not None and pd.notna(data["twin_conversion"])
        else np.nan
    )

    # 점수는 같은 업종을 분석한 상권들 사이에서의 상대적 위치(0~100)로 해석합니다.
    traffic_score = float(data["traffic_score"])
    consumer_score = float(data["consumer_score"])
    traffic_score_round = int(round(traffic_score))
    consumer_score_round = int(round(consumer_score))

    def level_label(score):
        if score < 40:
            return "낮은 편"
        elif score < 70:
            return "보통 수준"
        return "높은 편"

    traffic_label = level_label(traffic_score)
    conversion_label = level_label(consumer_score)

    # 두 지표를 조합한 현황 요약 — 원인 설명이 아니라 현재 상대적 위치만 설명
    if traffic_score >= 70 and consumer_score < 40:
        flow_type = "소비 연결 점검형"
        hero_line = "사람은 많이 다니지만, 소비 연결 수준은 낮은 편입니다."
        hero_sub = "현재 상권의 상대적 위치를 보여주는 결과입니다. 왜 이런 차이가 나타나는지는 시간대 진단과 비교 TWIN에서 추가로 살펴봅니다."
    elif traffic_score >= 70 and consumer_score >= 70:
        flow_type = "유동·소비 연결 상위형"
        hero_line = "사람의 흐름과 소비 연결이 모두 높은 편입니다."
        hero_sub = "같은 업종을 분석한 다른 상권들과 비교했을 때 두 지표가 모두 높은 수준입니다."
    elif traffic_score < 40 and consumer_score < 40:
        flow_type = "유동·소비 연결 점검형"
        hero_line = "사람의 흐름과 소비 연결이 모두 낮은 편입니다."
        hero_sub = "같은 업종을 분석한 다른 상권들과 비교했을 때 두 지표가 모두 낮은 수준입니다."
    elif traffic_score < 40 and consumer_score >= 70:
        flow_type = "소비 연결 강점형"
        hero_line = "사람의 흐름은 낮지만, 소비 연결 수준은 높은 편입니다."
        hero_sub = "같은 업종을 분석한 다른 상권들과 비교했을 때 유동보다 소비 연결의 상대적 위치가 높습니다."
    else:
        flow_type = "균형 점검형"
        hero_line = f"사람의 흐름은 {traffic_label}, 소비 연결은 {conversion_label}입니다."
        hero_sub = "같은 업종을 분석한 다른 상권들과 비교한 현재 위치입니다. 세부 차이는 다음 진단에서 확인할 수 있습니다."

    # 시간대 우선순위 데이터는 여러 페이지에서 사용하므로 페이지 분기 전에 생성
    eligible_rank = dead_candidates.copy()
    for _c in ["gap_log", "gap_percentile", "repeat_dead"]:
        if _c in eligible_rank.columns:
            eligible_rank[_c] = pd.to_numeric(eligible_rank[_c], errors="coerce")
    if all(_c in eligible_rank.columns for _c in ["gap_log", "gap_percentile", "repeat_dead"]):
        eligible_rank = eligible_rank[
            (eligible_rank["gap_log"] > 0) &
            (eligible_rank["gap_percentile"] >= 0.90) &
            (eligible_rank["repeat_dead"] >= 2)
        ].sort_values(["gap_log", "gap_percentile"], ascending=False)
    else:
        eligible_rank = eligible_rank.iloc[0:0]

    # 2. ONE-LINE DIAGNOSIS
    if page == "상권 진단":
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
                    <div style="font-size:27px;font-weight:850;color:#173c67;margin:7px 0;">
                        {traffic_label} <span style="font-size:18px;color:#637487;">· {traffic_score_round}점 / 100</span>
                    </div>
                    <div class="subtext">
                        같은 업종을 분석한 다른 상권들과 비교했을 때,
                        이 상권에 사람이 얼마나 많이 다니는지를 보여줍니다.
                    </div>
                </div>
                """, unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="card">
                    <div class="label">소비로 이어지는 정도</div>
                    <div style="font-size:27px;font-weight:850;color:#a55c00;margin:7px 0;">
                        {conversion_label} <span style="font-size:18px;color:#637487;">· {consumer_score_round}점 / 100</span>
                    </div>
                    <div class="subtext">
                        같은 업종을 분석한 다른 상권들과 비교했을 때,
                        이 상권의 소비 연결이 어느 정도인지를 보여줍니다.
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

        with st.expander("ⓘ 이 점수는 무엇을 의미하나요?"):
            st.markdown(
                f"""
                **사람의 흐름 · {traffic_score_round}점 / 100**  
                같은 업종을 분석한 상권 100곳을 줄 세웠다고 생각하면,
                이 상권의 유동 수준은 대략 **{traffic_score_round}번째 정도**입니다.

                **소비 연결 · {consumer_score_round}점 / 100**  
                같은 방식으로 비교했을 때 소비 연결 수준은 대략
                **{consumer_score_round}번째 정도**입니다.

                **점수 읽는 법**  
                · **0점부터 39점:** 낮은 편  
                · **40점부터 69점:** 보통 수준  
                · **70점부터 100점:** 높은 편  

                이 구간은 결과를 쉽게 읽기 위해 FLOW 화면에서 사용하는 기준입니다.

                **주의할 점**  
                이 점수는 실제 유동인구 수나 매출액, 미래 매출 예측값이 아닙니다.
                또 **왜 이런 결과가 나왔는지를 설명하는 점수도 아닙니다.**
                현재 상권이 같은 업종의 다른 상권들과 비교해 어느 정도 위치인지 보여주는 지표입니다.
                차이가 나타나는 이유는 이후 **시간대 진단과 비교 TWIN**에서 추가로 살펴봅니다.
                """
            )

        # -----------------------------
        # QUICK SUMMARY
        # -----------------------------
        quick_type = f"유동 {traffic_label} · 소비 연결 {conversion_label}"
        quick_twin = data["twin"] if data["twin"] else "비교 TWIN 없음"

        st.markdown("#### 한눈에 보는 FLOW 진단")
        q1, q2, q3 = st.columns(3)
        with q1:
            st.markdown(
                f"""<div class="card" style="min-height:145px;">
                <div class="label">상권 유형</div>
                <div style="font-size:20px;font-weight:850;color:#173c67;margin-top:9px;">{quick_type}</div>
                <div class="subtext">유동 {traffic_score_round}점 · 소비 연결 {consumer_score_round}점</div>
                </div>""", unsafe_allow_html=True
            )
        with q2:
            if has_dead_time:
                q2_value, q2_sub, q2_color = dead_time, "FLOW 기준을 충족한 우선 점검 시간", "#a55c00"
            else:
                q2_value, q2_sub, q2_color = "뚜렷한 시간 없음", "현재 FLOW 기준을 충족한 시간대가 없어요", "#173c67"
            st.markdown(
                f"""<div class="card" style="min-height:145px;">
                <div class="label">가장 먼저 볼 시간</div>
                <div style="font-size:24px;font-weight:850;color:{q2_color};margin-top:9px;">{q2_value}</div>
                <div class="subtext">{q2_sub}</div>
                </div>""", unsafe_allow_html=True
            )
        with q3:
            st.markdown(
                f"""<div class="card" style="min-height:145px;">
                <div class="label">비교해볼 상권</div>
                <div style="font-size:21px;font-weight:850;color:#173c67;margin-top:9px;">{quick_twin}</div>
                <div class="subtext">유동인구·시간대·연령대·상주/직장인구·점포·상권 규모 등 16개 특성이 비슷한 곳</div>
                </div>""", unsafe_allow_html=True
            )


    # 3. TIME
    if page == "시간대 진단":
        st.markdown('<div class="section-title">3. 소비 연결이 상대적으로 약한 시간은?</div>', unsafe_allow_html=True)

        if has_dead_time:
            st.markdown(
                f"""<div class="action-box">
                <div class="label">FLOW 기준을 충족한 우선 점검 시간</div>
                <div style="font-size:34px;font-weight:850;color:#a55c00;margin:5px 0 7px;">{dead_time}</div>
                <div style="font-size:16px;font-weight:700;color:#18324a;line-height:1.65;">
                같은 업종·같은 시간대의 다른 상권과 비교했을 때 소비 공백이 매우 크고,
                이러한 현상이 반복된 시간입니다.
                </div></div>""", unsafe_allow_html=True
            )
        else:
            st.markdown(
                """<div class="action-box" style="border-left-color:#245B91;background:#f5f9fd;">
                <div class="label">시간대 진단 결과</div>
                <div style="font-size:28px;font-weight:850;color:#173c67;margin:5px 0 7px;">뚜렷한 우선 점검 시간 없음</div>
                <div style="font-size:16px;font-weight:700;color:#18324a;line-height:1.65;">
                현재 선택한 상권·업종에서는 FLOW의 DEAD TIME 기준을 충족하는 시간대가 확인되지 않았습니다.
                </div>
                <div class="subtext">따라서 특정 시간대를 억지로 문제 시간으로 지정하지 않습니다.</div>
                </div>""", unsafe_allow_html=True
            )

        time_df = pd.DataFrame({
            "시간대": data["times"],
            "모형 기대수준": data["potential"],
            "실제 매출건수": data["actual"]
        })

        fig = go.Figure()
        fig.add_trace(go.Bar(x=time_df["시간대"], y=time_df["모형 기대수준"],
                             name="모형 기대수준", marker_color="#A8C7E8"))
        fig.add_trace(go.Bar(x=time_df["시간대"], y=time_df["실제 매출건수"],
                             name="실제 매출건수", marker_color="#245B91"))
        fig.update_layout(
            barmode="group", height=390,
            margin=dict(l=15, r=15, t=50, b=15),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(gridcolor="#e9eef3", title="", showticklabels=False),
            xaxis=dict(showgrid=False, title=""), bargap=0.28
        )
        if has_dead_time and dead_index is not None:
            fig.add_vrect(x0=dead_index - 0.45, x1=dead_index + 0.45,
                          fillcolor="rgba(255,177,85,0.14)", line_width=0, layer="below")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            """<div style="background:#f7f9fc;border:1px solid #dfe7ef;border-radius:10px;padding:12px 16px;margin:4px 0 14px;">
            <div style="font-weight:800;color:#173c67;margin-bottom:5px;">그래프는 이렇게 읽어요</div>
            <div style="font-size:14px;line-height:1.65;color:#526579;">
            연한 막대는 <b>모형이 계산한 기대수준</b>, 진한 막대는 <b>실제 매출건수</b>입니다.
            이 그래프는 시간대별 패턴을 비교하기 위한 보조 자료이며,
            <b>막대 차이만으로 DEAD TIME을 정하지 않습니다.</b>
            </div></div>""", unsafe_allow_html=True
        )

        if has_dead_time:
            st.info(f"{dead_time}은 아래 세 조건을 모두 충족해 우선 점검 시간으로 분류됐습니다.")
        else:
            st.info("현재 세 조건을 모두 충족한 시간대가 없습니다. 그래프는 시간대별 패턴을 참고하기 위한 보조 자료입니다.")

        st.markdown("#### FLOW는 언제 DEAD TIME으로 판단하나요?")
        st.markdown(
            """
            <div style="
                background:white;
                border:1px solid #dfe7ef;
                border-radius:14px;
                padding:16px 18px;
                margin:4px 0 8px;
                box-shadow:0 3px 12px rgba(20,50,80,0.04);
            ">
                <div style="display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;
                            font-size:16px;font-weight:800;color:#173c67;text-align:center;">
                    <span>① 기대보다 소비가 낮고</span>
                    <span style="color:#91a4b7;">→</span>
                    <span>② 같은 업종·시간대 상권 중 공백이 큰 편이며</span>
                    <span style="color:#91a4b7;">→</span>
                    <span>③ 여러 분기에 반복될 때</span>
                </div>
                <div style="text-align:center;font-size:14px;color:#607286;margin-top:10px;">
                    세 조건을 모두 만족하는 시간만 우선 점검 시간으로 표시합니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption("※ 현재 분석에서는 00~06시를 제외하고, 2025년 4개 분기 중 기준을 2회 이상 충족한 경우를 반복 신호로 봅니다.")

        with st.expander("ⓘ 계산 기준을 조금 더 자세히 보기"):
            st.markdown("**1. 모형 선택**")
            st.write(
                "2021~2024년 자료로 학습하고 2025년 자료에서 검증합니다. "
                "단순 유동모형과 상권특성 확장모형의 RMSE를 비교해 검증 성능이 더 나은 모형을 사용합니다."
            )
            st.markdown("**2. 상권 조건 반영**")
            st.write(
                "확장모형에는 시간대 유동인구, 상주인구, 직장인구, 유사업종 점포 수, 상권 면적, "
                "20대·30대 유동 비중, 주말 유동 비중, 직장/상주 구조, 업종, 시간대, 연도, 분기가 포함됩니다."
            )
            st.markdown("**3. DEAD TIME 판정**")
            st.write(
                "예측 로그값 - 실제 로그값 > 0이고, 같은 분기·업종·시간대의 다른 상권과 비교했을 때 "
                "그 차이가 상위 10%이며, 2025년 중 이 조건이 2회 이상 반복될 때 후보가 됩니다."
            )
            st.markdown("**4. 분석 가능 시간**")
            st.write(
                "00~06시는 제외하고, 2025년 4개 분기가 모두 관측되며 최소 한 분기 이상 실제 매출이 "
                "확인된 시간대만 판정합니다."
            )
            if has_dead_time and dead_index is not None:
                tr = chart_rows.iloc[dead_index]
                gp = pd.to_numeric(tr.get("gap_percentile", np.nan), errors="coerce")
                rd = pd.to_numeric(tr.get("repeat_dead", np.nan), errors="coerce")
                gl = pd.to_numeric(tr.get("gap_log", np.nan), errors="coerce")
                st.info(
                    f"현재 {dead_time}: 로그 차이 {gl:.2f} · "
                    f"동일 비교집단 내 상대 위치 {gp*100:.0f}% · 반복 {rd:.0f}회"
                )
            else:
                st.info(
                    "현재 선택한 상권·업종은 위 조건을 모두 충족한 시간대가 없어 "
                    "'뚜렷한 DEAD TIME 없음'으로 분류됩니다."
                )

        # 4. TWIN
    if page == "비교 TWIN":
        st.markdown('<div class="section-title">4. 비슷한 조건의 상권과 비교해볼까요?</div>', unsafe_allow_html=True)
    
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
                        우리와 구조가 비슷한 상권을 비교해 차이를 살펴봅니다.
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
                    <div style="font-size:15px;">시간대 진단</div>
                    <div style="font-size:20px;font-weight:850;color:#173c67;margin-top:6px;">{"우선 점검: " + dead_time if has_dead_time else "뚜렷한 DEAD TIME 없음"}</div>
                    </div>""", unsafe_allow_html=True
                )
            with vm:
                st.markdown("<div style='text-align:center;font-size:24px;font-weight:800;padding-top:70px;'>VS</div>", unsafe_allow_html=True)
            with v2:
                st.markdown(
                    f"""<div class="card" style="min-height:175px;text-align:center;">
                    <div class="label">비교 TWIN</div>
                    <div style="font-size:22px;font-weight:850;color:#173c67;margin:9px 0;">{data["twin"]}</div>
                    <div style="font-size:15px;">같은 비교 기준</div>
                    <div style="font-size:22px;font-weight:850;color:#245B91;margin-top:6px;">구조적으로 유사</div>
                    </div>""", unsafe_allow_html=True
                )
    
            with st.expander("ⓘ 분석값으로 비교하기"):
                if has_dead_time and dead_index is not None:
                    st.write(
                        f"현재 우리 상권의 우선 점검 시간은 {dead_time}입니다. "
                        "TWIN 비교는 특정 시간대의 원시 매출값을 직접 빼는 방식이 아니라, 아래 16개 상권 구조 특성의 차이를 중심으로 해석합니다."
                    )
                else:
                    st.write(
                        "현재 우리 상권에는 FLOW 기준을 충족한 DEAD TIME이 없습니다. "
                        "따라서 특정 시간대를 억지로 TWIN과 연결하지 않고, 아래 16개 상권 구조 특성의 차이를 중심으로 비교합니다."
                    )
    
            if data["why"]:
                st.markdown("#### 두 상권에서 차이가 큰 특성 TOP 3")
                st.caption("16개 비교 특성 중 두 상권의 차이가 상대적으로 크게 나타난 3개를 보여줍니다.")
                why_cols = st.columns(len(data["why"]))
                positive_features = []
                for i, (feature, diff, unit) in enumerate(data["why"]):
                    if diff > 0:
                        positive_features.append((feature, diff, unit))
                    with why_cols[i]:
                        # 연령대 유동 비중은 age_comparison.csv의 실제 비중값으로 표시
                        age_label = None
                        for _age in ["10대", "20대", "30대", "40대", "50대", "60대 이상"]:
                            if _age in str(feature) and "유동" in str(feature):
                                age_label = _age
                                break
    
                        if age_label is not None:
                            _age_row = age_df[
                                (age_df["area_code"] == str(selected_code).strip()) &
                                (age_df["category"] == str(category).strip()) &
                                (age_df["age_group"] == age_label)
                            ]
    
                            if not _age_row.empty:
                                _ar = _age_row.iloc[0]
                                _our_pct = float(_ar["area_share"]) * 100
                                _twin_pct = float(_ar["twin_share"]) * 100
                                _diff_pp = float(_ar["difference_pp"])
                                _direction = "우리 상권이 높음" if _diff_pp > 0 else ("우리 상권이 낮음" if _diff_pp < 0 else "두 상권이 비슷함")
                                _diff_text = f"{abs(_diff_pp):.1f}%p 차이"
                                _detail = (
                                    f"우리 상권 <b>{_our_pct:.1f}%</b> · "
                                    f"비교 TWIN <b>{_twin_pct:.1f}%</b><br>"
                                    f"<b>{_direction}</b> · {_diff_text}"
                                )
                            else:
                                direction = "우리 상권이 낮음" if diff < 0 else "우리 상권이 높음"
                                value = f"{abs(diff):.1f}" if abs(diff) < 100 else f"{abs(diff):,.0f}"
                                _detail = f"<b>{direction}</b><br>{value}{unit} 차이"
                        else:
                            direction = "우리 상권이 낮음" if diff < 0 else ("우리 상권이 높음" if diff > 0 else "두 상권이 비슷함")
    
                            # 시간대/주말 등 '유동 비중' 변수는 twin_difference.csv에서
                            # 0~1 비율의 '차이'만 제공하므로 %p로 변환해 표시합니다.
                            # (양쪽 절대 비중값은 이 파일에 없으므로 임의로 만들지 않습니다.)
                            if "유동 비중" in str(feature) and str(unit).strip() == "비율":
                                value = abs(float(diff)) * 100
                                _detail = f"<b>{direction}</b><br><b>{value:.1f}%p</b> 차이"
                            else:
                                value = f"{abs(diff):.1f}" if abs(diff) < 100 else f"{abs(diff):,.0f}"
                                _detail = f"<b>{direction}</b><br>{value}{unit} 차이"
    
                        st.markdown(
                            f"""<div class="card" style="min-height:155px;">
                            <div class="label">비교 단서 {i+1}</div>
                            <div style="font-size:18px;font-weight:800;color:#183f6c;margin:7px 0;">{feature}</div>
                            <div style="font-size:14px;line-height:1.6;">{_detail}</div>
                            </div>""", unsafe_allow_html=True
                        )
    
                meaningful_positive = [(f, d, u) for f, d, u in positive_features if abs(d) >= 0.05]
                if meaningful_positive:
                    pf, pdiff, punit = meaningful_positive[0]
                    st.success(
                        f"**우리 상권이 이미 가진 특징:** 비교 TWIN과 비교하면 `{pf}`은 우리 상권이 더 높게 나타납니다. "
                        "이는 매출 성과의 원인이라는 뜻이 아니라, 현재 상권이 가진 구조적 특징입니다."
                    )
    
                st.caption("※ 위 차이는 소비성과 차이의 원인으로 확정한 결과가 아니라, 추가로 확인할 비교 단서입니다.")
    
            # 연령대별 유동인구 구성 비교
            _age_match = age_df[
                (age_df["area_code"] == str(selected_code).strip()) &
                (age_df["category"] == str(category).strip())
            ].copy()
    
            if not _age_match.empty:
                age_order = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
                _age_match["age_group"] = pd.Categorical(
                    _age_match["age_group"], categories=age_order, ordered=True
                )
                _age_match = _age_match.sort_values("age_group")
    
                with st.expander("연령대별 유동인구 구성 자세히 보기"):
                    st.caption(
                        "우리 상권과 비교 TWIN을 방문하는 유동인구의 연령 구성을 비교합니다. "
                        "특정 업종·시간대의 실제 구매 고객 연령을 의미하지 않습니다."
                    )
                    age_display = _age_match[["age_group", "area_share", "twin_share", "difference_pp"]].copy()
                    age_display["우리 상권"] = (age_display["area_share"] * 100).map(lambda x: f"{x:.1f}%")
                    age_display["비교 TWIN"] = (age_display["twin_share"] * 100).map(lambda x: f"{x:.1f}%")
                    age_display["차이"] = age_display["difference_pp"].map(lambda x: f"{x:+.1f}%p")
                    age_display = age_display.rename(columns={"age_group": "연령대"})
                    st.dataframe(
                        age_display[["연령대", "우리 상권", "비교 TWIN", "차이"]],
                        hide_index=True,
                        use_container_width=True
                    )
                    biggest = _age_match.loc[_age_match["difference_pp"].abs().idxmax()]
                    direction_text = "높습니다" if biggest["difference_pp"] > 0 else "낮습니다"
                    st.markdown(
                        f"**가장 큰 연령 구성 차이** · {biggest['age_group']} 유동 비중이 "
                        f"우리 상권에서 **{abs(biggest['difference_pp']):.1f}%p {direction_text}**."
                    )
    
            with st.expander("ⓘ 비교 TWIN과 유사도는 어떻게 해석하나요?"):
                st.write(
                    "비교 TWIN은 아래 16개 특성을 함께 비교했을 때 우리 상권과 가장 비슷한 상권입니다. "
                    "유사도는 두 상권의 특성이 완전히 같다는 뜻이 아니라, 이 특성들의 상대적 위치가 얼마나 비슷한지를 나타내는 지수입니다."
                )
                st.markdown(
                    """
                    **비교에 사용한 16개 특성**

                    - **유동 규모:** 총 유동인구
                    - **연령 구성:** 20대 유동 비중, 30대 유동 비중
                    - **시간대 구성:** 00–06, 06–11, 11–14, 14–17, 17–21, 21–24 유동 비중
                    - **요일 구성:** 주말 유동 비중
                    - **생활·업무 인구:** 상주인구, 직장인구, 직장·상주 구조
                    - **점포 구성:** 해당 업종 점포 수, 프랜차이즈 점포 수
                    - **상권 규모:** 상권 면적
                    """
                )
                st.caption(
                    "※ 비교 TWIN은 '더 좋은 상권'을 뜻하지 않습니다. "
                    "현재 상권과 조건이 비슷해 차이를 살펴보기 위한 비교 대상입니다."
                )
    
        # 5. STORE DIAGNOSIS
    if page in ["가게 점검", "Action Point"]:
        if page == "Action Point":
            st.info("Action Point는 가게 점검 응답을 바탕으로 생성됩니다. 아래 항목을 입력하면 우선 확인할 순서를 보여드립니다.")
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
                    p3_how = "FLOW 보유: 상권 시간대 결과 · 비교 TWIN 비교"
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
