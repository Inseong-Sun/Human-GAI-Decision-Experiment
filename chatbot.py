import streamlit as st
import random
import uuid
import time
import html
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo


# =========================================================
# 1. 기본 설정
# =========================================================

st.set_page_config(
    page_title="인간-AI 의사결정 실험",
    page_icon="🤖",
    layout="centered"
)

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx1lANBZTZWsF9QO7BE8N2Gs_jOhJpHBYSurHZGgSSKU4OJwEISj-g90tVB64PRB-Fuhg/exec"

MESSAGE_DELAY = 0.55


# =========================================================
# 2. 파일럿 실험 문항
# =========================================================

QUESTIONS = [

    # -----------------------------------------------------
    # 1. 생산관리
    # 한 번에 더 많이 생산할 것인가
    # -----------------------------------------------------

    {
        "id": 1,
        "category": "생산관리",

        "question": """당신은 한 제조공장의 생산관리 담당자입니다.

이 공장에서는 여러 종류의 제품을 같은 설비에서 번갈아 생산하고 있습니다. 제품 종류가 바뀔 때마다 설비를 청소하고 설정을 다시 맞춰야 하기 때문에 그동안 생산이 중단됩니다.

최근 주문량이 증가하면서 제품을 바꾸는 횟수도 늘어나 생산일정에 여유가 줄어들고 있습니다.

한 번에 생산하는 양을 늘리면 제품을 바꾸는 횟수가 줄어 같은 시간 동안 더 많은 제품을 생산할 수 있고, 갑작스러운 추가 주문에도 대응하기 쉬워집니다.

반면 예상보다 주문이 줄거나 다른 제품의 주문이 갑자기 늘어날 경우 미리 생산한 제품이 재고로 남을 수 있으며, 이미 생산 중인 제품 때문에 다른 제품으로 빠르게 생산계획을 변경하기 어려울 수 있습니다.

당신이 생산관리 담당자라면 한 번에 생산하는 양을 늘리시겠습니까?

예: 생산량을 늘린다.
아니요: 현재 생산방식을 유지한다.""",

        "a_recommendation": "예",

        "a_response": """저는 한 번에 생산하는 양을 늘리는 쪽이 조금 더 적절하다고 생각합니다.

최근 주문량이 증가하고 있고 제품 변경 때마다 생산이 중단되고 있습니다. 생산량을 늘리면 제품 교체 횟수를 줄여 생산효율을 높이고 추가 주문에 대응할 여유도 확보할 수 있습니다.

재고 증가 가능성은 있지만, 현재 상황에서는 생산효율과 주문 대응능력의 장점이 더 크다고 판단됩니다.""",

        "b_if_yes_recommendation": "아니요",

        "b_if_yes_response": """저는 현재 생산방식을 유지하는 것이 더 적절하다고 판단합니다.

생산량을 늘리면 제품 교체 횟수가 줄어 생산효율은 높아질 수 있습니다. 하지만 수요가 예상과 달라질 경우 재고가 증가하고, 다른 제품의 주문이 갑자기 늘어나도 생산계획을 빠르게 변경하기 어려울 수 있습니다.

따라서 단기적인 생산효율보다 재고 부담을 줄이고 수요 변화에 유연하게 대응할 수 있는 현재 방식을 유지하는 것이 더 적절합니다.""",

        "b_if_no_recommendation": "예",

        "b_if_no_response": """저는 한 번에 생산하는 양을 늘리는 것이 더 적절하다고 판단합니다.

현재는 제품을 바꿀 때마다 설비 준비작업이 반복되어 실제 생산에 사용할 수 있는 시간이 줄어들고 있습니다. 생산량을 늘리면 제품 교체 횟수를 줄여 생산효율을 높일 수 있고, 최근처럼 주문이 증가하는 상황에서 추가 주문에 대응할 생산여유도 확보할 수 있습니다.

재고가 증가할 가능성은 있지만, 현재 상황에서는 생산효율과 주문 대응능력을 높이는 것이 더 중요한 선택이라고 판단합니다."""
    },


    # -----------------------------------------------------
    # 2. 생산관리
    # 갑자기 들어온 주문을 받을 것인가
    # -----------------------------------------------------

    {
        "id": 2,
        "category": "생산관리",

        "question": """당신은 한 제조공장의 생산관리 담당자입니다.

현재 공장은 이미 확정된 주문에 따라 생산계획을 운영하고 있으며, 지금 계획대로라면 기존 고객에게 약속한 날짜에 제품을 모두 공급할 수 있습니다.

그런데 기존 거래처에서 갑자기 빠른 납품이 필요한 추가 주문을 요청했습니다. 이를 받아들이면 추가적인 매출을 얻을 수 있고, 거래처의 긴급한 요구에 대응해 고객관계를 유지하는 데 도움이 될 수 있습니다.

반면 긴급 주문을 추가하려면 일부 제품의 생산순서를 변경해야 하고 작업자의 업무량도 늘어납니다. 또한 생산일정의 여유가 줄어들기 때문에 이후 설비고장이나 작업지연이 발생하면 기존 고객의 주문 일정에도 영향을 줄 가능성이 있습니다.

당신이 생산관리 담당자라면 긴급 주문을 받으시겠습니까?

예: 긴급 주문을 생산계획에 추가한다.
아니요: 기존 생산계획을 유지한다.""",

        "a_recommendation": "아니요",

        "a_response": """저는 긴급 주문을 받지 않고 기존 생산계획을 유지하는 쪽이 조금 더 적절하다고 생각합니다.

긴급 주문은 추가 매출과 고객 대응에 도움이 되지만, 생산순서를 변경하면 일정의 여유가 줄어 기존 주문에도 영향을 줄 가능성이 있습니다.

따라서 추가 매출보다 기존 고객의 납기와 생산계획의 안정성을 우선하는 편이 더 적절해 보입니다.""",

        "b_if_yes_recommendation": "아니요",

        "b_if_yes_response": """저는 긴급 주문을 받지 않고 기존 생산계획을 유지하는 것이 더 적절하다고 판단합니다.

긴급 주문을 받으면 추가 매출과 고객 대응 측면에서는 장점이 있습니다. 하지만 생산순서를 변경하면 일정의 여유가 줄어들고, 예상치 못한 문제가 발생할 경우 기존 고객의 납기에도 영향을 줄 수 있습니다.

따라서 추가적인 주문 기회보다 기존 납기와 생산계획의 안정성을 유지하는 것이 더 적절합니다.""",

        "b_if_no_recommendation": "예",

        "b_if_no_response": """저는 긴급 주문을 받아들이는 것이 더 적절하다고 판단합니다.

현재 생산계획을 일부 조정하더라도 기존 주문의 납기가 바로 지연되는 상황은 아닙니다. 긴급 주문을 수락하면 추가 매출을 확보하고 거래처의 요구에 적극적으로 대응할 수 있습니다.

따라서 일정의 여유가 다소 줄어들더라도 고객 대응과 추가적인 사업기회를 확보하는 것이 더 적절합니다."""
    },


    # -----------------------------------------------------
    # 3. 품질관리
    # 새로운 공급업체의 부품을 사용할 것인가
    # -----------------------------------------------------

    {
        "id": 3,
        "category": "품질관리",

        "question": """당신은 한 제조공장의 품질관리 담당자입니다.

현재 공장은 오랫동안 거래해 온 업체에서 핵심 부품을 공급받고 있습니다. 기존 업체의 부품은 품질이 안정적으로 유지되고 있지만 최근 공급가격이 계속 상승하고 있습니다.

새로운 업체가 기존보다 저렴한 가격으로 같은 규격의 부품을 제안했습니다. 새 업체가 제출한 품질자료와 시험용 부품은 모두 회사의 품질기준을 통과했습니다. 이 업체의 부품을 사용하면 생산비용을 줄이고 새로운 공급처를 확보할 수 있습니다.

반면 새로운 업체와는 거래 경험이 많지 않아 장기간 대량으로 공급받았을 때도 현재와 같은 품질이 안정적으로 유지될지는 충분히 확인되지 않았습니다. 기존 업체를 계속 이용하면 비용은 더 들지만 오랫동안 검증된 품질을 유지할 수 있습니다.

당신이 품질관리 담당자라면 새로운 공급업체의 부품을 실제 생산에 사용하시겠습니까?

예: 품질기준을 통과한 신규 업체의 부품을 사용한다.
아니요: 비용이 더 들더라도 검증된 기존 업체의 부품을 유지한다.""",

        "a_recommendation": "예",

        "a_response": """저는 새로운 공급업체의 부품을 사용하는 쪽이 조금 더 적절하다고 생각합니다.

신규 업체라는 불확실성은 있지만 품질자료와 시험용 부품이 모두 회사 기준을 충족했습니다. 또한 새로운 공급처를 확보하면 비용과 특정 업체에 대한 의존도를 줄일 수 있습니다.

따라서 품질을 지속적으로 확인하면서 신규 업체를 활용하는 것이 합리적이라고 판단됩니다.""",

        "b_if_yes_recommendation": "아니요",

        "b_if_yes_response": """저는 기존 공급업체의 부품을 계속 사용하는 것이 더 적절하다고 판단합니다.

신규 업체의 부품이 현재 품질기준을 통과했더라도 장기간 대량으로 공급했을 때 동일한 품질이 유지될지는 충분히 확인되지 않았습니다. 핵심 부품에 문제가 발생하면 완제품의 품질에도 영향을 줄 수 있습니다.

따라서 비용절감보다 장기간 검증된 품질 안정성과 공급 신뢰성을 유지하는 것이 더 적절합니다.""",

        "b_if_no_recommendation": "예",

        "b_if_no_response": """저는 새로운 공급업체의 부품을 사용하는 것이 더 적절하다고 판단합니다.

신규 업체의 품질자료와 시험용 부품은 모두 회사 기준을 충족했으며, 현재 확인된 결과에서는 품질상 문제가 나타나지 않았습니다. 또한 새로운 공급처를 확보하면 비용과 특정 업체에 대한 의존도를 줄일 수 있습니다.

따라서 지속적인 품질관리를 병행하면서 신규 공급업체를 활용하는 것이 더 적절합니다."""
    },


    # -----------------------------------------------------
    # 4. 품질관리
    # 회사의 품질기준을 더 엄격하게 할 것인가
    # -----------------------------------------------------

    {
        "id": 4,
        "category": "품질관리",

        "question": """당신은 한 제조공장의 품질관리 담당자입니다.

현재 회사에서 생산하는 제품은 고객이 요구하는 품질기준을 충족하고 있으며 정상적으로 판매되고 있습니다.

최근 품질팀에서는 제품마다 나타나는 작은 차이까지 줄이기 위해 고객 요구수준보다 더 엄격한 내부 품질기준을 적용하자고 제안했습니다. 이를 적용하면 제품 간 품질 차이를 줄이고 보다 일정한 품질을 유지할 수 있으며, 작은 이상도 출하 전에 걸러낼 가능성이 높아집니다.

반면 기존 기준에서는 정상제품으로 판매할 수 있었던 일부 제품까지 재작업하거나 폐기해야 할 수 있습니다. 그 결과 생산비용이 증가하고 실제 판매 가능한 제품의 양도 줄어들 수 있습니다.

당신이 품질관리 담당자라면 현재보다 엄격한 내부 품질기준을 적용하시겠습니까?

예: 비용이 증가하더라도 품질기준을 강화한다.
아니요: 현재도 고객 요구수준을 충족하므로 기존 기준을 유지한다.""",

        "a_recommendation": "아니요",

        "a_response": """저는 현재의 품질기준을 유지하는 쪽이 조금 더 적절하다고 생각합니다.

현재 제품은 이미 고객 요구기준을 충족하고 있습니다. 기준을 추가로 강화하면 사용에 문제가 없는 제품까지 재작업하거나 폐기해 비용과 자원 낭비가 증가할 수 있습니다.

따라서 현재 기준을 안정적으로 유지하는 편이 더 효율적이라고 판단됩니다.""",

        "b_if_yes_recommendation": "아니요",

        "b_if_yes_response": """저는 현재의 품질기준을 유지하는 것이 더 적절하다고 판단합니다.

현재 제품은 이미 고객이 요구하는 품질기준을 충족하고 있습니다. 기준을 추가로 강화하면 실제 사용에 문제가 없는 제품까지 재작업하거나 폐기하게 되어 생산비용과 자원 낭비가 증가할 수 있습니다.

따라서 추가적인 품질 향상보다 현재 기준을 안정적으로 유지하면서 생산효율을 확보하는 것이 더 적절합니다.""",

        "b_if_no_recommendation": "예",

        "b_if_no_response": """저는 현재보다 엄격한 내부 품질기준을 적용하는 것이 더 적절하다고 판단합니다.

현재 기준을 충족하더라도 제품마다 작은 차이가 반복되면 고객이 느끼는 품질의 일관성이 낮아질 수 있습니다. 기준을 강화하면 작은 이상을 미리 관리하고 보다 균일한 제품을 제공할 수 있습니다.

따라서 일부 비용이 증가하더라도 장기적인 품질 신뢰와 제품의 일관성을 높이는 것이 더 적절합니다."""
    },


    # -----------------------------------------------------
    # 5. 산업안전
    # 새벽배송 운영을 축소할 것인가
    # -----------------------------------------------------

    {
        "id": 5,
        "category": "산업안전",

        "question": """당신은 한 택배회사의 안전관리 담당자입니다.

회사는 고객이 밤에 주문한 상품을 다음 날 아침까지 받을 수 있도록 새벽배송을 운영하고 있습니다. 새벽배송은 고객 만족도가 높고, 해당 시간대의 배송을 통해 수입을 얻는 배송기사들도 있습니다.

하지만 새벽시간대 근무가 반복되면 수면과 회복시간이 부족해질 수 있고, 피로와 집중력 저하가 배송 중 실수나 사고위험으로 이어질 가능성이 있습니다.

새벽배송을 축소하면 배송기사의 야간근무 부담을 줄일 수 있지만, 일부 상품의 배송시간이 늦어지고 회사의 서비스 경쟁력이 낮아질 수 있습니다. 또한 새벽시간대 근무를 선호하는 기사들의 수입에도 영향을 줄 수 있습니다.

당신이 안전관리 담당자라면 새벽배송 운영을 축소하시겠습니까?

예: 배송기사의 피로와 사고위험을 줄이기 위해 새벽배송을 축소한다.
아니요: 새벽배송을 유지하되 근무시간과 휴식관리를 강화한다.""",

        "a_recommendation": "예",

        "a_response": """저는 새벽배송 운영을 일부 축소하는 쪽이 조금 더 적절하다고 생각합니다.

새벽배송은 고객 편의와 근무기회 측면에서 장점이 있지만, 반복적인 야간근무는 수면 부족과 피로를 높여 집중력과 사고위험에 영향을 줄 수 있습니다.

따라서 서비스상의 부담이 있더라도 작업자의 피로와 안전을 우선할 필요가 있다고 판단됩니다.""",

        "b_if_yes_recommendation": "아니요",

        "b_if_yes_response": """저는 새벽배송을 유지하면서 근무와 휴식관리를 강화하는 것이 더 적절하다고 판단합니다.

새벽배송을 축소하면 야간근무 부담은 줄어들지만 고객 서비스가 제한되고, 해당 시간대 근무를 원하는 배송기사의 업무와 수입에도 영향을 줄 수 있습니다. 피로 문제는 근무시간과 휴식시간을 조정하는 방식으로 관리할 수도 있습니다.

따라서 새벽배송 자체를 줄이기보다 서비스를 유지하면서 안전관리를 강화하는 것이 더 적절합니다.""",

        "b_if_no_recommendation": "예",

        "b_if_no_response": """저는 새벽배송 운영을 일부 축소하는 것이 더 적절하다고 판단합니다.

야간과 새벽시간의 반복적인 근무는 충분한 수면과 회복을 어렵게 만들고, 누적된 피로는 집중력 저하와 사고위험으로 이어질 수 있습니다. 휴식을 강화하더라도 지속적인 야간근무의 부담은 남을 수 있습니다.

따라서 운영상의 부담이 있더라도 작업자의 피로와 안전위험을 줄이는 것이 더 적절합니다."""
    },


    # -----------------------------------------------------
    # 6. 산업안전
    # 신규 작업자의 단독작업을 늦출 것인가
    # -----------------------------------------------------

    {
        "id": 6,
        "category": "산업안전",

        "question": """당신은 한 제조공장의 안전관리 담당자입니다.

최근 입사한 신규 작업자가 회사에서 정한 안전교육과 작업교육을 모두 이수했고, 필요한 평가도 통과했습니다. 지금까지 별다른 문제 없이 업무를 수행하고 있지만 실제 현장경험은 아직 많지 않습니다.

회사 기준상 이제 혼자 작업할 수 있습니다. 계획대로 단독작업을 시작하면 인력을 효율적으로 운영할 수 있고, 신규 작업자도 빠르게 독립적으로 업무를 수행할 수 있습니다.

반면 예상하지 못한 상황이 발생했을 때 현장경험이 부족한 작업자가 혼자 판단해야 할 수 있습니다. 일정 기간 더 숙련된 작업자와 함께 근무하도록 하면 즉시 도움을 받을 수 있고 실제 상황에 대한 경험도 더 쌓을 수 있지만, 숙련된 작업자 한 명이 계속 지원에 투입되어야 합니다.

당신이 안전관리 담당자라면 신규 작업자의 단독작업 시작을 늦추시겠습니까?

예: 일정 기간 더 숙련된 작업자와 함께 근무하도록 한다.
아니요: 교육과 평가를 통과했으므로 계획대로 단독작업을 시작한다.""",

        "a_recommendation": "아니요",

        "a_response": """저는 계획대로 단독작업을 시작하는 쪽이 조금 더 적절하다고 생각합니다.

신규 작업자는 현장경험이 많지는 않지만 필요한 안전교육과 작업교육을 이수하고 평가도 통과했습니다. 계속 숙련자를 함께 배치하면 인력운영 부담과 업무 독립 지연이 발생할 수 있습니다.

따라서 단독작업을 시작하되 필요할 때 지원받을 수 있는 체계를 유지하는 것이 적절해 보입니다.""",

        "b_if_yes_recommendation": "아니요",

        "b_if_yes_response": """저는 계획대로 단독작업을 시작하는 것이 더 적절하다고 판단합니다.

정규 작업자는 이미 필요한 안전교육과 작업교육을 이수했고 평가도 통과했습니다. 추가 동행기간이 길어지면 숙련된 작업자의 인력 활용이 제한되고 신규 작업자가 독립적으로 업무를 익히는 시점도 늦어질 수 있습니다.

따라서 정해진 기준을 충족한 만큼 필요한 지원체계를 유지하면서 단독작업을 시작하는 것이 더 적절합니다.""",

        "b_if_no_recommendation": "예",

        "b_if_no_response": """저는 일정 기간 더 숙련된 작업자와 함께 근무하는 것이 더 적절하다고 판단합니다.

교육과 평가를 통과했더라도 실제 현장에서는 교육 중 경험하지 못한 상황이 발생할 수 있습니다. 현장경험이 부족하면 예상하지 못한 상황에서 판단이나 대응이 늦어질 가능성이 있습니다.

따라서 인력운영에 일부 부담이 있더라도 현장경험을 더 확보한 뒤 단독작업을 시작하는 것이 더 적절합니다."""
    }
]


# =========================================================
# 3. CSS
# =========================================================

st.markdown(
    """
<style>

.block-container {
    max-width: 720px;
    padding-top: 3.5rem;
    padding-bottom: 5rem;
}

.chat-header {
    text-align: center;
    font-size: 24px;
    font-weight: 700;
    line-height: 1.4;
    padding-top: 0.2rem;
    margin-bottom: 3px;
}

.chat-subheader {
    text-align: center;
    font-size: 13px;
    color: #8b8b8b;
    margin-bottom: 25px;
}

@keyframes messageIn {
    0% {
        opacity: 0;
        transform: translateY(15px) scale(0.97);
    }

    70% {
        opacity: 1;
        transform: translateY(-2px) scale(1.01);
    }

    100% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.new-message {
    animation: messageIn 0.34s cubic-bezier(0.22, 1, 0.36, 1);
}

.ai-name {
    color: #909090;
    font-size: 11px;
    margin-left: 5px;
    margin-bottom: 3px;
}

.ai-row {
    display: flex;
    justify-content: flex-start;
    margin: 3px 0 12px 0;
}

.ai-bubble {
    display: inline-block;
    width: fit-content;
    max-width: 78%;
    padding: 11px 14px;
    background: #f1f3f5;
    color: #111;
    border-radius: 5px 17px 17px 17px;
    line-height: 1.55;
    font-size: 15px;
    word-break: keep-all;
    white-space: normal;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.025);
}

.user-row {
    display: flex;
    justify-content: flex-end;
    margin: 5px 0 14px 0;
}

.user-bubble {
    display: inline-block;
    width: fit-content;
    max-width: 72%;
    padding: 10px 14px;
    background: #dbeafe;
    color: #111;
    border-radius: 17px 5px 17px 17px;
    line-height: 1.5;
    font-size: 15px;
    word-break: keep-all;
    white-space: normal;
}

.stButton > button {
    min-height: 37px;
    border-radius: 19px;
    font-size: 14px;
    font-weight: 500;
    padding: 5px 14px;
    transition:
        transform 0.08s ease,
        box-shadow 0.10s ease,
        background-color 0.10s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
}

.stButton > button:active {
    transform: translateY(1px) scale(0.91);
    box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.15);
}

@media (max-width: 600px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 3rem;
    }

    .ai-bubble {
        max-width: 88%;
    }

    .user-bubble {
        max-width: 84%;
    }
}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# 4. 세션 초기화
# =========================================================

if "initialized" not in st.session_state:

    st.session_state.initialized = True

    st.session_state.participant_id = str(uuid.uuid4())[:8]
    st.session_state.group = random.choice(["A", "B"])

    st.session_state.stage = "intro_1"

    st.session_state.chat_history = []
    st.session_state.new_message_index = None

    st.session_state.responses = []
    st.session_state.question_index = 0

    # 사전 설문
    st.session_state.age = None
    st.session_state.gai_frequency = None
    st.session_state.gai_trust = None
    st.session_state.domain_knowledge = None

    # 문항 응답
    st.session_state.initial_choice = None
    st.session_state.initial_confidence = None

    st.session_state.ai_recommendation = None
    st.session_state.ai_response = None

    st.session_state.final_choice = None

    # 순수 판단시간
    st.session_state.pre_decision_start = None
    st.session_state.pre_decision_time = None

    st.session_state.post_decision_start = None
    st.session_state.post_decision_time = None

    # 저장 상태
    st.session_state.saved = False


# =========================================================
# 5. 메시지 함수
# =========================================================

def add_message(role, text):

    st.session_state.chat_history.append(
        {
            "role": role,
            "text": str(text)
        }
    )

    st.session_state.new_message_index = (
        len(st.session_state.chat_history) - 1
    )


def add_ai(text):
    add_message("ai", text)


def add_user(text):
    add_message("user", text)


# =========================================================
# 6. 채팅 출력
# =========================================================

def render_chat():

    new_index = st.session_state.new_message_index

    for index, message in enumerate(
        st.session_state.chat_history
    ):

        safe_text = html.escape(
            str(message["text"])
        ).replace(
            "\n",
            "<br>"
        )

        animation_class = (
            " new-message"
            if index == new_index
            else ""
        )

        if message["role"] == "ai":

            bubble_html = (
                '<div class="ai-name">AI 의사결정 도우미</div>'
                '<div class="ai-row">'
                f'<div class="ai-bubble{animation_class}">{safe_text}</div>'
                '</div>'
            )

        else:

            bubble_html = (
                '<div class="user-row">'
                f'<div class="user-bubble{animation_class}">{safe_text}</div>'
                '</div>'
            )

        st.markdown(
            bubble_html,
            unsafe_allow_html=True
        )

    st.session_state.new_message_index = None


# =========================================================
# 7. 자동 스크롤
# =========================================================

def scroll_bottom():

    st.components.v1.html(
        """
<script>
setTimeout(() => {

    const doc = window.parent.document;

    const main = doc.querySelector(
        '[data-testid="stAppViewContainer"]'
    );

    if (main) {
        main.scrollTo({
            top: main.scrollHeight,
            behavior: "smooth"
        });
    }

    window.parent.scrollTo({
        top: doc.body.scrollHeight,
        behavior: "smooth"
    });

}, 120);
</script>
""",
        height=0
    )


# =========================================================
# 8. AI 메시지 지연
# =========================================================

def delayed_ai(text, next_stage):

    time.sleep(MESSAGE_DELAY)

    add_ai(text)

    st.session_state.stage = next_stage

    st.rerun()


# =========================================================
# 9. AI 답변 결정
# =========================================================

def determine_ai_response():

    q = QUESTIONS[
        st.session_state.question_index
    ]

    # A집단
    if st.session_state.group == "A":

        st.session_state.ai_recommendation = (
            q["a_recommendation"]
        )

        st.session_state.ai_response = (
            q["a_response"]
        )

    # B집단
    else:

        if st.session_state.initial_choice == "예":

            st.session_state.ai_recommendation = (
                q["b_if_yes_recommendation"]
            )

            st.session_state.ai_response = (
                q["b_if_yes_response"]
            )

        else:

            st.session_state.ai_recommendation = (
                q["b_if_no_recommendation"]
            )

            st.session_state.ai_response = (
                q["b_if_no_response"]
            )


# =========================================================
# 10. 다음 문항 준비
# =========================================================

def reset_question_state():

    st.session_state.initial_choice = None
    st.session_state.initial_confidence = None

    st.session_state.ai_recommendation = None
    st.session_state.ai_response = None

    st.session_state.final_choice = None

    st.session_state.pre_decision_start = None
    st.session_state.pre_decision_time = None

    st.session_state.post_decision_start = None
    st.session_state.post_decision_time = None


# =========================================================
# 11. Google Sheets 저장
# =========================================================

def save_data():

    row = {
        "참가자번호":
            st.session_state.participant_id,

        "실험집단":
            st.session_state.group,

        "연령대":
            st.session_state.age,

        "생성형AI_사용빈도":
            st.session_state.gai_frequency,

        "생성형AI_신뢰도":
            st.session_state.gai_trust,

        "산업분야_사전지식":
            st.session_state.domain_knowledge
    }

    for response in st.session_state.responses:

        q = response["question_id"]

        row[f"문항{q}_최초선택"] = (
            response["initial_choice"]
        )

        row[f"문항{q}_최초확신도"] = (
            response["initial_confidence"]
        )

        row[f"문항{q}_AI추천"] = (
            response["ai_recommendation"]
        )

        row[f"문항{q}_최종선택"] = (
            response["final_choice"]
        )

        row[f"문항{q}_최종확신도"] = (
            response["final_confidence"]
        )

        row[f"문항{q}_선택변경여부"] = (
            response["choice_changed"]
        )

        row[f"문항{q}_AI추천수용여부"] = (
            response["ai_accepted"]
        )

        row[
            f"문항{q}_조언전_순수판단시간_초"
        ] = response["pre_decision_time"]

        row[
            f"문항{q}_조언후_순수판단시간_초"
        ] = response["post_decision_time"]

        row[
            f"문항{q}_응답완료시각"
        ] = response["timestamp"]

    response = requests.post(
        GOOGLE_SCRIPT_URL,
        json=row,
        timeout=30
    )

    response.raise_for_status()

    try:

        result = response.json()

    except ValueError:

        raise RuntimeError(
            "Google Sheets 서버가 올바른 JSON 응답을 반환하지 않았습니다."
        )

    if result.get("status") != "success":

        raise RuntimeError(
            f"Google Sheets 저장 실패: {result}"
        )


# =========================================================
# 12. 제목
# =========================================================

st.markdown(
    """
<div class="chat-header">
인간-AI 의사결정 실험
</div>
<div class="chat-subheader">
AI Decision Assistant
</div>
""",
    unsafe_allow_html=True
)


# =========================================================
# 13. 상태 머신 시작
# =========================================================

stage = st.session_state.stage


# =========================================================
# INTRO
# =========================================================

if stage == "intro_1":

    add_ai(
        """안녕하세요.

지금부터 산업 현장에서 발생할 수 있는 여러 의사결정 상황을 제시하겠습니다."""
    )

    st.session_state.stage = "intro_2"

    st.rerun()


elif stage == "intro_2":

    render_chat()

    delayed_ai(
        """각 상황을 확인한 뒤 본인의 판단에 따라 선택해 주세요.

이후 제가 해당 상황을 분석한 결과를 알려드리겠습니다.

정답을 맞히는 시험이 아니므로 본인의 판단에 따라 응답해 주세요.""",
        "intro_3"
    )


elif stage == "intro_3":

    render_chat()

    delayed_ai(
        """실험에는 약 5분이 소요됩니다.

실험 참여 및 익명 데이터 수집에 동의하시면 아래 버튼을 눌러주세요.""",
        "consent"
    )


# =========================================================
# 동의
# =========================================================

elif stage == "consent":

    render_chat()

    cols = st.columns([2.2, 1.8])

    with cols[0]:

        if st.button(
            "동의하고 실험 시작",
            use_container_width=True
        ):

            add_user(
                "동의하고 실험 시작"
            )

            st.session_state.stage = (
                "survey_intro"
            )

            st.rerun()


# =========================================================
# 사전 설문
# =========================================================

elif stage == "survey_intro":

    render_chat()

    delayed_ai(
        "실험을 시작하기 전에 몇 가지 간단한 질문을 드리겠습니다.",
        "survey_age_question"
    )


elif stage == "survey_age_question":

    render_chat()

    delayed_ai(
        "먼저 연령대를 선택해 주세요.",
        "survey_age"
    )


elif stage == "survey_age":

    render_chat()

    options = [
        "20세 미만",
        "20~29세",
        "30~39세",
        "40~49세",
        "50세 이상"
    ]

    cols = st.columns([1, 1, 1.4])

    for i, option in enumerate(options):

        with cols[i % 2]:

            if st.button(
                option,
                key=f"age_{i}",
                use_container_width=True
            ):

                st.session_state.age = option

                add_user(option)

                st.session_state.stage = (
                    "frequency_question"
                )

                st.rerun()


elif stage == "frequency_question":

    render_chat()

    delayed_ai(
        "평소 생성형 AI를 얼마나 자주 사용하십니까?",
        "frequency"
    )


elif stage == "frequency":

    render_chat()

    options = [
        "거의 사용하지 않음",
        "월 1~3회",
        "주 1~2회",
        "주 3~5회",
        "거의 매일"
    ]

    cols = st.columns([1, 1, 1.4])

    for i, option in enumerate(options):

        with cols[i % 2]:

            if st.button(
                option,
                key=f"frequency_{i}",
                use_container_width=True
            ):

                st.session_state.gai_frequency = option

                add_user(option)

                st.session_state.stage = (
                    "trust_question"
                )

                st.rerun()


elif stage == "trust_question":

    render_chat()

    delayed_ai(
        """평소 생성형 AI가 제공하는 정보를 어느 정도 신뢰하십니까?

1은 전혀 신뢰하지 않음, 7은 매우 신뢰함을 의미합니다.""",
        "trust"
    )


elif stage == "trust":

    render_chat()

    cols = st.columns(
        [1, 1, 1, 1, 1, 1, 1, 2]
    )

    for i in range(1, 8):

        with cols[i - 1]:

            if st.button(
                str(i),
                key=f"trust_{i}",
                use_container_width=True
            ):

                st.session_state.gai_trust = i

                add_user(str(i))

                st.session_state.stage = (
                    "knowledge_question"
                )

                st.rerun()


elif stage == "knowledge_question":

    render_chat()

    delayed_ai(
        """생산·품질·안전 등 산업 현장에 대한 본인의 사전 지식 수준은 어느 정도입니까?

1은 거의 지식이 없음, 7은 매우 잘 알고 있음을 의미합니다.""",
        "knowledge"
    )


elif stage == "knowledge":

    render_chat()

    cols = st.columns(
        [1, 1, 1, 1, 1, 1, 1, 2]
    )

    for i in range(1, 8):

        with cols[i - 1]:

            if st.button(
                str(i),
                key=f"knowledge_{i}",
                use_container_width=True
            ):

                st.session_state.domain_knowledge = i

                add_user(str(i))

                st.session_state.stage = (
                    "survey_complete"
                )

                st.rerun()


elif stage == "survey_complete":

    render_chat()

    delayed_ai(
        "감사합니다. 이제 의사결정 상황을 시작하겠습니다.",
        "decision_start"
    )


elif stage == "decision_start":

    render_chat()

    cols = st.columns([1.5, 2])

    with cols[0]:

        if st.button(
            "의사결정 시작",
            use_container_width=True
        ):

            add_user(
                "의사결정 시작"
            )

            st.session_state.stage = (
                "question_category"
            )

            st.rerun()


# =========================================================
# 분야 안내
# =========================================================

elif stage == "question_category":

    render_chat()

    q_index = st.session_state.question_index
    q = QUESTIONS[q_index]

    if (
        q_index > 0
        and
        QUESTIONS[q_index - 1]["category"]
        == q["category"]
    ):

        category_message = (
            f"이번에도 {q['category']} 관련 상황입니다."
        )

    else:

        category_message = (
            f"이번에는 {q['category']} 관련 상황입니다."
        )

    delayed_ai(
        category_message,
        "question_text"
    )


# =========================================================
# 최초 문제 제시
# =========================================================

elif stage == "question_text":

    render_chat()

    q = QUESTIONS[
        st.session_state.question_index
    ]

    time.sleep(MESSAGE_DELAY)

    add_ai(
        q["question"]
    )

    st.session_state.stage = (
        "initial_choice"
    )

    st.rerun()


# =========================================================
# 최초 선택
# =========================================================

elif stage == "initial_choice":

    render_chat()

    cols = st.columns([1, 1, 2.8])

    with cols[0]:

        initial_yes = st.button(
            "예",
            key=(
                f"initial_yes_"
                f"{st.session_state.question_index}"
            ),
            use_container_width=True
        )

    with cols[1]:

        initial_no = st.button(
            "아니요",
            key=(
                f"initial_no_"
                f"{st.session_state.question_index}"
            ),
            use_container_width=True
        )

    if st.session_state.pre_decision_start is None:

        st.session_state.pre_decision_start = (
            time.perf_counter()
        )

    if initial_yes:

        st.session_state.pre_decision_time = round(
            time.perf_counter()
            -
            st.session_state.pre_decision_start,
            2
        )

        st.session_state.initial_choice = "예"

        add_user("예")

        st.session_state.stage = (
            "initial_confidence_question"
        )

        st.rerun()

    if initial_no:

        st.session_state.pre_decision_time = round(
            time.perf_counter()
            -
            st.session_state.pre_decision_start,
            2
        )

        st.session_state.initial_choice = "아니요"

        add_user("아니요")

        st.session_state.stage = (
            "initial_confidence_question"
        )

        st.rerun()


# =========================================================
# 최초 확신도
# =========================================================

elif stage == "initial_confidence_question":

    render_chat()

    delayed_ai(
        """현재 판단에 얼마나 확신하십니까?

1은 전혀 확신하지 않음, 7은 매우 확신함을 의미합니다.""",
        "initial_confidence"
    )


elif stage == "initial_confidence":

    render_chat()

    cols = st.columns(
        [1, 1, 1, 1, 1, 1, 1, 2]
    )

    for i in range(1, 8):

        with cols[i - 1]:

            if st.button(
                str(i),
                key=(
                    f"initial_conf_"
                    f"{st.session_state.question_index}_"
                    f"{i}"
                ),
                use_container_width=True
            ):

                st.session_state.initial_confidence = i

                add_user(str(i))

                determine_ai_response()

                st.session_state.stage = (
                    "ai_analysis_1"
                )

                st.rerun()


# =========================================================
# AI 조언
# =========================================================

elif stage == "ai_analysis_1":

    render_chat()

    delayed_ai(
        "상황을 분석해 보았습니다.",
        "ai_analysis_2"
    )


elif stage == "ai_analysis_2":

    render_chat()

    delayed_ai(
        f"제 분석 결과, 저는 {st.session_state.ai_recommendation}를 추천합니다.",
        "ai_analysis_3"
    )


elif stage == "ai_analysis_3":

    render_chat()

    delayed_ai(
        st.session_state.ai_response,
        "ai_read_complete"
    )


# =========================================================
# AI 조언 확인 완료
# =========================================================

elif stage == "ai_read_complete":

    render_chat()

    cols = st.columns([1.4, 2])

    with cols[0]:

        if st.button(
            "최종 결정하기",
            key=(
                f"start_final_"
                f"{st.session_state.question_index}"
            ),
            use_container_width=True
        ):

            add_user(
                "최종 결정하기"
            )

            st.session_state.stage = (
                "final_question_repeat"
            )

            st.rerun()


# =========================================================
# 문제 다시 제시
# =========================================================

elif stage == "final_question_repeat":

    render_chat()

    q = QUESTIONS[
        st.session_state.question_index
    ]

    time.sleep(MESSAGE_DELAY)

    add_ai(
        q["question"]
    )

    st.session_state.stage = (
        "final_instruction"
    )

    st.rerun()


# =========================================================
# 최종 판단 안내
# =========================================================

elif stage == "final_instruction":

    render_chat()

    delayed_ai(
        "최종 판단을 내려주세요.",
        "final_choice"
    )


# =========================================================
# 최종 선택
# =========================================================

elif stage == "final_choice":

    render_chat()

    cols = st.columns([1, 1, 2.8])

    with cols[0]:

        final_yes = st.button(
            "예",
            key=(
                f"final_yes_"
                f"{st.session_state.question_index}"
            ),
            use_container_width=True
        )

    with cols[1]:

        final_no = st.button(
            "아니요",
            key=(
                f"final_no_"
                f"{st.session_state.question_index}"
            ),
            use_container_width=True
        )

    if st.session_state.post_decision_start is None:

        st.session_state.post_decision_start = (
            time.perf_counter()
        )

    if final_yes:

        st.session_state.post_decision_time = round(
            time.perf_counter()
            -
            st.session_state.post_decision_start,
            2
        )

        st.session_state.final_choice = "예"

        add_user("예")

        st.session_state.stage = (
            "final_confidence_question"
        )

        st.rerun()

    if final_no:

        st.session_state.post_decision_time = round(
            time.perf_counter()
            -
            st.session_state.post_decision_start,
            2
        )

        st.session_state.final_choice = "아니요"

        add_user("아니요")

        st.session_state.stage = (
            "final_confidence_question"
        )

        st.rerun()


# =========================================================
# 최종 확신도
# =========================================================

elif stage == "final_confidence_question":

    render_chat()

    delayed_ai(
        """최종 판단에 얼마나 확신하십니까?

1은 전혀 확신하지 않음, 7은 매우 확신함을 의미합니다.""",
        "final_confidence"
    )


elif stage == "final_confidence":

    render_chat()

    cols = st.columns(
        [1, 1, 1, 1, 1, 1, 1, 2]
    )

    for i in range(1, 8):

        with cols[i - 1]:

            if st.button(
                str(i),
                key=(
                    f"final_conf_"
                    f"{st.session_state.question_index}_"
                    f"{i}"
                ),
                use_container_width=True
            ):

                q_index = (
                    st.session_state.question_index
                )

                q = QUESTIONS[q_index]

                changed = int(
                    st.session_state.initial_choice
                    !=
                    st.session_state.final_choice
                )

                accepted = int(
                    st.session_state.final_choice
                    ==
                    st.session_state.ai_recommendation
                )

                response = {

                    "question_id":
                        q["id"],

                    "initial_choice":
                        st.session_state.initial_choice,

                    "initial_confidence":
                        st.session_state.initial_confidence,

                    "ai_recommendation":
                        st.session_state.ai_recommendation,

                    "final_choice":
                        st.session_state.final_choice,

                    "final_confidence":
                        i,

                    "choice_changed":
                        changed,

                    "ai_accepted":
                        accepted,

                    "pre_decision_time":
                        st.session_state.pre_decision_time,

                    "post_decision_time":
                        st.session_state.post_decision_time,

                    "timestamp":
                        datetime.now(
                            ZoneInfo("Asia/Seoul")
                        ).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                }

                st.session_state.responses.append(
                    response
                )

                add_user(str(i))

                next_index = q_index + 1

                if next_index >= len(QUESTIONS):

                    st.session_state.question_index = (
                        next_index
                    )

                    st.session_state.stage = (
                        "finish_1"
                    )

                else:

                    st.session_state.question_index = (
                        next_index
                    )

                    reset_question_state()

                    st.session_state.stage = (
                        "question_category"
                    )

                st.rerun()


# =========================================================
# 실험 완료
# =========================================================

elif stage == "finish_1":

    render_chat()

    delayed_ai(
        "모든 의사결정 상황이 완료되었습니다.",
        "finish_2"
    )


elif stage == "finish_2":

    render_chat()

    delayed_ai(
        """실험에 참여해 주셔서 감사합니다.

아래 종료 버튼을 눌러 실험을 마쳐주세요.""",
        "save"
    )


# =========================================================
# Google Sheets 저장
# =========================================================

elif stage == "save":

    render_chat()

    if not st.session_state.saved:

        try:

            save_data()

            st.session_state.saved = True

        except Exception as e:

            st.error(
                "응답 저장 중 오류가 발생했습니다. "
                "잠시 후 페이지를 새로고침하지 말고 다시 시도해 주세요."
            )

            st.code(str(e))

            st.stop()

    st.session_state.stage = (
        "finished"
    )

    st.rerun()


# =========================================================
# 종료
# =========================================================

elif stage == "finished":

    render_chat()

    st.markdown(
        f"""
<div style="
    text-align:center;
    color:#999;
    font-size:12px;
    margin-top:20px;
    margin-bottom:10px;
">
참가자 번호: {st.session_state.participant_id}
</div>
""",
        unsafe_allow_html=True
    )

    cols = st.columns(
        [1.2, 1, 1.2]
    )

    with cols[1]:

        if st.button(
            "종료",
            type="primary",
            use_container_width=True
        ):

            st.session_state.stage = (
                "closed"
            )

            st.rerun()


elif stage == "closed":

    render_chat()

    st.markdown(
        """
<div style="
    text-align:center;
    margin-top:25px;
    font-size:15px;
    color:#666;
    line-height:1.7;
">
실험이 종료되었습니다.<br>
참여해 주셔서 감사합니다.<br><br>
이 창을 닫으셔도 됩니다.
</div>
""",
        unsafe_allow_html=True
    )

    st.components.v1.html(
        """
<script>
setTimeout(function() {

    try {
        window.parent.close();
    } catch (e) {
    }

}, 400);
</script>
""",
        height=0
    )


# =========================================================
# 자동 스크롤
# =========================================================

scroll_bottom()