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
# INPUT
# -----------------------------
st.markdown(
    '<div class="section-title">내 상권 진단하기</div>',
    unsafe_allow_html=True
)

c1, c2 = st.columns(2)

with c1:
    area = st.selectbox(
        "상권 선택",
        ["광흥창역 6번", "길음역 7번", "제기동역 1번"]
    )

with c2:
    category = st.selectbox(
        "업종 선택",
        ["커피·음료", "한식", "편의점"]
    )

analyze = st.button("내 상권 진단하기 →")

# -----------------------------
# RESULT
# -----------------------------
if analyze:

    key = (area, category)

    if key not in demo_data:
        st.warning(
            "현재 DEMO 버전에서는 이 상권·업종 조합의 결과가 준비되지 않았습니다."
        )

    else:
        data = demo_data[key]

        potential = np.array(data["potential"])
        actual = np.array(data["actual"])
        gap = potential - actual

        dead_index = int(np.argmax(gap))
        dead_time = data["times"][dead_index]
        dead_gap = int(gap[dead_index])

        st.markdown(
            '<span class="demo-badge">DEMO DATA</span>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="section-title">{area} · {category} 분석 결과</div>',
            unsafe_allow_html=True
        )

        # -----------------------------
        # 진단 문장
        # -----------------------------
        if data["consumer_score"] < 50:
            diagnosis = "유동은 충분하지만 소비전환은 낮은 편입니다."
        elif data["consumer_score"] < 70:
            diagnosis = "유동 대비 소비전환은 보통 수준입니다."
        else:
            diagnosis = "유동이 비교적 원활하게 소비로 연결되고 있습니다."

        st.markdown(
            f'<div class="diagnosis-box">'
            f'<div style="font-size:14px;color:#71808f;font-weight:700;margin-bottom:6px;">상권 진단</div>'
            f'<div style="font-size:24px;font-weight:800;color:#18324a;">{diagnosis}</div>'
            f'<div style="font-size:14px;color:#5d6a76;margin-top:8px;">'
            f'가장 큰 소비공백 시간은 <b>{dead_time}</b>입니다.'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # -----------------------------
        # TOP SUMMARY
        # -----------------------------
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f'<div class="card">'
                f'<div class="label">FLOW SCORE</div>'
                f'<div class="big">{data["flow_score"]}</div>'
                f'<div class="subtext">유동량 대비 실제 소비 연결성을 종합한 진단 점수</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f'<div class="card">'
                f'<div class="label">전체 유동량 수준</div>'
                f'<div class="big">{data["traffic_score"]}</div>'
                f'<div class="subtext">주변을 지나가는 사람의 규모</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f'<div class="card">'
                f'<div class="label">소비 연결성</div>'
                f'<div class="big">{data["consumer_score"]}</div>'
                f'<div class="subtext">유동이 실제 지역 소비로 연결되는 수준</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="warning">'
            '<b>⚠️ 유동인구 착시 가능성이 있습니다.</b><br><br>'
            '주변을 지나는 사람의 규모에 비해 실제 지역 소비로 이어지는 정도가 상대적으로 낮습니다.'
            '</div>',
            unsafe_allow_html=True
        )

        # -----------------------------
        # TIME DIAGNOSIS
        # -----------------------------
        st.markdown(
            '<div class="section-title">시간대별 소비 기회 진단</div>',
            unsafe_allow_html=True
        )

        time_df = pd.DataFrame({
            "시간대": data["times"],
            "소비 잠재력": data["potential"],
            "실제 소비": data["actual"]
        })

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=time_df["시간대"],
                y=time_df["소비 잠재력"],
                name="소비 잠재력",
                marker_color="#A8C7E8"
            )
        )

        fig.add_trace(
            go.Bar(
                x=time_df["시간대"],
                y=time_df["실제 소비"],
                name="실제 소비",
                marker_color="#245B91"
            )
        )

        fig.update_layout(
            barmode="group",
            height=430,
            margin=dict(l=20, r=20, t=55, b=20),
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
                range=[0, 100],
                gridcolor="#e9eef3",
                title="점수"
            ),
            xaxis=dict(showgrid=False),
            bargap=0.28
        )

        fig.add_vrect(
            x0=dead_index - 0.45,
            x1=dead_index + 0.45,
            fillcolor="rgba(255,177,85,0.14)",
            line_width=0,
            layer="below"
        )

        fig.add_annotation(
            x=dead_time,
            y=96,
            text="DEAD TIME",
            showarrow=False,
            font=dict(size=12, color="#a55c00"),
            bgcolor="rgba(255,247,232,0.95)",
            bordercolor="#efcf99",
            borderpad=5
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        # -----------------------------
        # DEAD TIME CARD
        # -----------------------------
        st.markdown(
            f'<div class="dead-box">'
            f'<div class="label">가장 큰 소비공백</div>'
            f'<div style="font-size:34px;font-weight:800;color:#a55c00;margin-bottom:8px;">{dead_time}</div>'
            f'<div style="font-size:16px;line-height:1.7;margin-bottom:14px;">'
            f'이 시간대의 소비 잠재력은 <b>{data["potential"][dead_index]}</b>점, '
            f'실제 소비는 <b>{data["actual"][dead_index]}</b>점입니다.'
            f'</div>'
            f'<div style="font-size:18px;">Opportunity Gap <b>{dead_gap}점</b></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        # -----------------------------
        # BEST TWIN
        # -----------------------------
        st.markdown(
            '<div class="section-title">BEST TWIN</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="twin-box">'
            f'<div class="label">우리 상권과 가장 비슷하면서 소비전환이 더 높은 상권</div>'
            f'<div style="font-size:31px;font-weight:800;color:#173c67;margin-bottom:6px;">'
            f'{data["twin"]}'
            f'</div>'
            f'<div style="font-size:16px;">상권 유사도 <b>{data["similarity"]}%</b></div>'
            f'<div style="margin-top:14px;line-height:1.7;font-size:15px;">'
            f'우리 상권과 구조는 비슷하지만 <b>{dead_time}</b> 소비전환은 상대적으로 더 높은 비교 상권입니다.'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        twin1, twin2 = st.columns(2)

        with twin1:
            st.metric(
                "우리 상권 소비전환",
                f"{data['actual'][dead_index]}"
            )

        with twin2:
            difference = data["twin_conversion"] - data["actual"][dead_index]

            st.metric(
                "BEST TWIN 소비전환",
                f"{data['twin_conversion']}",
                delta=f"+{difference}"
            )

        st.markdown(
            f'<div class="compare-box">'
            f'우리 상권의 <b>{dead_time}</b> 소비전환은 '
            f'<b>{data["actual"][dead_index]}</b>점, '
            f'BEST TWIN은 <b>{data["twin_conversion"]}</b>점입니다.'
            f'<br><br>'
            f'즉, 비슷한 상권 구조에서도 소비전환에 '
            f'<b>{difference}점 차이</b>가 나타납니다.'
            f'</div>',
            unsafe_allow_html=True
        )

        # -----------------------------
        # WHY
        # -----------------------------
        st.markdown(
            '<div class="section-title">TWIN과 무엇이 다를까요?</div>',
            unsafe_allow_html=True
        )

        why_cols = st.columns(3)

        for i, (feature, diff, unit) in enumerate(data["why"]):

            direction_text = (
                f'TWIN 대비 {abs(diff)}{unit} 낮습니다'
                if diff < 0
                else f'TWIN 대비 {abs(diff)}{unit} 높습니다'
            )

            sign = "" if diff < 0 else "+"

            with why_cols[i]:
                st.markdown(
                    f'<div class="why-card">'
                    f'<div class="label">TWIN 대비 차이</div>'
                    f'<div style="font-size:20px;font-weight:800;color:#183f6c;margin-bottom:10px;">'
                    f'{feature}'
                    f'</div>'
                    f'<div style="font-size:27px;font-weight:800;color:#5c6f82;">'
                    f'{sign}{diff}{unit}'
                    f'</div>'
                    f'<div style="margin-top:8px;font-size:13px;color:#7c8996;">'
                    f'{direction_text}'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.caption(
            "※ 위 결과는 상권 간 특성 차이를 보여주는 것으로, 인과관계를 의미하지 않습니다."
        )

        # -----------------------------
        # ACTION POINT
        # -----------------------------
        st.markdown(
            '<div class="section-title">ACTION POINT</div>',
            unsafe_allow_html=True
        )

        first_feature, first_diff, first_unit = data["why"][0]

        action1_title = f"{dead_time} 소비전환 우선 점검"
        action1_text = (
            f"이 시간대의 소비 잠재력은 <b>{data['potential'][dead_index]}점</b>이지만 "
            f"실제 소비는 <b>{data['actual'][dead_index]}점</b>입니다. "
            f"다른 시간대보다 소비공백이 크므로 우선적으로 확인할 필요가 있습니다."
        )

        action2_title = f"{first_feature} 차이 확인"
        action2_text = (
            f"BEST TWIN과 비교했을 때 <b>{first_feature}</b>가 "
            f"<b>{abs(first_diff)}{first_unit}</b> "
            f"{'낮게' if first_diff < 0 else '높게'} 나타납니다. "
            f"이 차이가 {dead_time} 소비전환과 어떤 관계가 있는지 추가 확인해볼 수 있습니다."
        )

        action3_title = f"{data['twin']} 패턴 비교"
        action3_text = (
            f"우리 상권과 <b>{data['similarity']}%</b> 유사한 "
            f"<b>{data['twin']}</b>은 같은 시간대 소비전환이 "
            f"<b>{data['twin_conversion']}점</b>으로, "
            f"우리 상권보다 <b>{difference}점 높습니다.</b> "
            f"시간대별 유동구조와 소비 특성을 비교해볼 수 있습니다."
        )

        a1, a2, a3 = st.columns(3)

        with a1:
            st.markdown(
                f'<div class="why-card">'
                f'<div class="label">PRIORITY 01</div>'
                f'<div style="font-size:20px;font-weight:800;color:#183f6c;margin-bottom:12px;">'
                f'{action1_title}'
                f'</div>'
                f'<div style="font-size:14px;line-height:1.8;color:#5d6a76;">'
                f'{action1_text}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with a2:
            st.markdown(
                f'<div class="why-card">'
                f'<div class="label">PRIORITY 02</div>'
                f'<div style="font-size:20px;font-weight:800;color:#183f6c;margin-bottom:12px;">'
                f'{action2_title}'
                f'</div>'
                f'<div style="font-size:14px;line-height:1.8;color:#5d6a76;">'
                f'{action2_text}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        with a3:
            st.markdown(
                f'<div class="why-card">'
                f'<div class="label">PRIORITY 03</div>'
                f'<div style="font-size:20px;font-weight:800;color:#183f6c;margin-bottom:12px;">'
                f'{action3_title}'
                f'</div>'
                f'<div style="font-size:14px;line-height:1.8;color:#5d6a76;">'
                f'{action3_text}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.info(
            "현재 프로토타입은 서비스 구조 확인을 위한 DEMO 버전입니다. "
            "FLOW SCORE, 소비 잠재력, BEST TWIN, WHY 결과는 "
            "최종 데이터 분석 완료 후 실제 분석값으로 교체됩니다."
        )