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
st.caption("분석할 상권과 업종을 선택하세요.")

available_keys = list(demo_data.keys())
area_options = list(dict.fromkeys(k[0] for k in available_keys))
area = st.selectbox("상권 선택", area_options)

category_options = [k[1] for k in available_keys if k[0] == area]
category = st.selectbox("업종 선택", category_options)

with st.expander("ⓘ 내가 어느 상권인지 잘 모르겠어요"):
    st.write(
        "FLOW의 상권명은 분석 데이터의 상권 단위를 기준으로 합니다. "
        "최종 서비스에서는 익숙한 역·동네명과 분석 상권명을 함께 보여주는 방식으로 연결할 수 있습니다."
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
        "상권 활동·소비 여건": data["potential"],
        "실제 소비 수준": data["actual"]
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=time_df["시간대"], y=time_df["상권 활동·소비 여건"],
        name="상권 활동·소비 여건", marker_color="#A8C7E8"
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
            다른 시간대보다 상권의 활동·소비 여건과 실제 소비 사이의 간격이 크게 나타납니다.
            FLOW는 이를 '매출이 오를 시간'이 아니라 <b>우선 점검할 시간</b>으로 해석합니다.
        </div>
        """, unsafe_allow_html=True
    )

    with st.expander("ⓘ 그래프는 어떻게 계산됐나요?"):
        st.write(
            f"분석 내부 지수에서는 {dead_time}의 상권 조건을 고려한 상대적 소비 기대수준이 "
            f"{potential[dead_index]:.0f}, 실제 소비 수준이 {actual[dead_index]:.0f}로 계산되었습니다. "
            f"차이는 {dead_gap:.0f}입니다. 이 값은 원화 매출이나 미래 매출 예측치가 아닙니다."
        )

    # 4. TWIN
    st.markdown('<div class="section-title">4. 비슷한 조건인데 더 잘되는 곳은?</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="twin-box">
            <div class="label">BEST TWIN</div>
            <div style="font-size:31px;font-weight:850;color:#173c67;margin:7px 0;">{data["twin"]}</div>
            <div style="font-size:17px;font-weight:750;color:#18324a;">
                우리 상권과 구조는 비슷하지만 소비 연결은 더 활발한 비교상권입니다.
            </div>
            <div class="subtext">
                상권 구조 유사도 {data["similarity"]}% · 비슷한 조건에서도 다른 결과가 나타나는 지점을 찾기 위한 비교 기준
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="card" style="margin-top:12px;">
            <div class="label">핵심 비교</div>
            <div style="font-size:23px;font-weight:850;color:#173c67;margin:6px 0;">
                {dead_time}, 유사상권에서는 소비 연결이 더 활발합니다.
            </div>
            <div class="subtext">
                내부 분석지수 기준 우리 상권 {actual[dead_index]:.0f} · BEST TWIN {data["twin_conversion"]} 
                · 차이 +{twin_diff:.0f}
            </div>
        </div>
        """, unsafe_allow_html=True
    )

    st.markdown("#### 두 상권에서 눈에 띄는 차이")
    why_cols = st.columns(3)
    for i, (feature, diff, unit) in enumerate(data["why"]):
        with why_cols[i]:
            direction = "더 낮습니다" if diff < 0 else "더 높습니다"
            st.markdown(
                f"""
                <div class="card">
                    <div class="label">비교 포인트 {i+1}</div>
                    <div style="font-size:19px;font-weight:800;color:#183f6c;margin:7px 0;">{feature}</div>
                    <div style="font-size:15px;line-height:1.6;">
                        우리 상권이 BEST TWIN보다 <b>{abs(diff)}{unit} {direction}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

    st.caption("※ 위 차이는 원인으로 확정한 결과가 아니라, 추가로 살펴볼 비교 포인트입니다.")

    with st.expander("ⓘ BEST TWIN과 유사도는 어떻게 해석하나요?"):
        st.write(
            "유사도는 실제 특성의 일치율이 아니라 여러 상권 특성의 상대적 차이를 바탕으로 만든 구조적 유사도입니다. "
            "BEST TWIN은 인과관계를 증명하는 대상이 아니라 비슷한 조건에서 다른 결과가 나타나는 지점을 찾기 위한 비교 기준입니다."
        )

    # 5. STORE DIAGNOSIS
    st.markdown('<div class="section-title">5. 우리 가게에서는 무엇부터 확인해야 할까요?</div>', unsafe_allow_html=True)
    st.write(
        "상권의 문제와 내 가게의 문제는 다를 수 있습니다. "
        "간단한 매장 상황을 입력하면 **상권 결과와 비교해 확인 순서**를 좁혀드립니다."
    )

    compare_store = st.checkbox("내 가게 맞춤진단 시작하기", key="compare_store")

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
                result_title = "상권과 내 가게의 취약 시간이 같습니다."
                result_desc = (
                    f"상권에서도 {dead_time}의 소비공백이 가장 크고 내 가게도 같은 시간이 가장 약합니다. "
                    "점포만의 문제라고 보기 전에 상권 공통 패턴과 점포 운영을 함께 확인하는 것이 좋습니다."
                )
            else:
                result_title = "상권보다 내 가게의 개별 문제를 먼저 볼 필요가 있습니다."
                result_desc = (
                    f"상권은 {dead_time}이 가장 취약하지만 내 가게는 {store_weak}이 가장 약합니다. "
                    "상권 평균과 다른 패턴이므로 점포의 운영·입점·구매 과정을 먼저 확인하는 편이 타당합니다."
                )

            st.markdown("### 맞춤진단 결과")
            st.markdown(
                f"""
                <div class="diagnosis-box">
                    <div class="label">MY STORE × FLOW</div>
                    <div style="font-size:25px;font-weight:850;color:#173c67;margin:7px 0;">{result_title}</div>
                    <div class="subtext">{result_desc}</div>
                </div>
                """, unsafe_allow_html=True
            )

            # Build three prioritized actions from user's own answers.
            if store_stage == "사람은 지나가지만 가게로 잘 들어오지 않아요":
                p1_title = f"{store_weak} 입점 전환 확인"
                p1_text = "매장 앞을 지나는 사람 대비 실제로 들어오는 사람의 비율을 먼저 확인하세요."
                p1_data = "통행량 · 입점 수 · 입점률"
            elif store_stage == "손님은 들어오지만 주문·구매가 기대보다 적어요":
                p1_title = f"{store_weak} 구매 전환 확인"
                p1_text = "방문 이후 주문으로 이어지는 과정과 객단가를 먼저 확인하세요."
                p1_data = "방문자 수 · 주문건수 · 객단가"
            elif store_stage == "주변에 사람 자체가 적어요":
                p1_title = f"{store_weak} 실제 매장 앞 유동 확인"
                p1_text = "상권 전체가 아니라 내 매장 앞의 실제 통행량이 낮은지 먼저 확인하세요."
                p1_data = "매장 앞 통행량 · 입점 수"
            else:
                p1_title = f"{store_weak} 기본 운영지표 확인"
                p1_text = "현재 응답만으로 막히는 단계를 특정하기 어려워 기본 지표부터 확인하는 것이 좋습니다."
                p1_data = "통행량 · 입점 수 · 주문건수 · 객단가"

            if store_channel == "포장 중심":
                p2_title = "포장 고객 동선 확인"
                p2_text = "포장 중심 매장이므로 메뉴 확인 → 주문 → 수령 과정에서 불편이나 이탈이 있는지 확인하세요."
                p2_data = "포장 주문건수 · 대기시간 · 주문취소"
            elif store_channel == "배달 중심":
                p2_title = "배달 주문 흐름 확인"
                p2_text = "배달 중심 매장이므로 해당 시간대의 노출·주문·취소 흐름을 따로 확인하세요."
                p2_data = "배달 노출 · 주문건수 · 취소건수"
            elif store_channel == "매장 중심":
                p2_title = "매장 방문 흐름 확인"
                p2_text = "매장 중심 매장이므로 입점 이후 주문까지의 흐름을 시간대별로 확인하세요."
                p2_data = "입점 수 · 주문건수 · 회전"
            elif store_channel == "혼합형":
                p2_title = "판매 채널별로 나눠 확인"
                p2_text = "매장·포장·배달을 합쳐 보면 문제가 가려질 수 있어 채널별 주문 흐름을 분리해 확인하세요."
                p2_data = "매장 · 포장 · 배달 주문건수"
            else:
                p2_title = "판매 방식부터 구분"
                p2_text = "어떤 판매 방식에서 매출이 발생하는지부터 구분하면 취약시간의 원인을 더 좁힐 수 있습니다."
                p2_data = "매장 · 포장 · 배달 비중"

            if same_time:
                p3_title = f"{dead_time} 상권 공통 패턴과 함께 비교"
                p3_text = f"내 가게와 상권의 취약시간이 같으므로 {data['twin']}의 같은 시간대와 비교할 가치가 있습니다."
                p3_data = "내 점포 지표 · 상권 지표 · BEST TWIN"
            else:
                p3_title = f"상권의 {dead_time} 대응은 후순위"
                p3_text = f"현재 내 가게는 {store_weak}이 더 약하므로 상권 전체의 {dead_time}보다 내 점포 문제를 먼저 확인하세요."
                p3_data = "내 점포 시간대별 운영지표"

            st.markdown("### FLOW ACTION · 확인 순서")
            ac1, ac2, ac3 = st.columns(3)
            actions = [
                ("1순위", p1_title, p1_text, p1_data),
                ("2순위", p2_title, p2_text, p2_data),
                ("3순위", p3_title, p3_text, p3_data),
            ]
            for col, (rank, title, desc, needed) in zip([ac1, ac2, ac3], actions):
                with col:
                    st.markdown(
                        f"""
                        <div class="card" style="min-height:245px;">
                            <div class="label">{rank}</div>
                            <div style="font-size:19px;font-weight:850;color:#183f6c;margin:8px 0 10px;">{title}</div>
                            <div style="font-size:14px;line-height:1.7;margin-bottom:15px;">{desc}</div>
                            <div style="font-size:12px;font-weight:800;color:#71808f;">확인할 데이터</div>
                            <div style="font-size:13px;margin-top:4px;">{needed}</div>
                        </div>
                        """, unsafe_allow_html=True
                    )

            st.caption(
                "※ FLOW ACTION은 현재 상권 분석 결과와 사용자가 입력한 점포 상황을 바탕으로 "
                "확인 순서를 제시합니다. 특정 행동이 매출을 개선한다고 인과적으로 보장하는 처방은 아닙니다."
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
