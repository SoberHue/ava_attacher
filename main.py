import streamlit as st
from streamlit_cookies_controller import CookieController


# 导入你的页面模块，而不是尝试切换文件
# 假设你已经将page_deal和page_login的内容移到了单独的模块中
from pages.page_deal import show_page_deal
from pages.page_log import show_page_log

controller = CookieController()
st.session_state.controller = controller
# user_cookie = controller.get('xr_ava_attacher')
user_cookie = '呱呱大王！'
# 根据cookie是否存在来决定显示哪个“页面”
show_page_deal()
# if user_cookie:
#     st.session_state.user = user_cookie
#     show_page_deal()  # 显示deal页面的内容
# else:
#     # show_page_log()  # 显示login页面的内容
#     st.session_state.user = user_cookie
#     show_page_deal()
