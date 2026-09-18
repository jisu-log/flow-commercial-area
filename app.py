import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================================================
# 1. PAGE
# =========================================================
st.set_page_config(
    page_title="FLOW | 서울 골목상권 소비기회 진단",
    page_icon="🌊",
    layout="wide"
)

# =========================================================
# 2. DATA
# =========================================================
@st.cache_data
def load_data():
    area = pd.read_csv("area_summary.csv")
    time = pd.read_csv("time_result.csv")
    twin = pd.read_csv("twin_difference.csv")

    # 내부 결합키는 문자열로 통일
    area["area_code"] = area["area_code"].astype(str)
    time["area_code"] = time["area_code"].astype(str)

    return area, time, twin


try:
    area_df, time_df, twin_df = load_data()
except Exception as e:
    st.error("분석 데이터 파일을 불러오지 못했습니다.")
    st.code(str(e))
    st.stop()


# =========================================================
# 3. CSS
# =========================================================
st.markdown("""
<style>
    .stApp {
        background-color: #F7F9FC;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.8rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        color: #183B5B;
    }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #E4EAF0;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0 4px 14px rgba(20, 55, 90, 0.05);
    }

    [data-testid="stMetricLabel"] {
        font-weight: 700;
    }

    div.stButton > button {
        width: 100%;
        height: 50px;
        border-radius: 12px;
        font-weight: 700;
    }

    .small-note {
        color: #687786;
        font-size: 13px;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# 4. HELPERS
# =========================================================
def is_available(value):
    """CSV의 TRUE/FALSE를 안전하게 처리"""
    if isinstance(value, (bool, np.bool_)):
        return bool(value)

    return str(value).strip().lower() in [
        "true", "1", "yes", "y"
    ]


def valid_text(value):
    return pd.notna(value) and str(value).strip() not in ["", "nan", "None"]


def format_difference(value, unit):
    """
    twin_difference 표시용.
    비율은 원자료가 0~1 scale이므로 %p로 변환.
    """
    value = float(value)
    unit = "" if pd.isna(unit) else str(unit).strip()

    if unit == "비율":
        return f"{value * 100:+.1f}%p"

    if unit == "명":
        return f"{value:+,.0f}명"

    if unit == "개":
        return f"{value:+,.0f}개"

    if unit == "㎡":
        return f"{value:+,.0f}㎡"

    if unit == "%":
        return f"{value:+.1f}%"

    if abs(value) >= 1000:
        return f"{value:+,.0f}{unit}"

    return f"{value:+.1f}{unit}"


def flow_interpretation(score):
    if score < 30:
        return "상권 조건 대비 실제 소비성과가 상대적으로 낮은 편입니다."
    elif score < 70:
        return "상권 조건 대비 실제 소비성과가 중간 수준입니다."
    else:
        return "상권 조건 대비 실제 소비성과가 상대적으로 높은 편입니다."


# =========================================================
# 5. HERO
# =========================================================
st.title("🌊 FLOW")
st.subheader("사람은 많은데, 왜 소비로 이어지지 않을까?")

st.write(
    "유동인구만으로 상권을 판단하지 않습니다. "
    "FLOW는 상권 조건 대비 실제 소비성과와 시간대별 소비공백을 분석하고, "
    "구조적으로 유사하지만 소비성과가 더 높은 비교 상권을 찾아줍니다."
)

st.divider()


# =========================================================
# 6. SELECT
# =========================================================
st.header("내 상권 진단하기")

# area_code를 실제 내부 key로 사용
area_options = (
    area_df[["area_code", "area"]]
    .drop_duplicates(subset=["area_code"])
    .sort_values(["area", "area_code"])
    .reset_index(drop=True)
)

area_name_map = dict(
    zip(area_options["area_code"], area_options["area"])
)

col1, col2 = st.columns(2)

with col1:
    selected_code = st.selectbox(
        "상권 선택",
        options=area_options["area_code"].tolist(),
        format_func=lambda code: area_name_map.get(code, code)
    )

selected_area = area_name_map[selected_code]

# ---------------------------------------------------------
# 선택한 상권에 존재하는 업종을 CSV에서 자동으로 읽음
# → 향후 전체 업종 CSV로 교체하면 자동으로 업종 증가
# ---------------------------------------------------------
categories = (
    area_df.loc[
        area_df["area_code"] == selected_code,
        "category"
    ]
    .dropna()
    .drop_duplicates()
    .sort_values()
    .tolist()
)

with col2:
    selected_category = st.selectbox(
        "업종 선택",
        options=categories
    )

st.caption(
    "※ 현재 제공되는 업종은 최종 분석 데이터에 포함된 업종을 기준으로 합니다. "
    "향후 분석 데이터가 확대되면 선택 가능한 업종도 자동으로 확대됩니다."
)

run = st.button(
    "내 상권 진단하기",
    type="primary",
    use_container_width=True
)

if not run:
    st.stop()


# =========================================================
# 7. SELECT RESULT
# =========================================================
rows = area_df[
    (area_df["area_code"] == selected_code) &
    (area_df["category"] == selected_category)
]

if rows.empty:
    st.error("선택한 상권·업종의 분석 결과가 없습니다.")
    st.stop()

result = rows.iloc[0]

st.divider()
st.header(f"{selected_area} · {selected_category}")


# =========================================================
# 8. ANALYSIS AVAILABILITY
# =========================================================
if not is_available(result["analysis_available"]):

    st.warning(
        "최근 4개 분기의 활동 또는 관측 근거가 부족하여 분석할 수 없습니다."
    )

    if valid_text(result["analysis_status"]):
        st.caption(f"분석 상태: {result['analysis_status']}")

    st.stop()


# =========================================================
# 9. CORE VALUES
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
# 10. DIAGNOSIS
# =========================================================
st.subheader("상권 진단")

st.info(flow_interpretation(flow_score))

if dead_time == "뚜렷한 DEAD TIME 없음":
    st.write(
        "최근 4개 분기에서 반복적으로 확인되는 "
        "**뚜렷한 소비공백 시간대는 탐지되지 않았습니다.**"
    )
else:
    st.write(
        f"반복적으로 소비공백이 관측된 시간대는 "
        f"**{dead_time}**입니다."
    )


# =========================================================
# 11. METRICS
# =========================================================
m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        label="FLOW SCORE",
        value=f"{flow_score:.1f} / 100"
    )
    st.caption(
        "상권 조건 대비 실제 소비성과의 "
        "동일 업종 내 상대적 위치"
    )

with m2:
    st.metric(
        label="유동 수준",
        value=f"{traffic_score:.1f} / 100"
    )
    st.caption(
        "동일 업종 분석대상 상권 대비 "
        "유동인구의 상대적 백분위 수준"
    )

with m3:
    if dead_time == "뚜렷한 DEAD TIME 없음":
        st.metric(
            label="DEAD TIME",
            value="탐지 없음"
        )
        st.caption(
            "반복적으로 확인되는 뚜렷한 소비공백 없음"
        )
    else:
        st.metric(
            label="DEAD TIME",
            value=dead_time
        )
        st.caption(
            f"소비공백 상대점수 {dead_gap:.1f}"
        )

with st.expander("FLOW SCORE는 어떻게 읽나요?"):
    st.write(
        "FLOW SCORE는 절대적인 상권 평가점수가 아닙니다. "
        "유동인구와 상권 특성을 고려한 기대 소비수준 대비 실제 소비성과를 "
        "동일 업종 상권 안에서 상대적으로 비교한 0~100 지표입니다."
    )
    st.write(
        "점수가 높을수록 동일 업종의 다른 상권과 비교했을 때 "
        "주어진 상권 조건 대비 실제 소비가 상대적으로 활발함을 의미합니다."
    )


# =========================================================
# 12. TIME DATA
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
# 13. TIME CHART
# =========================================================
st.divider()
st.header("시간대별 소비 기회")

if selected_time.empty:

    st.warning("시간대별 분석 결과가 없습니다.")

else:

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=selected_time["time"].astype(str),
            y=selected_time["potential"],
            name="상대적 소비 기대수준"
        )
    )

    fig.add_trace(
        go.Bar(
            x=selected_time["time"].astype(str),
            y=selected_time["actual"],
            name="실제 소비수준"
        )
    )

    # DEAD TIME annotation만 추가
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
                text="DEAD TIME",
                showarrow=True,
                arrowhead=2,
                yshift=25
            )

    fig.update_layout(
        barmode="group",
        height=430,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="시간대",
        yaxis_title="소비수준",
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

    st.caption(
        "※ 상대적 소비 기대수준은 정확한 미래 매출 예측값이 아닙니다. "
        "유동인구 및 상권 특성을 고려한 통계적 비교 기준입니다."
    )


# =========================================================
# 14. DEAD TIME DETAIL
# =========================================================
st.subheader("DEAD TIME")

if dead_time == "뚜렷한 DEAD TIME 없음":

    st.success(
        "최근 4개 분기에서 반복적으로 확인되는 "
        "뚜렷한 DEAD TIME이 탐지되지 않았습니다."
    )

else:

    dead_rows = selected_time[
        selected_time["time"].astype(str) == dead_time
    ]

    st.warning(f"우선 확인 시간대: **{dead_time}**")

    if not dead_rows.empty:

        d = dead_rows.iloc[0]

        d1, d2, d3 = st.columns(3)

        with d1:
            st.metric(
                "상대적 소비 기대수준",
                f"{float(d['potential']):,.1f}"
            )

        with d2:
            st.metric(
                "실제 소비수준",
                f"{float(d['actual']):,.1f}"
            )

        with d3:
            st.metric(
                "Opportunity Gap",
                f"{float(d['gap']):,.1f}"
            )

        st.write(
            f"최근 4개 분기 중 **{int(d['repeat_dead'])}회** "
            "DEAD TIME 기준을 충족했습니다."
        )

    st.caption(
        "※ 00~06시는 DEAD TIME 판정에서 제외합니다. "
        "활동 근거가 충분한 시간대 중 동일 업종·분기·시간대 대비 "
        "소비공백이 상위 10%이고, 최근 4개 분기 중 최소 2회 반복된 "
        "경우를 DEAD TIME으로 탐지합니다."
    )


# =========================================================
# 15. BEST TWIN
# =========================================================
st.divider()
st.header("BEST TWIN")

has_twin = valid_text(twin_name)

if not has_twin:

    st.info(
        "현재 조건에서 성과가 더 높은 유사상권을 찾지 못했습니다."
    )

else:

    st.subheader(str(twin_name))

    if pd.notna(similarity):
        st.metric(
            "구조적 유사도",
            f"{similarity:.1f} / 100"
        )

    st.write(
        "동일 업종에서 상권 구조가 유사하면서 "
        "FLOW SCORE가 더 높은 비교 상권입니다."
    )

    if pd.notna(twin_conversion):

        t1, t2 = st.columns(2)

        with t1:
            st.metric(
                "우리 상권 FLOW SCORE",
                f"{flow_score:.1f}"
            )

        with t2:
            delta = twin_conversion - flow_score

            st.metric(
                "BEST TWIN FLOW SCORE",
                f"{twin_conversion:.1f}",
                delta=f"{delta:+.1f}"
            )

    with st.expander("구조적 유사도는 무엇인가요?"):
        st.write(
            "동일 업종의 16개 상권 특성을 백분위로 변환한 뒤 "
            "두 상권의 평균 절대 백분위 차이를 이용해 계산한 "
            "구조적 비교 지표입니다."
        )
        st.write(
            f"따라서 구조적 유사도 {similarity:.1f}은 "
            f"두 상권의 실제 특성이 {similarity:.1f}% 동일하다는 "
            "의미가 아닙니다."
        )


# =========================================================
# 16. TWIN DIFFERENCE
# =========================================================
if has_twin:

    st.subheader("TWIN과 무엇이 다를까요?")

    # twin_difference 파일에는 area_code가 없음
    twin_rows = twin_df[
        (twin_df["area"] == selected_area) &
        (twin_df["category"] == selected_category) &
        (twin_df["twin_name"] == twin_name)
    ].copy()

    twin_rows = twin_rows.sort_values("rank").head(3)

    if twin_rows.empty:

        st.info("BEST TWIN과의 특성 비교 결과가 없습니다.")

    else:

        compare_cols = st.columns(3)

        for i, (_, row) in enumerate(twin_rows.iterrows()):

            difference = float(row["difference"])
            display_difference = format_difference(
                difference,
                row["unit"]
            )

            with compare_cols[i]:

                st.markdown(
                    f"**TOP {int(row['rank'])} · {row['feature']}**"
                )

                st.metric(
                    label="TWIN 대비 차이",
                    value=display_difference
                )

                if difference > 0:
                    st.caption(
                        "우리 상권이 BEST TWIN보다 높은 특성"
                    )
                elif difference < 0:
                    st.caption(
                        "우리 상권이 BEST TWIN보다 낮은 특성"
                    )
                else:
                    st.caption(
                        "두 상권이 유사한 특성"
                    )

        st.caption(
            "※ 위 항목은 BEST TWIN과 비교했을 때 표준화된 차이가 큰 "
            "상권 특성 TOP3입니다. 소비성과 차이의 인과적 원인을 "
            "의미하지 않습니다."
        )


# =========================================================
# 17. ACTION POINT
# =========================================================
st.divider()
st.header("ACTION POINT")

# 1
if dead_time == "뚜렷한 DEAD TIME 없음":
    st.markdown("#### ① 전체 시간대의 소비 흐름 점검")
    st.write(
        "반복적으로 확인되는 뚜렷한 DEAD TIME은 없습니다. "
        "특정 시간대 하나보다 전체 시간대의 소비 흐름을 "
        "지속적으로 확인하는 것이 우선입니다."
    )
else:
    st.markdown(f"#### ① {dead_time} 시간대 우선 점검")
    st.write(
        f"최근 4개 분기에서 반복적으로 소비공백이 확인된 "
        f"**{dead_time}** 시간대를 우선적으로 점검할 수 있습니다."
    )

# 2
if has_twin and not twin_rows.empty:

    top_feature = twin_rows.iloc[0]["feature"]

    st.markdown(f"#### ② {top_feature} 차이 확인")
    st.write(
        f"BEST TWIN과 비교했을 때 상대적으로 차이가 큰 "
        f"**{top_feature}**을 우선 확인해볼 수 있습니다. "
        "이는 원인으로 단정하는 것이 아니라 추가 점검이 필요한 "
        "상권 특성을 의미합니다."
    )

else:

    st.markdown("#### ② 상권 구조 점검")
    st.write(
        "유동인구뿐 아니라 상주·직장인구, 시간대별 유동구조, "
        "점포구성 등 상권 특성을 함께 확인해볼 수 있습니다."
    )

# 3
if has_twin:

    st.markdown(f"#### ③ {twin_name}과 비교")
    st.write(
        f"구조적으로 유사하면서 소비성과가 더 높은 **{twin_name}**과 "
        "시간대별 유동 및 상권 특성의 차이를 비교해볼 수 있습니다."
    )

else:

    st.markdown("#### ③ 동일 업종 내 상대적 위치 확인")
    st.write(
        "현재 조건에서는 더 높은 성과의 유사상권이 탐지되지 않았습니다. "
        "동일 업종 내 FLOW SCORE와 유동 수준을 중심으로 "
        "현재 상권의 상대적 위치를 확인할 수 있습니다."
    )


# =========================================================
# 18. FOOTER
# =========================================================
st.divider()

st.caption(
    "FLOW는 서울시 상권 데이터를 기반으로 한 데이터 분석 프로토타입입니다. "
    "FLOW SCORE와 BEST TWIN은 동일 업종 내 상대적 비교를 위한 지표이며, "
    "개별 매장의 미래 매출을 예측하거나 특정 상권 특성이 소비성과의 "
    "인과적 원인임을 의미하지 않습니다."
)
