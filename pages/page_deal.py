from utils import *
import base64
import time
import streamlit as st




def show_page_deal():
    st.set_page_config('AVA Attacher', '🍪', layout='wide')
    st.header(f'欢迎你！{st.session_state.user}')
    st.session_state.good = False
    # container1 = st.container(h/eight=200)
    # container2 = st.container(height=200)
    # 添加文件上传按钮
    uploaded_file1 = st.file_uploader("选择聊天图", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_file2 = st.file_uploader("选择头像", type=["jpg", "jpeg", "png"], accept_multiple_files=False)
    # if uploaded_file2:
    #     st.image(uploaded_file2, caption='上传的头像')
    # 读取图片数据
    if uploaded_file1 and uploaded_file2:
        image_data2 = BytesIO(uploaded_file2.read())
        out_round_corners = round_corners(image_data2, 60)
        result_list = []
        with st.spinner('Wait for it...'):
            for img in uploaded_file1:
                image_data1 = BytesIO(img.read())
                out_color_to_white = color_to_white(image_data1)  # need
                avatar_positions = origin_ava_positions(out_color_to_white)
                # 圆角头像处理
                result = resize_and_overlay(image_data1, out_round_corners, avatar_positions)
                result_list.append(result)
        if result_list:
            for r in result_list:
                st.image(r, use_column_width=False)
                st.download_button(
                    label="Download img",
                    data=r,
                    file_name=f"{str(time.time()).replace('.','_')}.png",
                    mime="image/png"
                )