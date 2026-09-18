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

/* 전체 배경 */
.stApp {
    background-color: #F7F9FC;
}

.block-container {
    max-width: 1160px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

/* Metric 카드 */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E3EAF1;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0px 4px 16px rgba(23,79,130,0.05);
}

[data-testid="stMetricLabel"] {
    font-weight: 700;
}

/* 버튼 강제 파랑 */
div.stButton > button,
div.stButton > button[kind="primary"] {
    background-color: #174F82 !important;
    color: white !important;
    border: 1px solid #174F82 !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    min-height: 50px;
}

div.stButton > button:hover,
div.stButton > button[kind="primary"]:hover {
    background-color: #21689F !important;
    border-color: #21689F !important;
    color: white !important;
}

/* 링크 아이콘 없는 일반 소제목 */
.flow-mini-title {
    font-size: 18px;
    font-weight: 750;
    color: #183B5B;
    margin-top: 8px;
    margin-bottom: 5px;
}

.flow-label {
    font-size: 13px;
    color: #6E7D8C;
    font-weight: 700;
    margin-bottom: 4px;
}

.flow-result {
    font-size: 17px;
    font-weight: 650;
    color: #263C50;
}

.flow-note {
    font-size: 13px;
    color: #6B7885;
    line-height: 1.7;
}

.flow-highlight {
    background: #EDF5FB;
    border: 1px solid #D7E6F2;
    border-radius: 14px;
    padding: 17px 19px;
    margin-top: 10px;
    margin-bottom: 10px;
}

.flow-warning {
    background: #FFF8EB;
    border: 1px solid #F0D6A6;
    border-radius: 14px;
    padding: 17px 19px;
    margin-top: 10px;
    margin-bottom: 10px;
}

.flow-summary {
    background: #FFFFFF;
    border: 1px solid #E3EAF1;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 12px;
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


def level_text(score):
    if score < 30:
        return "낮은 편"
    elif score < 70:
        return "보통"
    else:
        return "높은 편"


def percentile_sentence(score):
    rank = int(round(score))

    if rank <= 0:
        rank = 1
    if rank >= 100:
        rank = 100

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


def direction_sentence(value):
    value = float(value)

    if value > 0:
        return "우리 상권이 더 높아요"
    elif value < 0:
        return "우리 상권이 더 낮아요"
    else:
        return "두 상권이 비슷해요"


# =========================================================
# HERO
# =========================================================
st.title("🌊 FLOW")
st.subheader("사람은 많은데, 왜 소비로 이어지지 않을까?")

st.write(
    "FLOW는 단순히 사람이 많은 상권을 찾는 서비스가 아닙니다. "
    "사람의 흐름이 실제 소비로 얼마나 이어지고 있는지 살펴보고, "
    "놓치고 있는 시간대와 비교해볼 만한 유사상권을 찾아줍니다."
)

st.divider()


# =========================================================
# SELECT AREA
# =========================================================
st.header("내 상권 진단하기")

st.write(
    "**어디에서 장사하고 계신가요?** "
    "서울시에서 정의한 골목상권을 기준으로 분석합니다."
)

with st.expander("상권명이 낯선가요?"):
    st.write(
        "FLOW의 '상권'은 역 자체나 임의의 반경을 의미하지 않습니다. "
        "서울시 상권분석서비스에서 정의한 골목상권 영역을 사용합니다."
    )
    st.write(
        "상권명에는 주변 역, 도로, 학교 등의 이름이 포함될 수 있습니다. "
        "예를 들어 '효창공원앞역 5번'은 역 5번 출구 자체가 아니라 "
        "그 명칭으로 지정된 골목상권 영역을 의미합니다."
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

select1, select2 = st.columns(2)

with select1:
    selected_code = st.selectbox(
        "분석할 골목상권 선택",
        options=area_options["area_code"].tolist(),
        format_func=lambda code: area_name_map.get(code, code),
        help="상권명을 입력해 검색할 수도 있습니다."
    )

selected_area = area_name_map[selected_code]

# 전체 분석 데이터의 업종을 자동으로 읽음.
# 나중에 전체 업종 CSV로 바꾸면 자동으로 추가됨.
categories = (
    area_df["category"]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

with select2:
    selected_category = st.selectbox(
        "업종 선택",
        options=categories
    )

st.caption(
    "현재 프로토타입은 최종 분석 데이터에 포함된 업종을 제공합니다. "
    "분석 범위가 확대되면 선택 가능한 업종도 자동으로 늘어납니다."
)

run = st.button(
    "내 상권 진단하기",
    type="primary",
    use_container_width=True
)

if not run:
    st.stop()


# =========================================================
# FIND RESULT
# =========================================================
rows = area_df[
    (area_df["area_code"] == selected_code) &
    (area_df["category"] == selected_category)
]

if rows.empty:
    st.warning(
        "선택한 골목상권과 업종 조합은 현재 분석 결과가 없습니다. "
        "다른 업종을 선택해 주세요."
    )
    st.stop()

result = rows.iloc[0]

st.divider()

st.header(f"{selected_area} · {selected_category}")

st.caption(
    "서울시 골목상권 단위 × 업종 단위 분석 결과"
)


# =========================================================
# AVAILABILITY
# =========================================================
if not is_available(result["analysis_available"]):
    st.warning(
        "최근 4개 분기의 활동 또는 관측 근거가 부족하여 "
        "이 상권·업종은 신뢰할 수 있는 진단 결과를 제공하기 어렵습니다."
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

dead_gap = (
    float(result["dead_gap"])
    if pd.notna(result["dead_gap"])
    else 0.0
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


# =========================================================
# EASY SUMMARY
# =========================================================
st.header("한눈에 보는 우리 상권")

if flow_score < 30:
    main_message = (
        "사람의 흐름과 상권 여건에 비해 "
        "실제 소비로 이어지는 정도가 상대적으로 낮습니다."
    )
elif flow_score < 70:
    main_message = (
        "사람의 흐름과 상권 여건 대비 "
        "소비 연결 성과가 중간 수준입니다."
    )
else:
    main_message = (
        "사람의 흐름과 상권 여건이 "
        "실제 소비로 비교적 잘 이어지고 있습니다."
    )

st.info(main_message)

score1, score2 = st.columns(2)

with score1:
    st.metric(
        "소비 연결력 · FLOW SCORE",
        f"{flow_score:.1f}점",
        level_text(flow_score)
    )

    st.write(
        f"**{percentile_sentence(flow_score)}**"
    )

    st.caption(
        "사람의 흐름과 상권 여건을 고려했을 때 "
        "실제 소비로 이어지는 상대적 수준입니다."
    )

with score2:
    st.metric(
        "유동 수준",
        f"{traffic_score:.1f}점",
        level_text(traffic_score)
    )

    st.write(
        f"**{percentile_sentence(traffic_score)}**"
    )

    if traffic_score >= 70:
        st.caption(
            "동일 업종 상권과 비교하면 사람의 흐름은 많은 편입니다."
        )
    elif traffic_score < 30:
        st.caption(
            "동일 업종 상권과 비교하면 사람의 흐름은 적은 편입니다."
        )
    else:
        st.caption(
            "동일 업종 상권과 비교하면 사람의 흐름은 중간 수준입니다."
        )


with st.expander("ⓘ FLOW SCORE는 무엇인가요?"):
    st.write(
        "FLOW SCORE는 단순 매출점수나 상권의 절대적인 우수성을 "
        "평가하는 점수가 아닙니다."
    )
    st.write(
        "유동인구, 상주·직장인구, 점포구성 등 상권 조건을 고려했을 때의 "
        "기대 소비수준과 실제 소비성과의 차이를 계산하고, "
        "이를 동일 업종 상권 내 상대적 위치인 0~100점으로 변환한 지표입니다."
    )
    st.write(
        "따라서 점수가 높을수록 주어진 상권 조건에 비해 "
        "실제 소비가 상대적으로 활발하게 연결되고 있음을 의미합니다."
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
# TIME OPPORTUNITY
# =========================================================
st.divider()
st.header("언제 소비 기회를 놓치고 있을까요?")

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
            dead_y = max(
                float(dead_rows.iloc[0]["potential"]),
                float(dead_rows.iloc[0]["actual"])
            )

            fig.add_annotation(
                x=dead_time,
                y=dead_y,
                text="주목할 시간",
                showarrow=True,
                arrowhead=2,
                yshift=25
            )

    fig.update_layout(
        barmode="group",
        height=420,
        margin=dict(l=20, r=20, t=40, b=20),
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
                f"**{dead_time}를 주목하세요.** "
                f"사람의 흐름과 상권 여건에 비해 실제 소비가 상대적으로 "
                f"부족한 현상이 최근 4개 분기 중 "
                f"**{repeat_dead}회** 반복되었습니다."
            )
    else:
        st.success(
            "특정 시간대에서 반복적으로 나타나는 "
            "뚜렷한 소비공백은 발견되지 않았습니다."
        )

    with st.expander("ⓘ 이 그래프는 어떻게 읽나요?"):
        st.write(
            "'상권 여건상 기대 소비'와 '실제 소비' 사이의 차이가 클수록 "
            "현재 상권의 사람 흐름과 조건에 비해 소비로 충분히 "
            "연결되지 못하고 있을 가능성을 보여줍니다."
        )
        st.write(
            "단, 기대 소비는 미래 매출액이나 매출건수를 정확히 예측한 값이 "
            "아니라 상권 간 비교를 위한 통계적 기준입니다."
        )


# =========================================================
# DEAD TIME
# =========================================================
st.subheader("놓치고 있는 시간 · DEAD TIME")

if dead_time == "뚜렷한 DEAD TIME 없음":
    st.success(
        "최근 4개 분기에서 반복적으로 확인되는 "
        "뚜렷한 DEAD TIME은 없습니다."
    )

else:
    dead_rows = selected_time[
        selected_time["time"].astype(str) == dead_time
    ]

    if not dead_rows.empty:
        d = dead_rows.iloc[0]

        st.markdown(
            f'<div class="flow-warning">'
            f'<div class="flow-label">가장 먼저 살펴볼 시간</div>'
            f'<div style="font-size:28px;font-weight:800;color:#9A6100;">'
            f'{dead_time}</div>'
            f'<div class="flow-result">'
            f'최근 4개 분기 중 {int(d["repeat_dead"])}회 반복 탐지'
            f'</div></div>',
            unsafe_allow_html=True
        )

    with st.expander("ⓘ DEAD TIME은 어떻게 정하나요?"):
        st.write(
            "00~06시는 판정에서 제외하고, 활동 근거가 충분한 시간대 중 "
            "동일 업종·분기·시간대와 비교했을 때 소비공백이 상위 10%에 "
            "해당하는 경우를 확인합니다."
        )
        st.write(
            "일시적인 현상을 DEAD TIME으로 판단하지 않기 위해 "
            "최근 4개 분기 중 최소 2회 반복된 시간대만 최종 탐지합니다."
        )


# =========================================================
# BEST TWIN
# =========================================================
st.divider()
st.header("우리와 닮았지만 소비 연결이 더 잘되는 곳")

has_twin = valid_text(twin_name)

if not has_twin:
    st.info(
        "현재 조건에서는 구조적으로 유사하면서 "
        "소비 연결 성과가 더 높은 비교 상권을 찾지 못했습니다."
    )

else:
    st.markdown(
        f'<div class="flow-highlight">'
        f'<div class="flow-label">BEST TWIN</div>'
        f'<div style="font-size:27px;font-weight:800;color:#174F82;">'
        f'{twin_name}</div>'
        f'<div class="flow-result">'
        f'상권 구조 유사도 {similarity:.1f}점'
        f'</div></div>',
        unsafe_allow_html=True
    )

    st.write(
        f"**{twin_name}**은 우리 상권과 유동·인구·점포구조 등이 "
        "비슷하면서 소비 연결 성과가 더 높은 상권입니다."
    )

    twin1, twin2 = st.columns(2)

    with twin1:
        st.metric(
            "우리 상권 소비 연결력",
            f"{flow_score:.1f}점"
        )

    with twin2:
        if pd.notna(twin_conversion):
            st.metric(
                "BEST TWIN 소비 연결력",
                f"{twin_conversion:.1f}점",
                f"{twin_conversion-flow_score:+.1f}점"
            )

    with st.expander("ⓘ BEST TWIN과 구조적 유사도는 무엇인가요?"):
        st.write(
            "BEST TWIN은 같은 업종 중 우리 상권과 구조적으로 유사하면서 "
            "FLOW SCORE가 더 높은 비교 상권입니다."
        )
        st.write(
            "구조적 유사도는 유동·인구·점포구조 등 16개 상권 특성의 "
            "백분위 차이를 이용해 계산합니다."
        )
        st.write(
            f"따라서 유사도 {similarity:.1f}점은 두 상권의 특성이 "
            f"{similarity:.1f}% 동일하다는 의미는 아닙니다."
        )


# =========================================================
# TWIN DIFFERENCE
# =========================================================
twin_rows = pd.DataFrame()

if has_twin:
    st.subheader("닮은 상권과 이런 점이 달라요")

    twin_rows = twin_df[
        (twin_df["area"] == selected_area) &
        (twin_df["category"] == selected_category) &
        (twin_df["twin_name"] == twin_name)
    ].copy()

    twin_rows = twin_rows.sort_values("rank").head(3)

    if twin_rows.empty:
        st.info("BEST TWIN과의 세부 특성 비교 결과가 없습니다.")

    else:
        cols = st.columns(3)

        for i, (_, row) in enumerate(twin_rows.iterrows()):
            value = float(row["difference"])
            readable_value = format_difference(
                value,
                row["unit"]
            )

            with cols[i]:
                st.markdown(
                    f'<div class="flow-summary">'
                    f'<div class="flow-label">'
                    f'TOP {int(row["rank"])}</div>'
                    f'<div class="flow-mini-title">'
                    f'{row["feature"]}</div>'
                    f'<div style="font-size:25px;font-weight:800;'
                    f'color:#174F82;">'
                    f'{readable_value}</div>'
                    f'<div class="flow-note">'
                    f'{direction_sentence(value)}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.caption(
            "위 항목은 BEST TWIN과 비교했을 때 상대적으로 차이가 큰 "
            "상권 특성입니다. 해당 특성이 소비성과 차이의 원인이라는 "
            "의미는 아닙니다."
        )


# =========================================================
# FINAL SUMMARY / ACTION
# =========================================================
st.divider()
st.header("FLOW가 찾은 핵심 포인트")

# Heading markdown을 쓰지 않으므로 hover 링크 아이콘이 생기지 않음.

if traffic_score >= 70:
    traffic_summary = (
        "동일 업종 상권과 비교하면 사람의 흐름은 많은 편입니다."
    )
elif traffic_score < 30:
    traffic_summary = (
        "동일 업종 상권과 비교하면 사람의 흐름은 적은 편입니다."
    )
else:
    traffic_summary = (
        "동일 업종 상권과 비교하면 사람의 흐름은 중간 수준입니다."
    )

st.markdown(
    '<div class="flow-mini-title">① 사람의 흐름</div>',
    unsafe_allow_html=True
)
st.write(traffic_summary)

st.markdown(
    '<div class="flow-mini-title">② 놓치고 있는 시간</div>',
    unsafe_allow_html=True
)

if dead_time == "뚜렷한 DEAD TIME 없음":
    st.write(
        "최근 4개 분기에서 반복적으로 나타나는 "
        "뚜렷한 소비공백 시간은 없습니다."
    )
else:
    st.write(
        f"**{dead_time}**에서 반복적인 소비공백이 관측되었습니다. "
        "이 시간대의 상품구성·운영방식·고객흐름 등을 우선 확인해볼 수 있습니다."
    )

st.markdown(
    '<div class="flow-mini-title">③ 비교해볼 상권</div>',
    unsafe_allow_html=True
)

if has_twin:
    st.write(
        f"우리와 구조가 비슷하지만 소비 연결력이 더 높은 "
        f"**{twin_name}**을 비교 대상으로 참고할 수 있습니다."
    )

    if not twin_rows.empty:
        feature_names = twin_rows["feature"].tolist()

        st.write(
            "두 상권에서 상대적으로 차이가 크게 나타난 항목은 "
            f"**{', '.join(feature_names)}**입니다."
        )
else:
    st.write(
        "현재 조건에서는 소비 연결력이 더 높은 적절한 "
        "BEST TWIN이 탐지되지 않았습니다."
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "FLOW는 서울시 상권 데이터를 기반으로 한 데이터 분석 프로토타입입니다. "
    "FLOW SCORE와 BEST TWIN은 동일 업종 내 상대적 비교를 위한 지표이며, "
    "개별 매장의 미래 매출을 예측하거나 특정 상권 특성이 소비성과의 "
    "인과적 원인임을 의미하지 않습니다."
)
