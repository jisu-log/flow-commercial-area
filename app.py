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
# DEMO DATA
# -----------------------------
demo_data = {
    ("광흥창역 6번", "커피·음료"): {
        "flow_score": 43,
        "traffic_score": 87,
        "consumer_score": 43,
        "twin": "불광역 8번",
        "similarity": 91,
        "twin_conversion": 68,
        "why": [
            ("직장인구", -24, "%"),
            ("음식업 다양성", -17, "%"),
            ("2030 유동비중", -11, "%p")
        ],
        "times": ["06~11", "11~14", "14~17", "17~21", "21~24"],
        "potential": [42, 68, 82, 71, 46],
        "actual": [39, 63, 41, 62, 43]
    },

    ("길음역 7번", "커피·음료"): {
        "flow_score": 57,
        "traffic_score": 79,
        "consumer_score": 57,
        "twin": "노원역 9번",
        "similarity": 88,
        "twin_conversion": 66,
        "why": [
            ("상주/직장 비율", -18, "%"),
            ("카페 밀도", 13, "%"),
            ("주말 유동비중", -9, "%p")
        ],
        "times": ["06~11", "11~14", "14~17", "17~21", "21~24"],
        "potential": [38, 66, 70, 81, 51],
        "actual": [35, 61, 59, 49, 46]
    },

    ("제기동역 1번", "한식"): {
        "flow_score": 62,
        "traffic_score": 74,
        "consumer_score": 62,
        "twin": "청량리역 인근",
        "similarity": 86,
        "twin_conversion": 64,
        "why": [
            ("직장인구", -15, "%"),
            ("음식점 다양성", -12, "%"),
            ("2030 유동비중", -8, "%p")
        ],
        "times": ["06~11", "11~14", "14~17", "17~21", "21~24"],
        "potential": [37, 73, 65, 71, 48],
        "actual": [34, 69, 57, 52, 44]
    }
}

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

st.markdown('<div class="section-title">1. 내 상권 찾아보기</div>', unsafe_allow_html=True)
st.caption("현재 DEMO에서는 준비된 상권·업종 조합만 선택할 수 있습니다.")

available_keys = list(demo_data.keys())
area_options = list(dict.fromkeys(k[0] for k in available_keys))
area = st.selectbox("상권 선택", area_options)

category_options = [k[1] for k in available_keys if k[0] == area]
category = st.selectbox("업종 선택", category_options)

with st.expander("ⓘ 내가 어느 상권인지 잘 모르겠어요"):
    st.write(
        "FLOW의 상권명은 분석 데이터의 상권 단위를 기준으로 표시합니다. "
        "최종 버전에서는 사용자가 익숙한 역·동네명과 분석 상권명을 함께 보여주는 방식으로 연결할 수 있습니다."
    )

if st.button("FLOW 진단하기 →", type="primary"):
    st.session_state.selected_key = (area, category)
    st.session_state.show_result = True

if st.session_state.show_result and st.session_state.selected_key in demo_data:
    area, category = st.session_state.selected_key
    data = demo_data[(area, category)]

    potential = np.array(data["potential"], dtype=float)
    actual = np.array(data["actual"], dtype=float)
    gap = potential - actual
    dead_index = int(np.argmax(gap))
    dead_time = data["times"][dead_index]
    dead_gap = float(gap[dead_index])
    twin_diff = float(data["twin_conversion"] - actual[dead_index])

    if data["consumer_score"] < 50:
        flow_type = "전환 개선형"
        hero_line = "사람은 있는데, 소비로 충분히 연결되지 않고 있습니다."
        hero_sub = "새로운 유동을 더 만드는 것보다 현재 존재하는 유동의 소비 전환을 먼저 살펴볼 상권입니다."
    elif data["consumer_score"] < 70:
        flow_type = "균형 점검형"
        hero_line = "유동과 소비 연결은 보통 수준이지만, 놓치는 시간대가 있습니다."
        hero_sub = "전체 평균보다 시간대별 소비공백을 중심으로 개선 기회를 확인해볼 상권입니다."
    else:
        flow_type = "연결 우수형"
        hero_line = "유동이 비교적 잘 소비로 연결되고 있습니다."
        hero_sub = "전체 수준보다 시간대별 편차와 비교상권의 강점을 중심으로 추가 기회를 확인해볼 수 있습니다."

    # -----------------------------
    # 2. HERO RESULT
    # -----------------------------
    st.markdown(f'<div class="section-title">2. {area} · {category}</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="diagnosis-box">
            <div class="label">FLOW DIAGNOSIS · {flow_type}</div>
            <div style="font-size:29px;font-weight:850;color:#173c67;line-height:1.35;margin:8px 0 8px;">
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
                <div class="label">소비 연결력 · FLOW SCORE</div>
                <div class="big">{data["flow_score"]}</div>
                <div class="subtext">상권 여건 대비 유동이 실제 소비로 연결되는 상대적 수준</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="card">
                <div class="label">유동 수준</div>
                <div class="big">{data["traffic_score"]}</div>
                <div class="subtext">같은 업종 비교 상권 가운데 사람 흐름의 상대적 수준</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.expander("ⓘ FLOW SCORE가 무엇인가요?"):
        st.write(
            "FLOW SCORE는 매출액이나 미래 매출 예측값이 아닙니다. "
            "상권 여건을 고려했을 때 유동이 실제 소비로 얼마나 연결되는지를 비교하기 위한 상대적 진단 지표입니다."
        )

    # -----------------------------
    # 3. TIME OPPORTUNITY
    # -----------------------------
    st.markdown('<div class="section-title">3. 가장 먼저 볼 시간은 언제일까요?</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="action-box">
            <div class="label">가장 큰 소비공백</div>
            <div style="font-size:32px;font-weight:850;color:#a55c00;margin:5px 0;">{dead_time}</div>
            <div style="font-size:16px;line-height:1.7;">
                상권 여건상 기대 수준은 <b>{potential[dead_index]:.0f}</b>, 실제 소비 수준은
                <b>{actual[dead_index]:.0f}</b>로 현재 DEMO 기준 <b>{dead_gap:.0f}점</b> 차이가 납니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    time_df = pd.DataFrame({
        "시간대": data["times"],
        "상권 여건상 기대 소비": data["potential"],
        "실제 소비": data["actual"]
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=time_df["시간대"], y=time_df["상권 여건상 기대 소비"],
        name="상권 여건상 기대 소비", marker_color="#A8C7E8"
    ))
    fig.add_trace(go.Bar(
        x=time_df["시간대"], y=time_df["실제 소비"],
        name="실제 소비", marker_color="#245B91"
    ))
    fig.update_layout(
        barmode="group", height=400,
        margin=dict(l=15, r=15, t=50, b=15),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(gridcolor="#e9eef3", title="상대 점수"),
        xaxis=dict(showgrid=False, title=""),
        bargap=0.28
    )
    fig.add_vrect(
        x0=dead_index - 0.45, x1=dead_index + 0.45,
        fillcolor="rgba(255,177,85,0.14)", line_width=0, layer="below"
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.info(
        f"**해석:** {dead_time}은 '이 시간에 반드시 매출이 오른다'는 뜻이 아니라, "
        "현재 상권에서 **소비 연결이 가장 아쉬워 우선 확인할 가치가 있는 시간대**입니다."
    )

    with st.expander("ⓘ 기대 소비와 소비공백은 무슨 뜻인가요?"):
        st.write(
            "기대 소비는 정확한 미래 매출 예측값이 아니라 상권 조건을 고려한 상대적 소비 기대수준입니다. "
            "소비공백은 이 기대수준과 실제 소비 사이의 차이를 뜻합니다."
        )

    # -----------------------------
    # 4. TWIN
    # -----------------------------
    st.markdown('<div class="section-title">4. 비슷한데 더 잘되는 상권은 어디일까요?</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="twin-box">
            <div class="label">BEST TWIN · 구조적으로 가장 유사한 비교상권</div>
            <div style="font-size:31px;font-weight:850;color:#173c67;margin:7px 0;">{data["twin"]}</div>
            <div style="font-size:16px;">상권 구조 유사도 <b>{data["similarity"]}%</b></div>
            <div class="subtext">
                우리 상권과 구조가 비슷한 후보 가운데 소비 연결 성과가 더 높은 곳입니다.
                '원래 이런 상권이라 어쩔 수 없는가?'를 비교해보기 위한 기준입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(
            f"""
            <div class="card">
                <div class="label">우리 상권 · {dead_time}</div>
                <div class="big">{actual[dead_index]:.0f}</div>
                <div class="subtext">소비 연결 수준</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with t2:
        st.markdown(
            f"""
            <div class="card">
                <div class="label">BEST TWIN · 비교 수준</div>
                <div class="big">{data["twin_conversion"]}</div>
                <div class="subtext">우리 상권보다 <b>+{twin_diff:.0f}점</b></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("#### 두 상권에서 크게 다른 특성")
    why_cols = st.columns(3)
    for i, (feature, diff, unit) in enumerate(data["why"]):
        with why_cols[i]:
            direction = "낮음" if diff < 0 else "높음"
            st.markdown(
                f"""
                <div class="card">
                    <div class="label">차이 TOP {i+1}</div>
                    <div style="font-size:18px;font-weight:800;color:#183f6c;margin-bottom:8px;">{feature}</div>
                    <div style="font-size:26px;font-weight:800;color:#5c6f82;">{abs(diff)}{unit}</div>
                    <div class="subtext">우리 상권이 더 {direction}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "※ 위 차이는 비교 포인트이며 소비성과 차이의 직접적인 원인이라는 의미는 아닙니다."
    )

    with st.expander("ⓘ BEST TWIN과 유사도는 어떻게 해석하나요?"):
        st.write(
            "유사도는 실제 특성의 일치율이 아니라 여러 상권 특성의 상대적 차이를 바탕으로 만든 구조적 유사도입니다. "
            "BEST TWIN은 인과관계를 증명하는 대상이 아니라, 비슷한 조건에서 다른 결과가 나타나는 지점을 찾기 위한 비교 기준입니다."
        )

    # -----------------------------
    # 5. STORE DIAGNOSIS
    # -----------------------------
    st.markdown('<div class="section-title">5. 우리 가게는 어디에서 막히고 있을까요?</div>', unsafe_allow_html=True)
    st.write(
        "여기부터는 **상권 데이터 + 사장님의 매장 상황**을 함께 봅니다. "
        "현재 데이터로 직접 비교할 수 있는 것은 시간대이며, 나머지 문항은 문제 지점을 좁히기 위한 점포 자가진단입니다."
    )

    compare_store = st.checkbox("내 가게 맞춤진단 시작하기", key="compare_store")

    if compare_store:
        store_weak = st.selectbox(
            "① 평소 주문이나 매출이 가장 약한 시간대는 언제인가요?",
            ["선택해주세요"] + list(data["times"]),
            key="store_weak_time"
        )

        store_stage = st.radio(
            "② 그 시간대에 가장 가깝다고 느끼는 상황은 무엇인가요?",
            [
                "잘 모르겠어요",
                "주변에 사람 자체가 적어요",
                "사람은 지나가지만 가게로 잘 들어오지 않아요",
                "손님은 들어오지만 주문·구매가 기대보다 적어요"
            ],
            key="store_stage",
            horizontal=False
        )

        store_channel = st.radio(
            "③ 평소 매출이 가장 많이 발생하는 방식은 무엇인가요?",
            ["매장 중심", "포장 중심", "배달 중심", "혼합형", "잘 모르겠어요"],
            key="store_channel",
            horizontal=True
        )

        if store_weak != "선택해주세요":
            same_time = store_weak == dead_time

            st.markdown("### 맞춤진단 결과")

            if same_time:
                result_title = "상권과 내 가게의 취약 시간이 겹칩니다."
                result_desc = (
                    f"상권에서도 **{dead_time}**의 소비공백이 가장 크고, "
                    f"내 가게도 같은 시간대가 가장 약하다고 응답했습니다. "
                    "따라서 점포 문제만 보기 전에 상권 공통 패턴과 점포 운영을 함께 확인할 가치가 있습니다."
                )
            else:
                result_title = "상권과 내 가게의 취약 시간이 다릅니다."
                result_desc = (
                    f"상권은 **{dead_time}**이 가장 취약하지만 내 가게는 **{store_weak}**이 가장 약합니다. "
                    "상권 평균만으로 설명하기보다 점포 개별 운영 요인을 우선 확인할 필요가 있습니다."
                )

            st.markdown(
                f"""
                <div class="diagnosis-box">
                    <div class="label">MY STORE × FLOW</div>
                    <div style="font-size:24px;font-weight:850;color:#173c67;margin:7px 0;">{result_title}</div>
                    <div class="subtext">{result_desc}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("#### 지금 가장 먼저 확인할 지점")

            if store_stage == "주변에 사람 자체가 적어요":
                if same_time:
                    action_title = "실제 매장 앞 유동부터 확인"
                    action_text = (
                        "상권 전체의 소비공백과 내 매장의 취약시간이 겹칩니다. "
                        "다만 '사람 자체가 적다'는 체감이 맞는지는 매장 앞 시간대별 통행량·입점 수를 먼저 확인해야 합니다."
                    )
                    check_items = "시간대별 매장 앞 통행량 · 입점 수 · 영업시간"
                else:
                    action_title = "상권보다 매장 위치·노출 조건 확인"
                    action_text = (
                        "상권 전체의 취약시간과 내 매장의 취약시간이 다릅니다. "
                        "따라서 상권 전체 유동보다 매장 앞 실제 유동과 위치·노출 차이를 먼저 점검하는 편이 타당합니다."
                    )
                    check_items = "매장 앞 통행량 · 입점 동선 · 영업시간"

            elif store_stage == "사람은 지나가지만 가게로 잘 들어오지 않아요":
                action_title = "유동 → 입점 전환 단계 확인"
                action_text = (
                    "사장님 응답에서는 '사람은 있지만 입점이 적다'는 단계가 지목됐습니다. "
                    "FLOW가 이 원인을 데이터로 확정한 것은 아니므로, 실제 입점률을 확인해 가설을 검증하는 것이 우선입니다."
                )
                check_items = "시간대별 통행량 · 입점 수 · 입점률"

            elif store_stage == "손님은 들어오지만 주문·구매가 기대보다 적어요":
                action_title = "입점 → 구매 전환 단계 확인"
                action_text = (
                    "사장님 응답에서는 방문 이후 주문·구매 단계가 취약하다고 나타났습니다. "
                    "주문건수와 객단가를 확인하면 '방문은 있는데 구매가 약한지'를 보다 구체적으로 점검할 수 있습니다."
                )
                check_items = "방문자 수 · 주문건수 · 객단가"

            else:
                action_title = f"{dead_time if same_time else store_weak} 데이터부터 확인"
                action_text = (
                    "현재 응답만으로는 유동·입점·구매 중 어느 단계가 문제인지 구분하기 어렵습니다. "
                    "시간대별 기본 운영지표를 확인하면 다음 진단 단계로 넘어갈 수 있습니다."
                )
                check_items = "통행량 · 입점 수 · 주문건수 · 객단가"

            st.markdown(
                f"""
                <div class="action-box">
                    <div class="label">FLOW ACTION</div>
                    <div style="font-size:25px;font-weight:850;color:#a55c00;margin:7px 0;">{action_title}</div>
                    <div style="font-size:15px;line-height:1.75;margin-bottom:12px;">{action_text}</div>
                    <div style="font-size:14px;font-weight:800;color:#183f6c;">확인할 데이터</div>
                    <div style="font-size:14px;margin-top:4px;">{check_items}</div>
                    <div style="font-size:13px;color:#71808f;margin-top:10px;">
                        매출 방식 응답: {store_channel}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if same_time:
                st.info(
                    f"**비교 힌트:** {data['twin']}은 유사한 상권 구조를 가지면서 소비 연결 수준이 더 높습니다. "
                    "점포 데이터를 확보하면 같은 시간대의 차이를 추가 비교할 수 있습니다."
                )
            else:
                st.info(
                    "현재는 상권 패턴과 점포 패턴이 다르므로 BEST TWIN보다 먼저 내 매장의 시간대별 운영지표를 확인하는 편이 좋습니다."
                )

        with st.expander("ⓘ 왜 고객 연령대는 묻지 않나요?"):
            st.write(
                "현재 DEMO 분석 결과에는 상권·업종·시간대별 고객 연령대 소비를 직접 비교할 수 있는 데이터가 없습니다. "
                "따라서 연령대를 입력받아 맞춤진단에 사용하는 것은 근거를 넘어설 수 있어 현재 버전에서는 제외했습니다. "
                "향후 연령대별 유동·소비 데이터가 추가되면 확장할 수 있습니다."
            )

    st.divider()
    st.markdown("### FLOW가 해주는 일")
    st.markdown(
        "**사람이 많은지를 보는 데서 끝나지 않고, 사람이 있는데도 소비로 연결되지 않는 시간대를 찾고 "
        "내 가게에서 무엇을 먼저 확인해야 하는지 좁혀줍니다.**"
    )
    st.caption(
        "현재 버전은 DEMO 데이터 기반 프로토타입입니다. "
        "개별 점포의 미래 매출이나 특정 요인의 인과효과를 예측하지 않으며, "
        "최종 분석 CSV 연결 후 실제 상권·업종 결과로 교체하는 구조입니다."
    )
