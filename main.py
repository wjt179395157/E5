# main.py - Streamlit界面主程序
"""
Streamlit可视化界面
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from app import AccountingApp
from models import TransactionType, EXPENSE_CATEGORIES, INCOME_CATEGORIES


# 页面配置
st.set_page_config(page_title="💰 个人记账本", page_icon="💰", layout="wide")

# 初始化应用
if "app" not in st.session_state:
    st.session_state.app = AccountingApp()

app = st.session_state.app


def show_dashboard():
    """仪表盘页面"""
    st.title("📊 财务仪表盘")

    # 余额卡片
    balance = app.get_balance()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "💰 当前余额", f"¥{balance:,.2f}", delta="账户总额", delta_color="off"
        )

    # 30天统计
    summary_30 = app.get_summary(30)

    with col2:
        st.metric(
            "📈 30天收入",
            f"¥{summary_30['total_income']:,.2f}",
            delta=f"{summary_30['count']}笔交易",
        )

    with col3:
        st.metric(
            "📉 30天支出",
            f"¥{summary_30['total_expense']:,.2f}",
            delta=f"-¥{summary_30['total_expense']:,.2f}",
            delta_color="inverse",
        )

    with col4:
        net = summary_30["balance"]
        st.metric(
            "💵 30天净收入",
            f"¥{net:,.2f}",
            delta="收入-支出",
            delta_color="normal" if net >= 0 else "inverse",
        )

    st.divider()

    # 图表区域
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 支出分类统计")
        expense_stats = app.get_category_stats("支出", 30)

        if not expense_stats.empty:
            fig = px.pie(
                expense_stats,
                values="金额",
                names="分类",
                title="近30天支出分类占比",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(expense_stats, use_container_width=True, hide_index=True)
        else:
            st.info("暂无支出数据")

    with col2:
        st.subheader("💰 收入分类统计")
        income_stats = app.get_category_stats("收入", 30)

        if not income_stats.empty:
            fig = px.pie(
                income_stats,
                values="金额",
                names="分类",
                title="近30天收入分类占比",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(income_stats, use_container_width=True, hide_index=True)
        else:
            st.info("暂无收入数据")

    # 趋势图
    st.subheader("📈 每日收支趋势")
    trend_df = app.get_daily_trend(30)

    if not trend_df.empty:
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=trend_df["日期"],
                y=trend_df["收入"],
                name="收入",
                marker_color="lightgreen",
            )
        )

        fig.add_trace(
            go.Bar(
                x=trend_df["日期"],
                y=-trend_df["支出"],  # 负值显示
                name="支出",
                marker_color="lightcoral",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=trend_df["日期"],
                y=trend_df["净收入"],
                name="净收入",
                mode="lines+markers",
                line=dict(color="blue", width=2),
            )
        )

        fig.update_layout(
            barmode="relative",
            title="近30天收支趋势",
            xaxis_title="日期",
            yaxis_title="金额（元）",
            hovermode="x unified",
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无数据")


def show_add_transaction():
    """添加交易页面"""
    st.title("📝 记一笔")

    # 初始化金额会话态
    if "amount" not in st.session_state:
        st.session_state["amount"] = 100.0

    # 定义回调函数用于快捷金额按钮
    def set_amount(value):
        st.session_state["amount"] = float(value)

    col1, col2 = st.columns([2, 1])

    with col2:
        # 快捷金额放在前面，这样按钮的回调会在输入框渲染前执行
        st.subheader("💡 快捷金额")

        quick_amounts = [10, 20, 50, 100, 200, 500, 1000, 2000]

        for amount_val in quick_amounts:
            st.button(
                f"¥{amount_val}",
                use_container_width=True,
                key=f"quick_{amount_val}",
                on_click=set_amount,  # 使用回调函数
                args=(amount_val,),  # 传递参数
            )

    with col1:
        # 交易类型选择
        trans_type = st.radio(
            "类型", ["支出", "收入"], horizontal=True, key="trans_type"
        )

        # 金额输入 - 绑定到统一的会话态键
        amount = st.number_input(
            "💰 金额", min_value=0.01, step=10.0, format="%.2f", key="amount"
        )

        # 分类选择
        if trans_type == "支出":
            categories = EXPENSE_CATEGORIES
        else:
            categories = INCOME_CATEGORIES

        category = st.selectbox("📂 分类", categories)

        # 备注输入
        note = st.text_input("📝 备注", placeholder="可选，输入备注信息...")

        # 提交按钮
        if st.button("✅ 提交记录", type="primary", use_container_width=True):
            try:
                trans_type_enum = (
                    TransactionType.EXPENSE
                    if trans_type == "支出"
                    else TransactionType.INCOME
                )
                app.add_transaction(
                    st.session_state["amount"], trans_type_enum, category, note
                )
                st.success(
                    f"✅ 记账成功！{trans_type} ¥{st.session_state['amount']:.2f}"
                )
                st.balloons()

                # 显示当前余额
                st.info(f"💰 当前余额: ¥{app.get_balance():,.2f}")

            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")


def show_transactions():
    """交易记录页面"""
    st.title("📋 交易记录")

    # 获取数据
    df = app.get_transactions_df()

    if df.empty:
        st.info("暂无交易记录")
        return

    # 筛选器
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        filter_type = st.multiselect(
            "类型筛选", ["收入", "支出"], default=["收入", "支出"]
        )

    with col2:
        categories = df["分类"].unique().tolist()
        filter_category = st.multiselect("分类筛选", categories, default=categories)

    with col3:
        limit = st.number_input("显示条数", min_value=10, max_value=1000, value=50)

    # 应用筛选
    df_filtered = df[
        (df["类型"].isin(filter_type)) & (df["分类"].isin(filter_category))
    ].head(limit)

    st.write(f"共 {len(df_filtered)} 条记录")

    # 显示表格
    display_df = df_filtered[["日期", "类型", "分类", "金额", "备注"]].copy()
    display_df["日期"] = display_df["日期"].dt.strftime("%Y-%m-%d %H:%M")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={"金额": st.column_config.NumberColumn("金额", format="¥%.2f")},
    )

    # 删除功能
    st.divider()
    st.subheader("🗑️ 删除记录")

    with st.form("delete_form"):
        transaction_ids = df_filtered["ID"].tolist()
        transaction_labels = [
            f"{row['日期'].strftime('%Y-%m-%d %H:%M')} - {row['类型']} - {row['分类']} - ¥{row['金额']:.2f}"
            for _, row in df_filtered.iterrows()
        ]

        selected = st.selectbox(
            "选择要删除的记录",
            range(len(transaction_ids)),
            format_func=lambda i: transaction_labels[i],
        )

        submitted = st.form_submit_button("🗑️ 删除", type="primary")

        if submitted:
            if app.delete_transaction(transaction_ids[selected]):
                st.success("✅ 删除成功")
                st.rerun()
            else:
                st.error("❌ 删除失败")


def show_statistics():
    """统计分析页面"""
    st.title("📊 统计分析")

    # 时间范围选择
    days = st.selectbox(
        "统计周期",
        [7, 15, 30, 60, 90, 180, 365],
        index=2,
        format_func=lambda x: f"近{x}天",
    )

    summary = app.get_summary(days)

    # 汇总卡片
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📈 总收入", f"¥{summary['total_income']:,.2f}")

    with col2:
        st.metric("📉 总支出", f"¥{summary['total_expense']:,.2f}")

    with col3:
        net = summary["balance"]
        st.metric(
            "💵 净收入", f"¥{net:,.2f}", delta_color="normal" if net >= 0 else "inverse"
        )

    st.divider()

    # 分类详细统计
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📉 支出详情")
        expense_stats = app.get_category_stats("支出", days)

        if not expense_stats.empty:
            # 柱状图
            fig = px.bar(
                expense_stats,
                x="分类",
                y="金额",
                text="金额",
                title=f"近{days}天支出分类",
                color="金额",
                color_continuous_scale="Reds",
            )
            fig.update_traces(texttemplate="¥%{text:.2f}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(expense_stats, use_container_width=True, hide_index=True)
        else:
            st.info("暂无支出数据")

    with col2:
        st.subheader("📈 收入详情")
        income_stats = app.get_category_stats("收入", days)

        if not income_stats.empty:
            # 柱状图
            fig = px.bar(
                income_stats,
                x="分类",
                y="金额",
                text="金额",
                title=f"近{days}天收入分类",
                color="金额",
                color_continuous_scale="Greens",
            )
            fig.update_traces(texttemplate="¥%{text:.2f}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(income_stats, use_container_width=True, hide_index=True)
        else:
            st.info("暂无收入数据")


# 侧边栏导航
with st.sidebar:
    st.title("💰 个人记账本")
    st.divider()

    page = st.radio(
        "导航",
        ["📊 仪表盘", "📝 记一笔", "📋 交易记录", "📈 统计分析"],
        label_visibility="collapsed",
    )

    st.divider()

    # 显示当前余额
    balance = app.get_balance()
    st.metric("💰 当前余额", f"¥{balance:,.2f}")

    # 今日统计
    today_summary = app.get_summary(1)
    st.metric("📅 今日收入", f"¥{today_summary['total_income']:.2f}")
    st.metric("📅 今日支出", f"¥{today_summary['total_expense']:.2f}")

    st.divider()
    st.caption("© 2024 个人记账本系统")


# 路由
if page == "📊 仪表盘":
    show_dashboard()
elif page == "📝 记一笔":
    show_add_transaction()
elif page == "📋 交易记录":
    show_transactions()
elif page == "📈 统计分析":
    show_statistics()
