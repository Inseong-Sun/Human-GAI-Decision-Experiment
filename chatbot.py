import streamlit as st
import random, uuid, time, html, requests

# 1. 기본 설정: 기존 Streamlit 화면과 Google Sheets 연동 방식은 유지
st.set_page_config(page_title="인간-AI 의사결정 실험", page_icon="🤖", layout="centered")
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbx1lANBZTZWsF9QO7BE8N2Gs_jOhJpHBYSurHZGgSSKU4OJwEISj-g90tVB64PRB-Fuhg/exec"
MESSAGE_DELAY = 0.55

# 2. 2차 파일럿 문항: 본문제1 → 본문제2 → 더미 → 본문제3
# 본문제는 A집단=사전설정 추천, B집단=초기선택 반대 추천. 더미는 두 집단 모두 초기선택을 옹호하며 저장하지 않음.
QUESTIONS = [
    {
        "id": 1, "category": "생산관리", "dummy": False,
        "role": "당신은 한 제조공장의 생산관리 담당자입니다.",
        "question": """공장에서는 여러 제품을 같은 설비에서 번갈아 생산하며, 제품이 바뀔 때마다 설비 설정을 변경해야 해 일정 시간 생산이 중단됩니다.
한 번에 생산하는 양을 늘리면 제품 전환 횟수가 줄어 설비를 더 효율적으로 사용할 수 있습니다. 반면 수요가 예상과 달라질 경우 재고가 늘어나고, 다른 제품의 주문 변화에 빠르게 대응하기 어려울 수 있습니다.""",
        "choice_prompt": "당신이라면 한 번에 생산하는 양을 늘리시겠습니까?",
        "options": "예: 생산 배치량을 늘린다.\n아니요: 현재 생산 배치량을 유지한다.",
        "yes_response": """저는 생산 배치량을 늘리는 것이 좋다고 생각합니다.
제품 전환 횟수를 줄이면 설비가 멈추는 시간을 줄이고 같은 시간에 더 많은 제품을 생산할 수 있기 때문입니다. 재고 증가 가능성은 있지만 생산효율을 높이는 것이 더 중요하다고 판단됩니다.""",
        "no_response": """저는 현재 생산 배치량을 유지하는 것이 좋다고 생각합니다.
생산량을 늘리면 수요가 달라졌을 때 불필요한 재고가 발생하고 다른 제품의 주문 변화에 대응하기 어려울 수 있기 때문입니다. 생산계획의 유연성을 유지하는 것이 더 중요하다고 판단됩니다.""",
        "a_recommendation": "예"
    },
    {
        "id": 2, "category": "품질관리", "dummy": False,
        "role": "당신은 한 제조공장의 품질관리 담당자입니다.",
        "question": """현재 제품은 회사의 품질 기준을 충족하고 있으며 최근 큰 품질 문제도 발생하지 않았습니다. 한편 일부 고객들은 이전보다 높은 수준의 품질을 요구하고 있습니다.
품질 기준을 강화하면 제품 간 품질 편차를 줄이고 보다 안정적인 품질을 제공할 수 있습니다. 반면 검사와 재작업이 늘어나 비용과 시간이 증가하고, 사용에 문제가 없는 제품까지 불량으로 처리될 수 있습니다.""",
        "choice_prompt": "당신이라면 현재보다 품질 기준을 강화하시겠습니까?",
        "options": "예: 품질 기준을 강화한다.\n아니요: 현재 품질 기준을 유지한다.",
        "yes_response": """저는 품질 기준을 강화하는 것이 좋다고 생각합니다.
기준을 강화하면 제품 간 품질 편차를 줄이고 고객에게 보다 안정적인 품질을 제공할 수 있기 때문입니다. 추가적인 검사 부담보다 제품의 품질 신뢰성을 높이는 것이 더 중요하다고 판단됩니다.""",
        "no_response": """저는 현재 품질 기준을 유지하는 것이 좋다고 생각합니다.
현재 기준에서도 제품에 문제가 없다면 기준 강화는 불필요한 검사와 재작업을 증가시킬 수 있기 때문입니다. 현재의 품질을 유지하면서 비용과 생산효율을 관리하는 것이 더 합리적이라고 판단됩니다.""",
        "a_recommendation": "아니요"
    },
    {
        "id": "D1", "category": "품질관리", "dummy": True,
        "role": "당신은 한 제조공장의 생산관리 담당자입니다.",
        "question": """현재 조립공정에서는 작업자가 여러 종류의 부품 중 필요한 부품을 선택해 정해진 방향으로 조립하고 있습니다. 간혹 비슷한 부품을 잘못 선택하거나 방향을 반대로 조립하는 실수가 발생합니다.
오류방지 장치를 적용하면 올바른 부품과 방향일 때만 조립이 가능해 작업자의 오조립을 줄일 수 있습니다. 반면 제품 종류가 변경될 때마다 장치를 다시 설정해야 하고, 예외 작업이나 재작업에 유연하게 대응하기 어려울 수 있습니다.""",
        "choice_prompt": "당신이라면 오류방지 장치를 적용하시겠습니까?",
        "options": "예: 오류방지 장치를 적용한다.\n아니요: 현재 작업방식을 유지한다.",
        "yes_response": """저는 오류방지 장치를 적용하는 것이 좋다고 생각합니다.
장치를 적용하면 잘못된 부품 선택이나 조립 방향 오류를 공정에서 바로 차단할 수 있기 때문입니다. 추가적인 설정 부담보다 작업자의 실수로 발생하는 오조립을 줄이는 것이 더 중요하다고 판단됩니다.""",
        "no_response": """저는 현재 작업방식을 유지하는 것이 좋다고 생각합니다.
오류방지 장치를 적용하면 제품 변경이나 예외 작업이 발생할 때마다 추가적인 설정과 조정이 필요할 수 있기 때문입니다. 작업자의 판단을 활용하면서 공정의 유연성을 유지하는 것이 더 합리적이라고 판단됩니다."""
    },
    {
        "id": 3, "category": "산업안전", "dummy": False,
        "role": "당신은 한 제조공장의 안전관리 담당자입니다.",
        "question": """공장에서는 설비의 온도와 진동을 감지해 일정 수준을 넘으면 작업자에게 경보를 보내는 센서를 사용하고 있습니다. 회사에서는 이상 징후를 더 빠르게 파악하기 위해 경보 기준을 현재보다 민감하게 조정하는 방안을 검토하고 있습니다.
경보 기준을 민감하게 하면 작은 이상 징후를 더 빨리 발견할 수 있습니다. 반면 정상적인 변화에도 경보가 발생해 작업이 자주 중단되고, 반복되는 오경보로 작업자가 경보에 둔감해질 수 있습니다.""",
        "choice_prompt": "당신이라면 경보 기준을 현재보다 민감하게 조정하시겠습니까?",
        "options": "예: 경보 기준을 민감하게 조정한다.\n아니요: 현재 경보 기준을 유지한다.",
        "yes_response": """저는 경보 기준을 더 민감하게 조정하는 것이 좋다고 생각합니다.
작은 이상 징후를 조기에 발견하면 설비 문제가 커지기 전에 대응할 수 있고 잠재적인 위험도 더 빠르게 파악할 수 있기 때문입니다. 일부 오경보가 발생하더라도 이상 상황을 조기에 확인하는 것이 더 중요하다고 판단됩니다.""",
        "no_response": """저는 현재 경보 기준을 유지하는 것이 좋다고 생각합니다.
경보가 지나치게 민감하면 정상적인 변화에도 작업이 반복적으로 중단되고, 잦은 오경보로 실제 위험 신호에 둔감해질 수 있기 때문입니다. 경보의 신뢰성을 유지하는 것이 더 중요하다고 판단됩니다.""",
        "a_recommendation": "예"
    }
]

# 3. 화면 스타일: 기존 인터페이스를 유지하고 AI 프로필 아이콘만 추가
st.markdown("""
<style>
.block-container{max-width:720px;padding-top:3.5rem;padding-bottom:5rem}.chat-header{text-align:center;font-size:24px;font-weight:700;line-height:1.4;padding-top:.2rem;margin-bottom:3px}.chat-subheader{text-align:center;font-size:13px;color:#8b8b8b;margin-bottom:25px}
@keyframes messageIn{0%{opacity:0;transform:translateY(15px) scale(.97)}70%{opacity:1;transform:translateY(-2px) scale(1.01)}100%{opacity:1;transform:translateY(0) scale(1)}}.new-message{animation:messageIn .34s cubic-bezier(.22,1,.36,1)}
.ai-message{display:flex;align-items:flex-start;gap:9px;margin:3px 0 12px}.ai-profile{width:34px;height:34px;min-width:34px;border-radius:50%;background:#eef1f4;display:flex;align-items:center;justify-content:center;border:1px solid #e0e3e7}.ai-profile svg{width:21px;height:21px}.ai-content{max-width:calc(100% - 43px)}.ai-name{color:#909090;font-size:11px;margin:0 0 3px 5px}.ai-row{display:flex;justify-content:flex-start}.ai-bubble{display:inline-block;width:fit-content;max-width:78%;padding:11px 14px;background:#f1f3f5;color:#111;border-radius:5px 17px 17px 17px;line-height:1.55;font-size:15px;word-break:keep-all;white-space:normal;box-shadow:0 1px 2px rgba(0,0,0,.025)}
.user-row{display:flex;justify-content:flex-end;margin:5px 0 14px}.user-bubble{display:inline-block;width:fit-content;max-width:72%;padding:10px 14px;background:#dbeafe;color:#111;border-radius:17px 5px 17px 17px;line-height:1.5;font-size:15px;word-break:keep-all;white-space:normal}.stButton>button{min-height:37px;border-radius:19px;font-size:14px;font-weight:500;padding:5px 14px;transition:transform .08s ease,box-shadow .10s ease,background-color .10s ease}.stButton>button:hover{transform:translateY(-1px);box-shadow:0 3px 8px rgba(0,0,0,.08)}.stButton>button:active{transform:translateY(1px) scale(.91);box-shadow:inset 0 2px 5px rgba(0,0,0,.15)}
.typing{display:flex;align-items:center;gap:5px;height:18px}.typing span{width:6px;height:6px;border-radius:50%;background:#7d8791;animation:typingDot 1s infinite ease-in-out}.typing span:nth-child(2){animation-delay:.15s}.typing span:nth-child(3){animation-delay:.3s}@keyframes typingDot{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-5px);opacity:1}}
@media(max-width:600px){.block-container{padding-left:1rem;padding-right:1rem;padding-top:3rem}.ai-bubble{max-width:88%}.user-bubble{max-width:84%}}
</style>""", unsafe_allow_html=True)

# 4. 세션 초기화: 최초 접속 시점부터 전체 사용시간 측정 시작
if "initialized" not in st.session_state:
    st.session_state.update(initialized=True, participant_id=str(uuid.uuid4())[:8], group=random.choice(["A", "B"]), stage="intro_1", chat_history=[], new_message_index=None, responses=[], question_index=0, age=None, gai_frequency=None, gai_trust=None, domain_knowledge=None, initial_choice=None, initial_confidence=None, ai_recommendation=None, ai_response=None, final_choice=None, pre_decision_start=None, pre_decision_time=None, post_decision_start=None, post_decision_time=None, experiment_start=time.perf_counter(), total_use_time=None, saved=False)

# 5. 채팅 출력 및 자동 스크롤
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
    # PC에서도 새 메시지·버튼이 생길 때 최신 영역이 보이도록 여러 시점에 하단 이동
    st.components.v1.html("""<script>
    function goBottom(){const d=window.parent.document;const c=d.querySelector('[data-testid="stAppViewContainer"]');if(c)c.scrollTo({top:c.scrollHeight,behavior:'smooth'});window.parent.scrollTo({top:d.body.scrollHeight,behavior:'smooth'});}
    [80,220,500].forEach(t=>setTimeout(goBottom,t));
    </script>""", height=0)

def delayed_ai(text, next_stage):
    time.sleep(MESSAGE_DELAY); add_ai(text); st.session_state.stage = next_stage; st.rerun()

# 6. 실험 로직: 더미는 집단과 무관하게 초기선택을 지지, 본문제의 기존 A/B 로직은 유지
def determine_ai_response():
    q = QUESTIONS[st.session_state.question_index]
    if q["dummy"]:
        rec = st.session_state.initial_choice
    elif st.session_state.group == "A":
        rec = q["a_recommendation"]
    else:
        rec = "아니요" if st.session_state.initial_choice == "예" else "예"
    st.session_state.ai_recommendation = rec
    st.session_state.ai_response = q["yes_response"] if rec == "예" else q["no_response"]

def reset_question_state():
    for key in ["initial_choice", "initial_confidence", "ai_recommendation", "ai_response", "final_choice", "pre_decision_start", "pre_decision_time", "post_decision_start", "post_decision_time"]:
        st.session_state[key] = None

# 7. Google Sheets 저장: 문항별 완료시각 제거, 마지막 열에 전체 사용시간(초) 저장
# 더미문항은 화면상 동일하게 진행하지만 responses에 넣지 않으므로 시트에 기록되지 않음.
def save_data():
    row = {"참가자번호": st.session_state.participant_id, "실험집단": st.session_state.group, "연령대": st.session_state.age, "생성형AI_사용빈도": st.session_state.gai_frequency, "생성형AI_신뢰도": st.session_state.gai_trust, "산업분야_사전지식": st.session_state.domain_knowledge}
    for r in st.session_state.responses:
        q = r["question_id"]
        row.update({f"문항{q}_최초선택": r["initial_choice"], f"문항{q}_최초확신도": r["initial_confidence"], f"문항{q}_AI추천": r["ai_recommendation"], f"문항{q}_최종선택": r["final_choice"], f"문항{q}_최종확신도": r["final_confidence"], f"문항{q}_선택변경여부": r["choice_changed"], f"문항{q}_AI추천수용여부": r["ai_accepted"], f"문항{q}_조언전_순수판단시간_초": r["pre_decision_time"], f"문항{q}_조언후_순수판단시간_초": r["post_decision_time"]})
    row["전체_사용시간_초"] = st.session_state.total_use_time
    response = requests.post(GOOGLE_SCRIPT_URL, json=row, timeout=30); response.raise_for_status()
    try: result = response.json()
    except ValueError: raise RuntimeError("Google Sheets 서버가 올바른 JSON 응답을 반환하지 않았습니다.")
    if result.get("status") != "success": raise RuntimeError(f"Google Sheets 저장 실패: {result}")

# 8. 반복 UI 함수: 기존 버튼 모양과 동작은 유지하면서 중복 코드만 축약
def choice_buttons(prefix):
    cols = st.columns([1, 1, 2.8]); result = None
    with cols[0]:
        if st.button("예", key=f"{prefix}_yes_{st.session_state.question_index}", use_container_width=True): result = "예"
    with cols[1]:
        if st.button("아니요", key=f"{prefix}_no_{st.session_state.question_index}", use_container_width=True): result = "아니요"
    return result

def rating_buttons(prefix):
    cols = st.columns([1,1,1,1,1,1,1,2])
    for i in range(1, 8):
        with cols[i-1]:
            if st.button(str(i), key=f"{prefix}_{st.session_state.question_index}_{i}", use_container_width=True): return i
    return None

# 9. 제목 및 상태 머신: 참가자에게 보이는 기존 진행방식은 그대로 유지
st.markdown('<div class="chat-header">인간-AI 의사결정 실험</div><div class="chat-subheader">AI Decision Assistant</div>', unsafe_allow_html=True)
stage = st.session_state.stage

if stage == "intro_1":
    add_ai("안녕하세요.\n지금부터 산업 현장에서 발생할 수 있는 여러 의사결정 상황을 제시하겠습니다."); st.session_state.stage = "intro_2"; st.rerun()
elif stage == "intro_2":
    render_chat(); delayed_ai("각 상황을 확인한 뒤 본인의 판단에 따라 선택해 주세요.\n이후 제가 해당 상황을 분석한 결과를 알려드리겠습니다.\n문항은 총 4문제입니다.\n정답을 맞히는 시험이 아니므로 본인의 판단에 따라 응답해 주세요.", "intro_3")
elif stage == "intro_3":
    render_chat(); delayed_ai("실험에는 약 5분이 소요됩니다.\n실험 참여 및 익명 데이터 수집에 동의하시면 아래 버튼을 눌러주세요.", "consent")
elif stage == "consent":
    render_chat(); cols = st.columns([2.2,1.8])
    with cols[0]:
        if st.button("동의하고 실험 시작", use_container_width=True): add_user("동의하고 실험 시작"); st.session_state.stage="survey_intro"; st.rerun()
elif stage == "survey_intro":
    render_chat(); delayed_ai("실험을 시작하기 전에 몇 가지 간단한 질문을 드리겠습니다.", "survey_age_question")
elif stage == "survey_age_question":
    render_chat(); delayed_ai("먼저 연령대를 선택해 주세요.", "survey_age")
elif stage == "survey_age":
    render_chat(); options=["29세 이하","30세부터 49세","50세 이상"]; cols=st.columns([1,1,1])
    for i, option in enumerate(options):
        with cols[i]:
            if st.button(option,key=f"age_{i}",use_container_width=True): st.session_state.age=option; add_user(option); st.session_state.stage="frequency_question"; st.rerun()
elif stage == "frequency_question":
    render_chat(); delayed_ai("평소 생성형 AI를 얼마나 자주 사용하십니까?", "frequency")
elif stage == "frequency":
    render_chat(); options=["거의 사용하지 않음","월 1~3회","주 1~2회","주 3~5회","거의 매일"]; cols=st.columns([1,1,1.4])
    for i, option in enumerate(options):
        with cols[i%2]:
            if st.button(option,key=f"frequency_{i}",use_container_width=True): st.session_state.gai_frequency=option; add_user(option); st.session_state.stage="trust_question"; st.rerun()
elif stage == "trust_question":
    render_chat(); delayed_ai("평소 생성형 AI가 제공하는 정보를 어느 정도 신뢰하십니까?\n1은 전혀 신뢰하지 않음, 7은 매우 신뢰함을 의미합니다.", "trust")
elif stage == "trust":
    render_chat(); value=rating_buttons("trust")
    if value: st.session_state.gai_trust=value; add_user(str(value)); st.session_state.stage="knowledge_question"; st.rerun()
elif stage == "knowledge_question":
    render_chat(); delayed_ai("생산·품질·안전 등 산업 현장에 대한 본인의 사전 지식 수준은 어느 정도입니까?\n1은 거의 지식이 없음, 7은 매우 잘 알고 있음을 의미합니다.", "knowledge")
elif stage == "knowledge":
    render_chat(); value=rating_buttons("knowledge")
    if value: st.session_state.domain_knowledge=value; add_user(str(value)); st.session_state.stage="survey_complete"; st.rerun()
elif stage == "survey_complete":
    render_chat(); delayed_ai("감사합니다. 이제 의사결정 상황을 시작하겠습니다.", "decision_start")
elif stage == "decision_start":
    render_chat(); cols=st.columns([1.5,2])
    with cols[0]:
        if st.button("의사결정 시작",use_container_width=True): add_user("의사결정 시작"); st.session_state.stage="question_category"; st.rerun()
elif stage == "question_category":
    render_chat(); delayed_ai(f"{st.session_state.question_index + 1}번 문항입니다.", "question_role")
elif stage == "question_role":
    render_chat(); delayed_ai(QUESTIONS[st.session_state.question_index]["role"], "question_text")
elif stage == "question_text":
    render_chat(); delayed_ai(QUESTIONS[st.session_state.question_index]["question"], "question_options")
elif stage == "question_options":
    render_chat(); q=QUESTIONS[st.session_state.question_index]; delayed_ai(f"{q['choice_prompt']}\n{q['options']}", "initial_choice")
elif stage == "initial_choice":
    render_chat()
    if st.session_state.pre_decision_start is None: st.session_state.pre_decision_start=time.perf_counter()
    value=choice_buttons("initial")
    if value:
        st.session_state.pre_decision_time=round(time.perf_counter()-st.session_state.pre_decision_start,2); st.session_state.initial_choice=value; add_user(value); st.session_state.stage="initial_confidence_question"; st.rerun()
elif stage == "initial_confidence_question":
    render_chat(); delayed_ai("현재 판단에 얼마나 확신하십니까?\n1은 전혀 확신하지 않음, 7은 매우 확신함을 의미합니다.", "initial_confidence")
elif stage == "initial_confidence":
    render_chat(); value=rating_buttons("initial_conf")
    if value: st.session_state.initial_confidence=value; add_user(str(value)); determine_ai_response(); st.session_state.stage="ai_analysis_1"; st.rerun()
elif stage == "ai_analysis_1":
    render_chat(); add_ai("상황을 분석해 보겠습니다."); st.session_state.stage="ai_typing"; st.rerun()
elif stage == "ai_typing":
    render_chat(); st.markdown(f'<div class="ai-message"><div class="ai-profile">{ROBOT_SVG}</div><div class="ai-content"><div class="ai-name">AI 의사결정 도우미</div><div class="ai-row"><div class="ai-bubble"><div class="typing"><span></span><span></span><span></span></div></div></div></div></div>', unsafe_allow_html=True); scroll_bottom(); time.sleep(2); st.session_state.stage="ai_analysis_2"; st.rerun()
elif stage == "ai_analysis_2":
    render_chat(); delayed_ai(f"제 분석 결과, 저는 {st.session_state.ai_recommendation}를 추천합니다.", "ai_analysis_3")
elif stage == "ai_analysis_3":
    render_chat(); delayed_ai(st.session_state.ai_response, "ai_read_complete")
elif stage == "ai_read_complete":
    render_chat(); cols=st.columns([1.4,2])
    with cols[0]:
        if st.button("최종 결정하기",key=f"start_final_{st.session_state.question_index}",use_container_width=True): add_user("최종 결정하기"); st.session_state.stage="final_question_repeat"; st.rerun()
elif stage == "final_question_repeat":
    render_chat(); q=QUESTIONS[st.session_state.question_index]; delayed_ai(f"{q['question']}\n\n{q['choice_prompt']}\n{q['options']}", "final_instruction")
elif stage == "final_instruction":
    render_chat(); delayed_ai("최종 판단을 내려주세요.", "final_choice")
elif stage == "final_choice":
    render_chat()
    if st.session_state.post_decision_start is None: st.session_state.post_decision_start=time.perf_counter()
    value=choice_buttons("final")
    if value:
        st.session_state.post_decision_time=round(time.perf_counter()-st.session_state.post_decision_start,2); st.session_state.final_choice=value; add_user(value); st.session_state.stage="final_confidence_question"; st.rerun()
elif stage == "final_confidence_question":
    render_chat(); delayed_ai("최종 판단에 얼마나 확신하십니까?\n1은 전혀 확신하지 않음, 7은 매우 확신함을 의미합니다.", "final_confidence")
elif stage == "final_confidence":
    render_chat(); value=rating_buttons("final_conf")
    if value:
        q=QUESTIONS[st.session_state.question_index]
        # 더미문항은 동일 절차를 수행하되 분석 데이터에는 넣지 않음.
        if not q["dummy"]:
            st.session_state.responses.append({"question_id":q["id"],"initial_choice":st.session_state.initial_choice,"initial_confidence":st.session_state.initial_confidence,"ai_recommendation":st.session_state.ai_recommendation,"final_choice":st.session_state.final_choice,"final_confidence":value,"choice_changed":int(st.session_state.initial_choice!=st.session_state.final_choice),"ai_accepted":int(st.session_state.final_choice==st.session_state.ai_recommendation),"pre_decision_time":st.session_state.pre_decision_time,"post_decision_time":st.session_state.post_decision_time})
        add_user(str(value)); next_index=st.session_state.question_index+1; st.session_state.question_index=next_index
        if next_index>=len(QUESTIONS): st.session_state.stage="finish_1"
        else: reset_question_state(); st.session_state.stage="question_category"
        st.rerun()
elif stage == "finish_1":
    render_chat(); delayed_ai("모든 의사결정 상황이 완료되었습니다.", "finish_2")
elif stage == "finish_2":
    render_chat(); delayed_ai("실험에 참여해 주셔서 감사합니다.\n오늘도 좋은 하루 보내세요 😄\n아래 종료 버튼을 눌러 실험을 마쳐주세요.", "finished")
elif stage == "finished":
    render_chat(); st.markdown(f'<div style="text-align:center;color:#999;font-size:12px;margin-top:20px;margin-bottom:10px">참가자 번호: {st.session_state.participant_id}</div>',unsafe_allow_html=True); cols=st.columns([1.2,1,1.2])
    with cols[1]:
        if st.button("종료",type="primary",use_container_width=True):
            # 종료 버튼을 누른 바로 이 순간까지를 전체 사용시간으로 계산한 뒤 저장
            if st.session_state.total_use_time is None: st.session_state.total_use_time=round(time.perf_counter()-st.session_state.experiment_start,2)
            try: save_data(); st.session_state.saved=True; st.session_state.stage="closed"; st.rerun()
            except Exception as e: st.error("응답 저장 중 오류가 발생했습니다. 잠시 후 페이지를 새로고침하지 말고 다시 시도해 주세요."); st.code(str(e)); st.stop()
elif stage == "closed":
    render_chat(); st.markdown('<div style="text-align:center;margin-top:25px;font-size:15px;color:#666;line-height:1.7">실험이 종료되었습니다.<br>참여해 주셔서 감사합니다.<br>오늘도 좋은 하루 보내세요 😄<br><br>이 창을 닫으셔도 됩니다.</div>',unsafe_allow_html=True)
    st.components.v1.html("""<script>setTimeout(function(){try{window.parent.close();}catch(e){}},400);</script>""",height=0)

scroll_bottom()
