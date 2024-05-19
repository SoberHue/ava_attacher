import streamlit as st

def show_page_log():
    controller = st.session_state.controller
    user = st.text_input(":panda_face: 你是谁！", "")
    if st.button("确认"):
        controller.set('xr_ava_attacher', user)
        st.session_state.user = user
        st.experimental_rerun()  # 重新运行应用以跳转到主页面
