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

AREA_FILE = _find_csv("area_summary_category_adjusted.csv")
TIME_FILE = _find_csv("time_result_category_adjusted.csv")
TWIN_FILE = _find_csv("twin_difference.csv")
AGE_FILE = _find_csv("age_comparison.csv")

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


/* 제목에 마우스를 올렸을 때 나타나는 Streamlit 앵커(링크) 아이콘 숨김 */
[data-testid="stHeaderActionElements"] {
    display: none !important;
}
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
    text-decoration: none !important;
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

/* ===== FLOW shared page system ===== */
.page-kicker{
    font-size:12px;
    font-weight:800;
    letter-spacing:.04em;
    color:#6f8294;
    margin:4px 0 5px;
}
.page-context{
    font-size:14px;
    color:#6b7d8d;
    margin:-8px 0 18px;
}
.result-strip{
    background:#ffffff;
    border:1px solid #dfe7ef;
    border-radius:14px;
    padding:14px 17px;
    margin:0 0 14px;
    box-shadow:0 3px 12px rgba(20,50,80,.035);
}
.result-strip .title{
    font-size:13px;
    font-weight:800;
    color:#6f8294;
    margin-bottom:5px;
}
.result-strip .value{
    font-size:22px;
    line-height:1.35;
    font-weight:850;
    color:#173c67;
}
.section-title{
    margin-top:32px;
    margin-bottom:10px;
}
.card,.diagnosis-box,.twin-box,.why-card,.compare-box{
    box-shadow:0 3px 12px rgba(20,50,80,.04);
}
.card{
    border-radius:14px;
    padding:20px;
}
.diagnosis-box,.twin-box{
    border-radius:14px;
    padding:20px 22px;
}
[data-testid="stExpander"]{
    border-color:#dfe7ef !important;
    border-radius:10px !important;
    background:#fbfcfe;
}
[data-testid="stDataFrame"]{
    border-radius:10px;
    overflow:hidden;
}
div[data-testid="stCheckbox"]{
    background:#ffffff;
    border:1px solid #dfe7ef;
    border-radius:12px;
    padding:9px 13px;
    margin:5px 0 12px;
}
hr{
    border-color:#e7edf3 !important;
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
    ["01  상권 진단", "02  시간대 진단", "03  비교 TWIN", "04  내 가게 점검"],
    label_visibility="collapsed"
)
page = {
    "01  상권 진단": "상권 진단",
    "02  시간대 진단": "시간대 진단",
    "03  비교 TWIN": "비교 TWIN",
    "04  내 가게 점검": "가게 점검",
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
    st.markdown('<div class="section-title">내 상권 찾아보기</div>', unsafe_allow_html=True)
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

        # flow_area_map.csv 원본에서 손상된 행정동명 표시 교정
        # 분석값에는 영향을 주지 않고 지역 탐색/검색 화면의 명칭만 수정합니다.
        region["dong"] = region["dong"].replace({
            "종로1?2?3?4가동": "종로1·2·3·4가동"
        })
    
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
        st.markdown(f'<div class="section-title">{area} · {category}</div>', unsafe_allow_html=True)
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

    # 시간대 분류: 정상 / 업종 공통 저활성 / 상권 고유 DEAD TIME 후보
    # area_summary의 adjusted_dead_time은 여러 후보 중 대표 1개만 담고 있으므로,
    # 화면에서는 time_result의 최종 판정을 이용해 모든 DEAD TIME 후보를 표시합니다.
    if "dead_time_class" in time_rows.columns:
        class_rows = time_rows[time_rows["time"].astype(str) != "00~06"].copy()
        common_low_times = class_rows.loc[
            class_rows["dead_time_class"].astype(str).eq("업종 공통 저활성 시간대"), "time"
        ].astype(str).tolist()
        unique_dead_times = class_rows.loc[
            class_rows["dead_time_class"].astype(str).eq("상권 고유 DEAD TIME 후보"), "time"
        ].astype(str).tolist()
    else:
        common_low_times, unique_dead_times = [], []

    # 대표 DEAD TIME은 데이터팀 area_summary 정의를 유지하되,
    # 실제 화면의 DEAD TIME 존재 여부와 목록은 전체 후보를 기준으로 합니다.
    dead_time_raw = row.get("adjusted_dead_time", row.get("dead_time", ""))
    representative_dead_time = "" if pd.isna(dead_time_raw) else str(dead_time_raw).strip()
    has_dead_time = len(unique_dead_times) > 0
    dead_time = " · ".join(unique_dead_times) if has_dead_time else "뚜렷한 DEAD TIME 없음"

    # 데이터팀의 최종 TWIN 판정을 그대로 사용합니다.
    # "없음"이면 twin_name에 어떤 값이 남아 있어도 절대 TWIN을 표시하지 않습니다.
    twin_status = "" if pd.isna(row.get("twin_status", np.nan)) else str(row.get("twin_status")).strip()
    twin_gain = pd.to_numeric(row.get("twin_performance_gain", np.nan), errors="coerce")
    twin_similarity = pd.to_numeric(row.get("similarity", np.nan), errors="coerce")
    _twin_name_check = "" if pd.isna(row.get("twin_name", np.nan)) else str(row.get("twin_name")).strip()

    if "없음" in twin_status:
        has_twin = False
    elif "있음" in twin_status:
        has_twin = bool(
            _twin_name_check
            and _twin_name_check.lower() not in ["nan", "none", "적합한 비교 상권 없음"]
        )
    else:
        # 상태값이 비정상/누락된 경우에만 twin_name을 보조적으로 사용
        has_twin = bool(
            _twin_name_check
            and _twin_name_check.lower() not in ["nan", "none", "적합한 비교 상권 없음"]
        )

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

    dead_indices = [
        times.index(t) for t in unique_dead_times if t in times
    ]
    if representative_dead_time in times:
        representative_dead_index = times.index(representative_dead_time)
        dead_gap = float(potential[representative_dead_index] - actual[representative_dead_index])
    elif dead_indices:
        dead_gap = float(potential[dead_indices[0]] - actual[dead_indices[0]])
    else:
        dead_gap = np.nan

    # 비교 TWIN 차이 TOP3
    twin_name_raw = row.get("twin_name", np.nan)
    twin_name = "" if pd.isna(twin_name_raw) else str(twin_name_raw).strip()
    if not has_twin:
        twin_name = ""
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
        "twin_performance_gain": float(twin_gain) if pd.notna(twin_gain) else np.nan,
        "twin_status": twin_status,
        "why": why,
    }

    # TWIN 차이는 데이터팀이 선택한 대표 DEAD TIME 기준으로 계산합니다.
    # 화면의 DEAD TIME 표시는 전체 후보를 보여주되, 단일 값이 필요한 계산은 대표 시간대를 사용합니다.
    twin_diff = (
        float(data["twin_conversion"] - actual[representative_dead_index])
        if has_dead_time
        and representative_dead_time in times
        and pd.notna(data["twin_conversion"])
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
        st.markdown('<div class="page-kicker">FLOW OVERVIEW</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{area} · {category}는 어떤 상권일까요?</div>', unsafe_allow_html=True)
        st.markdown('<div class="page-context">상권의 유동과 소비 연결 수준을 먼저 요약하고, 다음 진단에서 시간대와 비교 상권을 확인합니다.</div>', unsafe_allow_html=True)

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

        with st.expander("점수 기준 · 해석 방법"):
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
        quick_twin = data["twin"] if data["twin"] else "적합한 비교 상권 없음"

        st.markdown('<div style="font-size:18px;font-weight:850;color:#18324a;margin:22px 0 10px;">한눈에 보는 FLOW 진단</div>', unsafe_allow_html=True)
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
                <div class="subtext">구조 유사도 85점 이상이면서 같은 업종의 FLOW SCORE가 더 높은 비교 상권</div>
                </div>""", unsafe_allow_html=True
            )


    # 3. TIME
    if page == "시간대 진단":
        st.markdown('<div class="page-kicker">TIME DIAGNOSIS</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">소비 연결이 상대적으로 약한 시간은?</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="page-context">{area} · {category}의 시간대별 소비공백을 업종 특성까지 보정해 확인합니다.</div>', unsafe_allow_html=True)

        if has_dead_time:
            st.markdown(
                f"""<div class="action-box">
                <div class="label">상권 고유 DEAD TIME 후보</div>
                <div style="font-size:34px;font-weight:850;color:#a55c00;margin:5px 0 7px;">{dead_time}</div>
                <div style="font-size:16px;font-weight:700;color:#18324a;line-height:1.65;">
                우리 상권 안에서도 소비 연결이 약하고, 같은 업종·같은 시간대의 다른 상권과 비교해도
                공백이 큰 시간으로 남았습니다.
                </div></div>""", unsafe_allow_html=True
            )

            # 최종 DEAD TIME 후보의 선정 근거를 바로 표시
            reason_rows = chart_rows[
                chart_rows["time"].astype(str).isin(unique_dead_times)
            ].copy()
            if not reason_rows.empty:
                reason_bits = []
                for _, rr in reason_rows.iterrows():
                    t = str(rr["time"]).replace("~", "–")
                    within = pd.to_numeric(rr.get("within_area_gap_percentile", np.nan), errors="coerce")
                    peer = pd.to_numeric(rr.get("peer_gap_percentile", np.nan), errors="coerce")
                    repeat = pd.to_numeric(rr.get("repeat_dead", np.nan), errors="coerce")
                    parts = []
                    if pd.notna(within):
                        parts.append(f"상권 내부 {within*100:.0f}%")
                    if pd.notna(peer):
                        parts.append(f"동종업종 비교 {peer*100:.0f}%")
                    if pd.notna(repeat):
                        parts.append(f"{int(repeat)}개 분기 반복")
                    reason_bits.append(f"<b>{t}</b> · " + " · ".join(parts))

                st.markdown(
                    """<div style="background:#fffdf8;border:1px solid #ecd7b2;border-radius:10px;
                                padding:11px 15px;margin:-2px 0 12px;font-size:14px;line-height:1.75;color:#66543a;">
                    <b style="color:#8a5a13;">왜 DEAD TIME으로 선택됐나요?</b><br>"""
                    + "<br>".join(reason_bits) +
                    """<div style="margin-top:5px;color:#7a6c58;">
                    막대의 절대 차이가 가장 큰 시간이 아니라, 반복성과 상권 내부·동일 업종 비교 기준을 함께 통과한 시간입니다.
                    </div></div>""",
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                """<div class="action-box" style="border-left-color:#245B91;background:#f5f9fd;">
                <div class="label">시간대 진단 결과</div>
                <div style="font-size:28px;font-weight:850;color:#173c67;margin:5px 0 7px;">상권 고유 DEAD TIME 없음</div>
                <div style="font-size:16px;font-weight:700;color:#18324a;line-height:1.65;">
                업종·시간대 특성을 보정한 뒤 이 상권만의 뚜렷한 소비공백 시간은 확인되지 않았습니다.
                </div>
                <div style="font-size:14px;color:#607286;line-height:1.65;margin-top:7px;">
                기대수준보다 실제 소비가 낮아 보이는 시간이 있더라도, 같은 업종에서도 공통적으로 낮다면
                상권 고유 DEAD TIME으로 분류하지 않습니다.
                </div></div>""", unsafe_allow_html=True
            )

        if common_low_times:
            common_text = ", ".join(t.replace("~", "–") for t in common_low_times)
            st.markdown(
                f"""<div style="background:#fff8ec;border:1px solid #f0d8ad;border-radius:10px;padding:12px 15px;margin:10px 0 14px;">
                <b style="color:#8a5a13;">업종 공통 저활성 시간 · {common_text}</b><br>
                <span style="font-size:14px;color:#6c604f;">
                해당 업종에서 전반적으로 소비 연결이 약하게 나타나는 시간대입니다.
                이 상권에서도 소비공백 신호가 나타났지만, <b>업종 자체의 시간대 특성을 고려해
                상권 고유 DEAD TIME과 구분했습니다.</b>
                </span></div>""", unsafe_allow_html=True
            )

        time_df = pd.DataFrame({
            "시간대": data["times"],
            "상권 특성 기반 기대수준": data["potential"],
            "실제 매출건수": data["actual"]
        })
        fig = go.Figure()
        fig.add_trace(go.Bar(x=time_df["시간대"], y=time_df["상권 특성 기반 기대수준"],
                             name="상권 특성 기반 기대수준", marker_color="#A8C7E8"))
        fig.add_trace(go.Bar(x=time_df["시간대"], y=time_df["실제 매출건수"],
                             name="실제 매출건수", marker_color="#245B91"))
        fig.update_layout(
            barmode="group", height=390, margin=dict(l=15, r=15, t=50, b=15),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(
                gridcolor="#e9eef3",
                title=dict(text="소비 수준 (건)", font=dict(size=13, color="#526579")),
                showticklabels=True,
                tickfont=dict(size=11, color="#607286"),
                rangemode="tozero"
            ),
            xaxis=dict(showgrid=False, title=""), bargap=0.28
        )
        if has_dead_time:
            for dead_index in dead_indices:
                fig.add_vrect(x0=dead_index - 0.45, x1=dead_index + 0.45,
                              fillcolor="rgba(255,177,85,0.14)", line_width=0, layer="below")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown(
            """<div style="background:#f7f9fc;border:1px solid #dfe7ef;border-radius:10px;padding:11px 15px;margin:4px 0 12px;">
            <div style="font-weight:800;color:#173c67;margin-bottom:4px;">그래프 해석 포인트</div>
            <div style="font-size:14px;line-height:1.6;color:#526579;">
            연한 막대는 <b>상권 특성 기반 기대수준</b>, 진한 막대는 <b>실제 매출건수</b>입니다.
            <b>막대 차이가 가장 큰 시간이 곧 DEAD TIME인 것은 아닙니다.</b>
            최종 판정에는 반복성, 상권 내부 상대순위, 동일 업종·동일 시간대 비교가 함께 반영됩니다.
            </div></div>""", unsafe_allow_html=True
        )

        st.markdown(
            """<div style="background:white;border:1px solid #dfe7ef;border-radius:12px;padding:13px 16px;margin:2px 0 10px;">
            <div style="font-size:14px;font-weight:800;color:#173c67;margin-bottom:8px;">DEAD TIME 판정 흐름</div>
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:14px;font-weight:750;color:#294761;">
                <span style="background:#f4f7fa;border-radius:8px;padding:7px 10px;">① 반복 소비공백</span>
                <span style="color:#9aabbc;">→</span>
                <span style="background:#f4f7fa;border-radius:8px;padding:7px 10px;">② 상권 내부에서도 약함</span>
                <span style="color:#9aabbc;">→</span>
                <span style="background:#fff5e7;border-radius:8px;padding:7px 10px;color:#9a5b08;">③ 동종업종 비교에서도 유독 약함</span>
            </div>
            </div>""",
            unsafe_allow_html=True
        )

        if common_low_times and not has_dead_time:
            common_case = ", ".join(t.replace("~", "–") for t in common_low_times)
            st.markdown(
                f"""<div style="margin:-2px 0 14px;padding:10px 14px;border-left:4px solid #d49a3a;background:#fffaf1;
                            font-size:14px;line-height:1.65;color:#5f5749;">
                <b>현재 상권 판정:</b> {common_case}는 우리 상권 내에서는 소비공백이 큰 편이지만,
                동일 업종·동일 시간대 비교에서 <b>상위 10% 기준에 들지 않아</b>
                상권 고유 DEAD TIME에서 제외되었습니다.
                </div>""",
                unsafe_allow_html=True
            )

        with st.expander("상세 판정 기준 · 전체 시간대 보기"):
            st.write(
                "기존 DEAD TIME 후보를 출발점으로 사용하고, 상권 내부 시간대 gap 순위와 "
                "동일 업종·동일 시간대의 다른 상권 분포를 추가로 비교합니다."
            )
            st.write(
                "최종 보정 후보는 기존 후보이면서 상권 내부 gap 상위 25%에 해당하고, "
                "동일 업종·동일 시간대 비교에서 gap이 상위 10%이며 해당 그룹의 중앙값보다 큰 경우입니다."
            )
            detail_cols = [
                "time", "dead_time_class", "within_area_gap_percentile",
                "peer_gap_percentile", "category_baseline", "relative_gap"
            ]
            available_cols = [c for c in detail_cols if c in chart_rows.columns]
            detail = chart_rows[available_cols].copy()
            if "time" in detail.columns:
                detail["time"] = detail["time"].astype(str).str.replace("~", "–", regex=False)
                detail = detail.rename(columns={"time": "시간대"})
            if "dead_time_class" in detail.columns:
                detail = detail.rename(columns={"dead_time_class": "분류"})
            if "within_area_gap_percentile" in detail.columns:
                detail["상권 내부 위치"] = pd.to_numeric(detail["within_area_gap_percentile"], errors="coerce").map(
                    lambda x: "—" if pd.isna(x) else f"{x*100:.0f}%"
                )
            if "peer_gap_percentile" in detail.columns:
                detail["동일 업종·시간대 위치"] = pd.to_numeric(detail["peer_gap_percentile"], errors="coerce").map(
                    lambda x: "—" if pd.isna(x) else f"{x*100:.0f}%"
                )
            show_cols = [c for c in ["시간대", "분류", "상권 내부 위치", "동일 업종·시간대 위치"] if c in detail.columns]
            st.dataframe(detail[show_cols], hide_index=True, use_container_width=True)
            st.caption(
                "※ percentile은 같은 비교집단 안에서의 상대적 위치입니다. "
                "높을수록 소비공백(gap)이 상대적으로 큰 편이라는 뜻입니다."
            )

        # 4. TWIN
    if page == "비교 TWIN":
        st.markdown('<div class="page-kicker">TWIN COMPARISON</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">비슷하지만 더 잘되는 상권과 비교해볼까요?</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="page-context">{area} · {category}와 구조가 비슷하면서 소비 연결 성과가 더 높은 동일 업종 상권을 비교합니다.</div>', unsafe_allow_html=True)

        if not has_twin or not data["twin"]:
            st.markdown(
                """<div class="action-box" style="border-left-color:#245B91;background:#f5f9fd;">
                <div class="label">비교 TWIN 결과</div>
                <div style="font-size:27px;font-weight:850;color:#173c67;margin:5px 0 7px;">적합한 비교 상권 없음</div>
                <div style="font-size:15px;line-height:1.65;color:#526579;">
                구조 유사도 85점 이상이면서 같은 업종의 FLOW SCORE가 우리 상권보다 높은 상권을 찾지 못했습니다.
                조건을 낮춰 억지로 비교 상권을 제시하지 않습니다.
                </div></div>""", unsafe_allow_html=True
            )
            with st.expander("TWIN 선정 기준 보기"):
                st.write(
                    "TWIN 후보는 동일 업종 상권 중 16개 구조 특성의 유사도가 85점 이상이고, "
                    "FLOW SCORE가 선택 상권보다 높은 곳으로 제한합니다. 그 후보들 가운데 구조적으로 가장 유사한 상권을 선택합니다."
                )
                st.write("조건을 만족하는 상권이 없으면 '적합한 비교 상권 없음'으로 처리합니다.")
                st.caption(
                    f"현재 불러온 데이터: twin_name={row.get('twin_name', '—')} · "
                    f"유사도={row.get('similarity', '—')} · "
                    f"FLOW SCORE 차이={row.get('twin_performance_gain', '—')} · "
                    f"상태={row.get('twin_status', '—')}"
                )
        else:
            similarity_text = f"{data['similarity']:.1f}" if pd.notna(data["similarity"]) else "—"
            twin_score_text = f"{data['twin_conversion']:.1f}" if pd.notna(data["twin_conversion"]) else "—"
            gain_text = f"+{data['twin_performance_gain']:.1f}점" if pd.notna(data["twin_performance_gain"]) else "—"

            st.markdown(
                f"""<div class="twin-box">
                <div class="label">왜 {data["twin"]}을 보여주나요?</div>
                <div style="font-size:25px;font-weight:850;color:#173c67;margin:8px 0;">
                구조는 비슷하지만, 같은 업종의 소비 연결 성과는 더 높은 상권입니다.
                </div>
                <div class="subtext">
                구조 유사도 {similarity_text}점 · 16개 상권 특성을 종합한 비교용 지수
                </div></div>""", unsafe_allow_html=True
            )

            v1, vm, v2 = st.columns([1, .25, 1])
            with v1:
                st.markdown(
                    f"""<div class="card" style="min-height:185px;text-align:center;">
                    <div class="label">우리 상권</div>
                    <div style="font-size:21px;font-weight:850;color:#173c67;margin:9px 0;">{area}</div>
                    <div style="font-size:14px;color:#607286;">FLOW SCORE</div>
                    <div style="font-size:27px;font-weight:850;color:#173c67;margin-top:5px;">{data["flow_score"]:.1f}점</div>
                    </div>""", unsafe_allow_html=True
                )
            with vm:
                st.markdown("<div style='text-align:center;font-size:24px;font-weight:800;padding-top:72px;'>VS</div>", unsafe_allow_html=True)
            with v2:
                st.markdown(
                    f"""<div class="card" style="min-height:185px;text-align:center;">
                    <div class="label">비교 TWIN</div>
                    <div style="font-size:21px;font-weight:850;color:#173c67;margin:9px 0;">{data["twin"]}</div>
                    <div style="font-size:14px;color:#607286;">FLOW SCORE</div>
                    <div style="font-size:27px;font-weight:850;color:#245B91;margin-top:5px;">{twin_score_text}점</div>
                    <div style="font-size:15px;font-weight:800;color:#245B91;margin-top:7px;">↑ 우리 상권보다 {gain_text}</div>
                    </div>""", unsafe_allow_html=True
                )

            st.caption("※ FLOW SCORE가 더 높다는 것은 같은 업종 내 소비 연결의 상대적 위치가 더 높다는 뜻이며, 실제 매출액이 더 크다는 의미는 아닙니다.")

            if data["why"]:
                st.markdown("#### 두 상권에서 차이가 큰 특성 TOP 3")
                st.caption(
                    "16개 구조 특성 중 두 상권의 차이가 상대적으로 큰 3개입니다. "
                    "TWIN의 높은 FLOW SCORE를 설명하는 원인으로 확정한 결과는 아니며, "
                    "점포 운영에서 확인해볼 비교 단서입니다."
                )
                why_cols = st.columns(len(data["why"]))
                for i, (feature, diff, unit) in enumerate(data["why"]):
                    with why_cols[i]:
                        direction = "TWIN이 높음" if diff > 0 else ("우리 상권이 높음" if diff < 0 else "두 상권이 비슷함")
                        if "유동 비중" in str(feature) and str(unit).strip() == "비율":
                            value_text = f"{abs(float(diff))*100:.1f}%p 차이"
                        elif str(unit).strip() == "비율":
                            value_text = f"{abs(float(diff)):.2f} 차이"
                        else:
                            val = abs(float(diff))
                            value_text = f"{val:.1f}{unit} 차이" if val < 100 else f"{val:,.0f}{unit} 차이"
                        st.markdown(
                            f"""<div class="card" style="min-height:155px;">
                            <div class="label">비교 단서 {i+1}</div>
                            <div style="font-size:18px;font-weight:800;color:#183f6c;margin:7px 0;">{feature}</div>
                            <div style="font-size:14px;line-height:1.6;"><b>{direction}</b><br>{value_text}</div>
                            </div>""", unsafe_allow_html=True
                        )

            # age_comparison.csv가 새 TWIN과 일치할 때만 연령 상세표를 사용합니다.
            _age_match = age_df[
                (age_df["area_code"] == str(selected_code).strip()) &
                (age_df["category"] == str(category).strip()) &
                (age_df["twin_name"].astype(str).str.strip() == str(data["twin"]).strip())
            ].copy()

            if not _age_match.empty:
                age_order = ["10대", "20대", "30대", "40대", "50대", "60대 이상"]
                _age_match["age_group"] = pd.Categorical(_age_match["age_group"], categories=age_order, ordered=True)
                _age_match = _age_match.sort_values("age_group")
                with st.expander("연령대별 유동인구 구성 자세히 보기"):
                    st.caption(
                        "우리 상권과 현재 비교 TWIN의 유동인구 연령 구성을 비교합니다. "
                        "특정 업종·시간대의 실제 구매 고객 연령을 의미하지 않습니다."
                    )
                    age_display = _age_match[["age_group", "area_share", "twin_share", "difference_pp"]].copy()
                    age_display["우리 상권"] = (age_display["area_share"] * 100).map(lambda x: f"{x:.1f}%")
                    age_display["비교 TWIN"] = (age_display["twin_share"] * 100).map(lambda x: f"{x:.1f}%")
                    age_display["차이"] = age_display["difference_pp"].map(lambda x: f"{x:+.1f}%p")
                    age_display = age_display.rename(columns={"age_group": "연령대"})
                    st.dataframe(age_display[["연령대", "우리 상권", "비교 TWIN", "차이"]],
                                 hide_index=True, use_container_width=True)

            with st.expander("ⓘ 비교 TWIN 선정 기준과 유사도 보기"):
                st.write(
                    "동일 업종 상권 중 구조 유사도 85점 이상이면서 FLOW SCORE가 우리 상권보다 높은 곳만 후보가 됩니다. "
                    "그 후보들 가운데 16개 구조 특성이 가장 유사한 상권을 비교 TWIN으로 선택합니다."
                )
                st.info(
                    "유사도 85점은 16개 구조 특성의 업종 내 상대적 위치가 충분히 비슷하다는 선정 기준입니다. "
                    "두 상권의 실제 특성이 85% 일치한다는 뜻은 아닙니다."
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
                    "※ 구조 유사도는 실제 특성의 일치율이 아니라 16개 특성의 업종 내 상대적 위치 차이를 종합한 비교용 지수입니다."
                )

        # 5. STORE DIAGNOSIS
    if page == "내 가게 점검":
        st.markdown('<div class="page-kicker">MY STORE CHECK</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">우리 가게에서는 무엇부터 확인해야 할까요?</div>', unsafe_allow_html=True)
        st.markdown(
            """<div class="result-strip">
            <div class="title">상권 분석에서 점포 점검으로</div>
            <div style="font-size:14px;line-height:1.65;color:#526579;">
            상권 분석 결과와 사장님의 응답을 함께 비교해 <b>다음으로 확인할 항목</b>을 정합니다.
            개별 점포의 POS·입점 데이터는 연결되어 있지 않으므로, 원인을 확정하는 처방이 아니라 점검 가이드로 활용합니다.
            </div></div>""",
            unsafe_allow_html=True
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
    
                st.markdown('<div style="font-size:18px;font-weight:850;color:#18324a;margin:22px 0 10px;">맞춤 점검 결과</div>', unsafe_allow_html=True)
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
    
                st.markdown('<div style="font-size:18px;font-weight:850;color:#18324a;margin:24px 0 10px;">FLOW ACTION · 확인 순서</div>', unsafe_allow_html=True)
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
