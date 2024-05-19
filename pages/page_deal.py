from utils import *
import base64
import time
import streamlit as st
from itertools import cycle




def show_page_deal():
    st.set_page_config('AVA Attacher', '🍪', layout='wide')
    st.header(f'欢迎你！{st.session_state.user}')
    st.session_state.good = False
    container1 = st.container(height=300, border=True)
    container2 = st.container(height=300, border=True)
    # 添加文件上传按钮
    uploaded_file1 = container1.file_uploader("选择聊天图", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    uploaded_file2 = container2.file_uploader("选择头像", type=["jpg", "jpeg", "png"], accept_multiple_files=False)

    # if uploaded_files:
    #     THUMBNAIL_HEIGHT = 200  # 确保这个高度适合您的布局需求，之前示例中误写为20
    #
    #     # 计算每行可以展示的图片数量（这里假设一个合适的数量，您可能需要根据实际情况调整）
    #     images_per_row = 12  # 例如，每行展示12张图片
    #     columns = container1.columns(images_per_row)  # 创建相应数量的列
    #
    #     for idx, uploaded_file in enumerate(uploaded_files):
    #         image_data = uploaded_file.read()
    #         image = Image.open(BytesIO(image_data))
    #
    #         # 直接基于THUMBNAIL_HEIGHT调整高度，宽度按比例计算
    #         width, original_height = image.size
    #         new_height = THUMBNAIL_HEIGHT
    #         ratio = new_height / original_height
    #         new_width = int(width * ratio)
    #
    #         resized_image = image.resize((new_width, new_height), resample=Image.LANCZOS)
    #         img_byte_arr = BytesIO()
    #         resized_image.save(img_byte_arr, format='PNG')
    #         img_byte_arr.seek(0)
    #
    #         col_idx = idx % images_per_row
    #         columns[col_idx].image(img_byte_arr, caption=uploaded_file.name, use_column_width=False)

    # 读取图片数据
    if uploaded_file1 and uploaded_file2:
        image_data2 = BytesIO(uploaded_file2.read())
        result_list = []
        with st.spinner('Wait for it...'):
            container2.image(uploaded_file2, caption='上传的头像', use_column_width="never")
            for img in uploaded_file1:
                image_data2.seek(0)
                image_data1 = BytesIO(img.read())
                out_color_to_white = color_to_white(image_data1)  # need
                avatar_positions = origin_ava_positions(out_color_to_white)

                # 圆角头像处理
                out_round_corners = round_corners(image_data2, 90)
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

        # # 当用户上传文件后执行以下操作
        # if st.session_state.get('good', None):
        #     # 使用st.image显示上传的图片
        #     st.image(result, caption='处理完的图片', use_column_width=True)
        #     st.session_state.good = False
        #     # 定义一个下载按钮，当点击时触发下载
        #     if st.button('Download Image'):
        #         # 将BytesIO对象转换为Base64编码，以便在HTML中使用
        #         img_str = base64.b64encode(result.getvalue()).decode()
        #         href = f'<a href="data:image/png;base64,{img_str}" download="example_image.png">Download PNG Image</a>'
        #         # 在Streamlit中显示可点击的链接
        #         st.markdown(href, unsafe_allow_html=True)
        #     st.success('Done!')
        # else:
        #     st.success('我也不知道咋出错啦!问问那个搞开发的叭！记得把出错的数据给他！')
