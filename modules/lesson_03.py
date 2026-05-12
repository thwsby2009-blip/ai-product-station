import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.gridspec as gs
import os
import platform

def run():
    # ═══ 0. 環境設定 (字體處理) ═══
    # 解決 Linux 伺服器沒有微軟正黑體的問題
    if platform.system() == "Windows":
        plt.rcParams["font.family"] = ["Microsoft JhengHei"]
    else:
        plt.rcParams["font.family"] = ["DejaVu Sans"] # Linux 通用字體
    plt.rcParams["axes.unicode_minus"] = False 

    st.title("🎓 Lesson 03: Pandas 全流程實作與進階視覺化")
    st.caption("涵蓋講義 P77 - P90：數據清洗、分組、合併、樞紐及專業儀表板")

    # ═══ 1. P77: 數據載入與清洗 ═══
    # 建立範例資料 (若讀取失敗則自動生成，確保程式不中斷)
    try:
        if os.path.exists("data/practice_income.csv"):
            df_inc = pd.read_csv("data/practice_income.csv")
            df_exp = pd.read_csv("data/practice_expense.csv")
        else:
            # 自動生成模擬數據以利教學示範
            df_inc = pd.DataFrame({
                "年齡組": ["20-30", "31-40", "41-50", "51-60"],
                "月薪": [35000, 55000, 75000, 85000],
                "獎金": [5000, 8000, 15000, 20000]
            })
            df_exp = pd.DataFrame({
                "年齡組": ["20-30", "31-40", "41-50", "51-60"],
                "食衣住行支出": [20000, 25000, 30000, 28000],
                "娛樂教育支出": [5000, 10000, 15000, 12000]
            })
        st.sidebar.success("✅ 數據載入成功")
    except Exception as e:
        st.error(f"資料載入失敗: {e}")
        st.stop()

    # ═══ 2~3. P78-P79: 分組與合併 ═══
    df_inc_avg = df_inc.groupby("年齡組")[["月薪", "獎金"]].mean().reset_index()
    df_final = pd.merge(df_inc_avg, df_exp, on="年齡組", how="inner")
    
    df_final["總收入"] = df_final["月薪"] + df_final["獎金"]
    df_final["總支出"] = df_final["食衣住行支出"] + df_final["娛樂教育支出"]
    df_final["儲蓄額"] = df_final["總收入"] - df_final["總支出"]

    # ═══ 4. P80: Pivot Table 樞紐分析 ═══
    st.header("🎛️ 樞紐分析預覽 (P80)")
    df_pivot = df_final.pivot_table(index="年齡組", values=["總收入", "總支出", "儲蓄額"])
    st.dataframe(df_pivot.style.background_gradient(cmap="YlGn"))

    # ═══ 5. P81: Plotly 互動視覺化 ═══
    st.divider()
    st.header("📈 進階圖表實作 (P81)")
    t1, t2, t3 = st.tabs(["圓餅圖", "散佈圖", "折線圖"])
    with t1:
        fig_pie = px.pie(df_final, values='總收入', names='年齡組', hole=0.4, title="收入貢獻占比")
        st.plotly_chart(fig_pie, use_container_width=True)
    with t2:
        st.scatter_chart(data=df_final, x="月薪", y="總支出", color="年齡組")
    with t3:
        st.line_chart(data=df_final, x="年齡組", y=["月薪", "獎金"])

    # ═══ 6. P82: 資料分箱 (pd.cut) ═══
    st.divider()
    st.header("📦 P82: 資料分箱與標籤化")
    bins = [-float('inf'), 10000, 20000, float('inf')]
    labels = ["🔴 消費緊繃", "🟡 財務穩健", "🟢 儲蓄優渥"]
    df_final["財務狀態"] = pd.cut(df_final["儲蓄額"], bins=bins, labels=labels)
    st.dataframe(df_final[["年齡組", "儲蓄額", "財務狀態"]].sort_values("儲蓄額", ascending=False))

    # ═══ 7. P85: 時間序列處理 ═══
    st.divider()
    st.header("📅 P85: 時間序列處理")
    time_data = {
        "日期": pd.to_datetime(["2024-01-01", "2024-02-14", "2024-03-08", "2024-04-04", "2024-05-01"]),
        "當日營業額": [50000, 85000, 62000, 78000, 55000]
    }
    df_time = pd.DataFrame(time_data)
    df_time["月份"] = df_time["日期"].dt.month
    df_time["星期幾"] = df_time["日期"].dt.day_name()
    st.dataframe(df_time)

    # ═══ 8~10. P86-P88: Matplotlib & Seaborn 視覺化 ═══
    st.divider()
    st.header("📊 P86-P88: 統計視覺化盛宴")
    
    # 模擬 P88 Tips 資料集
    try:
        tips = sns.load_dataset("tips")
        fig_sns, axes = plt.subplots(1, 2, figsize=(12, 5))
        sns.boxplot(data=tips, x="day", y="total_bill", ax=axes[0], palette="Greens")
        axes[0].set_title("各星期消費分布 (箱型圖)")
        sns.violinplot(data=tips, x="sex", y="tip", ax=axes[1], palette="Set2")
        axes[1].set_title("男女小費分布 (小提琴圖)")
        st.pyplot(fig_sns)
    except:
        st.warning("⚠️ 無法連線載入 Seaborn 內建資料集，跳過此練習。")

    # ═══ 11. P90: 銷售儀表板 (GridSpec) ═══
    st.divider()
    st.header("📊 P90: 專業銷售儀表板佈局")
    fig_dash = plt.figure(figsize=(12, 7))
    grid = gs.GridSpec(2, 2, figure=fig_dash)
    
    # 上方折線圖
    ax1 = fig_dash.add_subplot(grid[0, :])
    ax1.plot(range(1, 13), np.random.randint(80, 150, 12), "b-o", label="實際銷售")
    ax1.set_title("月度銷售趨勢")
    
    # 左下長條圖
    ax2 = fig_dash.add_subplot(grid[1, 0])
    ax2.bar(["北", "中", "南"], [450, 380, 410], color="skyblue")
    ax2.set_title("區域績效")
    
    # 右下圓餅圖
    ax3 = fig_dash.add_subplot(grid[1, 1])
    ax3.pie([35, 25, 40], labels=["A", "B", "C"], autopct="%1.1f%%")
    ax3.set_title("產品占比")
    
    plt.tight_layout()
    st.pyplot(fig_dash)

    # ═══ 12. 數據導出 ═══
    st.divider()
    st.header("💾 數據導出")
    csv = df_final.to_csv(index=False).encode('utf-8-sig')
    st.download_button(label="📥 下載 CSV 分析報表", data=csv, file_name='report.csv', mime='text/csv')
