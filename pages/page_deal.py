from utils import *
import base64


def show_page_deal():
    st.set_page_config('AVA Attacher', '🍪', layout='wide')
    st.header(f'欢迎你！{st.session_state.user}')
    st.session_state.good = False
    container1 = st.container(height=300,border=bool)
    container2 = st.container(height=300,border=bool)
    col1, col2 = container1.columns(2)
    col3, col4 = container2.columns(2)
    # 添加文件上传按钮
    uploaded_file1 = col1.file_uploader("选择聊天图", type=["jpg", "jpeg", "png"])
    uploaded_file2 = col3.file_uploader("选择头像", type=["jpg", "jpeg", "png"])
    # 读取图片数据
    if uploaded_file1 and uploaded_file2:
        with st.spinner('Wait for it...'):
            col2.image(uploaded_file1, caption='上传的聊天图', use_column_width="always")
            col4.image(uploaded_file2, caption='上传的头像', use_column_width="always")
            image_data1 = BytesIO(uploaded_file1.read())
            image_data2 = BytesIO(uploaded_file2.read())

            out_color_to_white = color_to_white(image_data1)  # need
            avatar_positions = origin_ava_positions(out_color_to_white)

            # 圆角头像处理
            out_round_corners = round_corners(image_data2, 90)
            result = resize_and_overlay(image_data1, out_round_corners, avatar_positions)

        # 当用户上传文件后执行以下操作
        if st.session_state.get('good', None):
            # 使用st.image显示上传的图片
            st.image(result, caption='处理完的图片', use_column_width=True)
            st.session_state.good = False
            # 定义一个下载按钮，当点击时触发下载
            if st.button('Download Image'):
                # 将BytesIO对象转换为Base64编码，以便在HTML中使用
                img_str = base64.b64encode(result.getvalue()).decode()
                href = f'<a href="data:image/png;base64,{img_str}" download="example_image.png">Download PNG Image</a>'
                # 在Streamlit中显示可点击的链接
                st.markdown(href, unsafe_allow_html=True)
            st.success('Done!')
        else:
            st.success('我也不知道咋出错啦!问问那个搞开发的叭！记得把出错的数据给他！')

