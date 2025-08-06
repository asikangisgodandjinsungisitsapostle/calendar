#!/usr/bin/env python3
"""
미션 알람 앱 실행 스크립트
이 스크립트를 실행하면 자동으로 Streamlit 앱이 시작됩니다.
"""

import subprocess
import sys
import os

def check_streamlit():
    """Streamlit이 설치되어 있는지 확인"""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit():
    """Streamlit 설치"""
    print("Streamlit이 설치되어 있지 않습니다. 설치를 시작합니다...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
        print("Streamlit 설치가 완료되었습니다!")
        return True
    except subprocess.CalledProcessError:
        print("Streamlit 설치에 실패했습니다.")
        return False

def run_app():
    """미션 알람 앱 실행"""
    app_file = "mission_alarm_app.py"
    
    if not os.path.exists(app_file):
        print(f"오류: {app_file} 파일을 찾을 수 없습니다.")
        print("현재 디렉토리에 mission_alarm_app.py 파일이 있는지 확인해주세요.")
        return False
    
    print("미션 알람 앱을 시작합니다...")
    print("브라우저에서 http://localhost:8501 로 접속하세요.")
    print("앱을 종료하려면 Ctrl+C를 누르세요.")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_file,
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n앱이 종료되었습니다.")
    except Exception as e:
        print(f"앱 실행 중 오류가 발생했습니다: {e}")
        return False
    
    return True

def main():
    """메인 함수"""
    print("=" * 50)
    print("🎯 미션 알람 앱")
    print("=" * 50)
    
    # Streamlit 설치 확인
    if not check_streamlit():
        if not install_streamlit():
            print("설치에 실패했습니다. 수동으로 설치해주세요:")
            print("pip install streamlit")
            return
    
    # 앱 실행
    run_app()

if __name__ == "__main__":
    main()

