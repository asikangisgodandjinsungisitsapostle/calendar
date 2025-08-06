import streamlit as st
import json
import datetime
import calendar
import random
import threading
import time
import os
import re
from typing import Dict, List, Any

# study 모듈 임포트 (기존 코드 유지)
try:
    import study
except ImportError as e:
    st.error(f"study 모듈을 불러올 수 없습니다: {e}")
    study = None

# 페이지 설정
st.set_page_config(
    page_title="미션 알람",
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
        if 'easter_egg_mp3' not in st.session_state:
            st.session_state.easter_egg_mp3 = False
        if 'easter_egg_mp4' not in st.session_state:
            st.session_state.easter_egg_mp4 = False
    
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
        st.session_state.schedules[date_key].append({
            'task': task,
            'completed': False,
            'created_at': datetime.datetime.now().isoformat()
        })
        self.save_data()

        # 이스터에그 트리거
        if "mp3" in task.lower():
            st.session_state.easter_egg_mp3 = True
        if "mp4" in task.lower():
            st.session_state.easter_egg_mp4 = True

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

def show_youtube_page():
    st.header("▶️ YouTube 동영상")
    st.write("여기에 YouTube 동영상을 삽입할 수 있습니다.")

    youtube_url = st.text_input("YouTube 동영상 URL을 입력하세요:", key="youtube_url_input")

    if youtube_url:
        video_id_match = re.search(r"(?:v=|youtu\.be/|embed/|watch\?v=)([a-zA-Z0-9_-]{11})", youtube_url)
        if video_id_match:
            video_id = video_id_match.group(1)
            st.video(f"https://www.youtube.com/watch?v={video_id}")
        else:
            st.error("유효한 YouTube 동영상 URL이 아닙니다.")

def show_deadline_youtube_page():
    st.header("▶️ 마감에 쫓길 때")
    st.video("https://www.youtube.com/watch?v=C3p4QDW3-g8")

# Google Drive 공유 링크를 직접 다운로드/스트리밍 가능한 링크로 변환하는 함수
def get_gdrive_direct_link(google_drive_share_link):
    file_id_match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", google_drive_share_link)
    if file_id_match:
        file_id = file_id_match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return None

# MP3 플레이어 페이지
def show_mp3_player_page():
    st.header("🎵 MP3 플레이어")
    st.write("구글 드라이브 MP3 폴더의 파일을 재생합니다.")

    mp3_links = [
        "https://drive.google.com/file/d/1XmZFMM36-p8E26BE9o0GhcPGhiglhEsS/view?usp=sharing", # 예시 링크, 실제 파일 링크로 대체 필요
        # 여기에 사용자의 실제 MP3 파일 공유 링크를 추가하세요.
    ]

    if not mp3_links:
        st.info("재생할 MP3 파일 링크가 없습니다. 'mp3' 이스터에그를 통해 추가해주세요.")
        return

    selected_mp3 = st.selectbox("재생할 MP3 선택", mp3_links)
    direct_link = get_gdrive_direct_link(selected_mp3)

    if direct_link:
        st.audio(direct_link, format='audio/mp3')
    else:
        st.error("유효한 구글 드라이브 MP3 링크가 아닙니다.")

# MP4 플레이어 페이지
def show_mp4_player_page():
    st.header("▶️ MP4 플레이어")
    st.write("구글 드라이브 MP4 폴더의 파일을 재생합니다.")

    mp4_links = [
        "https://drive.google.com/file/d/1OCudWUdyzNNxQVu6R1HH4M1wc-3uDvSM/view?usp=sharing", # 예시 링크, 실제 파일 링크로 대체 필요
        # 여기에 사용자의 실제 MP4 파일 공유 링크를 추가하세요.
    ]

    if not mp4_links:
        st.info("재생할 MP4 파일 링크가 없습니다. 'mp4' 이스터에그를 통해 추가해주세요.")
        return

    selected_mp4 = st.selectbox("재생할 MP4 선택", mp4_links)
    direct_link = get_gdrive_direct_link(selected_mp4)

    if direct_link:
        st.video(direct_link, format='video/mp4')
    else:
        st.error("유효한 구글 드라이브 MP4 링크가 아닙니다.")

def main():
    """메인 애플리케이션"""
    # 앱 초기화
    app = MissionAlarmApp()
    
    # 사이드바 네비게이션
    st.sidebar.title("🎯 미션 알람")
    st.sidebar.markdown("---")
    
    # 페이지 선택
    pages = {
        "📆 월간 일정": "calendar",
        "⏰ 알람 설정": "alarm", 
        "❓ 미션 퀴즈": "quiz",
        "⚙️ 설정": "settings",
        "📙 스터디" : "study",
        "▶️ 마감에 쫓길 때" : "deadline_youtube"
    }

    # 이스터에그 페이지 추가
    if st.session_state.easter_egg_mp3:
        pages["🎵 MP3 플레이어"] = "mp3_player"
    if st.session_state.easter_egg_mp4:
        pages["▶️ MP4 플레이어"] = "mp4_player"
    
    selected_page = st.sidebar.radio("페이지 선택", list(pages.keys()))
    page_key = pages[selected_page]
    
    # 현재 상태 표시
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 현재 상태")
    
    today = datetime.date.today()
    today_schedules = app.get_schedules(today)
    completed_count = sum(1 for s in today_schedules if s['completed'])
    total_count = len(today_schedules)
    
    st.sidebar.info(f"오늘의 일정: {completed_count}/{total_count} 완료")
    
    # 페이지 렌더링
    if page_key == "calendar":
        show_calendar_page(app)
    elif page_key == "alarm":
        show_alarm_page(app)
    elif page_key == "quiz":
        show_quiz_page(app)
    elif page_key == "settings":
        show_settings_page(app)
    elif page_key == "study":
        if study:
            study.show_study_page()
        else:
            st.warning("study 모듈을 불러올 수 없습니다.")
    elif page_key == "deadline_youtube":
        show_deadline_youtube_page()
    elif page_key == "mp3_player":
        show_mp3_player_page()
    elif page_key == "mp4_player":
        show_mp4_player_page()

if __name__ == "__main__":
    main()







