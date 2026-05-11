import streamlit as st

def run():
    st.header("📘 0. 帳號註冊與環境檢查")

    st.write("這一堂課的重點：建立開發環境與基本工具使用")

    st.subheader("🔗 常用工具連結")
    st.link_button("ChatGPT 登入", "https://chat.openai.com/")
    st.link_button("Microsoft Designer", "https://designer.microsoft.com/")

    st.info("這裡只放『課程內容』，不要放 sidebar 或 selectbox")
