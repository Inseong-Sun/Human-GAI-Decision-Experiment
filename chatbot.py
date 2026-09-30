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
    # 모바일·PC 모두 위에서 아래로 동일한 순서가 유지되도록 단일 열에 배치
    render_chat(); options=["거의 사용하지 않음","월 1~3회","주 1~2회","주 3~5회","거의 매일"]
    for i, option in enumerate(options):
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
    render_chat(); q=QUESTIONS[st.session_state.question_index]; delayed_ai(f"{q['question']}\n{q['choice_prompt']}", "question_options")
elif stage == "question_options":
    render_chat(); q=QUESTIONS[st.session_state.question_index]; delayed_ai(q["options"], "initial_choice")
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
    render_chat(); st.markdown(f'<div class="ai-message"><div class="ai-profile">{ROBOT_SVG}</div><div class="ai-content"><div class="ai-name">AI 의사결정 도우미</div><div class="ai-row"><div class="ai-bubble"><div class="typing"><span></span><span></span><span></span></div></div></div></div></div>', unsafe_allow_html=True); scroll_bottom(); time.sleep(3); st.session_state.stage="ai_analysis_2"; st.rerun()
elif stage == "ai_analysis_2":
    render_chat(); delayed_ai(f"제 분석 결과, 저는 {st.session_state.ai_recommendation}를 추천합니다.", "ai_analysis_3")
elif stage == "ai_analysis_3":
    render_chat(); delayed_ai(st.session_state.ai_response, "ai_read_complete")
elif stage == "ai_read_complete":
    render_chat(); cols=st.columns([1.4,2])
    with cols[0]:
        if st.button("최종 결정하기",key=f"start_final_{st.session_state.question_index}",use_container_width=True): add_user("최종 결정하기"); st.session_state.stage="final_question_repeat"; st.rerun()
elif stage == "final_question_repeat":
    render_chat(); q=QUESTIONS[st.session_state.question_index]; delayed_ai(f"{q['question']}\n{q['choice_prompt']}", "final_question_options")
elif stage == "final_question_options":
    render_chat(); delayed_ai(QUESTIONS[st.session_state.question_index]["options"], "final_instruction")
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
        if st.button("종료",type="primary",use_container_width=True,disabled=st.session_state.saving or st.session_state.saved):
            # 클릭 즉시 저장 전용 단계로 이동해 연속 클릭이 같은 응답을 여러 번 전송하지 못하게 함.
            if st.session_state.total_use_time is None: st.session_state.total_use_time=round(time.perf_counter()-st.session_state.experiment_start,2)
            st.session_state.saving=True; st.session_state.stage="saving"; st.rerun()
elif stage == "saving":
    render_chat()
    if not st.session_state.saved:
        try:
            save_data(); st.session_state.saved=True; st.session_state.saving=False; st.session_state.stage="closed"; st.rerun()
        except Exception as e:
            st.session_state.saving=False; st.session_state.stage="finished"
            st.error("응답 저장 중 오류가 발생했습니다. 종료 버튼을 다시 눌러주세요."); st.code(str(e)); st.stop()
    else:
        st.session_state.saving=False; st.session_state.stage="closed"; st.rerun()
elif stage == "closed":
