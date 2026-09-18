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
        "FLOW의 상권명은 실제 분석 데이터의 상권 단위를 기준으로 표시합니다. "
        "최종 버전에서는 사용자가 익숙한 역·동네명과 분석 상권명을 함께 보여주는 방식이 좋습니다."
    )

if st.button("내 상권 진단하기 →", type="primary"):
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
    difference = float(data["twin_conversion"] - actual[dead_index])

    st.markdown(f'<div class="section-title">2. {area} · {category} 진단</div>', unsafe_allow_html=True)

    if data["consumer_score"] < 50:
        flow_type = "전환 개선형"
        diagnosis = "사람의 흐름은 충분하지만 소비 연결 성과는 그에 비해 높지 않은 상권입니다."
        next_message = "새로운 유동을 더 만드는 것보다, 현재 존재하는 유동이 실제 소비로 연결되는 과정부터 확인해볼 가치가 있습니다."
    elif data["consumer_score"] < 70:
        flow_type = "균형 점검형"
        diagnosis = "유동과 소비 연결이 중간 수준으로 나타나는 상권입니다."
        next_message = "특정 시간대의 소비공백과 유사상권의 차이를 함께 확인해 개선 여지를 찾는 것이 좋습니다."
    else:
        flow_type = "연결 우수형"
        diagnosis = "유동이 비교적 원활하게 소비로 연결되는 상권입니다."
        next_message = "전체 수준보다 시간대별 편차와 비교상권의 강점을 중심으로 추가 기회를 확인해볼 수 있습니다."

    st.markdown(
        f"""
        <div class="diagnosis-box">
            <div class="label">FLOW 상권 유형</div>
            <div style="font-size:28px;font-weight:800;color:#183f6c;margin-bottom:8px;">{flow_type}</div>
            <div style="font-size:18px;font-weight:700;color:#18324a;">{diagnosis}</div>
            <div class="subtext">{next_message}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.metric("소비 연결력 · FLOW SCORE", f"{data['flow_score']}점")
        st.caption("상권 여건을 고려했을 때 유동이 실제 소비로 연결되는 상대적 수준입니다.")
    with c2:
        st.metric("유동 수준", f"{data['traffic_score']}점")
        st.caption("같은 업종의 비교 상권 가운데 사람 흐름이 어느 정도인지 보여주는 상대적 수준입니다.")

    with st.expander("ⓘ FLOW SCORE는 무엇인가요?"):
        st.write(
            "FLOW SCORE는 단순 유동인구 점수가 아닙니다. "
            "사람이 많이 지나는지뿐 아니라, 그 상권의 조건에서 실제 소비가 얼마나 연결되는지를 "
            "비교하기 위한 진단 지표입니다. 점수 자체를 매출액으로 해석하면 안 됩니다."
        )

    # -----------------------------
    # TIME
    # -----------------------------
    st.markdown('<div class="section-title">3. 언제 소비 기회를 놓치고 있을까요?</div>', unsafe_allow_html=True)

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
        barmode="group", height=430,
        margin=dict(l=20, r=20, t=55, b=20),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(gridcolor="#e9eef3", title="상대 점수"),
        xaxis=dict(showgrid=False, title="시간대"),
        bargap=0.28
    )
    fig.add_vrect(
        x0=dead_index - 0.45, x1=dead_index + 0.45,
        fillcolor="rgba(255,177,85,0.14)", line_width=0, layer="below"
    )
    fig.add_annotation(
        x=dead_time, y=float(max(potential.max(), actual.max())) * 1.04,
        text="주목할 시간", showarrow=False,
        font=dict(size=12, color="#a55c00"),
        bgcolor="rgba(255,247,232,0.95)", bordercolor="#efcf99", borderpad=5
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.warning(
        f"**{dead_time}을 먼저 확인해 보세요.** "
        f"이 시간대는 상권 여건상 기대 소비와 실제 소비의 차이가 가장 크게 나타납니다 "
        f"(현재 DEMO 기준 차이 {dead_gap:.0f}점)."
    )
    with st.expander("ⓘ 기대 소비와 '소비공백'은 무슨 뜻인가요?"):
        st.write(
            "기대 소비는 정확한 미래 매출 예측값이 아니라 상권 조건을 고려한 상대적 소비 기대수준입니다. "
            "소비공백은 이 기대수준과 실제 소비 사이의 차이를 뜻합니다. "
            "따라서 '이 시간에 매출이 반드시 늘어난다'는 의미가 아니라 우선 확인할 시간대를 찾는 용도입니다."
        )

    # -----------------------------
    # TWIN
    # -----------------------------
    st.markdown('<div class="section-title">4. 우리와 닮았지만 더 잘되는 곳</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="twin-box">
            <div class="label">BEST TWIN</div>
            <div style="font-size:31px;font-weight:800;color:#173c67;margin-bottom:6px;">{data["twin"]}</div>
            <div style="font-size:16px;">상권 구조 유사도 <b>{data["similarity"]}%</b></div>
            <div class="subtext">
                우리 상권과 구조가 비슷한 비교상권 중 소비 연결 성과가 더 높은 곳입니다.
                닮은 조건에서도 결과가 달라지는 지점을 찾기 위한 비교 기준입니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    t1, t2 = st.columns(2)
    with t1:
        st.metric(f"우리 상권 {dead_time} 소비 연결", f"{actual[dead_index]:.0f}점")
    with t2:
        st.metric("BEST TWIN 소비 연결", f"{data['twin_conversion']}점", delta=f"+{difference:.0f}점")

    st.markdown("#### 닮은 상권과 이런 점이 달라요")
    why_cols = st.columns(3)
    for i, (feature, diff, unit) in enumerate(data["why"]):
        with why_cols[i]:
            direction = "낮아요" if diff < 0 else "높아요"
            st.metric(feature, f"{abs(diff)}{unit}", delta=f"우리 상권이 더 {direction}", delta_color="off")

    st.caption(
        "※ 위 항목은 BEST TWIN과 비교했을 때 차이가 크게 나타난 상권 특성입니다. "
        "소비성과 차이의 직접적인 원인이라는 의미는 아닙니다."
    )
    with st.expander("ⓘ BEST TWIN은 어떻게 찾나요?"):
        st.write(
            "BEST TWIN은 상권 구조가 유사한 후보 가운데 소비 연결 성과가 더 높은 비교 상권입니다. "
            "유사도는 실제 특성의 '일치율'이 아니라 여러 상권 특성의 상대적 차이를 바탕으로 만든 구조적 유사도입니다."
        )

    # -----------------------------
    # ACTION
    # -----------------------------
    st.markdown('<div class="section-title">5. 그래서 무엇을 먼저 확인해야 할까요?</div>', unsafe_allow_html=True)
    st.write(
        "FLOW는 개별 점포의 매출 원인을 단정하지 않습니다. 대신 **상권 데이터에서 먼저 확인할 문제의 방향**을 좁혀줍니다."
    )

    first_feature, first_diff, first_unit = data["why"][0]

    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown("**① 취약 시간부터 확인**")
        st.write(
            f"{dead_time}에 상권의 소비공백이 가장 큽니다. "
            "내 매장에서도 같은 시간대에 주문·방문·매출이 약한지 먼저 확인합니다."
        )
    with a2:
        st.markdown("**② 유동보다 전환을 확인**")
        st.write(
            f"현재 유형은 **{flow_type}**입니다. 단순히 사람을 더 모으기보다 "
            "지나는 사람이 실제 방문·주문으로 이어지지 않는 지점을 확인하는 것이 우선입니다."
        )
    with a3:
        st.markdown("**③ 비교상권에서 힌트 찾기**")
        st.write(
            f"{data['twin']}과 비교했을 때 **{first_feature}** 차이가 크게 나타납니다. "
            "이 차이를 원인으로 단정하지 말고 운영시간·상품구성·고객층을 점검할 비교 포인트로 활용합니다."
        )

    # -----------------------------
    # STORE CHECK
    # -----------------------------
    st.markdown('<div class="section-title">6. 우리 가게도 같은 문제일까요?</div>', unsafe_allow_html=True)
    st.write(
        "상권 분석만으로는 **우리 가게 자체의 문제인지, 동네 전체의 문제인지** 구분하기 어렵습니다. "
        "내 매장의 취약 시간대를 알고 있다면 아래에서 상권 패턴과 비교해볼 수 있습니다."
    )

    compare_store = st.checkbox("내 가게의 취약 시간대와 비교해보기", key="compare_store")

    if compare_store:
        store_weak = st.multiselect(
            "평소 주문이나 매출이 특히 낮다고 느끼는 시간대를 선택하세요.",
            data["times"],
            key="store_weak_times"
        )

        if store_weak:
            if dead_time in store_weak:
                st.success(
                    f"**상권과 점포의 취약 시간이 겹칩니다.** "
                    f"상권에서도 {dead_time}이 가장 큰 소비공백 시간이고, 내 매장에서도 같은 시간이 약합니다. "
                    "상권 공통 패턴의 영향을 받을 가능성을 먼저 확인해볼 수 있습니다."
                )
            else:
                selected = ", ".join(store_weak)
                st.warning(
                    f"**상권과 점포의 취약 시간이 다릅니다.** "
                    f"상권은 {dead_time}이 가장 취약하지만 내 매장은 {selected}이 약하다고 응답했습니다. "
                    "이 경우 상권 문제만으로 설명하기보다 매장 운영시간, 메뉴, 가격, 배달·포장 비중 등 "
                    "점포 개별 요인을 함께 확인할 필요가 있습니다."
                )

        with st.expander("시간대별 매출 데이터가 있다면 더 정확하게 할 수 있나요?"):
            st.write(
                "가능합니다. 향후 POS 등의 시간대별 매출·주문 데이터를 연결하면 "
                "상권의 취약 시간과 실제 점포의 취약 시간을 자동 비교할 수 있습니다. "
                "주문건수, 객단가, 영업시간, 배달·포장·오프라인 매출 구성까지 있으면 "
                "점포 단위 진단을 더 구체화할 수 있습니다."
            )

    st.divider()
    st.markdown("### FLOW의 역할")
    st.write(
        "**사람이 없는 곳을 찾는 데서 끝나지 않고, 사람이 있는데도 소비로 연결되지 않는 지점을 발견합니다.**"
    )
    st.caption(
        "현재 버전은 DEMO 데이터 기반 프로토타입입니다. "
        "개별 점포의 미래 매출이나 특정 요인의 인과효과를 예측하는 서비스가 아니며, "
        "최종 분석 CSV 연결 후 실제 상권·업종 결과로 교체하는 구조입니다."
    )
