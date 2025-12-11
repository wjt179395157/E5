# test_app.py - 修复版
"""
记账应用单元测试
"""
import pytest
import os
import json
from datetime import datetime, timedelta
from app import AccountingApp
from models import TransactionType, Transaction
from storage import Storage


@pytest.fixture
def temp_data_file(tmp_path):
    """创建临时数据文件"""
    data_file = tmp_path / "test_data.json"
    return str(data_file)


@pytest.fixture
def app(temp_data_file):
    """创建测试用的应用实例"""
    # 直接创建带有临时文件的应用实例
    app_instance = AccountingApp()
    app_instance.storage = Storage(temp_data_file)
    return app_instance


@pytest.fixture
def app_with_data(temp_data_file):
    """创建带有初始数据的应用实例"""
    # 准备测试数据
    test_data = {
        'transactions': [
            {
                'id': 'test-1',
                'amount': 1000.0,
                'type': 'INCOME',
                'category': '工资💰',
                'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
                'note': '测试收入'
            },
            {
                'id': 'test-2',
                'amount': 200.0,
                'type': 'EXPENSE',
                'category': '餐饮🍜',
                'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
                'note': '测试支出'
            },
            {
                'id': 'test-3',
                'amount': 500.0,
                'type': 'INCOME',
                'category': '奖金🎁',
                'date': (datetime.now() - timedelta(days=35)).strftime('%Y-%m-%d %H:%M:%S'),
                'note': '超过30天的收入'
            }
        ],
        'balance': 1300.0
    }
    
    with open(temp_data_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    app_instance = AccountingApp()
    app_instance.storage = Storage(temp_data_file)
    return app_instance


# ============================================================
# 测试子功能1: add_transaction (添加交易)
# 目标: 12个测试用例,覆盖各种边界条件
# ============================================================

class TestAddTransaction:
    """测试添加交易功能"""
    
    def test_add_expense_valid(self, app):
        """测试用例1: 添加有效的支出交易"""
        result = app.add_transaction(
            amount=100.0,
            trans_type=TransactionType.EXPENSE,
            category="餐饮🍜",
            note="午餐"
        )
        
        assert result is not None
        assert result.amount == 100.0
        assert result.type == TransactionType.EXPENSE
        assert result.category == "餐饮🍜"
        assert result.note == "午餐"
        assert app.get_balance() == -100.0
    
    def test_add_income_valid(self, app):
        """测试用例2: 添加有效的收入交易"""
        result = app.add_transaction(
            amount=5000.0,
            trans_type=TransactionType.INCOME,
            category="工资💰",
            note="月薪"
        )
        
        assert result is not None
        assert result.amount == 5000.0
        assert result.type == TransactionType.INCOME
        assert app.get_balance() == 5000.0
    
    def test_add_transaction_without_note(self, app):
        """测试用例3: 添加交易时不提供备注"""
        result = app.add_transaction(
            amount=50.0,
            trans_type=TransactionType.EXPENSE,
            category="交通🚗"
        )
        
        assert result.note == ""
        assert result.amount == 50.0
    
    def test_add_transaction_zero_amount(self, app):
        """测试用例4: 添加金额为0的交易(边界条件)"""
        with pytest.raises(ValueError, match="金额必须大于0"):
            app.add_transaction(
                amount=0.0,
                trans_type=TransactionType.EXPENSE,
                category="餐饮🍜"
            )
    
    def test_add_transaction_negative_amount(self, app):
        """测试用例5: 添加负金额的交易(边界条件)"""
        with pytest.raises(ValueError, match="金额必须大于0"):
            app.add_transaction(
                amount=-100.0,
                trans_type=TransactionType.INCOME,
                category="工资💰"
            )
    
    def test_add_transaction_very_small_amount(self, app):
        """测试用例6: 添加极小金额的交易(边界条件)"""
        result = app.add_transaction(
            amount=0.01,
            trans_type=TransactionType.EXPENSE,
            category="其他📦",
            note="最小金额"
        )
        
        assert result.amount == 0.01
        assert app.get_balance() == -0.01
    
    def test_add_transaction_very_large_amount(self, app):
        """测试用例7: 添加极大金额的交易(边界条件)"""
        result = app.add_transaction(
            amount=999999999.99,
            trans_type=TransactionType.INCOME,
            category="投资📈",
            note="大额收入"
        )
        
        assert result.amount == 999999999.99
        assert app.get_balance() == 999999999.99
    
    def test_add_multiple_transactions(self, app):
        """测试用例8: 连续添加多个交易"""
        app.add_transaction(100.0, TransactionType.INCOME, "工资💰", "收入1")
        app.add_transaction(50.0, TransactionType.EXPENSE, "餐饮🍜", "支出1")
        app.add_transaction(200.0, TransactionType.INCOME, "奖金🎁", "收入2")
        app.add_transaction(30.0, TransactionType.EXPENSE, "交通🚗", "支出2")
        
        balance = app.get_balance()
        assert balance == 220.0  # 100 - 50 + 200 - 30
        
        transactions = app.storage.get_all_transactions()
        assert len(transactions) == 4
    
    def test_add_transaction_with_special_characters(self, app):
        """测试用例9: 备注包含特殊字符"""
        result = app.add_transaction(
            amount=100.0,
            trans_type=TransactionType.EXPENSE,
            category="餐饮🍜",
            note="测试!@#$%^&*()_+{}[]|\\:;<>?,./~`"
        )
        
        assert result.note == "测试!@#$%^&*()_+{}[]|\\:;<>?,./~`"
    
    def test_add_transaction_with_long_note(self, app):
        """测试用例10: 备注包含长文本"""
        long_note = "这是一个很长的备注" * 100
        result = app.add_transaction(
            amount=100.0,
            trans_type=TransactionType.EXPENSE,
            category="其他📦",
            note=long_note
        )
        
        assert result.note == long_note
    
    def test_add_transaction_generates_unique_id(self, app):
        """测试用例11: 验证每个交易都有唯一ID"""
        t1 = app.add_transaction(100.0, TransactionType.INCOME, "工资💰")
        t2 = app.add_transaction(200.0, TransactionType.EXPENSE, "餐饮🍜")
        t3 = app.add_transaction(300.0, TransactionType.INCOME, "奖金🎁")
        
        assert t1.id != t2.id
        assert t2.id != t3.id
        assert t1.id != t3.id
    
    def test_add_transaction_persists_to_storage(self, app, temp_data_file):
        """测试用例12: 验证交易被正确保存到存储"""
        app.add_transaction(
            amount=250.0,
            trans_type=TransactionType.EXPENSE,
            category="购物🛒",
            note="购物消费"
        )
        
        # 重新加载数据验证持久化
        with open(temp_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert len(data['transactions']) == 1
        assert data['transactions'][0]['amount'] == 250.0
        assert data['balance'] == -250.0


# ============================================================
# 测试子功能2: get_summary (获取汇总统计)
# 目标: 13个测试用例,覆盖各种场景
# ============================================================

class TestGetSummary:
    """测试获取汇总统计功能"""
    
    def test_get_summary_empty_data(self, app):
        """测试用例1: 空数据时的汇总"""
        summary = app.get_summary(30)
        
        assert summary['total_income'] == 0
        assert summary['total_expense'] == 0
        assert summary['balance'] == 0
        assert summary['count'] == 0
    
    def test_get_summary_with_data_30_days(self, app_with_data):
        """测试用例2: 有数据时的30天汇总"""
        summary = app_with_data.get_summary(30)
        
        # 应该包含test-1和test-2(都在30天内),不包含test-3(超过30天)
        assert summary['total_income'] == 1000.0
        assert summary['total_expense'] == 200.0
        assert summary['balance'] == 800.0
        assert summary['count'] == 2
    
    def test_get_summary_with_data_7_days(self, app_with_data):
        """测试用例3: 7天内的汇总"""
        summary = app_with_data.get_summary(7)
        
        # 所有测试数据都在7天内
        assert summary['total_income'] == 1000.0
        assert summary['total_expense'] == 200.0
        assert summary['count'] == 2
    
    def test_get_summary_with_data_60_days(self, app_with_data):
        """测试用例4: 60天内的汇总"""
        summary = app_with_data.get_summary(60)
        
        # 应该包含所有交易(包括35天前的)
        assert summary['total_income'] == 1500.0  # 1000 + 500
        assert summary['total_expense'] == 200.0
        assert summary['balance'] == 1300.0
        assert summary['count'] == 3
    
    def test_get_summary_one_day(self, app):
        """测试用例5: 测试1天的汇总"""
        # 添加今天的交易
        app.add_transaction(100.0, TransactionType.INCOME, "工资💰")
        app.add_transaction(50.0, TransactionType.EXPENSE, "餐饮🍜")
        
        summary = app.get_summary(1)
        
        assert summary['total_income'] == 100.0
        assert summary['total_expense'] == 50.0
        assert summary['balance'] == 50.0
        assert summary['count'] == 2
    
    def test_get_summary_only_income(self, app):
        """测试用例6: 只有收入的情况"""
        app.add_transaction(1000.0, TransactionType.INCOME, "工资💰")
        app.add_transaction(500.0, TransactionType.INCOME, "奖金🎁")
        
        summary = app.get_summary(30)
        
        assert summary['total_income'] == 1500.0
        assert summary['total_expense'] == 0
        assert summary['balance'] == 1500.0
        assert summary['count'] == 2
    
    def test_get_summary_only_expense(self, app):
        """测试用例7: 只有支出的情况"""
        app.add_transaction(200.0, TransactionType.EXPENSE, "餐饮🍜")
        app.add_transaction(100.0, TransactionType.EXPENSE, "交通🚗")
        
        summary = app.get_summary(30)
        
        assert summary['total_income'] == 0
        assert summary['total_expense'] == 300.0
        assert summary['balance'] == -300.0
        assert summary['count'] == 2
    
    def test_get_summary_zero_days(self, app_with_data):
        """测试用例8: 0天的边界条件"""
        summary = app_with_data.get_summary(0)
        
        # 0天意味着今天,测试数据都不是今天的
        assert summary['count'] == 0
    
    def test_get_summary_negative_days(self, app_with_data):
        """测试用例9: 负数天数的边界条件"""
        summary = app_with_data.get_summary(-10)
        
        # 负数天数应该返回空结果
        assert summary['count'] == 0
    
    def test_get_summary_very_large_days(self, app_with_data):
        """测试用例10: 超大天数(如1000天)"""
        summary = app_with_data.get_summary(1000)
        
        # 应该包含所有交易
        assert summary['total_income'] == 1500.0
        assert summary['total_expense'] == 200.0
        assert summary['count'] == 3
    
    def test_get_summary_balance_calculation(self, app):
        """测试用例11: 验证余额计算的正确性"""
        app.add_transaction(5000.0, TransactionType.INCOME, "工资💰")
        app.add_transaction(1000.0, TransactionType.EXPENSE, "住房🏠")
        app.add_transaction(500.0, TransactionType.EXPENSE, "餐饮🍜")
        app.add_transaction(200.0, TransactionType.INCOME, "奖金🎁")
        
        summary = app.get_summary(30)
        
        expected_balance = 5000 - 1000 - 500 + 200
        assert summary['balance'] == expected_balance
        assert summary['balance'] == summary['total_income'] - summary['total_expense']
    
    def test_get_summary_with_decimal_amounts(self, app):
        """测试用例12: 带小数的金额计算"""
        app.add_transaction(99.99, TransactionType.INCOME, "工资💰")
        app.add_transaction(33.33, TransactionType.EXPENSE, "餐饮🍜")
        app.add_transaction(66.66, TransactionType.EXPENSE, "交通🚗")
        
        summary = app.get_summary(30)
        
        assert abs(summary['total_income'] - 99.99) < 0.01
        assert abs(summary['total_expense'] - 99.99) < 0.01
        assert abs(summary['balance'] - 0) < 0.01
    
    def test_get_summary_multiple_periods(self, app):
        """测试用例13: 测试不同时间段的统计一致性"""
        # 添加不同时间的交易
        app.add_transaction(100.0, TransactionType.INCOME, "工资💰")
        app.add_transaction(50.0, TransactionType.EXPENSE, "餐饮🍜")
        
        summary_7 = app.get_summary(7)
        summary_30 = app.get_summary(30)
        summary_365 = app.get_summary(365)
        
        # 由于所有交易都是今天的,所以三个时间段的结果应该相同
        assert summary_7 == summary_30 == summary_365


# ============================================================
# 运行测试的辅助测试
# ============================================================

def test_transaction_count(app):
    """额外测试: 验证交易计数"""
    assert len(app.storage.get_all_transactions()) == 0
    
    app.add_transaction(100.0, TransactionType.INCOME, "工资💰")
    assert len(app.storage.get_all_transactions()) == 1
    
    app.add_transaction(50.0, TransactionType.EXPENSE, "餐饮🍜")
    assert len(app.storage.get_all_transactions()) == 2


def test_dataframe_generation(app):
    """额外测试: 验证DataFrame生成"""
    df = app.get_transactions_df()
    assert df.empty
    
    app.add_transaction(100.0, TransactionType.INCOME, "工资💰")
    df = app.get_transactions_df()
    assert not df.empty
    assert len(df) == 1
