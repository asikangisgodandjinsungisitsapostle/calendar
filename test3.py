import streamlit as st

st.sidebar.title("메뉴")
page = st.sidebar.radio("페이지 선택", ["홈,", "기능 1", "결과 보기"])

if page == "홈":
    st.title("나의 AI 앱에 오신 것을 환영합니다!")
    st.write("이 앱은 당신을 위한 앱입니다")

elif page == "기능1":
    pass

elif page == "결과 보기":
    pass