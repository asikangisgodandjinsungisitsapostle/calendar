import streamlit as st
from datetime import datetime
import pandas as pd
import math

# 세션 상태 초기화 함수
def init_session_state():
    for key, default in {
        'start_date': None,
        'exam_date': None,
        'exam_date_saved': False,
        'show_subject_input': False,
        'subject_data': [],
        'show_result': False,
        'edit_index': None,
        'edit_mode': False,
        'message': ""
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

def run_study_planner():
    init_session_state()

    st.title("📚 시험 공부 계획 도우미")

    # 1. 시험 날짜 입력
    if not st.session_state.exam_date_saved:
        st.subheader("1️⃣ 시험 날짜 입력")

        st.text_input("공부 시작 날짜 (예: 7/15)", key="start_date_input")
        st.text_input("시험 날짜 (예: 7/25)", key="exam_date_input")

        if st.button("시험 날짜 저장"):
            try:
                current_year = datetime.now().year
                start_date_str = st.session_state.start_date_input
                exam_date_str = st.session_state.exam_date_input

                start_date = datetime.strptime(f"{current_year}/{start_date_str}", "%Y/%m/%d").date()
                exam_date = datetime.strptime(f"{current_year}/{exam_date_str}", "%Y/%m/%d").date()

                if exam_date <= start_date:
                    st.error("❌ 시험 날짜는 공부 시작 날짜보다 이후여야 합니다.")
                else:
                    st.session_state.start_date = start_date
                    st.session_state.exam_date = exam_date
                    st.session_state.exam_date_saved = True
                    st.session_state.show_subject_input = True  # ✅ 자동으로 과목 입력으로 이동
                    st.success(f"시험 기간 저장됨: {start_date} ~ {exam_date} ({(exam_date - start_date).days}일)")
                    st.rerun()
            except ValueError:
                st.error("❌ 날짜 형식이 올바르지 않습니다. 예: 7/15")

    # 3. 과목 입력 및 수정
    if st.session_state.show_subject_input:
        st.subheader("2️⃣ 과목 및 시험범위 입력")

        if st.session_state.edit_mode:
            subject_names = [s['과목명'] for s in st.session_state.subject_data]
            selected_idx = st.selectbox(
                "수정할 과목을 선택하세요",
                options=range(len(subject_names)),
                format_func=lambda i: subject_names[i],
                key="selected_subject_idx"
            )
        else:
            selected_idx = None

        if st.session_state.edit_mode and selected_idx is not None:
            sub = st.session_state.subject_data[selected_idx]
            default_name = sub['과목명']
            default_range = f"{sub['시작 페이지']}~{sub['끝 페이지']}"
        else:
            default_name = ""
            default_range = ""

        name = st.text_input("과목명", value=default_name, key="name_input")
        page_range = st.text_input("시험 범위 (예: 10~35)", value=default_range, key="page_input")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("과목 저장"):
                if st.session_state.start_date is None or st.session_state.exam_date is None:
                    st.error("❌ 시험 날짜를 먼저 입력하고 저장해야 합니다.")
                    st.session_state.show_subject_input = False
                    st.session_state.exam_date_saved = False
                    st.rerun()
                
                if not name or not page_range:
                    st.error("모든 항목을 입력해주세요.")
                else:
                    try:
                        parts = page_range.replace(" ", "").split("~")
                        if len(parts) != 2:
                            st.error("시험 범위는 '숫자~숫자' 형식이어야 합니다.")
                        else:
                            start_page = int(parts[0])
                            end_page = int(parts[1])
                            page_count = end_page - start_page + 1
                            if page_count <= 0:
                                st.error("❌ 끝 페이지가 시작 페이지보다 작거나 같습니다.")
                            else:
                                study_days = (st.session_state.exam_date - st.session_state.start_date).days
                                if study_days <= 0:
                                    st.error("❌ 시험 기간이 올바르지 않습니다.")
                                else:
                                    daily_amount = math.ceil(page_count / study_days)
                                    new_subject = {
                                        '과목명': name,
                                        '시작 페이지': start_page,
                                        '끝 페이지': end_page,
                                        '총 페이지 수': page_count,
                                        '공부 기간(일)': study_days,
                                        '하루 공부량': daily_amount
                                    }
                                    if st.session_state.edit_mode and selected_idx is not None:
                                        st.session_state.subject_data[selected_idx] = new_subject
                                        st.success(f"{name} 수정 완료!")
                                        st.session_state.edit_mode = False
                                    else:
                                        st.session_state.subject_data.append(new_subject)
                                        st.success(f"{name} 저장됨! ")
                                    st.rerun()
                    except ValueError:
                        st.error("숫자를 정확히 입력했는지 확인하세요.")
                    except Exception as e:
                        st.error(f"알 수 없는 오류가 발생했습니다: {e}")

        with col2:
            if st.button("📊 결과 확인하기"):
                st.session_state.show_result = True
                st.rerun()

        with col3:
            if len(st.session_state.subject_data) == 0:
                st.write("과목 수정할 데이터가 없습니다.")
            else:
                if st.button("📝 과목 수정 시작"):
                    st.session_state.edit_mode = True
                    st.rerun()

        # ✅ 추가: 2단계에서도 시험 날짜 다시 입력 가능
        st.markdown("---")
        if st.button("🔄 시험 날짜 다시 입력"):
            st.session_state.exam_date_saved = False
            st.session_state.start_date = None
            st.session_state.exam_date = None
            st.session_state.message = ""
            st.session_state.show_subject_input = False
            st.session_state.edit_mode = False
            st.rerun()

    # 4. 결과 출력
    if st.session_state.show_result:
        st.subheader("📋 과목별 공부 계획 요약 (표)")
        if st.session_state.subject_data:
            df = pd.DataFrame(st.session_state.subject_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("아직 저장된 과목이 없습니다.")

