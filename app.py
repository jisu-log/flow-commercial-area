import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================================================
# PAGE
# =========================================================
st.set_page_config(
    page_title="FLOW | 골목상권 소비기회 진단",
    page_icon="🌊",
    layout="wide"
)

# =========================================================
# DATA
# =========================================================
@st.cache_data
def load_data():
    area = pd.read_csv("area_summary.csv")
    time = pd.read_csv("time_result.csv")
    twin = pd.read_csv("twin_difference.csv")

    area["area_code"] = area["area_code"].astype(str)
    time["area_code"] = time["area_code"].astype(str)

    return area, time, twin


try:
    area_df, time_df, twin_df = load_data()
except Exception as e:
    st.error("분석 데이터를 불러오지 못했습니다.")
    st.code(str(e))
    st.stop()


# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>

.stApp {
    background-color: #F7F9FC;
}

.block-container {
    max-width: 1160px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2EAF1;
    padding: 20px;
    border-radius: 17px;
    box-shadow: 0 4px 14px rgba(20,60,100,0.05);
}

[data-testid="stMetricLabel"] {
    font-weight: 700;
}

/* BLUE BUTTON */
div.stButton > button,
div.stButton > button[kind="primary"] {
    background-color: #174F82 !important;
    color: white !important;
    border: 1px solid #174F82 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    min-height: 49px;
}

div.stButton > button:hover,
div.stButton > button[kind="primary"]:hover {
    background-color: #24699F !important;
    border-color: #24699F !important;
    color: white !important;
}

/* heading 대신 사용 → 링크 아이콘 방지 */
.flow-title {
    font-size: 20px;
    font-weight: 800;
    color: #183B5B;
    margin-top: 13px;
    margin-bottom: 5px;
}

.flow-small-title {
    font-size: 17px;
    font-weight: 750;
    color: #183B5B;
    margin-bottom: 4px;
}

.flow-label {
    font-size: 12px;
    font-weight: 700;
    color: #72808E;
    margin-bottom: 4px;
}

.flow-note {
    color: #6B7885;
    font-size: 13px;
    line-height: 1.7;
}

.flow-blue {
    background: #EDF5FB;
    border: 1px solid #D6E5F1;
    border-radius: 15px;
    padding: 18px 20px;
    margin: 10px 0;
}

.flow-yellow {
    background: #FFF8EA;
    border: 1px solid #F0D7A6;
    border-radius: 15px;
    padding: 18px 20px;
    margin: 10px 0;
}

.flow-green {
    background: #EFF8F3;
    border: 1px solid #D5E9DD;
    border-radius: 15px;
    padding: 18px 20px;
    margin: 10px 0;
}

.flow-card {
    background: white;
    border: 1px solid #E2EAF1;
    border-radius: 16px;
    padding: 18px;
    min-height: 145px;
}

.type-box {
    background: #EAF3FA;
    border-left: 5px solid #174F82;
    border-radius: 14px;
    padding: 20px 22px;
    margin: 14px 0;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def is_available(value):
    if isinstance(value, (bool, np.bool_)):
        return bool(value)

    return str(value).strip().lower() in [
        "true", "1", "yes", "y"
    ]


def valid_text(value):
    return (
        pd.notna(value)
        and str(value).strip() not in ["", "nan", "None"]
    )


def level(score):
    if score < 30:
        return "낮은 편"
    elif score < 70:
        return "보통"
    else:
        return "높은 편"


def percentile_text(score):
    rank = int(round(score))
    rank = max(1, min(rank, 100))
    return f"같은 업종 상권 100곳 중 약 {rank}번째 수준"


def format_difference(value, unit):
    value = float(value)
    unit = "" if pd.isna(unit) else str(unit).strip()

    if unit == "비율":
        return f"{abs(value) * 100:.1f}%p"

    if unit == "명":
        return f"{abs(value):,.0f}명"

    if unit == "개":
        return f"{abs(value):,.0f}개"

    if unit == "㎡":
        return f"{abs(value):,.0f}㎡"

    if unit == "%":
        return f"{abs(value):.1f}%p"

    if abs(value) >= 1000:
        return f"{abs(value):,.0f}{unit}"

    return f"{abs(value):.1f}{unit}"


def direction(value):
    value = float(value)

    if value > 0:
        return "우리 상권이 더 높아요"
    elif value < 0:
        return "우리 상권이 더 낮아요"
    else:
        return "두 상권이 비슷해요"


# ---------------------------------------------------------
# 상권 유형 분류
#
# 70점 이상 = 상대적으로 높은 수준
# 30점 미만 = 상대적으로 낮은 수준
# 중간 구간은 보통으로 처리
# ---------------------------------------------------------
def diagnose_type(traffic, flow):

    if traffic >= 70 and flow < 70:
        return (
            "전환 개선형",
            "사람의 흐름은 충분하지만 소비 연결 성과는 그에 비해 높지 않은 상권입니다.",
            "새로운 유동을 더 만드는 것보다 현재 존재하는 유동이 실제 소비로 연결되는 과정부터 살펴볼 가치가 있습니다."
        )

    elif traffic >= 70 and flow >= 70:
        return (
            "강점 유지형",
            "사람의 흐름도 많고 소비 연결 성과도 높은 상권입니다.",
            "현재 강점이 어느 시간대에서 만들어지는지 확인하고 유지하는 방향이 중요합니다."
        )

    elif traffic < 30 and flow < 70:
        return (
            "유입·전환 점검형",
            "사람의 흐름 자체가 적고 소비 연결 성과도 높지 않은 상권입니다.",
            "유입 부족과 소비 연결 문제를 함께 살펴볼 필요가 있습니다."
        )

    elif traffic < 70 and flow >= 70:
        return (
            "효율형",
            "유동 규모가 아주 높지는 않지만 소비 연결 성과는 높은 상권입니다.",
            "현재 방문객을 소비로 연결하는 힘이 상대적으로 좋은 상권입니다."
        )

    else:
        return (
            "균형 점검형",
            "유동과 소비 연결이 모두 중간 범위에 위치한 상권입니다.",
            "전체 점수보다 시간대별 소비공백과 유사상권 비교를 중심으로 살펴보는 것이 좋습니다."
        )


# =========================================================
# HERO
# =========================================================
st.title("🌊 FLOW")
st.subheader("사람은 많은데, 왜 소비로 이어지지 않을까?")

st.write(
    "FLOW는 서울 골목상권의 **사람 흐름 → 실제 소비 연결**을 분석합니다. "
    "내 상권에서 놓치고 있는 시간대를 찾고, "
    "구조는 비슷하지만 소비 연결이 더 잘되는 상권과 비교해 "
    "무엇을 먼저 확인해야 하는지 알려드립니다."
)

st.divider()


# =========================================================
# INPUT
# =========================================================
st.header("1. 내 상권 찾아보기")

st.write(
    "서울시에서 정의한 **골목상권 단위**로 분석합니다."
)

with st.expander("ⓘ 내가 어느 골목상권인지 잘 모르겠어요"):
    st.write(
        "상권명은 역이나 특정 지점 자체를 의미하지 않습니다. "
        "서울시 상권분석서비스에서 지정한 골목상권 영역의 이름입니다."
    )
    st.write(
        "현재 프로토타입에서는 상권명을 검색해 선택할 수 있으며, "
        "향후 주소·지도 기반으로 해당 골목상권을 바로 찾을 수 있도록 "
        "확장할 수 있습니다."
    )


area_options = (
    area_df[["area_code", "area"]]
    .drop_duplicates(subset=["area_code"])
    .sort_values(["area", "area_code"])
    .reset_index(drop=True)
)

area_name_map = dict(
    zip(area_options["area_code"], area_options["area"])
)

c1, c2 = st.columns(2)

with c1:
    selected_code = st.selectbox(
        "분석할 골목상권",
        options=area_options["area_code"].tolist(),
        format_func=lambda x: area_name_map.get(x, x)
    )

selected_area = area_name_map[selected_code]

# 전체 CSV 업종 자동 인식
categories = (
    area_df["category"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

with c2:
    selected_category = st.selectbox(
        "업종",
        options=categories
    )

st.caption(
    "현재 제공 업종은 분석 데이터에 포함된 업종 기준입니다. "
    "향후 전체 업종 분석 CSV로 교체하면 선택 가능한 업종도 자동으로 확대됩니다."
)

# =========================================================
# 진단 실행 상태 저장
# =========================================================

if "diagnosis_started" not in st.session_state:
    st.session_state.diagnosis_started = False

if "diagnosed_code" not in st.session_state:
    st.session_state.diagnosed_code = None

if "diagnosed_category" not in st.session_state:
    st.session_state.diagnosed_category = None


if st.button(
    "내 상권 진단하기",
    type="primary",
    use_container_width=True
):
    st.session_state.diagnosis_started = True
    st.session_state.diagnosed_code = selected_code
    st.session_state.diagnosed_category = selected_category


if not st.session_state.diagnosis_started:
    st.stop()


# 실제 분석에는 버튼을 눌렀을 당시 선택값 사용
selected_code = st.session_state.diagnosed_code
selected_category = st.session_state.diagnosed_category
selected_area = area_name_map[selected_code]


# =========================================================
# FIND RESULT
# =========================================================
rows = area_df[
    (area_df["area_code"] == selected_code) &
    (area_df["category"] == selected_category)
]

if rows.empty:
    st.warning(
        "선택한 상권과 업종 조합은 현재 분석 결과가 없습니다. "
        "다른 업종을 선택해 주세요."
    )
    st.stop()

result = rows.iloc[0]

if not is_available(result["analysis_available"]):
    st.warning(
        "최근 4개 분기의 활동 또는 관측 근거가 부족하여 "
        "이 상권·업종은 신뢰할 수 있는 분석 결과를 제공하기 어렵습니다."
    )
    st.stop()


# =========================================================
# VALUES
# =========================================================
flow_score = float(result["flow_score"])
traffic_score = float(result["traffic_score"])

dead_time = (
    str(result["dead_time"])
    if valid_text(result["dead_time"])
    else "뚜렷한 DEAD TIME 없음"
)

twin_name = result["twin_name"]

similarity = (
    float(result["similarity"])
    if pd.notna(result["similarity"])
    else np.nan
)

twin_conversion = (
    float(result["twin_conversion"])
    if pd.notna(result["twin_conversion"])
    else np.nan
)

has_twin = valid_text(twin_name)

type_name, type_desc, type_action = diagnose_type(
    traffic_score,
    flow_score
)


# =========================================================
# TIME DATA
# =========================================================
selected_time = time_df[
    (time_df["area_code"] == selected_code) &
    (time_df["category"] == selected_category)
].copy()

time_order = [
    "00~06",
    "06~11",
    "11~14",
    "14~17",
    "17~21",
    "21~24"
]

if not selected_time.empty:
    selected_time["time"] = pd.Categorical(
        selected_time["time"],
        categories=time_order,
        ordered=True
    )
    selected_time = selected_time.sort_values("time")


# =========================================================
# RESULT
# =========================================================
st.divider()

st.header(
    f"2. {selected_area} · {selected_category} 진단"
)

st.caption(
    "서울시 골목상권 × 업종 단위 분석 결과입니다."
)


# =========================================================
# TYPE
# =========================================================
st.markdown(
    f"""
    <div class="type-box">
        <div class="flow-label">FLOW 상권 유형</div>
        <div style="
            font-size:29px;
            font-weight:800;
            color:#174F82;
            margin-bottom:6px;">
            {type_name}
        </div>
        <div style="
            font-size:16px;
            font-weight:600;
            color:#31485B;
            margin-bottom:8px;">
            {type_desc}
        </div>
        <div class="flow-note">
            {type_action}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CORE SCORE
# =========================================================
st.subheader("한눈에 보는 우리 상권")

s1, s2 = st.columns(2)

with s1:
    st.metric(
        "소비 연결력 · FLOW SCORE",
        f"{flow_score:.1f}점",
        level(flow_score)
    )

    st.write(
        f"**{percentile_text(flow_score)}**"
    )

    st.caption(
        "상권 여건을 고려했을 때 실제 소비로 "
        "연결되는 상대적 수준"
    )

with s2:
    st.metric(
        "유동 수준",
        f"{traffic_score:.1f}점",
        level(traffic_score)
    )

    st.write(
        f"**{percentile_text(traffic_score)}**"
    )

    st.caption(
        "같은 업종 상권과 비교한 사람 흐름의 상대적 수준"
    )


with st.expander("ⓘ FLOW SCORE를 쉽게 설명해 주세요"):
    st.write(
        "사람이 많다고 반드시 소비가 많이 발생하는 것은 아닙니다."
    )
    st.write(
        "FLOW SCORE는 유동인구뿐 아니라 상주·직장인구, "
        "점포구성 등 상권 여건을 함께 고려했을 때 "
        "실제 소비가 얼마나 잘 연결되고 있는지를 "
        "같은 업종 상권끼리 비교한 0~100의 상대적 지표입니다."
    )
    st.write(
        "따라서 70점이라고 해서 상권 자체가 '70점짜리'라는 의미는 아닙니다."
    )


# =========================================================
# TIME CHART
# =========================================================
st.divider()
st.header("3. 언제 소비 기회를 놓치고 있을까요?")

if selected_time.empty:

    st.warning("시간대별 분석 결과가 없습니다.")

else:

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=selected_time["time"].astype(str),
            y=selected_time["potential"],
            name="상권 여건상 기대 소비"
        )
    )

    fig.add_trace(
        go.Bar(
            x=selected_time["time"].astype(str),
            y=selected_time["actual"],
            name="실제 소비"
        )
    )

    if dead_time in time_order:

        dead_rows = selected_time[
            selected_time["time"].astype(str) == dead_time
        ]

        if not dead_rows.empty:

            max_y = max(
                float(dead_rows.iloc[0]["potential"]),
                float(dead_rows.iloc[0]["actual"])
            )

            fig.add_annotation(
                x=dead_time,
                y=max_y,
                text="주목할 시간",
                showarrow=True,
                arrowhead=2,
                yshift=25
            )

    fig.update_layout(
        barmode="group",
        height=420,
        margin=dict(l=20, r=20, t=45, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="시간대",
        yaxis_title="상대적 소비 수준",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


    if dead_time != "뚜렷한 DEAD TIME 없음":

        dead_rows = selected_time[
            selected_time["time"].astype(str) == dead_time
        ]

        if not dead_rows.empty:

            d = dead_rows.iloc[0]
            repeat_dead = int(d["repeat_dead"])

            st.warning(
                f"**{dead_time}를 먼저 확인해 보세요.** "
                f"상권 여건에 비해 실제 소비가 상대적으로 부족한 현상이 "
                f"최근 4개 분기 중 **{repeat_dead}회** 반복되었습니다."
            )

    else:

        st.success(
            "특정 시간대에서 반복적으로 나타나는 "
            "뚜렷한 소비공백은 발견되지 않았습니다."
        )


with st.expander("ⓘ 기대 소비와 DEAD TIME은 무슨 뜻인가요?"):
    st.write(
        "'상권 여건상 기대 소비'는 미래 매출 예측값이 아닙니다. "
        "유동인구와 여러 상권 조건을 고려했을 때 통계적으로 "
        "비교하기 위한 상대적 기준입니다."
    )
    st.write(
        "DEAD TIME은 이 기대수준과 실제 소비 사이의 공백이 "
        "같은 업종·시간대에서 상대적으로 크고, "
        "최근 4개 분기 중 최소 2회 반복된 시간입니다."
    )
    st.write(
        "00~06시는 DEAD TIME 판정에서 제외됩니다."
    )


# =========================================================
# TWIN
# =========================================================
st.divider()
st.header("4. 우리와 닮았지만 더 잘되는 곳")

twin_rows = pd.DataFrame()

if not has_twin:

    st.info(
        "현재 조건에서는 구조적으로 유사하면서 "
        "소비 연결 성과가 더 높은 비교 상권을 찾지 못했습니다."
    )

else:

    st.markdown(
        f"""
        <div class="flow-blue">
            <div class="flow-label">BEST TWIN</div>
            <div style="
                font-size:28px;
                font-weight:800;
                color:#174F82;">
                {twin_name}
            </div>
            <div style="
                font-size:15px;
                font-weight:650;
                margin-top:5px;">
                상권 구조 유사도 {similarity:.1f}점
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        f"**{twin_name}**은 우리 상권과 유동·인구·점포구조 등이 "
        "비슷하지만 소비 연결 성과는 더 높은 비교 상권입니다."
    )

    t1, t2 = st.columns(2)

    with t1:
        st.metric(
            "우리 상권 소비 연결력",
            f"{flow_score:.1f}점"
        )

    with t2:
        if pd.notna(twin_conversion):
            st.metric(
                "BEST TWIN 소비 연결력",
                f"{twin_conversion:.1f}점",
                f"{twin_conversion-flow_score:+.1f}점"
            )


    twin_rows = twin_df[
        (twin_df["area"] == selected_area) &
        (twin_df["category"] == selected_category) &
        (twin_df["twin_name"] == twin_name)
    ].copy()

    twin_rows = twin_rows.sort_values("rank").head(3)


    if not twin_rows.empty:

        st.subheader("닮은 상권과 이런 점이 달라요")

        cols = st.columns(3)

        for i, (_, row) in enumerate(twin_rows.iterrows()):

            value = float(row["difference"])
            readable = format_difference(
                value,
                row["unit"]
            )

            with cols[i]:

                st.markdown(
                    f"""
                    <div class="flow-card">
                        <div class="flow-label">
                            TOP {int(row["rank"])}
                        </div>
                        <div class="flow-small-title">
                            {row["feature"]}
                        </div>
                        <div style="
                            font-size:24px;
                            font-weight:800;
                            color:#174F82;
                            margin:8px 0;">
                            {readable}
                        </div>
                        <div class="flow-note">
                            {direction(value)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.caption(
            "위 항목은 BEST TWIN과 비교했을 때 차이가 크게 나타난 "
            "상권 특성입니다. 해당 특성이 소비성과 차이의 직접적인 "
            "원인이라는 의미는 아닙니다."
        )


with st.expander("ⓘ BEST TWIN은 어떻게 찾나요?"):
    st.write(
        "같은 업종의 상권 중 유동·인구·점포구조 등 "
        "16개 상권 특성이 우리 상권과 유사하면서 "
        "FLOW SCORE가 더 높은 상권을 찾습니다."
    )
    st.write(
        "구조적 유사도는 실제 특성이 몇 % 동일하다는 뜻이 아니라 "
        "16개 특성의 상대적 위치 차이를 이용한 비교 지표입니다."
    )


# =========================================================
# DECISION SUPPORT
# =========================================================
st.divider()
st.header("5. 그래서 무엇을 먼저 확인해야 할까요?")

st.write(
    "FLOW는 개별 점포의 매출 원인을 단정하지 않습니다. "
    "대신 현재 상권 데이터에서 **우선 확인할 문제의 방향**을 제시합니다."
)

# 1
st.markdown(
    '<div class="flow-title">① 상권 유형부터 확인</div>',
    unsafe_allow_html=True
)

st.write(
    f"현재 상권은 **{type_name}**입니다. {type_action}"
)

# 2
st.markdown(
    '<div class="flow-title">② 시간대 확인</div>',
    unsafe_allow_html=True
)

if dead_time != "뚜렷한 DEAD TIME 없음":

    st.write(
        f"**{dead_time}**에 상권 차원의 소비공백이 반복되고 있습니다. "
        "내 매장에서도 같은 시간대의 주문이나 매출이 낮은지 먼저 비교해 보세요."
    )

else:

    st.write(
        "상권 전체에서 반복적으로 나타나는 특정 DEAD TIME은 없습니다. "
        "내 매장만 특정 시간대 매출이 낮다면 점포 수준의 문제일 가능성을 "
        "추가로 살펴볼 필요가 있습니다."
    )

# 3
st.markdown(
    '<div class="flow-title">③ 비교상권에서 힌트 찾기</div>',
    unsafe_allow_html=True
)

if has_twin:

    st.write(
        f"**{twin_name}**은 구조가 비슷하지만 소비 연결 성과가 더 높습니다."
    )

    if not twin_rows.empty:
        feature_names = twin_rows["feature"].tolist()

        st.write(
            "두 상권에서 상대적으로 차이가 크게 나타난 항목은 "
            f"**{', '.join(feature_names)}**입니다. "
            "원인으로 단정하기보다 추가로 확인할 비교 포인트로 활용할 수 있습니다."
        )

else:

    st.write(
        "현재 조건에서는 적절한 BEST TWIN이 없어 "
        "동일 업종 내 FLOW SCORE와 시간대별 소비공백을 중심으로 "
        "살펴보는 것이 적절합니다."
    )


# =========================================================
# STORE SELF CHECK
# =========================================================
st.divider()
st.header("6. 우리 가게도 같은 문제일까요?")

st.write(
    "상권 분석만으로는 **우리 가게 자체의 문제인지, "
    "동네 전체의 문제인지** 구분하기 어렵습니다."
)

st.write(
    "내 매장의 시간대별 상황을 알고 있다면 아래에서 "
    "상권 분석 결과와 간단히 비교해볼 수 있습니다."
)

use_store_check = st.checkbox(
    "내 가게의 취약 시간대와 비교해보기"
)

if use_store_check:

    store_weak_times = st.multiselect(
        "평소 주문이나 매출이 특히 낮다고 느끼는 시간대를 선택하세요.",
        options=[
            "06~11",
            "11~14",
            "14~17",
            "17~21",
            "21~24"
        ]
    )

    if store_weak_times:

        if (
            dead_time != "뚜렷한 DEAD TIME 없음"
            and dead_time in store_weak_times
        ):

            st.success(
                f"**상권 공통형 소비공백 가능성**\n\n"
                f"내 매장에서 약하다고 느끼는 **{dead_time}**가 "
                f"상권 전체에서도 반복적인 DEAD TIME으로 탐지되었습니다. "
                f"점포 하나만의 현상이라기보다 해당 상권·업종에서 "
                f"공통적으로 나타나는 시간대 패턴일 가능성을 먼저 "
                f"살펴볼 수 있습니다."
            )

        elif dead_time == "뚜렷한 DEAD TIME 없음":

            st.warning(
                "**점포 개별형 점검 필요**\n\n"
                "상권 전체에서는 반복적인 DEAD TIME이 탐지되지 않았지만 "
                "내 매장에서는 취약 시간대가 존재합니다. "
                "상권 자체보다 매장별 상품구성, 가격, 노출, 운영시간 등의 "
                "점포 수준 요소를 추가로 확인해볼 필요가 있습니다."
            )

        else:

            st.warning(
                "**상권과 점포의 취약 시간이 다릅니다.**\n\n"
                f"상권에서는 **{dead_time}**가 DEAD TIME으로 탐지됐지만 "
                f"내 매장의 취약 시간은 "
                f"**{', '.join(store_weak_times)}**입니다. "
                "상권 공통 패턴과 매장 개별 패턴을 구분해서 살펴볼 필요가 있습니다."
            )

    else:

        st.caption(
            "취약 시간대를 하나 이상 선택하면 상권 결과와 비교해 드립니다."
        )


with st.expander("시간대별 매출 데이터가 있다면 더 정확하게 할 수 있나요?"):
    st.write(
        "가능합니다. 현재 버전은 사용자가 체감하는 취약 시간대를 "
        "상권 데이터와 비교하는 간단한 프로토타입입니다."
    )
    st.write(
        "향후 POS 등의 실제 점포 시간대별 매출 데이터를 연결하면 "
        "'상권도 약하고 내 매장도 약한 시간', "
        "'상권은 괜찮지만 내 매장만 약한 시간' 등을 "
        "보다 객관적으로 구분할 수 있습니다."
    )


# =========================================================
# FINAL
# =========================================================
st.divider()

st.markdown(
    '<div class="flow-title">FLOW의 역할</div>',
    unsafe_allow_html=True
)

st.write(
    "**사람이 없는 곳을 찾는 것에서 끝나지 않고, "
    "사람이 있는데도 소비로 연결되지 않는 지점을 발견합니다.**"
)

st.caption(
    "FLOW는 서울시 상권 데이터를 기반으로 한 데이터 분석 프로토타입입니다. "
    "분석 결과는 상권×업종 수준의 상대적 비교이며 개별 점포의 미래 매출을 "
    "예측하거나 특정 요인이 매출 부진의 직접적인 원인임을 의미하지 않습니다."
)
