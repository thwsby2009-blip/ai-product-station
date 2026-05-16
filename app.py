import streamlit as st
import sys
import os
import importlib
# --- 核心修正：強制讓 Python 看到 modules 資料夾 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

st.set_page_config(page_title="AI 課程", layout="wide")

# 1️⃣ 選項對照表
options = {
    "1. AI 產品設計全流程工作站": "modules.lesson_0",
    "2. AI 分析數據": "modules.lesson_1",
    "3. AI 金流數據分析": "modules.lesson_02",
    "4. AI 數據分析": "modules.lesson_03",
    "5. AI 網頁功能協助開發": "modules.lesson_04",
    "6. 🌊 台灣海象即時儀表板": "modules.lesson_05"
    "7. AI 簡報工具入口": "modules.lesson_06"
}

# 2️⃣ UI 介面
lesson_ui = st.selectbox("📖 課程選擇", list(options.keys()))
module_path = options[lesson_ui]

st.divider()

# 3️⃣ 動態執行
try:
    # 根據選擇動態載入模組
    target_module = importlib.import_module(module_path)
    if hasattr(target_module, 'run'):
        target_module.run()
    else:
        st.error(f"錯誤：{module_path} 檔案中找不到 run() 函式")
except ImportError as e:
    st.error(f"無法載入課程模組：{e}")
    st.info("💡 解決辦法：請檢查 GitHub 中是否存在 'modules' 資料夾，且裡面必須有一個空的 '__init__.py' 檔案。")
except Exception as e:
    st.error(f"發生意外錯誤：{e}")
