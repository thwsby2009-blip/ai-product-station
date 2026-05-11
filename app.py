from modules import lesson_0, lesson_1, lesson_420, lesson_427, colab

# 🔑 1. UI顯示名稱（人看的）
options = {
    "0. 帳號註冊": "lesson_0",
    "1. ChatGPT": "lesson_1",
    "4/20 Pandas課程": "lesson_420",
    "4/27 AI整合": "lesson_427",
    "Colab": "colab"
}

# sidebar 顯示中文
lesson_ui = st.selectbox("課程選擇", list(options.keys()))

# 🔑 2. 轉換成 module key
lesson_key = options[lesson_ui]

# 🔑 3. module 對應表
lesson_map = {
    "lesson_0": lesson_0,
    "lesson_1": lesson_1,
    "lesson_420": lesson_420,
    "lesson_427": lesson_427,
    "colab": colab
}

# 🔑 4. 防呆執行
if lesson_key in lesson_map:
    lesson_map[lesson_key].run()
else:
    st.error("找不到對應課程模組")
