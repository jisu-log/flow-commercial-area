import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =========================================================
# PAGE SETTING
# =========================================================
st.set_page_config(
    page_title="FLOW",
    page_icon="🌊",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    area_df = pd.read_csv("area_summary.csv")
    time_df = pd.read_csv("time_result.csv")
    twin_df = pd.read_csv("twin_difference.csv")

    # 상권코드는 문자열로 통일
    area_df["area_code"] = area_df["area_code"].astype(str)
    time_df["area_code"] = time_df["area_code"].astype(str)

    return area_df, time_df, twin_df


try:
    area_df, time_df, twin_df = load_data()
except Exception as e:
    st.error("데이터 파일을 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()


# =========================================================
# CSS
# =========================================================
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

/* HERO */

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

/* TITLES */

.section-title {
    font-size: 27px;
    font-weight: 800;
    margin-top: 42px;
    margin-bottom: 16px;
    color: #18324a;
}

/* CARDS */

.card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.05);
    border: 1px solid #e9eef3;
    min-height: 155px;
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

/* DIAGNOSIS */

.diagnosis-box {
    background: white;
    border: 1px solid #e5ebf1;
    border-radius: 18px;
    padding: 22px 24px;
    margin-bottom: 18px;
}

.warning {
    background: #fff7e8;
    border-left: 5px solid #e7a33e;
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 14px;
}

/* DEAD TIME */

.dead-box {
    background: #fff7e8;
    border: 1px solid #f1d19b;
    border-radius: 18px;
    padding: 24px;
    margin-top: 10px;
}

.no-dead-box {
    background: #f1f7f4;
    border: 1px solid #d8e8df;
    border-radius: 18px;
    padding: 24px;
    margin-top: 10px;
}

/* TWIN */

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

/* WHY */

.why-card {
    background: white;
    border: 1px solid #e7ecf1;
    border-radius: 16px;
    padding: 20px;
    min-height: 180px;
}

/* INFO */

.info-box {
    background: #f4f7fa;
    border: 1px solid #e1e8ef;
    border-radius: 14px;
    padding: 17px 20px;
    font-size: 13px;
    line-height: 1.75;
    color: #657381;
    margin-top: 14px;
}

/* BUTTON */

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


# =========================================================
# HERO
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">FLOW</div>
        <div class="hero-sub">사람은 많은데, 왜 소비로 이어지지 않을까?</div>
        <div class="hero-desc">
            단순 유동인구가 아닌 실제 소비 연결성을 분석합니다.<br>
            시간대별 소비공백과 유사상권 비교를 통해<br>
            서울 골목상권의 숨은 소비 기회를 찾아보세요.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SELECT AREA
# =========================================================
st.markdown(
    '<div class="section-title">내 상권 진단하기</div>',
    unsafe_allow_html=True
)

# 상권코드 기준으로 상권 목록 생성
area_options = (
    area_df[["area_code", "area"]]
    .drop_duplicates()
    .sort_values("area")
    .reset_index(drop=True)
)

# 화면에는 상권명 표시
area_labels = {
    row["area_code"]: row["area"]
    for _, row in area_options.iterrows()
}

c1, c2 = st.columns(2)

with c1:
    selected_code = st.selectbox(
        "상권 선택",
        options=area_options["area_code"].tolist(),
        format_func=lambda x: area_labels.get(x, x)
    )

selected_area = area_labels[selected_code]

# 선택한 상권에 실제 존재하는 업종만 표시
available_categories = (
    area_df.loc[
        area_df["area_code"] == selected_code,
        "category"
    ]
    .dropna()
    .unique()
    .tolist()
)

with c2:
    selected_category = st.selectbox(
        "업종 선택",
        options=available_categories
    )

analyze = st.button("내 상권 진단하기 →")


# =========================================================
# RESULT
# =========================================================
if analyze:

    # -----------------------------------------------------
    # AREA SUMMARY
    # -----------------------------------------------------
    selected_rows = area_df[
        (area_df["area_code"] == selected_code) &
        (area_df["category"] == selected_category)
    ]

    if selected_rows.empty:
        st.error("선택한 상권·업종의 분석 결과를 찾을 수 없습니다.")
        st.stop()

    result = selected_rows.iloc[0]

    # -----------------------------------------------------
    # ANALYSIS AVAILABLE CHECK
    # -----------------------------------------------------
    if not bool(result["analysis_available"]):

        st.markdown(
            f'<div class="section-title">'
            f'{selected_area} · {selected_category}'
            f'</div>',
            unsafe_allow_html=True
        )

        st.warning(
            "최근 4개 분기의 활동 또는 관측 근거가 부족하여 "
            "분석할 수 없습니다."
        )

        if pd.notna(result.get("analysis_status")):
            st.caption(f"분석 상태: {result['analysis_status']}")

        st.stop()

    # -----------------------------------------------------
    # VALUES
    # -----------------------------------------------------
    flow_score = float(result["flow_score"])
    traffic_score = float(result["traffic_score"])

    dead_time = result["dead_time"]

    if pd.notna(result["dead_gap"]):
        dead_gap = float(result["dead_gap"])
    else:
        dead_gap = 0

    twin_name = result["twin_name"]
    similarity = result["similarity"]
    twin_conversion = result["twin_conversion"]

    # -----------------------------------------------------
    # TIME DATA
    # -----------------------------------------------------
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

    selected_time["time"] = pd.Categorical(
        selected_time["time"],
        categories=time_order,
        ordered=True
    )

    selected_time = selected_time.sort_values("time")

    # -----------------------------------------------------
    # RESULT TITLE
    # -----------------------------------------------------
    st.markdown(
        f'<div class="section-title">'
        f'{selected_area} · {selected_category} 분석 결과'
        f'</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # DIAGNOSIS
    # -----------------------------------------------------
    if flow_score < 30:
        diagnosis = "상권 조건 대비 실제 소비성과가 낮은 편입니다."
    elif flow_score < 70:
        diagnosis = "상권 조건 대비 실제 소비성과가 중간 수준입니다."
    else:
        diagnosis = "상권 조건 대비 실제 소비성과가 높은 편입니다."

    if dead_time == "뚜렷한 DEAD TIME 없음":
        dead_sentence = "반복적으로 확인되는 뚜렷한 소비공백 시간은 탐지되지 않았습니다."
    else:
        dead_sentence = f"반복적으로 소비공백이 관측된 시간대는 {dead_time}입니다."

    st.markdown(
        f"""
        <div class="diagnosis-box">
            <div style="
                font-size:14px;
                color:#71808f;
                font-weight:700;
                margin-bottom:6px;">
                상권 진단
            </div>

            <div style="
                font-size:24px;
                font-weight:800;
                color:#18324a;">
                {diagnosis}
            </div>

            <div style="
                font-size:14px;
                color:#5d6a76;
                margin-top:8px;">
                {dead_sentence}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # SUMMARY CARDS
    # -----------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="card">
                <div class="label">FLOW SCORE</div>
                <div class="big">{flow_score:.1f}</div>
                <div class="subtext">
                    상권 조건 대비 실제 소비성과의<br>
                    동일 업종 내 상대적 위치
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="card">
                <div class="label">유동 수준</div>
                <div class="big">{traffic_score:.1f}</div>
                <div class="subtext">
                    동일 업종 분석대상 상권 대비<br>
                    유동인구의 상대적 백분위 수준
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:

        if dead_time != "뚜렷한 DEAD TIME 없음":
            third_value = f"{dead_gap:.1f}"
            third_desc = f"{dead_time}의 반복 소비공백 규모"
        else:
            third_value = "—"
            third_desc = "뚜렷한 DEAD TIME이 탐지되지 않음"

        st.markdown(
            f"""
            <div class="card">
                <div class="label">DEAD TIME GAP</div>
                <div class="big">{third_value}</div>
                <div class="subtext">
                    {third_desc}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="info-box">
            <b>FLOW SCORE는 절대적인 상권 점수가 아닙니다.</b><br>
            유동인구와 상권 특성을 고려한 기대 소비수준 대비 실제 소비성과를
            동일 업종 상권 내에서 상대적으로 비교한 지표입니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # TIME CHART
    # =====================================================
    st.markdown(
        '<div class="section-title">시간대별 소비 기회 진단</div>',
        unsafe_allow_html=True
    )

    if selected_time.empty:

        st.info("시간대별 분석 결과가 없습니다.")

    else:

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=selected_time["time"].astype(str),
                y=selected_time["potential"],
                name="상대적 소비 기대수준",
                marker_color="#A8C7E8"
            )
        )

        fig.add_trace(
            go.Bar(
                x=selected_time["time"].astype(str),
                y=selected_time["actual"],
                name="실제 소비수준",
                marker_color="#245B91"
            )
        )

        # DEAD TIME 강조
        if dead_time != "뚜렷한 DEAD TIME 없음":

            dead_row = selected_time[
                selected_time["time"].astype(str) == str(dead_time)
            ]

            if not dead_row.empty:

                dead_index = time_order.index(str(dead_time))

                fig.add_vrect(
                    x0=dead_index - 0.45,
                    x1=dead_index + 0.45,
                    fillcolor="rgba(255,177,85,0.15)",
                    line_width=0,
                    layer="below"
                )

                max_y = max(
                    selected_time["potential"].max(),
                    selected_time["actual"].max()
                )

                fig.add_annotation(
                    x=str(dead_time),
                    y=max_y * 1.05,
                    text="DEAD TIME",
                    showarrow=False,
                    font=dict(
                        size=12,
                        color="#a55c00"
                    ),
                    bgcolor="rgba(255,247,232,0.95)",
                    bordercolor="#efcf99",
                    borderpad=5
                )

        fig.update_layout(
            barmode="group",
            height=440,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(
                gridcolor="#e9eef3",
                title="소비수준"
            ),
            xaxis=dict(
                showgrid=False,
                title="시간대"
            ),
            bargap=0.28
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        st.caption(
            "※ 상대적 소비 기대수준은 미래 매출 예측값이 아닙니다. "
            "유동인구 및 상권 특성을 고려한 통계적 비교 기준입니다."
        )

    # =====================================================
    # DEAD TIME
    # =====================================================
    st.markdown(
        '<div class="section-title">DEAD TIME</div>',
        unsafe_allow_html=True
    )

    if dead_time == "뚜렷한 DEAD TIME 없음":

        st.markdown(
            """
            <div class="no-dead-box">
                <div class="label">분석 결과</div>

                <div style="
                    font-size:25px;
                    font-weight:800;
                    color:#365d4b;
                    margin-bottom:8px;">
                    뚜렷한 DEAD TIME 없음
                </div>

                <div style="
                    font-size:15px;
                    line-height:1.7;">
                    최근 4개 분기에서 반복적으로 확인되는
                    뚜렷한 소비공백 시간대가 탐지되지 않았습니다.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        dead_time_row = selected_time[
            selected_time["time"].astype(str) == str(dead_time)
        ]

        if not dead_time_row.empty:

            d = dead_time_row.iloc[0]

            dead_potential = float(d["potential"])
            dead_actual = float(d["actual"])
            repeat_dead = int(d["repeat_dead"])

            st.markdown(
                f"""
                <div class="dead-box">

                    <div class="label">
                        반복적으로 관측된 소비공백 시간
                    </div>

                    <div style="
                        font-size:34px;
                        font-weight:800;
                        color:#a55c00;
                        margin-bottom:8px;">
                        {dead_time}
                    </div>

                    <div style="
                        font-size:16px;
                        line-height:1.8;
                        margin-bottom:14px;">

                        상대적 소비 기대수준
                        <b>{dead_potential:,.1f}</b>

                        &nbsp; / &nbsp;

                        실제 소비수준
                        <b>{dead_actual:,.1f}</b>

                        <br>

                        소비공백
                        <b>{dead_gap:,.1f}</b>

                        &nbsp;·&nbsp;

                        최근 4개 분기 중
                        <b>{repeat_dead}회</b> DEAD TIME 기준 충족

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        st.caption(
            "※ DEAD TIME은 00~06시를 제외하고, 활동 근거가 충분한 시간대 중 "
            "동일 업종·분기·시간대 대비 소비공백이 상위 10%이며 "
            "최근 4개 분기 중 최소 2회 반복된 경우를 기준으로 탐지합니다."
        )

    # =====================================================
    # BEST TWIN
    # =====================================================
    st.markdown(
        '<div class="section-title">BEST TWIN</div>',
        unsafe_allow_html=True
    )

    # TWIN 없는 경우
    if pd.isna(twin_name) or str(twin_name).strip() == "":

        st.info(
            "현재 조건에서 성과가 더 높은 유사상권을 찾지 못했습니다."
        )

    else:

        st.markdown(
            f"""
            <div class="twin-box">

                <div class="label">
                    구조적으로 유사하면서 FLOW SCORE가 더 높은 비교 상권
                </div>

                <div style="
                    font-size:31px;
                    font-weight:800;
                    color:#173c67;
                    margin-bottom:7px;">
                    {twin_name}
                </div>

                <div style="font-size:16px;">
                    구조적 유사도
                    <b>{float(similarity):.1f}</b>
                </div>

                <div style="
                    margin-top:14px;
                    line-height:1.7;
                    font-size:15px;">
                    동일 업종 내에서 상권 구조가 유사하면서
                    상대적 소비성과가 더 높은 상권입니다.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        twin1, twin2 = st.columns(2)

        with twin1:
            st.metric(
                "우리 상권 FLOW SCORE",
                f"{flow_score:.1f}"
            )

        with twin2:

            twin_difference_score = (
                float(twin_conversion) - flow_score
            )

            st.metric(
                "BEST TWIN FLOW SCORE",
                f"{float(twin_conversion):.1f}",
                delta=f"+{twin_difference_score:.1f}"
            )

        st.markdown(
            f"""
            <div class="info-box">
                <b>구조적 유사도란?</b><br>
                동일 업종의 16개 상권 특성을 백분위로 변환한 뒤,
                두 상권의 평균 절대 백분위 차이를 이용해 계산한
                구조적 비교 지표입니다.
                실제 특성이 {float(similarity):.1f}% 동일하다는 의미는 아닙니다.
            </div>
            """,
            unsafe_allow_html=True
        )

        # =================================================
        # TWIN DIFFERENCE TOP 3
        # =================================================
        st.markdown(
            '<div class="section-title">TWIN과 무엇이 다를까요?</div>',
            unsafe_allow_html=True
        )

        # twin_difference에는 area_code가 없으므로
        # area + category 사용
        twin_rows = twin_df[
            (twin_df["area"] == selected_area) &
            (twin_df["category"] == selected_category)
        ].copy()

        twin_rows = twin_rows.sort_values("rank").head(3)

        if twin_rows.empty:

            st.info("TWIN 특성 비교 결과가 없습니다.")

        else:

            why_cols = st.columns(len(twin_rows))

            for i, (_, row) in enumerate(twin_rows.iterrows()):

                feature = row["feature"]
                difference = float(row["difference"])
                unit = row["unit"]

                if difference > 0:
                    direction = "높음"
                    sign = "+"
                elif difference < 0:
                    direction = "낮음"
                    sign = ""
                else:
                    direction = "유사"
                    sign = ""

                if abs(difference) >= 1000:
                    diff_text = f"{difference:,.0f}"
                else:
                    diff_text = f"{difference:.1f}"

                with why_cols[i]:

                    st.markdown(
                        f"""
                        <div class="why-card">

                            <div class="label">
                                TWIN 대비 차이 · TOP {int(row['rank'])}
                            </div>

                            <div style="
                                font-size:20px;
                                font-weight:800;
                                color:#183f6c;
                                margin-bottom:12px;">
                                {feature}
                            </div>

                            <div style="
                                font-size:27px;
                                font-weight:800;
                                color:#5c6f82;">
                                {sign}{diff_text}{unit}
                            </div>

                            <div style="
                                margin-top:9px;
                                font-size:13px;
                                color:#7c8996;">
                                우리 상권이 TWIN보다 {direction}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.caption(
                "※ 위 항목은 BEST TWIN과 비교했을 때 표준화된 차이가 큰 "
                "상권 특성 TOP3입니다. 소비성과 차이의 인과적 원인을 의미하지 않습니다."
            )

        # =================================================
        # ACTION POINT
        # =================================================
        st.markdown(
            '<div class="section-title">ACTION POINT</div>',
            unsafe_allow_html=True
        )

        action_cols = st.columns(3)

        # ACTION 1
        with action_cols[0]:

            if dead_time == "뚜렷한 DEAD TIME 없음":

                action1_title = "시간대별 흐름 유지 점검"
                action1_text = (
                    "반복적으로 확인되는 뚜렷한 DEAD TIME은 없습니다. "
                    "특정 시간대 하나보다 전체 시간대의 소비 흐름을 "
                    "지속적으로 확인해보세요."
                )

            else:

                action1_title = f"{dead_time} 우선 점검"
                action1_text = (
                    f"최근 4개 분기에서 반복적으로 소비공백이 관측된 "
                    f"{dead_time} 시간대를 우선적으로 확인해보세요."
                )

            st.markdown(
                f"""
                <div class="why-card">

                    <div class="label">
                        PRIORITY 01
                    </div>

                    <div style="
                        font-size:20px;
                        font-weight:800;
                        color:#183f6c;
                        margin-bottom:12px;">
                        {action1_title}
                    </div>

                    <div style="
                        font-size:14px;
                        line-height:1.8;
                        color:#5d6a76;">
                        {action1_text}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        # ACTION 2
        with action_cols[1]:

            if not twin_rows.empty:

                first_row = twin_rows.iloc[0]
                first_feature = first_row["feature"]

                action2_title = f"{first_feature} 차이 확인"

                action2_text = (
                    f"BEST TWIN과 가장 큰 구조적 차이 중 하나는 "
                    f"'{first_feature}'입니다. "
                    f"소비성과와의 관련성을 추가로 점검할 수 있습니다."
                )

            else:

                action2_title = "상권 구조 점검"

                action2_text = (
                    "유동·상주·직장인구와 시간대별 유동구조 등 "
                    "상권 특성을 함께 점검해보세요."
                )

            st.markdown(
                f"""
                <div class="why-card">

                    <div class="label">
                        PRIORITY 02
                    </div>

                    <div style="
                        font-size:20px;
                        font-weight:800;
                        color:#183f6c;
                        margin-bottom:12px;">
                        {action2_title}
                    </div>

                    <div style="
                        font-size:14px;
                        line-height:1.8;
                        color:#5d6a76;">
                        {action2_text}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        # ACTION 3
        with action_cols[2]:

            action3_title = f"{twin_name} 비교"

            action3_text = (
                f"구조적 유사도 {float(similarity):.1f}인 "
                f"{twin_name}과 시간대별 유동 및 상권 특성을 비교해 "
                f"차이가 발생하는 지점을 확인해보세요."
            )

            st.markdown(
                f"""
                <div class="why-card">

                    <div class="label">
                        PRIORITY 03
                    </div>

                    <div style="
                        font-size:20px;
                        font-weight:800;
                        color:#183f6c;
                        margin-bottom:12px;">
                        {action3_title}
                    </div>

                    <div style="
                        font-size:14px;
                        line-height:1.8;
                        color:#5d6a76;">
                        {action3_text}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="info-box" style="margin-top:45px;">
        <b>분석 안내</b><br>
        FLOW는 서울시 상권분석서비스 데이터를 기반으로
        유동인구와 실제 소비의 관계를 비교하는 상권 진단 프로토타입입니다.
        FLOW SCORE와 BEST TWIN은 동일 업종 내 상대적 비교를 위한 지표이며,
        개별 매장의 미래 매출을 예측하거나 특정 특성이 매출의 원인임을
        의미하지 않습니다.
    </div>
    """,
    unsafe_allow_html=True
)
