# models.py - 数据模型
"""
数据模型
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """交易类型"""

    INCOME = "收入"
    EXPENSE = "支出"


@dataclass
class Transaction:
    """交易记录"""

    id: str
    amount: float
    type: TransactionType
    category: str
    date: str
    note: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "type": self.type.name,
            "category": self.category,
            "date": self.date,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            amount=data["amount"],
            type=TransactionType[data["type"]],
            category=data["category"],
            date=data["date"],
            note=data.get("note", ""),
        )


# 预设分类
EXPENSE_CATEGORIES = [
    "餐饮🍜",
    "交通🚗",
    "购物🛒",
    "娱乐🎬",
    "医疗⚕️",
    "教育📚",
    "住房🏠",
    "其他📦",
]
INCOME_CATEGORIES = ["工资💰", "奖金🎁", "投资📈", "兼职💼", "其他💵"]
