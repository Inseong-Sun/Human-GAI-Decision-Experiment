import streamlit as st
import random, uuid, time, html, requests, threading
from datetime import datetime

# 실험 설정: 처치 집단은 완전무작위, 문제는 개인별 완전무작위 순서
st.set_page_config(page_title="인간-AI 의사결정 실험", page_icon="🤖", layout="centered")
GOOGLE_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbx1lANBZTZWsF9QO7BE8N2Gs_jOhJpHBYSurHZGgSSKU4OJwEISj-g90tVB64PRB-Fuhg/exec'
MESSAGE_DELAY = 0.55

# 각 문항의 실제 제시 순서는 무작위이나 시트 저장 순서는 고정
QUESTIONS = [{'id': '단순1',
  'role': '당신은 생활용품 제조공장의 생산관리 담당자입니다.',
  'question': '최근 주요 설비에서 평소보다 큰 진동과 소음이 발생했지만 정상 작동 중이며, 즉시 중단해야 할 수준은 아닙니다. 현재 진동과 소음이 일시적인 현상인지, 부품 마모로 '
              '인해 발생한 것인지는 확인되지 않았습니다.\n'
              '\n'
              '지금 정비하면 반나절 생산이 중단되지만 고장 위험을 줄일 수 있습니다. 반면 다음 주까지 가동하면 생산 일정은 유지할 수 있지만 갑작스러운 고장으로 장기간 생산이 '
              '중단될 위험이 있습니다.',
  'choice_prompt': '어떤 방안을 선택하시겠습니까?',
  'options': ['A. 지금 즉시 정비한다.', 'B. 다음 주 예정된 날짜에 정비한다.'],
  'information': '다음은 설비의 진동과 소음이 증가했을 때 서로 다른 방식으로 대응한 과거 사례입니다.\n'
                 '\n'
                 '사례 1. 즉시 정비\n'
                 '설비의 진동과 소음이 증가하여 즉시 점검한 결과, 회전 부품의 마모가 발견되어 교체했습니다. 반나절 동안 생산이 중단됐지만, 이후에는 추가 고장 없이 정상 '
                 '가동했습니다.\n'
                 '\n'
                 '사례 2. 예정일 정비\n'
                 '다른 시기에는 비슷한 증상이 발생했지만 예정된 정비일까지 설비를 가동했습니다. 그동안 고장은 발생하지 않았으며, 이후 정기 점검에서도 즉시 교체할 수준의 결함은 '
                 '발견되지 않았습니다.',
  'evaluation': 'A안. 즉시 정비\n'
                '설비의 이상 원인을 조기에 확인하고, 부품 마모가 발견되면 고장으로 이어지기 전에 조치할 수 있습니다. 그러나 실제 결함이 크지 않더라도 반나절 동안 생산을 '
                '중단해야 하므로 불필요한 생산 차질이 발생할 수 있습니다.\n'
                '\n'
                'B안. 예정일 정비\n'
                '설비를 중단하지 않고 기존 생산 일정을 유지할 수 있어 당장의 생산 차질을 피할 수 있습니다. 그러나 실제 부품 마모가 진행 중이라면 정비를 미루는 동안 고장이 '
                '발생해 반나절보다 긴 생산 중단으로 이어질 수 있습니다.'},
 {'id': '단순2',
  'role': '당신은 여러 종류의 제품을 생산하는 제조공장의 생산관리 담당자입니다.',
  'question': '이 공장은 같은 설비에서 여러 제품을 번갈아 생산하며, 제품이 바뀔 때마다 설비 설정을 변경하느라 생산이 잠시 중단됩니다.\n'
              '\n'
              '한 번에 생산하는 양을 늘리면 설비 변경 횟수가 줄어 생산 효율이 높아지지만, 판매되지 않은 제품의 재고가 증가할 수 있습니다. 반대로 현재 생산 배치량을 유지하면 '
              '재고 부담은 적지만 설비 변경으로 인한 생산 중단이 반복됩니다.',
  'choice_prompt': '어떤 방안을 선택하시겠습니까?',
  'options': ['A. 한 번에 생산하는 양을 늘린다.', 'B. 현재 생산 배치량을 유지한다.'],
  'information': '과거 유사한 제조공장에서도 설비 변경시간과 재고 부담을 고려하여 생산 배치량을 다르게 운영한 사례가 있었습니다.\n'
                 '\n'
                 '사례 1. 배치량 확대\n'
                 '한 제조공장에서는 생산 배치량을 늘려 설비 변경 횟수를 줄이고 생산을 조기에 완료했습니다. 그러나 예상보다 주문량이 감소하면서 재고가 쌓였고, 보관 공간 부족으로 '
                 '다음 생산계획을 조정해야 했습니다.\n'
                 '\n'
                 '사례 2. 기존 배치량 유지\n'
                 '다른 제조공장에서는 주문량 변화에 대응하기 위해 기존 배치량을 유지했습니다. 갑작스러운 주문 변경에는 유연하게 대응했지만, 잦은 설비 변경으로 생산시간이 부족해 '
                 '추가 주문의 납기를 재협의해야 했습니다.',
  'evaluation': 'A안. 생산 배치량 확대\n'
                '배치량을 늘리면 설비 변경시간이 줄어 생산 효율이 높아집니다. 특히 수요가 안정적일 때 효과적이지만, 수요 변동이 크면 재고와 보관 부담이 증가할 수 있습니다.\n'
                '\n'
                'B안. 기존 배치량 유지\n'
                '기존 배치량을 유지하면 수요 변화에 유연하게 대응하고 재고 부담을 줄일 수 있습니다. 다만 설비 변경이 잦으면 생산 가능 시간이 감소해 추가 주문 대응이 어려워질 '
                '수 있습니다.'},
 {'id': '복잡1',
  'role': '당신은 자동차 부품 제조공장의 생산계획 담당자입니다.',
  'question': '현재 공장은 기존 고객의 주문을 생산하고 있으며, 설비 가동 일정에 여유가 거의 없습니다.\n'
              '\n'
              '그런데 주요 고객사에서 이번 주 안에 긴급 주문을 추가로 생산해 달라고 요청했습니다. 기존 생산을 중단하고 긴급 주문을 우선하면 주요 고객의 납기를 맞출 수 있지만 '
              '기존 고객의 납품이 지연됩니다.\n'
              '\n'
              '반면 기존 생산계획을 유지하면 기존 고객의 납기는 지킬 수 있지만 긴급 주문을 놓칠 수 있습니다.\n'
              '\n'
              '설비를 나누어 운영하면 두 주문을 일부 처리할 수 있지만, 제품 전환 과정에서 설비가 멈추고 생산 가능한 총량이 감소합니다.\n'
              '\n'
              '기존에 품질 승인을 받은 외부 협력업체를 활용하면 생산 여력은 늘어나지만, 추가 비용과 납품 전 품질 확인 시간이 필요합니다.',
  'choice_prompt': '현재 상황에서 가장 적절한 생산 운영 방안은 무엇입니까?',
  'options': ['A. 긴급 주문을 우선 생산한다.',
              'B. 기존 생산계획을 유지한다.',
              'C. 설비를 번갈아 운영해 기존 주문과 긴급 주문을 나누어 생산한다.',
              'D. 긴급 주문 일부를 외부 생산업체에 맡긴다.'],
  'information': '다음은 생산 일정에 여유가 부족한 상황에서 긴급 주문이 추가되었을 때 서로 다른 방식으로 대응한 과거 사례입니다.\n'
                 '\n'
                 '사례 1. 긴급 주문 우선 생산\n'
                 '주요 고객의 긴급 주문을 처리하기 위해 기존 생산을 중단하고 생산순서를 변경했습니다. 긴급 주문의 납기는 맞췄지만 기존 고객의 납품 일정이 지연되었으며, 지연된 '
                 '물량을 공급하는 과정에서 추가 운송비가 발생했습니다.\n'
                 '\n'
                 '사례 2. 기존 생산계획 유지\n'
                 '기존 고객과 약속한 납기를 지키기 위해 생산계획을 변경하지 않았습니다. 기존 주문은 모두 예정대로 납품했지만, 긴급 주문을 요청한 주요 고객이 일부 물량을 다른 '
                 '업체에 발주하면서 추가 주문을 확보하지 못했습니다.\n'
                 '\n'
                 '사례 3. 설비 교대 운영\n'
                 '기존 주문과 긴급 주문을 모두 처리하기 위해 설비를 번갈아 운영했습니다. 두 고객에게 일부 물량을 예정대로 공급했지만, 잦은 제품 전환으로 생산 가능 시간이 '
                 '감소하여 남은 물량의 생산 일정을 다시 조정해야 했습니다.\n'
                 '\n'
                 '사례 4. 외부 협력업체 활용\n'
                 '긴급 주문 일부를 기존에 품질 승인을 받은 협력업체에 맡겼습니다. 내부 설비의 생산 부담을 줄이고 추가 물량을 확보했지만, 외부 생산품의 품질 확인에 시간이 '
                 '소요되어 일부 물량의 출하가 지연되었습니다.',
  'evaluation': 'A안. 긴급 주문 우선 생산\n'
                '주요 고객의 긴급 납기를 확보할 수 있으며, 기존 주문에 납기 여유가 있다면 일정 조정이 가능합니다. 그러나 기존 고객의 납기 여유가 부족하면 지연 피해가 커질 수 '
                '있습니다.\n'
                '\n'
                'B안. 기존 생산계획 유지\n'
                '기존 고객의 납기를 지키고 생산계획 변경에 따른 차질을 줄일 수 있습니다. 다만 긴급 주문의 중요도가 높거나 향후 거래 가능성이 크다면 주문을 수용하지 못한 부담이 '
                '커질 수 있습니다.\n'
                '\n'
                'C안. 설비 교대 운영\n'
                '두 주문을 나누어 처리할 수 있지만, 제품 전환시간이 길수록 실제 생산 가능량이 감소합니다. 따라서 두 주문의 납기 여유가 충분하지 않다면 모두 지연될 가능성이 '
                '있습니다.\n'
                '\n'
                'D안. 외부 업체 활용\n'
                '추가 생산능력을 확보하면서 기존 생산계획의 변경을 줄일 수 있습니다. 그러나 협력업체의 생산 여력과 품질 확인에 필요한 시간이 부족하면 추가 비용을 부담하고도 '
                '납기를 맞추기 어려울 수 있습니다.'},
 {'id': '복잡2',
  'role': '당신은 물류창고의 안전관리 담당자입니다.',
  'question': '현재 창고에서는 작업자와 운반 차량이 가까워지면 경고음이 울립니다. 최근 불필요한 경고가 반복되면서 작업자들이 경고에 익숙해져 실제 위험 상황에도 늦게 반응하는 문제가 '
              '발생하고 있습니다.\n'
              '\n'
              '차량 이동이 많은 구역은 빠른 경고가 필요하지만, 이동이 적은 구역에서는 불필요한 경고가 자주 발생하고 있습니다.\n'
              '\n'
              '경보 범위를 줄이면 불필요한 경고가 감소할 수 있지만 위험을 알리는 시점도 늦어집니다. 반면 구역별로 경보 범위를 다르게 적용하면 각 구역의 특성에 맞출 수 있지만, '
              '관리 인력이 부족해 설정 오류가 발생할 가능성이 있습니다.\n'
              '\n'
              '또한 개선 예산이 제한되어 있어 LED 경광등을 추가하더라도 일부 구역에만 설치할 수 있습니다. 모든 방안은 필수 안전 기준을 충족하는 범위에서 시행됩니다.',
  'choice_prompt': '가장 적절한 운영 방안은 무엇입니까?',
  'options': ['A. 현재 경보 범위를 유지한다.',
              'B. 모든 구역의 경보 범위를 일부 줄인다.',
              'C. 차량 이동량에 따라 구역별 경보 범위를 다르게 적용한다.',
              'D. 기존 경보 범위는 유지하되, 차량 이동이 많은 구역에 LED 경광등을 추가하여 경고음과 시각적 경고를 함께 제공한다.'],
  'information': '다음은 과거 유사한 물류창고에서 경보 운영 방식을 다르게 적용한 사례입니다.\n'
                 '\n'
                 '사례 1. A안 — 경보 범위 유지\n'
                 '한 물류창고에서는 기존 경보 범위를 유지했습니다. 차량 접근을 조기에 감지했지만 반복적인 경고로 작업자들의 반응이 늦어져 추가 안전교육을 실시했습니다.\n'
                 '\n'
                 '사례 2. B안 — 경보 범위 축소\n'
                 '다른 창고에서는 경보 범위를 축소해 불필요한 경고를 줄였습니다. 그러나 차량 이동이 많은 구역에서는 위험 감지가 늦어져 해당 구역의 경보 범위를 다시 '
                 '확대했습니다.\n'
                 '\n'
                 '사례 3. C안 — 구역별 차등 적용\n'
                 '한 창고에서는 차량 이동량에 따라 경보 범위를 다르게 적용했습니다. 불필요한 경고는 줄었지만, 일부 구역에서 설정 오류가 발견되어 전체 경보 설정을 '
                 '재점검했습니다.\n'
                 '\n'
                 '사례 4. D안 — LED 경광등 추가\n'
                 '다른 창고에서는 차량 이동이 많은 구역에 LED 경광등을 추가했습니다. 작업자들의 차량 접근 인식이 개선됐지만, 미설치 구역에서는 경고 피로가 지속되어 추가 '
                 '설치를 검토했습니다.',
  'evaluation': 'A안. 경보 범위 유지\n'
                '기존 경보 범위를 유지하면 위험을 조기에 감지하고 현재 운영 체계를 그대로 활용할 수 있습니다. 그러나 불필요한 경고가 반복되면 작업자의 반응이 둔해져 실제 위험 '
                '상황에서도 대응이 늦어질 수 있습니다.\n'
                '\n'
                'B안. 경보 범위 축소\n'
                '불필요한 경고를 줄여 작업자의 반응을 개선할 수 있습니다. 하지만 위험 감지 시점도 늦어지므로, 차량 이동이 많은 구역에서는 충분한 대응 시간을 확보하지 못할 수 '
                '있습니다.\n'
                '\n'
                'C안. 구역별 차등 적용\n'
                '구역별 이동 특성에 맞춰 경보 범위를 조정하면 불필요한 경고를 줄일 수 있습니다. 그러나 구역마다 다른 기준을 관리해야 하므로 운영 부담이 증가하고, 설정 오류가 '
                '발생하면 위험 감지가 적절히 이루어지지 않을 수 있습니다.\n'
                '\n'
                'D안. LED 경광등 추가\n'
                '기존 경보 범위를 유지하면서 LED 경광등을 추가하면 조기 감지 기능을 유지하고 차량 접근을 더 쉽게 인식할 수 있습니다. 다만 설치 예산으로 인해 개선 범위가 '
                '제한되고, 미설치 구역의 경고 피로는 지속될 수 있습니다.'}]

st.markdown("""

<style>

.block-container{max-width:720px;padding-top:3.5rem;padding-bottom:5rem}.chat-header{text-align:center;font-size:24px;font-weight:700;line-height:1.4;padding-top:.2rem;margin-bottom:3px}.chat-subheader{text-align:center;font-size:13px;color:#8b8b8b;margin-bottom:25px}

@keyframes messageIn{0%{opacity:0;transform:translateY(15px) scale(.97)}70%{opacity:1;transform:translateY(-2px) scale(1.01)}100%{opacity:1;transform:translateY(0) scale(1)}}.new-message{animation:messageIn .34s cubic-bezier(.22,1,.36,1)}

.ai-message{display:flex;align-items:flex-start;gap:9px;margin:3px 0 12px}.ai-profile{width:34px;height:34px;min-width:34px;border-radius:50%;background:#eef1f4;display:flex;align-items:center;justify-content:center;border:1px solid #e0e3e7}.ai-profile svg{width:21px;height:21px}.ai-content{width:calc(100% - 43px);min-width:0}.ai-name{color:#909090;font-size:11px;margin:0 0 3px 5px}.ai-row{display:flex;justify-content:flex-start}.ai-bubble{display:inline-block;width:max-content;max-width:min(96%,760px);padding:11px 14px;background:#f1f3f5;color:#111;border-radius:5px 17px 17px 17px;line-height:1.55;font-size:15px;word-break:keep-all;overflow-wrap:break-word;white-space:normal;box-shadow:0 1px 2px rgba(0,0,0,.025)}

.user-row{display:flex;justify-content:flex-end;margin:5px 0 14px}.user-bubble{display:inline-block;width:fit-content;max-width:72%;padding:10px 14px;background:#dbeafe;color:#111;border-radius:17px 5px 17px 17px;line-height:1.5;font-size:15px;word-break:keep-all;white-space:normal}.stButton>button{min-height:37px;border-radius:19px;font-size:14px;font-weight:500;padding:5px 14px;transition:transform .08s ease,box-shadow .10s ease,background-color .10s ease}.stButton>button:hover{transform:translateY(-1px);box-shadow:0 3px 8px rgba(0,0,0,.08)}.stButton>button:active{transform:translateY(1px) scale(.91);box-shadow:inset 0 2px 5px rgba(0,0,0,.15)}

.typing{display:flex;align-items:center;gap:5px;height:18px}.typing span{width:6px;height:6px;border-radius:50%;background:#7d8791;animation:typingDot 1s infinite ease-in-out}.typing span:nth-child(2){animation-delay:.15s}.typing span:nth-child(3){animation-delay:.3s}@keyframes typingDot{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-5px);opacity:1}}

@media(max-width:600px){.block-container{padding-left:1rem;padding-right:1rem;padding-top:3rem}.ai-content{width:calc(100% - 43px)}.ai-bubble{width:max-content;max-width:100%;font-size:15px;padding:10px 12px}.user-bubble{max-width:84%}}

</style>""", unsafe_allow_html=True)




if "initialized" not in st.session_state:
    order=list(range(4)); random.shuffle(order)
    st.session_state.update(initialized=True, participant_id=str(uuid.uuid4())[:8], group=random.choice("ABCD"),
        question_order=order, question_index=0, responses={}, stage="intro_1", chat_history=[], new_message_index=None,
        age=None, gai_frequency=None, gai_trust=None, domain_knowledge=None,
        initial_choice=None, initial_confidence=None, final_choice=None, saved=False, saving=False)

ROBOT_SVG = '''<svg viewBox="0 0 24 24" fill="none" stroke="#59636e" stroke-width="1.7"><rect x="5" y="7" width="14" height="11" rx="3"/><path d="M12 4v3M9 12h.01M15 12h.01M9 15h6"/><circle cx="12" cy="3" r="1" fill="#59636e" stroke="none"/></svg>'''

def add_message(role, text):

    st.session_state.chat_history.append({"role": role, "text": str(text)})

    st.session_state.new_message_index = len(st.session_state.chat_history) - 1

def add_ai(text): add_message("ai", text)

def add_user(text): add_message("user", text)

def render_chat():

    new_index = st.session_state.new_message_index

    for index, message in enumerate(st.session_state.chat_history):

        text = html.escape(str(message["text"])).replace("\n", "<br>")

        ani = " new-message" if index == new_index else ""

        if message["role"] == "ai":

            bubble = f'<div class="ai-message"><div class="ai-profile">{ROBOT_SVG}</div><div class="ai-content"><div class="ai-name">AI 의사결정 도우미</div><div class="ai-row"><div class="ai-bubble{ani}">{text}</div></div></div></div>'

        else:

            bubble = f'<div class="user-row"><div class="user-bubble{ani}">{text}</div></div>'

        st.markdown(bubble, unsafe_allow_html=True)

    st.session_state.new_message_index = None



def scroll_bottom():

    # 현재 화면의 가장 마지막 요소를 기준으로 PC·모바일 모두 끝까지 자동 스크롤.

    st.markdown('<div id="chat-scroll-anchor" style="height:1px"></div>', unsafe_allow_html=True)

    st.components.v1.html("""<script>

    const w=window.parent,d=w.document;

    function goBottom(){

      const anchor=d.getElementById('chat-scroll-anchor');

      if(anchor) anchor.scrollIntoView({behavior:'auto',block:'end'});

      const app=d.querySelector('[data-testid="stAppViewContainer"]');

      if(app) app.scrollTop=app.scrollHeight;

      const main=d.querySelector('[data-testid="stMain"]');

      if(main) main.scrollTop=main.scrollHeight;

      w.scrollTo(0,Math.max(d.body.scrollHeight,d.documentElement.scrollHeight));

    }

    requestAnimationFrame(goBottom);

    [60,150,300,600,1000].forEach(t=>setTimeout(goBottom,t));

    </script>""", height=0)



def delayed_ai(text, next_stage):

    time.sleep(MESSAGE_DELAY); add_ai(text); st.session_state.stage = next_stage; st.rerun()




# 화면에 표시되는 문제 번호와 분석용 문항 ID를 분리
def current_question():
    return QUESTIONS[st.session_state.question_order[st.session_state.question_index]]

def reset_question_state():
    for key in ("initial_choice", "initial_confidence", "final_choice"):
        st.session_state[key]=None

# 서버 프로세스에서 동일 참가자 중복 POST 방지
@st.cache_resource
def get_save_registry():
    return {"lock": threading.Lock(), "saved_ids": set()}

def save_data():
    s=st.session_state
    row={"참가자번호":s.participant_id,"실험집단":s.group,"연령대":s.age,
         "생성형AI_사용빈도":s.gai_frequency,"생성형AI_신뢰도":s.gai_trust,
         "산업분야_사전지식":s.domain_knowledge}
    for ident in ("단순1","단순2","복잡1","복잡2"):
        r=s.responses[ident]
        for key,value in (("최초선택",r["initial_choice"]),("최초확신도",r["initial_confidence"]),
                          ("최종선택",r["final_choice"]),("최종확신도",r["final_confidence"]),
                          ("선택변경여부",r["choice_changed"]),("확신도변화",r["confidence_change"])):
            row[f"{ident}_{key}"]=value
    row["응답일시"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response=requests.post(GOOGLE_SCRIPT_URL,json=row,timeout=30)
    response.raise_for_status()
    try: result=response.json()
    except ValueError: raise RuntimeError("Google Sheets 서버에서 JSON 응답을 받지 못했습니다.")
    if result.get("status")!="success": raise RuntimeError(f"Google Sheets 저장 실패: {result}")

def save_data_once():
    registry=get_save_registry(); pid=st.session_state.participant_id
    with registry["lock"]:
        if pid in registry["saved_ids"]: return False
        save_data(); registry["saved_ids"].add(pid)
        return True

def choice_buttons(prefix):
    options=current_question()["options"]
    if len(options)==2:
        cols=st.columns([1,1,0.3])
    else:
        cols=st.columns([1])
    selected=None
    for i,option in enumerate(options):
        with cols[i if len(options)==2 else 0]:
            if st.button("ABCD"[i],key=f"{prefix}_{st.session_state.question_index}_{i}",use_container_width=True):
                selected="ABCD"[i]
    return selected

def rating_buttons(prefix):
    cols=st.columns([1,1,1,1,1,1,1,2])
    for i in range(1,8):
        with cols[i-1]:
            if st.button(str(i),key=f"{prefix}_{st.session_state.question_index}_{i}",use_container_width=True): return i
    return None

st.markdown('<div class="chat-header">인간-AI 의사결정 실험</div><div class="chat-subheader">AI Decision Assistant</div>',unsafe_allow_html=True)
stage=st.session_state.stage

if stage=="intro_1":
    add_ai("안녕하세요.\n지금부터 산업 현장에서 발생할 수 있는 의사결정 상황을 제시하겠습니다.")
    st.session_state.stage="intro_2"; st.rerun()
elif stage=="intro_2":
    render_chat(); delayed_ai("각 상황을 읽고 본인의 판단에 따라 선택해 주세요.\n이후 제공되는 정보를 확인하고 다시 선택하게 됩니다.\n문항은 총 4문제이며, 정답을 맞히는 시험이 아닙니다.","intro_3")
elif stage=="intro_3":
    render_chat(); delayed_ai("실험 참여 및 익명 데이터 수집에 동의하시면 아래 버튼을 눌러주세요.","consent")
elif stage=="consent":
    render_chat()
    if st.button("동의하고 실험 시작"):
        add_user("동의하고 실험 시작"); st.session_state.stage="survey_intro"; st.rerun()
elif stage=="survey_intro":
    render_chat(); delayed_ai("실험을 시작하기 전에 몇 가지 간단한 질문을 드리겠습니다.","survey_age_question")
elif stage=="survey_age_question":
    render_chat(); delayed_ai("먼저 연령대를 선택해 주세요.","survey_age")
elif stage=="survey_age":
    render_chat(); opts=["29세 이하","30세부터 49세","50세 이상"]
    cols=st.columns(3)
    for i,opt in enumerate(opts):
        with cols[i]:
            if st.button(opt,key=f"age_{i}",use_container_width=True):
                st.session_state.age=opt; add_user(opt); st.session_state.stage="frequency_question"; st.rerun()
elif stage=="frequency_question":
    render_chat(); delayed_ai("평소 생성형 AI를 얼마나 자주 사용하십니까?","frequency")
elif stage=="frequency":
    # 기존 실험과 동일한 5개 빈도 범주를 순서대로 표시합니다.
    render_chat(); options=["거의 사용하지 않음","월 1~3회","주 1~2회","주 3~5회","거의 매일"]
    for i,option in enumerate(options):
        if st.button(option,key=f"frequency_{i}",use_container_width=True):
            st.session_state.gai_frequency=option; add_user(option); st.session_state.stage="trust_question"; st.rerun()
elif stage=="trust_question":
    render_chat(); delayed_ai("평소 생성형 AI가 제공하는 정보를 어느 정도 신뢰하십니까?\n1은 전혀 신뢰하지 않음, 7은 매우 신뢰함을 의미합니다.","trust")
elif stage=="trust":
    render_chat(); value=rating_buttons("trust")
    if value is not None:
        st.session_state.gai_trust=value; add_user(str(value)); st.session_state.stage="knowledge_question"; st.rerun()
elif stage=="knowledge_question":
    render_chat(); delayed_ai("생산·품질·안전 등 산업 현장에 대한 본인의 사전 지식 수준은 어느 정도입니까?\n1은 거의 지식이 없음, 7은 매우 잘 알고 있음을 의미합니다.","knowledge")
elif stage=="knowledge":
    render_chat(); value=rating_buttons("knowledge")
    if value is not None:
        st.session_state.domain_knowledge=value; add_user(str(value)); st.session_state.stage="survey_complete"; st.rerun()
elif stage=="survey_complete":
    render_chat(); delayed_ai("감사합니다. 이제 상황과 대안을 제시하겠습니다.","decision_start")
elif stage=="decision_start":
    render_chat()
    if st.button("의사결정 시작"):
        add_user("의사결정 시작"); st.session_state.stage="question_category"; st.rerun()
elif stage=="question_category":
    render_chat(); delayed_ai(f"{st.session_state.question_index+1}번 문항입니다.","question_role")
elif stage=="question_role":
    render_chat(); delayed_ai(current_question()["role"],"question_text")
elif stage=="question_text":
    render_chat(); q=current_question(); delayed_ai(q["question"]+"\n"+q["choice_prompt"],"question_options")
elif stage=="question_options":
    render_chat(); delayed_ai("\n".join(current_question()["options"]),"initial_choice")
elif stage=="initial_choice":
    render_chat(); value=choice_buttons("initial")
    if value is not None:
        st.session_state.initial_choice=value; add_user(value); st.session_state.stage="initial_confidence_question"; st.rerun()
elif stage=="initial_confidence_question":
    render_chat(); delayed_ai("현재 판단에 얼마나 확신하십니까?\n1은 전혀 확신하지 않음, 7은 매우 확신함을 의미합니다.","initial_confidence")
elif stage=="initial_confidence":
    render_chat(); value=rating_buttons("initial_conf")
    if value is not None:
        st.session_state.initial_confidence=value; add_user(str(value)); st.session_state.stage="support_start"; st.rerun()
elif stage=="support_start":
    render_chat()
    # A집단에는 AI 정보와 대안평가를 전혀 노출하지 않음
    if st.session_state.group=="A": st.session_state.stage="final_instruction"; st.rerun()
    add_ai("상황을 분석해 보겠습니다."); st.session_state.stage="support_typing"; st.rerun()
elif stage=="support_typing":
    render_chat(); st.markdown(f'<div class="ai-message"><div class="ai-profile">{ROBOT_SVG}</div><div class="ai-content"><div class="ai-name">AI 의사결정 도우미</div><div class="ai-row"><div class="ai-bubble"><div class="typing"><span></span><span></span><span></span></div></div></div></div></div>',unsafe_allow_html=True)
    scroll_bottom(); time.sleep(3); st.session_state.stage="support_info"; st.rerun()
elif stage=="support_info":
    render_chat()
    if st.session_state.group in ("B", "D"):
        st.session_state.support_parts = ["AI 분석 결과 — 과거 유사 사례"] + current_question()["information"].split("\n\n")
        st.session_state.support_part_index = 0
        st.session_state.stage = "support_info_parts"
    else:
        st.session_state.stage = "support_eval"
    st.rerun()
elif stage=="support_info_parts":
    render_chat()
    i = st.session_state.support_part_index
    parts = st.session_state.support_parts
    if i < len(parts):
        delayed_ai(parts[i], "support_info_next")
    else:
        st.session_state.stage = "support_eval"; st.rerun()
elif stage=="support_info_next":
    st.session_state.support_part_index += 1
    st.session_state.stage = "support_info_parts"
    st.rerun()
elif stage=="support_eval":
    render_chat()
    if st.session_state.group in ("C", "D"):
        st.session_state.support_parts = ["AI 분석 결과 — 대안별 평가"] + current_question()["evaluation"].split("\n\n")
        st.session_state.support_part_index = 0
        st.session_state.stage = "support_eval_parts"
    else:
        st.session_state.stage = "support_complete"
    st.rerun()
elif stage=="support_eval_parts":
    render_chat()
    i = st.session_state.support_part_index
    parts = st.session_state.support_parts
    if i < len(parts):
        delayed_ai(parts[i], "support_eval_next")
    else:
        st.session_state.stage = "support_complete"; st.rerun()
elif stage=="support_eval_next":
    st.session_state.support_part_index += 1
    st.session_state.stage = "support_eval_parts"
    st.rerun()
elif stage=="support_complete":
    render_chat()
    if st.button("다음으로"):
        add_user("다음으로"); st.session_state.stage="final_instruction"; st.rerun()
elif stage=="final_instruction":
    render_chat(); delayed_ai("다시 선택해 주세요.","final_question_repeat")
elif stage=="final_question_repeat":
    render_chat(); q=current_question(); delayed_ai(q["question"]+"\n"+q["choice_prompt"],"final_options")
elif stage=="final_options":
    render_chat(); delayed_ai("\n".join(current_question()["options"]),"final_choice")
elif stage=="final_choice":
    render_chat(); value=choice_buttons("final")
    if value is not None:
        st.session_state.final_choice=value; add_user(value); st.session_state.stage="final_confidence_question"; st.rerun()
elif stage=="final_confidence_question":
    render_chat(); delayed_ai("최종 판단에 얼마나 확신하십니까?\n1은 전혀 확신하지 않음, 7은 매우 확신함을 의미합니다.","final_confidence")
elif stage=="final_confidence":
    render_chat(); value=rating_buttons("final_conf")
    if value is not None:
        s=st.session_state; q=current_question()
        s.responses[q["id"]]={"initial_choice":s.initial_choice,"initial_confidence":s.initial_confidence,
            "final_choice":s.final_choice,"final_confidence":value,
            "choice_changed":int(s.initial_choice!=s.final_choice),
            "confidence_change":value-s.initial_confidence}
        add_user(str(value)); s.question_index+=1
        if s.question_index==4: s.stage="finish_1"
        else: reset_question_state(); s.stage="question_category"
        st.rerun()
elif stage=="finish_1":
    render_chat(); delayed_ai("모든 의사결정 상황이 완료되었습니다.","finish_2")
elif stage=="finish_2":
    render_chat(); delayed_ai("실험에 참여해 주셔서 감사합니다.\n오늘도 좋은 하루 보내세요.\n아래 종료 버튼을 눌러 실험을 마쳐주세요.","finished")
elif stage=="finished":
    render_chat(); st.markdown(f'<div style="text-align:center;color:#999;font-size:12px;margin-top:20px;margin-bottom:10px">참가자 번호: {st.session_state.participant_id}</div>',unsafe_allow_html=True)
    cols=st.columns([1.2,1,1.2])
    with cols[1]:
        if st.button("종료",type="primary",use_container_width=True,disabled=st.session_state.saving or st.session_state.saved):
            st.session_state.saving=True; st.session_state.stage="saving"; st.rerun()
elif stage=="saving":
    render_chat()
    if not st.session_state.saved:
        try:
            save_data_once(); st.session_state.saved=True; st.session_state.saving=False; st.session_state.stage="closed"; st.rerun()
        except Exception as e:
            st.session_state.saving=False; st.session_state.stage="finished"
            st.error("응답 저장 중 오류가 발생했습니다. 종료 버튼을 다시 눌러주세요."); st.code(str(e)); st.stop()
    else:
        st.session_state.saving=False; st.session_state.stage="closed"; st.rerun()
elif stage=="closed":
    render_chat(); st.markdown('<div style="text-align:center;margin-top:25px;font-size:15px;color:#666;line-height:1.7">실험이 종료되었습니다.<br>참여해 주셔서 감사합니다.<br>이 창을 닫으셔도 됩니다.</div>',unsafe_allow_html=True)
scroll_bottom()
