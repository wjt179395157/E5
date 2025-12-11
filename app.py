# app.py - 核心逻辑
"""
记账应用核心
"""
import uuid
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from models import Transaction, TransactionType, EXPENSE_CATEGORIES, INCOME_CATEGORIES
from storage import Storage


class AccountingApp:
    """记账应用"""

    def __init__(self):
        self.storage = Storage()

    def add_transaction(
        self, amount: float, trans_type: TransactionType, category: str, note: str = ""
    ):
        """添加交易"""
        if amount <= 0:
            raise ValueError("金额必须大于0")

        transaction = Transaction(
            id=str(uuid.uuid4()),
            amount=amount,
            type=trans_type,
            category=category,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            note=note,
        )

        self.storage.add_transaction(transaction)
        return transaction

    def get_balance(self) -> float:
        """获取当前余额"""
        return self.storage.get_balance()

    def get_transactions_df(self) -> pd.DataFrame:
        """获取交易记录DataFrame"""
        transactions = self.storage.get_all_transactions()

        if not transactions:
            return pd.DataFrame(columns=["日期", "类型", "分类", "金额", "备注", "ID"])

        data = []
        for t in transactions:
            data.append(
                {
                    "日期": t.date,
                    "类型": t.type.value,
                    "分类": t.category,
                    "金额": t.amount,
                    "备注": t.note,
                    "ID": t.id,
                }
            )

        df = pd.DataFrame(data)
        df["日期"] = pd.to_datetime(df["日期"])
        return df.sort_values("日期", ascending=False)

    def delete_transaction(self, transaction_id: str):
        """删除交易"""
        return self.storage.delete_transaction(transaction_id)

    def get_summary(self, days: int = 30):
        """获取汇总统计"""
        df = self.get_transactions_df()

        if df.empty:
            return {"total_income": 0, "total_expense": 0, "balance": 0, "count": 0}

        start_date = datetime.now() - timedelta(days=days)
        df_period = df[df["日期"] >= start_date]

        income = df_period[df_period["类型"] == "收入"]["金额"].sum()
        expense = df_period[df_period["类型"] == "支出"]["金额"].sum()

        return {
            "total_income": income,
            "total_expense": expense,
            "balance": income - expense,
            "count": len(df_period),
        }

    def get_category_stats(self, trans_type: str, days: int = 30):
        """获取分类统计"""
        df = self.get_transactions_df()

        if df.empty:
            return pd.DataFrame()

        start_date = datetime.now() - timedelta(days=days)
        df_period = df[df["日期"] >= start_date]
        df_filtered = df_period[df_period["类型"] == trans_type]

        if df_filtered.empty:
            return pd.DataFrame()

        stats = df_filtered.groupby("分类")["金额"].agg(["sum", "count"]).reset_index()
        stats.columns = ["分类", "金额", "笔数"]
        stats = stats.sort_values("金额", ascending=False)
        stats["占比"] = (stats["金额"] / stats["金额"].sum() * 100).round(2)

        return stats

    def get_daily_trend(self, days: int = 30):
        """获取每日趋势"""
        df = self.get_transactions_df()

        if df.empty:
            return pd.DataFrame()

        start_date = datetime.now() - timedelta(days=days)
        df_period = df[df["日期"] >= start_date].copy()

        df_period["日期"] = df_period["日期"].dt.date

        # 分别统计收入和支出
        daily = df_period.groupby(["日期", "类型"])["金额"].sum().reset_index()
        daily = daily.pivot(index="日期", columns="类型", values="金额").fillna(0)

        if "收入" not in daily.columns:
            daily["收入"] = 0
        if "支出" not in daily.columns:
            daily["支出"] = 0

        daily["净收入"] = daily["收入"] - daily["支出"]
        daily = daily.reset_index()

        return daily
