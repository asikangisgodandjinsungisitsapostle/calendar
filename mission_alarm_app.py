import streamlit as st
import json
import datetime
import calendar
import random
import threading
import time
import os
import re
import requests
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Any
# from streamlit_player import st_player  # 주석 처리

import streamlit.components.v1 as components

# study 모듈 임포트 (기존 코드 유지)
try:
    import study
except ImportError as e:
    st.error(f"study 모듈을 불러올 수 없습니다: {e}")
    study = None

# 페이지 설정
st.set_page_config(
    page_title="공부 도우미",
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 파일 경로
DATA_FILE = "mission_alarm_data.json"

class MissionAlarmApp:
    def __init__(self):
        self.load_data()
        
    def load_data(self):
        """데이터 파일에서 데이터 로드"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    st.session_state.schedules = data.get('schedules', {})
                    st.session_state.alarms = data.get('alarms', {})
                    st.session_state.settings = data.get('settings', {})
            except Exception as e:
                st.error(f"데이터 로드 중 오류 발생: {e}")
                self.init_default_data()
        else:
            self.init_default_data()
    
    def init_default_data(self):
        """기본 데이터 초기화"""
        if 'schedules' not in st.session_state:
            st.session_state.schedules = {}
        if 'alarms' not in st.session_state:
            st.session_state.alarms = {}
        if 'settings' not in st.session_state:
            st.session_state.settings = {
                'mission_alarm_enabled': True,
                'sound_enabled': True,
                'vibration_enabled': True
            }
        # 이스터에그 상태는 main 함수에서 직접 초기화하므로 여기서는 제거
    
    def save_data(self):
        """데이터를 파일에 저장"""
        try:
            data = {
                'schedules': st.session_state.schedules,
                'alarms': st.session_state.alarms,
                'settings': st.session_state.settings
            }
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"데이터 저장 중 오류 발생: {e}")
    
    def get_date_key(self, date):
        """날짜를 문자열 키로 변환"""
        return date.strftime("%Y-%m-%d")
    
    def add_schedule(self, date, task):
        """일정 추가"""
        date_key = self.get_date_key(date)
        if date_key not in st.session_state.schedules:
            st.session_state.schedules[date_key] = []
        
        # 이스터에그 키워드 체크 (일정 추가하지 않음)
        easter_egg_keywords = [
            "mp3", "mp4", "stock", "bocchitherock", "youtube", 
            "이루마", "유키 구라모토", "류이치 사카모토"
        ]
        
        is_easter_egg = any(keyword in task.lower() for keyword in easter_egg_keywords)
        
        if not is_easter_egg:
            # 이스터에그가 아닌 경우에만 일정에 추가
            st.session_state.schedules[date_key].append({
                'task': task,
                'completed': False,
                'created_at': datetime.datetime.now().isoformat()
            })
            self.save_data()
        
        # 이스터에그 트리거 (일정 추가 여부와 관계없이)
        if "mp3" in task.lower():
            st.session_state.easter_egg_mp3 = True
        if "mp4" in task.lower():
            st.session_state.easter_egg_mp4 = True
        if "stock" in task.lower():
            st.session_state.easter_egg_stock = True
        if "bocchitherock" in task.lower():
            st.session_state.easter_egg_bocchitherock = True
        if "asiankungfugeneration" in task.lower():
            st.session_state.easter_egg_asiankungfugeneration = True
        if "kino" in task.lower():
            st.session_state.easter_egg_kino = True
        if "youtube" in task.lower():
            st.session_state.easter_egg_youtube = True
        if "이루마" in task.lower():
            st.session_state.easter_egg_yiruma = True
        if "유키 구라모토" in task.lower():
            st.session_state.easter_egg_yukikuramoto = True
        if "류이치 사카모토" in task.lower():
            st.session_state.easter_egg_ryuichisakamoto = True

    def get_schedules(self, date):
        """특정 날짜의 일정 조회"""
        date_key = self.get_date_key(date)
        return st.session_state.schedules.get(date_key, [])
    
    def delete_schedule(self, date, index):
        """일정 삭제"""
        date_key = self.get_date_key(date)
        if date_key in st.session_state.schedules and 0 <= index < len(st.session_state.schedules[date_key]):
            del st.session_state.schedules[date_key][index]
            if not st.session_state.schedules[date_key]:
                del st.session_state.schedules[date_key]
            self.save_data()
    
    def toggle_schedule_completion(self, date, index):
        """일정 완료 상태 토글"""
        date_key = self.get_date_key(date)
        if date_key in st.session_state.schedules and 0 <= index < len(st.session_state.schedules[date_key]):
            st.session_state.schedules[date_key][index]['completed'] = not st.session_state.schedules[date_key][index]['completed']
            self.save_data()

def show_calendar_page(app):
    """월간 일정 등록 페이지"""
    st.header("📆 월간 일정 관리")
    
    # 현재 날짜
    today = datetime.date.today()
    
    # 년월 선택
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("년도", range(today.year - 1, today.year + 2), index=1)
    with col2:
        selected_month = st.selectbox("월", range(1, 13), index=today.month - 1)
    
    # 달력 표시
    cal = calendar.monthcalendar(selected_year, selected_month)
    month_name = calendar.month_name[selected_month]
    
    st.subheader(f"{selected_year}년 {selected_month}월")
    
    # 달력 그리드 생성
    days = ['월', '화', '수', '목', '금', '토', '일']
    cols = st.columns(7)
    
    # 요일 헤더
    for i, day in enumerate(days):
        with cols[i]:
            st.write(f"**{day}**")
    
    # 달력 날짜 표시
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.write("")
                else:
                    date_obj = datetime.date(selected_year, selected_month, day)
                    schedules = app.get_schedules(date_obj)
                    
                    # 날짜 버튼
                    if st.button(f"{day}", key=f"cal_{selected_year}_{selected_month}_{day}"):
                        st.session_state.selected_date = date_obj
                    
                    # 일정 개수 표시
                    if schedules:
                        st.caption(f"📝 {len(schedules)}개")
    
    # 선택된 날짜의 일정 관리
    if 'selected_date' in st.session_state:
        selected_date = st.session_state.selected_date
        st.divider()
        st.subheader(f"{selected_date.strftime('%Y년 %m월 %d일')} 일정")
        
        # 새 일정 추가
        with st.expander("새 일정 추가", expanded=True):
            new_task = st.text_input("해야 할 일을 입력하세요", key="new_task")
            if st.button("일정 추가"):
                if new_task.strip():
                    app.add_schedule(selected_date, new_task.strip())
                    st.success("일정이 추가되었습니다!")
                    st.rerun()
                else:
                    st.warning("일정 내용을 입력해주세요.")
        
        # 기존 일정 표시
        schedules = app.get_schedules(selected_date)
        if schedules:
            st.write("**등록된 일정:**")
            for i, schedule in enumerate(schedules):
                col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
                
                with col1:
                    completed = st.checkbox("", value=schedule['completed'], key=f"check_{selected_date}_{i}")
                    if completed != schedule['completed']:
                        app.toggle_schedule_completion(selected_date, i)
                        st.rerun()
                
                with col2:
                    if schedule['completed']:
                        st.write(f"~~{schedule['task']}~~")
                    else:
                        st.write(schedule['task'])
                
                with col3:
                    if st.button("🗑️", key=f"del_{selected_date}_{i}"):
                        app.delete_schedule(selected_date, i)
                        st.rerun()
        else:
            st.info("등록된 일정이 없습니다.")

def show_alarm_page(app):
    """알람 설정 페이지"""
    st.header("⏰ 알람 설정")
    
    # 알람 설정 폼
    with st.form("alarm_settings"):
        st.subheader("새 알람 추가")
        
        col1, col2 = st.columns(2)
        with col1:
            alarm_time = st.time_input("알람 시간", value=datetime.time(7, 0))
        with col2:
            alarm_name = st.text_input("알람 이름", placeholder="예: 아침 기상")
        
        # 반복 요일 선택
        st.write("반복 요일:")
        days_of_week = ['월', '화', '수', '목', '금', '토', '일']
        selected_days = []
        cols = st.columns(7)
        
        for i, day in enumerate(days_of_week):
            with cols[i]:
                if st.checkbox(day, key=f"day_{i}"):
                    selected_days.append(i)
        
        # 미션 알람 설정
        mission_enabled = st.checkbox("미션 알람 활성화", value=True)
        
        # 알람 추가 버튼
        if st.form_submit_button("알람 추가"):
            if alarm_name.strip():
                alarm_id = f"alarm_{len(st.session_state.alarms)}"
                st.session_state.alarms[alarm_id] = {
                    'name': alarm_name.strip(),
                    'time': alarm_time.strftime("%H:%M"),
                    'days': selected_days,
                    'mission_enabled': mission_enabled,
                    'active': True,
                    'created_at': datetime.datetime.now().isoformat()
                }
                app.save_data()
                st.success("알람이 추가되었습니다!")
                st.rerun()
            else:
                st.warning("알람 이름을 입력해주세요.")
    
    # 기존 알람 목록
    st.divider()
    st.subheader("등록된 알람")
    
    if st.session_state.alarms:
        for alarm_id, alarm in st.session_state.alarms.items():
            with st.expander(f"{alarm['name']} - {alarm['time']}", expanded=False):
                col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
                
                with col1:
                    active = st.checkbox("활성화", value=alarm['active'], key=f"active_{alarm_id}")
                    if active != alarm['active']:
                        st.session_state.alarms[alarm_id]['active'] = active
                        app.save_data()
                
                with col2:
                    days_text = ', '.join([days_of_week[day] for day in alarm['days']]) if alarm['days'] else '매일'
                    st.write(f"**반복:** {days_text}")
                    st.write(f"**미션 알람:** {'활성화' if alarm['mission_enabled'] else '비활성화'}")
                
                with col3:
                    if st.button("삭제", key=f"delete_{alarm_id}"):
                        del st.session_state.alarms[alarm_id]
                        app.save_data()
                        st.rerun()
    else:
        st.info("등록된 알람이 없습니다.")

def show_quiz_page(app):
    """미션 퀴즈 페이지"""
    st.header("❓ 미션 퀴즈")
    
    # 오늘 날짜의 일정 가져오기
    today = datetime.date.today()
    today_schedules = app.get_schedules(today)
    
    if not today_schedules:
        st.warning("오늘 등록된 일정이 없습니다. 먼저 일정을 등록해주세요.")
        return
    
    # 완료되지 않은 일정만 필터링
    incomplete_schedules = [s for s in today_schedules if not s['completed']]
    
    if not incomplete_schedules:
        st.success("오늘의 모든 일정을 완료했습니다! 🎉")
        return
    
    st.write(f"**오늘 날짜:** {today.strftime('%Y년 %m월 %d일')}")
    st.write("**미션:** 오늘 해야 할 일을 모두 선택하세요!")
    
    # 퀴즈 생성
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
        st.session_state.quiz_options = []
        st.session_state.correct_answers = []
    
    if not st.session_state.quiz_generated:
        # 정답 (실제 오늘의 할 일)
        correct_tasks = [s['task'] for s in incomplete_schedules]
        
        # 오답 생성 (가짜 할 일들)
        fake_tasks = [
            "게임하기", "TV 보기", "늦잠 자기", "과자 먹기", 
            "소셜미디어 보기", "웹툰 보기", "음악 듣기", "쇼핑하기"
        ]
        
        # 실제 할 일과 겹치지 않는 가짜 할 일 선택
        available_fake_tasks = [task for task in fake_tasks if task not in correct_tasks]
        
        # 퀴즈 옵션 생성 (정답 + 오답)
        num_fake = min(3, len(available_fake_tasks))  # 최대 3개의 오답
        selected_fake_tasks = random.sample(available_fake_tasks, num_fake)
        
        all_options = correct_tasks + selected_fake_tasks
        random.shuffle(all_options)
        
        st.session_state.quiz_options = all_options
        st.session_state.correct_answers = correct_tasks
        st.session_state.quiz_generated = True
    
    # 퀴즈 표시
    st.write("**다음 중 오늘 해야 할 일을 모두 선택하세요:** (복수 선택 가능)")
    
    selected_options = []
    for i, option in enumerate(st.session_state.quiz_options):
        if st.checkbox(option, key=f"quiz_option_{i}"):
            selected_options.append(option)
    
    # 정답 확인
    col1, col2 = st.columns(2)
    with col1:
        if st.button("정답 확인", type="primary"):
            correct_set = set(st.session_state.correct_answers)
            selected_set = set(selected_options)
            
            if correct_set == selected_set:
                st.success("🎉 정답입니다! 미션 완료!")
                st.balloons()
                
                # 퀴즈 초기화
                st.session_state.quiz_generated = False
                
                # 선택적: 알람 해제 시뮬레이션
                st.info("알람이 해제되었습니다. 오늘도 화이팅!")
            else:
                st.error("❌ 틀렸습니다. 다시 시도해보세요!")
                
                # 힌트 제공
                if len(selected_set) != len(correct_set):
                    st.warning(f"힌트: 정답은 총 {len(correct_set)}개입니다.")
    
    with col2:
        if st.button("퀴즈 다시 생성"):
            st.session_state.quiz_generated = False
            st.rerun()

def show_settings_page(app):
    """설정 페이지"""
    st.header("⚙️ 설정")
    
    # 일반 설정
    st.subheader("일반 설정")
    
    mission_alarm_enabled = st.checkbox(
        "미션 알람 기본 활성화", 
        value=st.session_state.settings.get('mission_alarm_enabled', True)
    )
    
    sound_enabled = st.checkbox(
        "알람 소리 활성화", 
        value=st.session_state.settings.get('sound_enabled', True)
    )
    
    vibration_enabled = st.checkbox(
        "진동 활성화", 
        value=st.session_state.settings.get('vibration_enabled', True)
    )
    
    # 설정 저장
    if st.button("설정 저장"):
        st.session_state.settings.update({
            'mission_alarm_enabled': mission_alarm_enabled,
            'sound_enabled': sound_enabled,
            'vibration_enabled': vibration_enabled
        })
        app.save_data()
        st.success("설정이 저장되었습니다!")
    
    # 데이터 관리
    st.divider()
    st.subheader("데이터 관리")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("데이터 백업"):
            try:
                backup_data = {
                    'schedules': st.session_state.schedules,
                    'alarms': st.session_state.alarms,
                    'settings': st.session_state.settings,
                    'backup_date': datetime.datetime.now().isoformat()
                }
                
                backup_filename = f"mission_alarm_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                st.download_button(
                    label="백업 파일 다운로드",
                    data=json.dumps(backup_data, ensure_ascii=False, indent=2),
                    file_name=backup_filename,
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"백업 중 오류 발생: {e}")
    
    with col2:
        uploaded_file = st.file_uploader("백업 파일 복원", type=['json'])
        if uploaded_file is not None:
            try:
                backup_data = json.load(uploaded_file)
                
                if st.button("데이터 복원"):
                    st.session_state.schedules = backup_data.get('schedules', {})
                    st.session_state.alarms = backup_data.get('alarms', {})
                    st.session_state.settings = backup_data.get('settings', {})
                    app.save_data()
                    st.success("데이터가 복원되었습니다!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"파일 읽기 오류: {e}")

def get_gdrive_direct_link(gdrive_url):
    file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', gdrive_url)
    if file_id_match:
        file_id = file_id_match.group(1)
        return f"https://drive.google.com/uc?id={file_id}&export=download" # 스트리밍에 더 적합한 방식
    return None

def show_mp3_player_page():
    st.header("🎵 MP3 플레이어")
    st.write("구글 드라이브 MP3 폴더의 파일을 재생합니다.")

    mp3_links = [
    "https://drive.google.com/file/d/1pjSb8ggY2lGpwSIbTS69GV1UtrNcYWMI/view?usp=drive_link",
    "https://drive.google.com/file/d/1i64_JIjUgmHpwqPjIC4yXRKXyw29WHdT/view?usp=drive_link",
    "https://drive.google.com/file/d/1yapRpt6b_Vob04LD5urfOGbwJUOX4qje/view?usp=drive_link",
    "https://drive.google.com/file/d/1wmMqT9kMikudoVNCV2Hh1Qqa4533xOSJ/view?usp=drive_link",
    "https://drive.google.com/file/d/1QfBpaXbXl78rtmCtVMDgCSUjTPRR6Fgx/view?usp=drive_link",
    "https://drive.google.com/file/d/1BKJB4vYmbGkYfKTWKX0JT2QIwCXpcohs/view?usp=drive_link",
    "https://drive.google.com/file/d/10iU2Ult1kJPjpg75oibi36fZNCPSKPMM/view?usp=drive_link",
    "https://drive.google.com/file/d/1v4uF4GcG9kDHN7prK-pqvgFVTawAYP9x/view?usp=drive_link",
    "https://drive.google.com/file/d/1RwTjmBmKIzTcOYQIyg--ho8OiKsUeJkP/view?usp=drive_link",
    "https://drive.google.com/file/d/1RaFY9-h9viGPGHTeAGwLP0dDB3pWUW0x/view?usp=drive_link",
    "https://drive.google.com/file/d/1TP9O2uspXhRyZ9-P_MHbGwavUP-l72gl/view?usp=drive_link",
    "https://drive.google.com/file/d/1L7SSblN-JWoOwVxBBkGk9FcGiVrFUoR2/view?usp=drive_link",
    "https://drive.google.com/file/d/10PeTTtNqaSOlsNmj7R6R5Wsk4v8Zbzc6/view?usp=drive_link",
    "https://drive.google.com/file/d/1gZJ39b6yAG_WwhS3NWN8Q2o0_xx7FxQs/view?usp=drive_link",
    "https://drive.google.com/file/d/1tIbXYbZolFMNxQsIMmgNxrB3GDVwuJO4/view?usp=drive_link",
    "https://drive.google.com/file/d/1ATrqRJoaUpNISpuZYdZKl-0GtNpX2Hj_/view?usp=drive_link",
    "https://drive.google.com/file/d/13JRfwIJ_xEPCGgPICsPywrtX8hfRupbq/view?usp=drive_link",
    "https://drive.google.com/file/d/1LC00M-nUrVqmy8u3Fcd80pua3qblBuHX/view?usp=drive_link",
    "https://drive.google.com/file/d/11DY96gRj2Y-J-3WKl9IA9ijSUvmsKtZc/view?usp=drive_link",
    "https://drive.google.com/file/d/1qXbMlWaJN0ibUR7u9PBjsUxTPpHh8k1A/view?usp=drive_link",
    "https://drive.google.com/file/d/1z8EpJmp4dGqw9jJz0BysFHvnvy2hkRWL/view?usp=drive_link",
    "https://drive.google.com/file/d/1LjujjEZDZ7mxCwSX82No8hHuubzRqwzy/view?usp=drive_link",
    "https://drive.google.com/file/d/1iglKcJ1oO3YaiNEyyIqhg4z9oyRGDIRB/view?usp=drive_link",
    "https://drive.google.com/file/d/1uLV3BYIoMv_ZLndEjtUdHE0y84DtiNKG/view?usp=drive_link",
    "https://drive.google.com/file/d/1uA3JSBH9nO3yg_iDA7yWK3di3ZMi5dSu/view?usp=drive_link",
    "https://drive.google.com/file/d/1M2IbuCOnsRRIvaxtPdvXLqJ6_GA7HjVP/view?usp=drive_link",
    "https://drive.google.com/file/d/1lTQPZz7OlBBX9VUtPDktKj2ZKBqm5Ms4/view?usp=drive_link",
    "https://drive.google.com/file/d/1EY142_T-QPwfnA5gKOOsReOfR_uCJhya/view?usp=drive_link",
    "https://drive.google.com/file/d/1AaXahnWDHLVa8oL_Z4GiUc5Df5Axhtga/view?usp=drive_link",
    "https://drive.google.com/file/d/1YyVzjp11IA9UV9FjJyKdkB8aKahiZv1S/view?usp=drive_link",
    "https://drive.google.com/file/d/1NxBrMarj1Nt-rF1P2U1Oj9k35xkRw2qs/view?usp=drive_link",
    "https://drive.google.com/file/d/1CleB68hnhUp0t7auymlhJdNPVhncPxEj/view?usp=drive_link"
]



    if mp3_links:
        mp3_options = []
        for link in mp3_links:
            file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', link)
            if file_id_match:
                file_id = file_id_match.group(1)
                mp3_options.append(f"MP3 파일 ({file_id[:5]}...)")
            else:
                mp3_options.append("유효하지 않은 링크")

        selected_mp3_index = st.selectbox("재생할 MP3 선택", range(len(mp3_options)), format_func=lambda x: mp3_options[x])
        selected_mp3_url = mp3_links[selected_mp3_index]
        
        direct_link = get_gdrive_direct_link(selected_mp3_url)
        
        if direct_link:
            try:
                response = requests.get(direct_link, stream=True)
                if response.status_code == 200:
                    temp_audio_file = "temp_audio.mp3"
                    with open(temp_audio_file, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    st.audio(temp_audio_file, format='audio/mp3')
                    os.remove(temp_audio_file)
                else:
                    st.error(f"MP3 파일을 가져올 수 없습니다. 상태 코드: {response.status_code}")
            except Exception as e:
                st.error(f"MP3 재생 중 오류 발생: {e}")
        else:
            st.error("유효한 MP3 링크를 찾을 수 없습니다.")
    else:
        st.info("등록된 MP3 파일이 없습니다.")

def show_mp4_player_page():
    st.header("▶️ MP4 플레이어")
    st.write("구글 드라이브 MP4 폴더의 파일을 재생합니다.")

    mp4_links = [
    "https://drive.google.com/file/d/1gtrzzlyr9iCARkpAr8_YP4VOHOX1ScB6/view?usp=drive_link",
    "https://drive.google.com/file/d/1tq6YLU6uivbDuoJuak6rEZw6hjlkbQWq/view?usp=drive_link",
    "https://drive.google.com/file/d/177_x1zgCDrjtNNlpMHN7TDku7e4q7dmq/view?usp=drive_link",
    "https://drive.google.com/file/d/13sse143mm0EhAx5hWXzg7IjucqD04o3O/view?usp=drive_link",
    "https://drive.google.com/file/d/12ZvbaMM2UQCL0RZkuY0fzhjJY7NnL90x/view?usp=drive_link",
    "https://drive.google.com/file/d/1orXrOvqMVoRoZUY5P8NbrfPM4YlnAYYP/view?usp=drive_link",
    "https://drive.google.com/file/d/1Br8R70O3jkYa_ET2C1zF_MUOVO1KEukt/view?usp=drive_link",
    "https://drive.google.com/file/d/1RaZ4EchnCqSiTxvFeFNLbLLyVvvslO4x/view?usp=drive_link",
    "https://drive.google.com/file/d/1pa4ZyGFbUZVpX8pcqpmjxzpSErw8_ypn/view?usp=drive_link",
    "https://drive.google.com/file/d/1po2Q5lbsGSXeHsqYWS5BpFs_nW0TSD8S/view?usp=drive_link",
    "https://drive.google.com/file/d/1Kt-KMHBSjO1QKQkh91BMOWmg8wZDj9AS/view?usp=drive_link",
    "https://drive.google.com/file/d/1JRw786xtTotlT0A6ISpjS1lOWkv5Mxj_/view?usp=drive_link",
    "https://drive.google.com/file/d/1GxRrdvAEblTepDtWrzLxapfeu1vZ1REA/view?usp=drive_link"
]


    if mp4_links:
        mp4_options = []
        for link in mp4_links:
            file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', link)
            if file_id_match:
                file_id = file_id_match.group(1)
                mp4_options.append(f"MP4 파일 ({file_id[:5]}...)")
            else:
                mp4_options.append("유효하지 않은 링크")

        selected_mp4_index = st.selectbox("재생할 MP4 선택", range(len(mp4_options)), format_func=lambda x: mp4_options[x])
        selected_mp4_url = mp4_links[selected_mp4_index]

        direct_link = get_gdrive_direct_link(selected_mp4_url)

        if direct_link:
            try:
                response = requests.get(direct_link, stream=True)
                if response.status_code == 200:
                    temp_video_file = "temp_video.mp4"
                    with open(temp_video_file, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    st.video(temp_video_file, format='video/mp4')
                    os.remove(temp_video_file)
                else:
                    st.error(f"MP4 파일을 가져올 수 없습니다. 상태 코드: {response.status_code}")
            except Exception as e:
                st.error(f"MP4 재생 중 오류 발생: {e}")
        else:
            st.error("유효한 MP4 링크를 찾을 수 없습니다.")
    else:
        st.info("등록된 MP4 파일이 없습니다.")

def show_stock_chart_page():
    st.header("📈 주식 차트")
    st.write("KRX 종목 코드 또는 Google Finance 링크를 입력하여 주식 차트를 조회합니다.")

    stock_input = st.text_input("종목 코드 (예: 000660:KRX, AAPL) 또는 Google Finance 링크", key="stock_input")
    
    periods = {
        "1일": "1d",
        "5일": "5d",
        "1개월": "1mo",
        "6개월": "6mo",
        "YTD": "ytd",
        "1년": "1y",
        "5년": "5y",
        "최대": "max"
    }
    selected_period_name = st.selectbox("조회 기간", list(periods.keys()))
    selected_period_yf = periods[selected_period_name]

    if st.button("차트 조회"):
        if stock_input:
            ticker_symbol = ""
            if "google.com/finance/quote/" in stock_input:
                match = re.search(r'/quote/([^/:]+):([^/?]+)', stock_input)
                if match:
                    symbol_part = match.group(1)
                    exchange_part = match.group(2)
                    if exchange_part == "KRX":
                        ticker_symbol = f"{symbol_part}.KS"
                    else:
                        ticker_symbol = f"{symbol_part}.{exchange_part}" 
                else:
                    st.error("유효한 Google Finance 링크가 아닙니다.")
                    return
            elif ":KRX" in stock_input.upper():
                ticker_symbol = stock_input.replace(":KRX", ".KS").upper()
            else:
                ticker_symbol = stock_input.upper()

            try:
                stock = yf.Ticker(ticker_symbol)
                hist = stock.history(period=selected_period_yf)

                if not hist.empty:
                    # 회사 정보 가져오기
                    info = stock.info
                    company_name = info.get('longName', info.get('shortName', ticker_symbol))
                    
                    st.subheader(f"{company_name} ({ticker_symbol}) 주식 차트 ({selected_period_name})")

                    fig = go.Figure(data=[
                        go.Candlestick(
                            x=hist.index,
                            open=hist['Open'],
                            high=hist['High'],
                            low=hist['Low'],
                            close=hist['Close']
                        )
                    ])
                    fig.update_layout(
                        title=f"{company_name} ({ticker_symbol}) - {selected_period_name}",
                        xaxis_rangeslider_visible=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("주요 정보")
                    col1, col2 = st.columns(2)
                    with col1:
                        current_price = info.get('currentPrice', info.get('regularMarketPrice', 'N/A'))
                        st.write(f"**현재가:** {current_price}")
                        market_cap = info.get('marketCap', 'N/A')
                        if market_cap != 'N/A' and isinstance(market_cap, (int, float)):
                            market_cap = f"{market_cap:,.0f}"
                        st.write(f"**시가총액:** {market_cap}")
                        pe_ratio = info.get('trailingPE', 'N/A')
                        if pe_ratio != 'N/A' and isinstance(pe_ratio, (int, float)):
                            pe_ratio = f"{pe_ratio:.2f}"
                        st.write(f"**PER:** {pe_ratio}")
                    with col2:
                        change_percent = info.get('regularMarketChangePercent', 'N/A')
                        if change_percent != 'N/A' and isinstance(change_percent, (int, float)):
                            change_percent = f"{change_percent:.2f}%"
                        st.write(f"**변동률 (1일):** {change_percent}")
                        volume = info.get('volume', info.get('regularMarketVolume', 'N/A'))
                        if volume != 'N/A' and isinstance(volume, (int, float)):
                            volume = f"{volume:,.0f}"
                        st.write(f"**거래량:** {volume}")
                        high_52 = info.get('fiftyTwoWeekHigh', 'N/A')
                        low_52 = info.get('fiftyTwoWeekLow', 'N/A')
                        st.write(f"**52주 최고/최저:** {high_52} / {low_52}")

                else:
                    st.warning(f"{ticker_symbol}에 대한 데이터를 찾을 수 없습니다. 종목 코드를 확인해주세요.")
            except Exception as e:
                st.error(f"주식 정보를 가져오는 중 오류 발생: {e}")
        else:
            st.warning("종목 코드를 입력해주세요.")



def get_youtube_playlist_id(url):
    """유튜브 플레이리스트 URL에서 ID 추출"""
    import urllib.parse as urlparse
    parsed = urlparse.urlparse(url)
    query = urlparse.parse_qs(parsed.query)
    return query.get("list", [None])[0]

def show_youtube_playlist_page(title, playlist_url):
    st.set_page_config(layout="wide")
    st.header(f"🎸 {title} 플레이리스트")
    st.write(f"{title}의 YouTube 플레이리스트를 재생합니다.")

    playlist_id = get_youtube_playlist_id(playlist_url)

    if playlist_id:
        embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}"

        # 반응형 YouTube iframe 삽입
        html_code = f"""
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; height: auto;">
            <iframe src="{embed_url}" frameborder="0"
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                    allowfullscreen>
            </iframe>
        </div>
        """

        # components에 충분한 높이 주기
        components.html(html_code, height=600, width=1000)
    else:
        st.error("유효한 YouTube 플레이리스트 링크가 아닙니다.")


def show_study_page():
    if study:
        study.run_study_planner()
    else:
        st.error("study 모듈을 불러올 수 없습니다. study.py 파일이 올바른 위치에 있는지 확인해주세요.")
def show_deadline_youtube_page():
    st.header("▶️ 마감에 쫓길 때")
    st.video("https://www.youtube.com/watch?v=C3p4QDW3-g8")

MEAL_API_KEY = "ea52474581cf41c2bf2291ef389adf61"

# 학교 검색 함수
def search_school(school_name):
    url = f"https://open.neis.go.kr/hub/schoolInfo?KEY={MEAL_API_KEY}&Type=json&SCHUL_NM={school_name}"
    res = requests.get(url)
    data = res.json()
    if "schoolInfo" not in data:
        return []
    return data["schoolInfo"][1]["row"]

# 급식 조회 함수
def get_meals(office_code, school_code, start_date, end_date):
    url = (
        f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={MEAL_API_KEY}"
        f"&Type=json&pIndex=1&pSize=100&ATPT_OFCDC_SC_CODE={office_code}"
        f"&SD_SCHUL_CODE={school_code}&MLSV_FROM_YMD={start_date}&MLSV_TO_YMD={end_date}"
    )
    res = requests.get(url)
    data = res.json()
    if "mealServiceDietInfo" not in data:
        return []
    return data["mealServiceDietInfo"][1]["row"]

# 중식 매핑
def prepare_lunch_map(meals):
    lunch_map = {}
    for m in meals:
        if m["MMEAL_SC_NM"] == "중식":
            date = pd.to_datetime(m["MLSV_YMD"]).date()
            menu = m["DDISH_NM"].replace("<br/>", "\n")
            lunch_map[date] = menu
    return lunch_map

# 달력 렌더링
def generate_lunch_calendar(year, month, lunch_map):
    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(year, month)
    table = "<style>td {vertical-align: top; white-space: pre-wrap; font-size: 13px; padding: 8px;}</style>"
    table += "<table border='1' style='width: 100%; border-collapse: collapse; text-align: left;'>"
    table += "<thead><tr>" + "".join(f"<th>{day}</th>" for day in ["월", "화", "수", "목", "금", "토", "일"]) + "</tr></thead><tbody>"
    for week in month_days:
        table += "<tr>"
        for date in week:
            if date.month != month:
                table += "<td></td>"
            else:
                menu = lunch_map.get(date, "")
                table += f"<td><strong>{date.day}</strong><br/>{menu}</td>"
        table += "</tr>"
    table += "</tbody></table>"
    return table

# 메인 앱
def show_meals_page():
    st.title("🍱 학교 급식 달력 (중식만)")

    school_name = st.text_input("학교 이름을 입력하세요", "", key="school_name_input")

    if school_name:
        school_list = search_school(school_name)

        if school_list:
            selected_school = st.selectbox(
                "학교를 선택하세요",
                [f"{s['SCHUL_NM']} ({s['ORG_RDNMA']})" for s in school_list],
                key="school_select"
            )

            selected_data = school_list[
                [f"{s['SCHUL_NM']} ({s['ORG_RDNMA']})" for s in school_list].index(selected_school)
            ]
            office_code = selected_data["ATPT_OFCDC_SC_CODE"]
            school_code = selected_data["SD_SCHUL_CODE"]

            # 선택: 오늘 / 이번주 / 이번달
            option = st.radio("표시할 기간을 선택하세요", ("오늘", "이번 주", "이번 달"))

            today = datetime.date.today()

            if option == "오늘":
                start_date = end_date = today.strftime("%Y%m%d")
            elif option == "이번 주":
                start = today - datetime.timedelta(days=today.weekday())
                end = start + datetime.timedelta(days=6)
                start_date = start.strftime("%Y%m%d")
                end_date = end.strftime("%Y%m%d")
            elif option == "이번 달":
                start = today.replace(day=1)
                last_day = calendar.monthrange(today.year, today.month)[1]
                end = today.replace(day=last_day)
                start_date = start.strftime("%Y%m%d")
                end_date = end.strftime("%Y%m%d")

            meals = get_meals(office_code, school_code, start_date, end_date)

            if meals:
                lunch_map = prepare_lunch_map(meals)

                if option == "이번 달":
                    calendar_html = generate_lunch_calendar(today.year, today.month, lunch_map)
                    st.markdown(calendar_html, unsafe_allow_html=True)
                else:
                    # 오늘 / 이번 주는 표 형식으로 표시
                    df = pd.DataFrame(
                        [{"날짜": date, "중식": menu} for date, menu in sorted(lunch_map.items())]
                    )
                    st.dataframe(df, use_container_width=True)
            else:
                st.warning("급식 정보를 찾을 수 없습니다.")
        else:
            st.warning("해당 이름의 학교를 찾을 수 없습니다.")

# ✅ 테스트용 YouTube API 키
API_KEY = "AIzaSyDv3dWd4U9AqsMS2DKwzPBbqWy3a6YkV-g"

# 🔍 유튜브 검색 함수 (개선된 버전)
def search_youtube(query, max_results=50):
    try:
        from bs4 import BeautifulSoup
        
        videos = []
        
        # 여러 페이지에서 검색 결과 수집
        for page in range(3):  # 3페이지까지 시도
            try:
                # YouTube 검색 URL (페이지별)
                if page == 0:
                    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                else:
                    search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}&sp=CAI%253D&page={page+1}"
                
                # User-Agent 설정
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                }
                
                response = requests.get(search_url, headers=headers, timeout=10)
                response.raise_for_status()  # HTTP 오류 체크
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 여러 방법으로 비디오 정보 추출
                page_videos = []
                
                # 방법 1: ytInitialData에서 추출
                for script in soup.find_all('script'):
                    script_text = str(script)
                    if 'var ytInitialData' in script_text:
                        import re
                        import json
                        
                        try:
                            data_match = re.search(r'var ytInitialData = ({.*?});', script_text, re.DOTALL)
                            if data_match:
                                data = json.loads(data_match.group(1))
                                
                                # 검색 결과에서 비디오 정보 추출
                                if 'contents' in data:
                                    contents = data['contents']
                                    if 'twoColumnSearchResultsRenderer' in contents:
                                        search_results = contents['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                                        
                                        for item in search_results:
                                            if 'videoRenderer' in item:
                                                video = item['videoRenderer']
                                                video_id = video.get('videoId', '')
                                                title = video.get('title', {}).get('runs', [{}])[0].get('text', '')
                                                thumbnail = video.get('thumbnail', {}).get('thumbnails', [{}])[-1].get('url', '')
                                                
                                                if video_id and title and video_id not in [v['id'] for v in videos]:
                                                    page_videos.append({
                                                        'id': video_id,
                                                        'title': title,
                                                        'link': f"https://www.youtube.com/watch?v={video_id}",
                                                        'thumbnail': thumbnail
                                                    })
                        except Exception as e:
                            st.warning(f"JSON 파싱 오류: {e}")
                            continue
                
                # 방법 2: 정규식으로 추출
                if not page_videos:
                    script_text = str(soup)
                    video_ids = re.findall(r'"videoId":"([^"]+)"', script_text)
                    titles = re.findall(r'"title":"([^"]+)"', script_text)
                    
                    for i, video_id in enumerate(video_ids):
                        if i < len(titles) and video_id not in [v['id'] for v in videos]:
                            page_videos.append({
                                'id': video_id,
                                'title': titles[i],
                                'link': f"https://www.youtube.com/watch?v={video_id}",
                                'thumbnail': f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                            })
                
                videos.extend(page_videos)
                
                # 중복 제거
                seen_ids = set()
                unique_videos = []
                for video in videos:
                    if video['id'] not in seen_ids:
                        seen_ids.add(video['id'])
                        unique_videos.append(video)
                
                videos = unique_videos
                
                if len(videos) >= max_results:
                    break
                    
                # 페이지 간 딜레이
                time.sleep(1)
                
            except requests.RequestException as e:
                st.warning(f"네트워크 오류 (페이지 {page+1}): {e}")
                continue
            except Exception as e:
                st.warning(f"페이지 {page+1} 로드 중 오류: {e}")
                continue
        
        return videos[:max_results]
        
    except Exception as e:
        st.error(f"YouTube 검색 중 오류 발생: {e}")
        return []

# 🖥️ Streamlit 앱 UI (iframe 사용)
def show_youtube_search_page():
    st.header("▶️ YouTube 검색")
    st.write("YouTube에서 영상을 검색하고 앱에서 직접 재생할 수 있습니다.")

    query = st.text_input("검색어를 입력하세요:", key="youtube_search_query")

    if query:
        # 세션 상태 초기화
        if 'youtube_results' not in st.session_state:
            st.session_state.youtube_results = []
        if 'youtube_current_page' not in st.session_state:
            st.session_state.youtube_current_page = 0
        if 'youtube_loading' not in st.session_state:
            st.session_state.youtube_loading = False
        if 'playing_video' not in st.session_state:
            st.session_state.playing_video = None

        # 검색 버튼
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔍 검색", key="youtube_search_button"):
                with st.spinner("검색 중..."):
                    st.session_state.youtube_results = search_youtube(query, max_results=50)
                    st.session_state.youtube_current_page = 0
                    st.rerun()

        # 결과가 있으면 표시
        if st.session_state.youtube_results:
            st.success(f"{len(st.session_state.youtube_results)}개의 영상이 검색되었습니다.")
            
            # 현재 재생 중인 영상이 있으면 표시
            if st.session_state.playing_video:
                st.markdown("### 🎬 현재 재생 중")
                
                # YouTube embed URL로 변환
                video_id = st.session_state.playing_video.split('v=')[-1]
                embed_url = f"https://www.youtube.com/embed/{video_id}"
                
                # iframe으로 YouTube 영상 표시
                st.markdown(f"""
                <iframe width="100%" height="400" src="{embed_url}" 
                        frameborder="0" allowfullscreen></iframe>
                """, unsafe_allow_html=True)
                
                if st.button("❌ 재생 중지"):
                    st.session_state.playing_video = None
                    st.rerun()
                st.markdown("---")
            
            # 페이지당 21개씩 표시
            items_per_page = 21
            total_pages = (len(st.session_state.youtube_results) + items_per_page - 1) // items_per_page
            
            # 현재 페이지의 결과
            start_idx = st.session_state.youtube_current_page * items_per_page
            end_idx = start_idx + items_per_page
            current_results = st.session_state.youtube_results[start_idx:end_idx]
            
            # 페이지 정보
            st.info(f"페이지 {st.session_state.youtube_current_page + 1}/{total_pages} - {len(current_results)}개 영상")
            
            # 그리드 레이아웃으로 표시 (3열 x 7행 = 21개)
            cols = st.columns(3)
            for i, video in enumerate(current_results):
                col = cols[i % 3]
                
                with col:
                    try:
                        # 썸네일과 제목을 카드 형태로 표시
                        st.markdown(f"""
                        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin: 5px;">
                            <img src="{video['thumbnail']}" width="100%" style="border-radius: 4px;">
                            <p style="margin-top: 8px; font-weight: bold; font-size: 14px;">{video['title']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 재생 버튼과 YouTube 링크
                        col_play, col_link = st.columns([1, 1])
                        
                        with col_play:
                            if st.button(f"▶️ 재생", key=f"play_{video['id']}"):
                                st.session_state.playing_video = video['link']
                                st.rerun()
                        
                        with col_link:
                            st.markdown(f"[YouTube에서 보기]({video['link']})")
                        
                    except Exception as e:
                        st.error(f"비디오 표시 중 오류: {e}")
            
            # 네비게이션 버튼
            st.markdown("---")
            nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns(5)
            
            with nav_col1:
                if st.button("◀️ 이전", disabled=(st.session_state.youtube_current_page == 0)):
                    st.session_state.youtube_current_page = max(0, st.session_state.youtube_current_page - 1)
                    st.rerun()
            
            with nav_col2:
                st.write(f"페이지 {st.session_state.youtube_current_page + 1}/{total_pages}")
            
            with nav_col3:
                if st.button("다음 ▶️", disabled=(st.session_state.youtube_current_page >= total_pages - 1)):
                    st.session_state.youtube_current_page = min(total_pages - 1, st.session_state.youtube_current_page + 1)
                    st.rerun()
            
            with nav_col4:
                if st.button("처음으로"):
                    st.session_state.youtube_current_page = 0
                    st.rerun()
            
            with nav_col5:
                if st.button("더 로드", disabled=st.session_state.youtube_loading):
                    st.session_state.youtube_loading = True
                    with st.spinner("더 많은 결과를 로드 중..."):
                        # 추가 검색 결과 로드
                        additional_results = search_youtube(query, max_results=50)
                        # 중복 제거하면서 추가
                        existing_ids = {v['id'] for v in st.session_state.youtube_results}
                        new_results = [v for v in additional_results if v['id'] not in existing_ids]
                        st.session_state.youtube_results.extend(new_results)
                        st.session_state.youtube_loading = False
                        st.rerun()
            
            # 자동 로드 옵션
            if st.checkbox("자동으로 더 로드", key="auto_load"):
                if st.session_state.youtube_current_page >= total_pages - 1:
                    # 마지막 페이지에 도달하면 자동으로 더 로드
                    if not st.session_state.youtube_loading:
                        st.session_state.youtube_loading = True
                        with st.spinner("자동으로 더 많은 결과를 로드 중..."):
                            additional_results = search_youtube(query, max_results=50)
                            existing_ids = {v['id'] for v in st.session_state.youtube_results}
                            new_results = [v for v in additional_results if v['id'] not in existing_ids]
                            st.session_state.youtube_results.extend(new_results)
                            st.session_state.youtube_loading = False
                            st.rerun()
        else:
            st.warning("검색 결과가 없습니다.")


def main():
    app = MissionAlarmApp()
    st.sidebar.title("📙 공부 도우미")
    st.sidebar.markdown("---")

    # 이스터에그 상태 초기화 (앱이 로드될 때마다)
    if "easter_egg_mp3" not in st.session_state:
        st.session_state.easter_egg_mp3 = False
    if "easter_egg_mp4" not in st.session_state:
        st.session_state.easter_egg_mp4 = False
    if "easter_egg_stock" not in st.session_state:
        st.session_state.easter_egg_stock = False
    if "easter_egg_asiankungfugeneration" not in st.session_state:
        st.session_state.easter_egg_asiankungfugeneration = False
    if "easter_egg_kino" not in st.session_state:
        st.session_state.easter_egg_kino = False
    if "easter_egg_bocchitherock" not in st.session_state:
        st.session_state.easter_egg_bocchitherock = False
    if "easter_egg_youtube" not in st.session_state:
        st.session_state.easter_egg_youtube = False
    if "easter_egg_yiruma" not in st.session_state:
        st.session_state.easter_egg_yiruma = False
    if "easter_egg_yukikuramoto" not in st.session_state:
        st.session_state.easter_egg_yukikuramoto = False
    if "easter_egg_ryuichisakamoto" not in st.session_state:
        st.session_state.easter_egg_ryuichisakamoto = False

    # 사이드바 메뉴
    pages = {
        "📆 월간 일정 관리": show_calendar_page,
       # "⏰ 알람 설정": show_alarm_page,
        "❓ 미션 퀴즈": show_quiz_page,
        "🍱 급식 메뉴": show_meals_page,
        "⚙️ 설정": show_settings_page,
        "▶️ 마감에 쫓길 때": show_deadline_youtube_page
    }

    # study 모듈이 성공적으로 임포트되었을 때만 '스터디' 메뉴 추가
    if study:
        pages["📙 스터디"] = show_study_page

    # 이스터에그 메뉴 추가
    if st.session_state.easter_egg_mp3:
        pages["🎵 MP3 플레이어"] = show_mp3_player_page
    if st.session_state.easter_egg_mp4:
        pages["▶️ MP4 플레이어"] = show_mp4_player_page
    if st.session_state.easter_egg_stock:
        pages["📈 주식 차트"] = show_stock_chart_page
    if st.session_state.easter_egg_asiankungfugeneration:
        pages["🎸 ASIAN KUNG-FU GENERATION"] = lambda: show_youtube_playlist_page("ASIAN KUNG-FU GENERATION", "https://www.youtube.com/watch?v=-UC-77f6z9A&list=PLo661GiwfpLtFKbyzWqbURwVJlyGkNMjR")
    if st.session_state.easter_egg_kino:
        pages["🎵 Kino"] = lambda: show_youtube_playlist_page("Kino", "https://www.youtube.com/watch?v=06N4m8iH_DY&list=PL1wBAksWomErk77CKALQTrgaSE5foHeYi&index=1")
    if st.session_state.easter_egg_bocchitherock:
        pages["🎸 Bocchi the Rock!"] = lambda: show_youtube_playlist_page("Bocchi the Rock!", "https://www.youtube.com/watch?v=SDk1RA4g8CA&list=PLEAVhzkMlRMFB3lvPiaabqY9KbkRi0rLQ")
    if st.session_state.easter_egg_youtube:
        pages["▶️ YouTube 검색"] = show_youtube_search_page
    if st.session_state.easter_egg_yiruma:
        pages["🎹 이루마"] = lambda: show_youtube_playlist_page("이루마", "https://www.youtube.com/watch?v=7maJOI3QMu0&list=PLHTh1InhhwT7J5jlmscJeR3aHqP0iYFbG")
    if st.session_state.easter_egg_yukikuramoto:
        pages["🎹 유키 구라모토"] = lambda: show_youtube_playlist_page("유키 구라모토", "https://www.youtube.com/watch?v=7maJOI3QMu0&list=PLHTh1InhhwT7J5jlmscJeR3aHqP0iYFbG")
    if st.session_state.easter_egg_ryuichisakamoto:
        pages["🎹 류이치 사카모토"] = lambda: show_youtube_playlist_page("류이치 사카모토", "https://www.youtube.com/watch?v=7maJOI3QMu0&list=PLHTh1InhhwT7J5jlmscJeR3aHqP0iYFbG")
        
    selected_page = st.sidebar.radio("페이지 선택", list(pages.keys()))

    # 선택된 페이지 렌더링
    if selected_page in [
        "🎵 MP3 플레이어",
        "▶️ MP4 플레이어",
        "📈 주식 차트",
        "🎸 ASIAN KUNG-FU GENERATION",
        "🎵 Kino", 
        "🎸 Bocchi the Rock!",
        "▶️ YouTube 검색",
        "🎹 이루마",
        "🎹 유키 구라모토",
        "🎹 류이치 사카모토"]:
        pages[selected_page]()
    elif selected_page == "📙 스터디":
        show_study_page()
    elif selected_page == "▶️ 마감에 쫓길 때":
        show_deadline_youtube_page()
    elif selected_page == "🍱 급식 메뉴":
        show_meals_page()
    else:
        pages[selected_page](app)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 제작자 정보")
    st.sidebar.markdown("[instagram](https://www.instagram.com/adenosine_triphosphates/)")

if __name__ == "__main__":
    main()




