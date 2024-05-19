from utils import *
import time
import streamlit as st

# 假设其他函数如round_corners, color_to_white, origin_ava_positions, resize_and_overlay已定义
def img_to_base64(img_data):
    import base64
    encoded = base64.b64encode(img_data).decode()
    return f"data:image/png;base64,{encoded}"

def process_images(uploaded_file1, uploaded_file2):
    image_data2 = BytesIO(uploaded_file2.read())
    out_round_corners = round_corners(image_data2, 70)
    result_list = []
    with st.spinner('Wait for it...'):
        for img in uploaded_file1:
            image_data1 = BytesIO(img.read())
            out_color_to_white = color_to_white(image_data1)
            avatar_positions = origin_ava_positions(out_color_to_white)
            result = resize_and_overlay(image_data1, out_round_corners, avatar_positions)
            result_list.append(result)
    st.session_state.generated = 1
    return result_list

def show_page_deal():
    st.set_page_config('AVA Attacher', '🍪')
    st.header(f'欢迎你！{st.session_state.get("user", "")}')

    if "generated_images" not in st.session_state:
        st.session_state.generated_images = []

    uploaded_file1 = st.file_uploader("选择聊天图", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_file2 = st.file_uploader("选择头像", type=["jpg", "jpeg", "png"], accept_multiple_files=False)
    st.session_state.generated = 0

    # 确保result_list初始化
    result_list = []

    if uploaded_file1 and uploaded_file2:
        st.session_state.result_list = process_images(uploaded_file1, uploaded_file2)

    if st.session_state.generated:
        if st.session_state.result_list:
            index = 0
            for r in st.session_state.result_list:
                # 将图像数据转换为Base64编码的URL
                img_base64 = img_to_base64(r.getvalue())

                container = st.container()
                col1, col2 = container.columns([0.7, 0.3])
                # 使用Base64编码的URL显示图像
                # col1.markdown(f'<img src="{img_base64}" alt="Image">', unsafe_allow_html=True)
                st.divider()
                col1.markdown(f'<img src="{img_base64}" style = "width: 600px; height: auto;">', unsafe_allow_html=True)


                # # 在下载按钮中使用Base64编码的数据
                # col2.download_button(
                #     label="Download img",
                #     data=img_base64,
                #     file_name=f"{str(time.time()).replace('.', '_')}.png",
                #     mime="image/png",
                #     key=f"download_{index}"
                # )
                # index += 1
# 调用函数展示页面
show_page_deal()