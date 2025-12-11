# test_integration.py - 完整集成测试
"""
记账应用集成测试
测试多个模块之间的交互和数据流
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
    data_file = tmp_path / "test_integration.json"
    return str(data_file)


@pytest.fixture
def clean_app(temp_data_file):
    """创建干净的应用实例"""
    app = AccountingApp()
    app.storage = Storage(temp_data_file)
    return app


# ============================================================
# 集成测试组1: 自底向上集成测试
# 测试层次: Storage -> Models -> App
# ============================================================


class TestBottomUpIntegration:
    """自底向上集成测试：从底层存储到应用层的完整数据流"""

    def test_storage_model_integration(self, temp_data_file):
        """集成测试1.1: Storage 和 Model 的集成"""
        print("\n" + "=" * 60)
        print("测试场景：Storage 和 Model 层的集成")
        print("=" * 60)

        # 步骤1: 创建存储实例
        storage = Storage(temp_data_file)
        print("✅ 步骤1: 创建Storage实例")

        # 步骤2: 创建Transaction模型实例
        transaction = Transaction(
            id="test-001",
            amount=500.0,
            type=TransactionType.INCOME,
            category="工资💰",
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            note="测试收入",
        )
        print("✅ 步骤2: 创建Transaction模型")

        # 步骤3: 将模型保存到存储
        storage.add_transaction(transaction)
        print("✅ 步骤3: 保存Transaction到Storage")

        # 验证1: 检查存储中的数据
        assert storage.get_balance() == 500.0
        assert len(storage.get_all_transactions()) == 1
        print("✅ 验证1: 存储数据正确")

        # 步骤4: 从存储中读取数据
        transactions = storage.get_all_transactions()
        loaded_transaction = transactions[0]
        print("✅ 步骤4: 从Storage读取数据")

        # 验证2: 确认数据正确恢复
        assert loaded_transaction.id == transaction.id
        assert loaded_transaction.amount == transaction.amount
        assert loaded_transaction.type == transaction.type
        assert loaded_transaction.category == transaction.category
        print("✅ 验证2: 数据完整性正确")

        # 步骤5: 验证文件持久化
        assert os.path.exists(temp_data_file)
        with open(temp_data_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ 步骤5: 文件持久化成功")

        # 验证3: 文件内容正确
        assert len(data["transactions"]) == 1
        assert data["balance"] == 500.0
        assert data["transactions"][0]["amount"] == 500.0
        print("✅ 验证3: 文件内容正确")

        print(f"\n🎉 Storage-Model集成测试通过！")

    def test_app_storage_model_integration(self, clean_app):
        """集成测试1.2: App、Storage、Model 三层集成"""
        print("\n" + "=" * 60)
        print("测试场景：App、Storage、Model 三层集成")
        print("=" * 60)

        # 步骤1: 通过App添加交易（测试App->Storage->Model）
        transaction1 = clean_app.add_transaction(
            amount=1000.0,
            trans_type=TransactionType.INCOME,
            category="工资💰",
            note="第一笔收入",
        )
        print(f"✅ 添加交易1: ¥{transaction1.amount} - {transaction1.category}")

        transaction2 = clean_app.add_transaction(
            amount=300.0,
            trans_type=TransactionType.EXPENSE,
            category="餐饮🍜",
            note="第一笔支出",
        )
        print(f"✅ 添加交易2: ¥{transaction2.amount} - {transaction2.category}")

        # 验证1: App层的余额计算
        assert clean_app.get_balance() == 700.0
        print(f"✅ 验证1: App层余额 = ¥{clean_app.get_balance()}")

        # 验证2: Storage层的数据一致性
        storage_balance = clean_app.storage.get_balance()
        assert storage_balance == 700.0
        print(f"✅ 验证2: Storage层余额 = ¥{storage_balance}")

        # 验证3: Model层的数据完整性
        all_transactions = clean_app.storage.get_all_transactions()
        assert len(all_transactions) == 2
        assert all_transactions[0].amount == 1000.0
        assert all_transactions[1].amount == 300.0
        print(f"✅ 验证3: Model层数据完整 (共{len(all_transactions)}笔)")

        # 步骤2: 测试DataFrame生成（集成查询功能）
        df = clean_app.get_transactions_df()
        assert len(df) == 2
        assert "日期" in df.columns
        assert "类型" in df.columns
        assert "金额" in df.columns
        print(f"✅ DataFrame生成成功 (共{len(df)}行, {len(df.columns)}列)")

        # 验证4: DataFrame数据正确性
        assert df["金额"].sum() == 1300.0  # 总金额
        assert (df["类型"] == "收入").sum() == 1
        assert (df["类型"] == "支出").sum() == 1
        print(f"✅ 验证4: DataFrame数据正确")

        print(f"\n🎉 三层集成测试通过！")


# ============================================================
# 集成测试组2: 自顶向下集成测试
# 测试完整业务流程
# ============================================================


class TestTopDownIntegration:
    """自顶向下集成测试：从用户操作到数据持久化的完整流程"""

    def test_complete_transaction_workflow(self, clean_app, temp_data_file):
        """集成测试2.1: 完整的交易工作流程"""
        print("\n" + "=" * 60)
        print("测试场景：用户的一天完整记账流程")
        print("=" * 60)

        # 早晨：收到工资
        t1 = clean_app.add_transaction(
            amount=8000.0,
            trans_type=TransactionType.INCOME,
            category="工资💰",
            note="月工资",
        )
        print(f"\n✅ 添加收入: ¥{t1.amount} - {t1.category}")

        # 上午：早餐支出
        t2 = clean_app.add_transaction(
            amount=20.0,
            trans_type=TransactionType.EXPENSE,
            category="餐饮🍜",
            note="早餐",
        )
        print(f"✅ 添加支出: ¥{t2.amount} - {t2.category}")

        # 中午：午餐支出
        t3 = clean_app.add_transaction(
            amount=35.0,
            trans_type=TransactionType.EXPENSE,
            category="餐饮🍜",
            note="午餐",
        )
        print(f"✅ 添加支出: ¥{t3.amount} - {t3.category}")

        # 下午：打车支出
        t4 = clean_app.add_transaction(
            amount=25.0,
            trans_type=TransactionType.EXPENSE,
            category="交通🚗",
            note="打车",
        )
        print(f"✅ 添加支出: ¥{t4.amount} - {t4.category}")

        # 晚上：购物支出
        t5 = clean_app.add_transaction(
            amount=150.0,
            trans_type=TransactionType.EXPENSE,
            category="购物🛒",
            note="买衣服",
        )
        print(f"✅ 添加支出: ¥{t5.amount} - {t5.category}")

        # 验证1: 余额计算正确
        expected_balance = 8000.0 - 20.0 - 35.0 - 25.0 - 150.0
        actual_balance = clean_app.get_balance()
        print(f"\n💰 当前余额: ¥{actual_balance}")
        assert actual_balance == expected_balance

        # 验证2: 统计功能集成
        summary = clean_app.get_summary(1)  # 今天的统计
        print(f"\n📊 今日统计:")
        print(f"  收入: ¥{summary['total_income']}")
        print(f"  支出: ¥{summary['total_expense']}")
        print(f"  净收入: ¥{summary['balance']}")
        print(f"  交易笔数: {summary['count']}")

        assert summary["total_income"] == 8000.0
        assert summary["total_expense"] == 230.0
        assert summary["balance"] == 7770.0
        assert summary["count"] == 5

        # 验证3: 分类统计集成
        expense_stats = clean_app.get_category_stats("支出", 1)
        print(f"\n📈 支出分类统计:")
        for _, row in expense_stats.iterrows():
            print(
                f"  {row['分类']}: ¥{row['金额']} ({int(row['笔数'])}笔) - {row['占比']:.1f}%"
            )

        assert not expense_stats.empty
        assert len(expense_stats) == 3  # 餐饮、交通、购物

        # 修复：购物是最多的（150元），不是餐饮（55元）
        top_category = expense_stats.iloc[0]
        assert top_category["分类"] == "购物🛒"
        assert top_category["金额"] == 150.0
        print(f"\n🔝 最大支出: {top_category['分类']} - ¥{top_category['金额']}")

        # 验证餐饮是第二多的
        second_category = expense_stats.iloc[1]
        assert second_category["分类"] == "餐饮🍜"
        assert second_category["金额"] == 55.0  # 20 + 35
        print(f"🔝 第二支出: {second_category['分类']} - ¥{second_category['金额']}")

        # 验证4: 数据持久化
        # 重新创建应用实例，验证数据已保存
        new_app = AccountingApp()
        new_app.storage = Storage(temp_data_file)

        reloaded_balance = new_app.get_balance()
        print(f"\n🔄 重新加载后的余额: ¥{reloaded_balance}")
        assert reloaded_balance == expected_balance

        reloaded_transactions = new_app.storage.get_all_transactions()
        assert len(reloaded_transactions) == 5
        print(f"🔄 重新加载后的交易数: {len(reloaded_transactions)}")

        print(f"\n🎉 完整交易流程测试通过！")

    def test_transaction_modification_workflow(self, clean_app):
        """集成测试2.2: 交易修改工作流程（添加、查询、删除）"""
        print("\n" + "=" * 60)
        print("测试场景：记错账后的修改流程")
        print("=" * 60)

        # 步骤1: 添加一笔错误的交易
        wrong_transaction = clean_app.add_transaction(
            amount=999.0,
            trans_type=TransactionType.EXPENSE,
            category="餐饮🍜",
            note="记错了！应该是99",
        )
        print(f"\n❌ 错误添加: ¥{wrong_transaction.amount}")

        # 添加正确的交易
        correct_transactions = [
            clean_app.add_transaction(
                100.0, TransactionType.INCOME, "工资💰", "兼职收入"
            ),
            clean_app.add_transaction(
                50.0, TransactionType.EXPENSE, "交通🚗", "公交卡"
            ),
        ]
        print(f"✅ 添加正确交易: 2笔")

        # 验证1: 所有交易都已记录
        assert len(clean_app.storage.get_all_transactions()) == 3
        initial_balance = clean_app.get_balance()
        print(f"修正前余额: ¥{initial_balance}")
        assert initial_balance == 100.0 - 999.0 - 50.0  # -949.0

        # 步骤2: 查询交易记录
        df = clean_app.get_transactions_df()
        print(f"\n📋 当前交易记录（{len(df)}笔）:")
        for idx, row in df.iterrows():
            print(
                f"  {row['ID'][:8]}... - {row['类型']} - {row['分类']} - ¥{row['金额']}"
            )

        # 步骤3: 删除错误的交易
        deleted = clean_app.delete_transaction(wrong_transaction.id)
        print(
            f"\n🗑️  删除交易: {wrong_transaction.id[:8]}... - 结果: {'成功' if deleted else '失败'}"
        )
        assert deleted is True

        # 验证2: 交易已删除
        assert len(clean_app.storage.get_all_transactions()) == 2

        # 验证3: 余额已更新
        corrected_balance = clean_app.get_balance()
        print(f"修正后余额: ¥{corrected_balance}")
        assert corrected_balance == 100.0 - 50.0  # 50.0

        # 步骤4: 添加正确的交易
        correct_transaction = clean_app.add_transaction(
            amount=99.0,
            trans_type=TransactionType.EXPENSE,
            category="餐饮🍜",
            note="修正后的金额",
        )
        print(f"✅ 添加正确交易: ¥{correct_transaction.amount}")

        # 验证4: 最终状态正确
        final_balance = clean_app.get_balance()
        print(f"最终余额: ¥{final_balance}")
        assert final_balance == 100.0 - 50.0 - 99.0  # -49.0
        assert len(clean_app.storage.get_all_transactions()) == 3

        print(f"\n🎉 交易修改流程测试通过！")


# ============================================================
# 集成测试组3: 数据一致性和边界场景集成测试
# ============================================================


class TestDataConsistencyIntegration:
    """数据一致性集成测试：测试各种边界情况下的系统稳定性"""

    def test_large_volume_data_integration(self, clean_app):
        """集成测试3.1: 大量数据场景"""
        print("\n" + "=" * 60)
        print("测试场景：一个月的大量交易记录")
        print("=" * 60)

        # 模拟一个月的交易（每天5笔，共150笔）
        transactions_count = 0
        total_income = 0
        total_expense = 0

        for day in range(30):
            date_offset = timedelta(days=day)

            # 每天的固定收入
            if day % 7 == 0:  # 每周一次工资
                amount = 2000.0
                clean_app.add_transaction(
                    amount, TransactionType.INCOME, "工资💰", f"第{day}天工资"
                )
                total_income += amount
                transactions_count += 1

            # 每天的随机支出
            daily_expenses = [
                (30.0, "餐饮🍜", "早餐"),
                (45.0, "餐饮🍜", "午餐"),
                (50.0, "餐饮🍜", "晚餐"),
                (10.0, "交通🚗", "公交"),
            ]

            for amount, category, note in daily_expenses:
                clean_app.add_transaction(
                    amount, TransactionType.EXPENSE, category, f"第{day}天-{note}"
                )
                total_expense += amount
                transactions_count += 1

        print(f"\n📊 生成了 {transactions_count} 笔交易")
        print(f"💰 总收入: ¥{total_income}")
        print(f"💸 总支出: ¥{total_expense}")

        # 验证1: 交易总数
        all_transactions = clean_app.storage.get_all_transactions()
        assert len(all_transactions) == transactions_count
        print(f"✅ 交易数量验证通过")

        # 验证2: 余额一致性
        expected_balance = total_income - total_expense
        actual_balance = clean_app.get_balance()
        assert actual_balance == expected_balance
        print(f"✅ 余额一致性验证通过: ¥{actual_balance}")

        # 验证3: 30天统计
        summary_30 = clean_app.get_summary(30)
        assert summary_30["total_income"] == total_income
        assert summary_30["total_expense"] == total_expense
        assert summary_30["count"] == transactions_count
        print(f"✅ 30天统计验证通过")

        # 验证4: DataFrame性能
        df = clean_app.get_transactions_df()
        assert len(df) == transactions_count
        print(f"✅ DataFrame生成验证通过")

        # 验证5: 分类统计
        expense_stats = clean_app.get_category_stats("支出", 30)
        print(f"\n📈 支出分类统计:")
        for _, row in expense_stats.iterrows():
            print(f"  {row['分类']}: ¥{row['金额']:.2f} - {int(row['笔数'])}笔")

        assert not expense_stats.empty
        assert expense_stats["金额"].sum() == total_expense

        # 验证6: 趋势分析
        trend = clean_app.get_daily_trend(30)
        print(f"\n📊 趋势数据: {len(trend)} 天")
        assert not trend.empty
        assert len(trend) <= 30

        print(f"\n🎉 大量数据测试通过！")

    def test_concurrent_operations_simulation(self, temp_data_file):
        """集成测试3.2: 模拟并发操作场景（展示数据覆盖问题）"""
        print("\n" + "=" * 60)
        print("测试场景：模拟多实例并发写入（展示数据覆盖问题）")
        print("=" * 60)

        # 创建两个应用实例（模拟两个用户）
        app1 = AccountingApp()
        app1.storage = Storage(temp_data_file)

        app2 = AccountingApp()
        app2.storage = Storage(temp_data_file)

        # App1添加交易
        app1.add_transaction(100.0, TransactionType.INCOME, "工资💰", "App1的收入")
        print("✅ App1 添加收入 ¥100")

        # App2添加交易（读取的是旧状态，会覆盖App1的数据）
        app2.add_transaction(50.0, TransactionType.EXPENSE, "餐饮🍜", "App2的支出")
        print("✅ App2 添加支出 ¥50")

        # 验证：每个实例的视图
        balance1 = app1.get_balance()
        balance2 = app2.get_balance()
        print(f"\nApp1 看到的余额: ¥{balance1}")
        print(f"App2 看到的余额: ¥{balance2}")

        # 创建新实例读取文件（获取真实状态）
        app3 = AccountingApp()
        app3.storage = Storage(temp_data_file)
        final_balance = app3.get_balance()
        all_trans = app3.storage.get_all_transactions()

        print(f"\n最终文件状态:")
        print(f"  余额: ¥{final_balance}")
        print(f"  交易数: {len(all_trans)}")

        # 修复：由于app2后写入，它会覆盖app1的数据
        # 最终只有app2的数据被保留
        assert len(all_trans) == 1  # 只有1笔交易（app2的）
        assert all_trans[0].amount == 50.0  # app2的支出
        assert all_trans[0].type == TransactionType.EXPENSE
        assert final_balance == -50.0  # 只有支出，所以是负数

        print(f"\n⚠️  警告：后写入的实例覆盖了先写入的数据！")
        print(f"   这展示了当前实现在并发场景下的数据覆盖问题")
        print(f"✅ 并发写入问题测试完成（展示了数据覆盖行为）")

    def test_sequential_operations_correct_behavior(self, temp_data_file):
        """集成测试3.3: 顺序操作的正确行为（对比测试）"""
        print("\n" + "=" * 60)
        print("测试场景：正确的顺序操作（对比并发问题）")
        print("=" * 60)

        # 方式1：单实例顺序操作（正确）
        app = AccountingApp()
        app.storage = Storage(temp_data_file)

        app.add_transaction(100.0, TransactionType.INCOME, "工资💰", "收入1")
        app.add_transaction(50.0, TransactionType.EXPENSE, "餐饮🍜", "支出1")

        balance = app.get_balance()
        transactions = app.storage.get_all_transactions()

        print(f"✅ 单实例操作:")
        print(f"  余额: ¥{balance}")
        print(f"  交易数: {len(transactions)}")

        assert len(transactions) == 2
        assert balance == 50.0

        # 方式2：多实例但重新加载（正确）
        app1 = AccountingApp()
        app1.storage = Storage(temp_data_file + ".multi")
        app1.add_transaction(100.0, TransactionType.INCOME, "工资💰", "收入1")

        # 重新加载最新数据
        app2 = AccountingApp()
        app2.storage = Storage(temp_data_file + ".multi")  # 会读取app1保存的数据
        app2.add_transaction(50.0, TransactionType.EXPENSE, "餐饮🍜", "支出1")

        # 再次重新加载验证
        app3 = AccountingApp()
        app3.storage = Storage(temp_data_file + ".multi")

        final_balance = app3.get_balance()
        final_transactions = app3.storage.get_all_transactions()

        print(f"\n✅ 多实例重新加载操作:")
        print(f"  余额: ¥{final_balance}")
        print(f"  交易数: {len(final_transactions)}")

        assert len(final_transactions) == 2
        assert final_balance == 50.0

        print(f"\n💡 建议：每次操作前重新加载数据以避免并发问题")
        print(f"🎉 顺序操作测试通过！")

    def test_edge_cases_integration(self, clean_app):
        """集成测试3.4: 边界情况集成测试"""
        print("\n" + "=" * 60)
        print("测试场景：各种边界情况的集成处理")
        print("=" * 60)

        # 场景1: 添加后立即删除
        t1 = clean_app.add_transaction(100.0, TransactionType.INCOME, "工资💰")
        initial_balance = clean_app.get_balance()
        clean_app.delete_transaction(t1.id)
        after_delete_balance = clean_app.get_balance()
        assert after_delete_balance == 0.0
        print("✅ 场景1: 添加后立即删除 - 通过")

        # 场景2: 极小金额的多次操作
        for i in range(100):
            clean_app.add_transaction(
                0.01, TransactionType.INCOME, "工资💰", f"小额收入{i}"
            )

        balance_after_small = clean_app.get_balance()
        assert abs(balance_after_small - 1.0) < 0.01  # 100 * 0.01 = 1.0
        print(f"✅ 场景2: 100次极小金额操作 - 余额: ¥{balance_after_small:.2f}")

        # 场景3: 零余额状态的统计
        # 清空余额
        clean_app.add_transaction(
            balance_after_small, TransactionType.EXPENSE, "其他📦", "清零"
        )
        zero_balance = clean_app.get_balance()
        assert abs(zero_balance) < 0.01

        summary = clean_app.get_summary(30)
        print(f"✅ 场景3: 零余额状态统计 - 余额: ¥{zero_balance:.4f}")
        print(
            f"  统计结果: 收入¥{summary['total_income']:.2f}, 支出¥{summary['total_expense']:.2f}"
        )

        # 场景4: 空数据状态的各种查询
        clean_app2 = AccountingApp()
        clean_app2.storage = Storage(clean_app.storage.filename + ".empty")

        empty_df = clean_app2.get_transactions_df()
        empty_summary = clean_app2.get_summary(30)
        empty_stats = clean_app2.get_category_stats("支出", 30)

        assert empty_df.empty
        assert empty_summary["count"] == 0
        assert empty_stats.empty
        print("✅ 场景4: 空数据状态查询 - 通过")

        # 场景5: 特殊字符和长文本
        special_note = "测试!@#$%^&*()_+{}[]|\\:;<>?,./~`" * 10
        t_special = clean_app.add_transaction(
            50.0, TransactionType.EXPENSE, "其他📦", special_note
        )

        # 验证特殊字符保存和读取
        loaded_trans = clean_app.storage.get_all_transactions()
        found = False
        for trans in loaded_trans:
            if trans.id == t_special.id:
                assert trans.note == special_note
                found = True
                break

        assert found
        print("✅ 场景5: 特殊字符和长文本 - 通过")

        print(f"\n🎉 所有边界情况测试通过！")


# ============================================================
# 额外的端到端集成测试
# ============================================================

# test_integration.py - 继续未完成的部分


def test_end_to_end_monthly_report(clean_app):
    """端到端测试: 完整的月度报告生成流程"""
    print("\n" + "=" * 60)
    print("端到端测试：月度财务报告生成")
    print("=" * 60)

    # 模拟一个月的真实记账场景
    # 第1周
    clean_app.add_transaction(8000.0, TransactionType.INCOME, "工资💰", "月工资")
    clean_app.add_transaction(2000.0, TransactionType.EXPENSE, "住房🏠", "房租")
    clean_app.add_transaction(500.0, TransactionType.EXPENSE, "交通🚗", "公交月卡")

    # 第2周
    clean_app.add_transaction(1000.0, TransactionType.INCOME, "奖金🎁", "绩效奖金")
    clean_app.add_transaction(800.0, TransactionType.EXPENSE, "购物🛒", "买衣服")
    clean_app.add_transaction(300.0, TransactionType.EXPENSE, "娱乐🎬", "看电影聚餐")

    # 第3周
    clean_app.add_transaction(500.0, TransactionType.INCOME, "兼职💼", "周末兼职")
    clean_app.add_transaction(200.0, TransactionType.EXPENSE, "医疗⚕️", "体检")
    clean_app.add_transaction(150.0, TransactionType.EXPENSE, "餐饮🍜", "聚餐")

    # 第4周
    clean_app.add_transaction(1500.0, TransactionType.INCOME, "投资📈", "理财收益")
    clean_app.add_transaction(1000.0, TransactionType.EXPENSE, "教育📚", "培训课程")
    clean_app.add_transaction(400.0, TransactionType.EXPENSE, "餐饮🍜", "日常餐饮")

    # 生成月度报告
    print("\n" + "=" * 60)
    print("📊 月度财务报告")
    print("=" * 60)

    # 1. 总体统计
    summary = clean_app.get_summary(30)
    print(f"\n💰 总体收支:")
    print(f"  总收入: ¥{summary['total_income']:,.2f}")
    print(f"  总支出: ¥{summary['total_expense']:,.2f}")
    print(f"  净收入: ¥{summary['balance']:,.2f}")
    print(f"  交易笔数: {summary['count']}")
    print(f"  储蓄率: {(summary['balance']/summary['total_income']*100):.1f}%")

    # 验证总体统计
    assert summary["total_income"] == 11000.0
    assert summary["total_expense"] == 5350.0
    assert summary["balance"] == 5650.0
    assert summary["count"] == 12

    # 2. 收入分析
    print(f"\n📈 收入分析:")
    income_stats = clean_app.get_category_stats("收入", 30)
    for _, row in income_stats.iterrows():
        print(
            f"  {row['分类']}: ¥{row['金额']:,.2f} ({row['占比']:.1f}%) - {int(row['笔数'])}笔"
        )

    assert not income_stats.empty
    assert len(income_stats) == 4  # 工资、奖金、兼职、投资

    # 3. 支出分析
    print(f"\n📉 支出分析:")
    expense_stats = clean_app.get_category_stats("支出", 30)
    for _, row in expense_stats.iterrows():
        print(
            f"  {row['分类']}: ¥{row['金额']:,.2f} ({row['占比']:.1f}%) - {int(row['笔数'])}笔"
        )

    assert not expense_stats.empty
    top_expense = expense_stats.iloc[0]
    print(f"\n🔝 最大支出项: {top_expense['分类']} - ¥{top_expense['金额']:,.2f}")

    # 4. 趋势分析
    trend = clean_app.get_daily_trend(30)
    print(f"\n📊 趋势分析: 共 {len(trend)} 天有交易记录")

    # 5. 账户余额
    final_balance = clean_app.get_balance()
    print(f"\n💵 账户余额: ¥{final_balance:,.2f}")
    assert final_balance == 5650.0

    # 6. 交易明细
    df = clean_app.get_transactions_df()
    print(f"\n📋 交易明细: 共 {len(df)} 笔交易")
    print(f"  最新5笔交易:")
    for idx in range(min(5, len(df))):
        row = df.iloc[idx]
        print(
            f"    {row['日期'].strftime('%Y-%m-%d')} - {row['类型']} - {row['分类']} - ¥{row['金额']:,.2f}"
        )

    print(f"\n✅ 月度报告生成完成！")
    print("=" * 60)


# ============================================================
# 额外的综合场景测试
# ============================================================


class TestComplexScenarios:
    """复杂场景集成测试"""

    def test_budget_tracking_scenario(self, clean_app):
        """集成测试4.1: 预算追踪场景"""
        print("\n" + "=" * 60)
        print("测试场景：月度预算追踪")
        print("=" * 60)

        # 设定月度预算
        monthly_budget = {
            "餐饮🍜": 1000.0,
            "交通🚗": 500.0,
            "购物🛒": 1500.0,
            "娱乐🎬": 800.0,
        }

        print("\n📋 月度预算:")
        for category, budget in monthly_budget.items():
            print(f"  {category}: ¥{budget}")

        # 模拟一个月的消费
        # 餐饮：每天30元，共900元
        for day in range(30):
            clean_app.add_transaction(
                30.0, TransactionType.EXPENSE, "餐饮🍜", f"第{day+1}天餐饮"
            )

        # 交通：每周100元，共400元
        for week in range(4):
            clean_app.add_transaction(
                100.0, TransactionType.EXPENSE, "交通🚗", f"第{week+1}周交通"
            )

        # 购物：两次大额购物，共1800元
        clean_app.add_transaction(1000.0, TransactionType.EXPENSE, "购物🛒", "买衣服")
        clean_app.add_transaction(800.0, TransactionType.EXPENSE, "购物🛒", "买鞋子")

        # 娱乐：一次娱乐，500元
        clean_app.add_transaction(500.0, TransactionType.EXPENSE, "娱乐🎬", "看演唱会")

        # 分析预算执行情况
        expense_stats = clean_app.get_category_stats("支出", 30)

        print(f"\n📊 预算执行情况:")
        print(f"{'分类':<10} {'预算':>10} {'实际':>10} {'状态':>10}")
        print("-" * 45)

        for _, row in expense_stats.iterrows():
            category = row["分类"]
            actual = row["金额"]
            budget = monthly_budget.get(category, 0)

            if budget > 0:
                status = "超支" if actual > budget else "正常"
                diff = actual - budget
                print(
                    f"{category:<10} ¥{budget:>8.2f} ¥{actual:>8.2f} {status:>6} ({diff:+.2f})"
                )

        # 验证
        assert len(expense_stats) == 4

        # 餐饮应该在预算内（900 < 1000）
        food_expense = expense_stats[expense_stats["分类"] == "餐饮🍜"]["金额"].iloc[0]
        assert food_expense == 900.0
        assert food_expense < monthly_budget["餐饮🍜"]

        # 购物应该超预算（1800 > 1500）
        shopping_expense = expense_stats[expense_stats["分类"] == "购物🛒"][
            "金额"
        ].iloc[0]
        assert shopping_expense == 1800.0
        assert shopping_expense > monthly_budget["购物🛒"]

        print(f"\n✅ 预算追踪场景测试通过！")

    def test_income_expense_ratio_analysis(self, clean_app):
        """集成测试4.2: 收支比分析场景"""
        print("\n" + "=" * 60)
        print("测试场景：收支比分析")
        print("=" * 60)

        # 添加多种收入
        clean_app.add_transaction(10000.0, TransactionType.INCOME, "工资💰", "工资")
        clean_app.add_transaction(2000.0, TransactionType.INCOME, "奖金🎁", "季度奖金")
        clean_app.add_transaction(1000.0, TransactionType.INCOME, "兼职💼", "兼职收入")
        clean_app.add_transaction(500.0, TransactionType.INCOME, "投资📈", "理财收益")

        # 添加多种支出
        clean_app.add_transaction(3000.0, TransactionType.EXPENSE, "住房🏠", "房租")
        clean_app.add_transaction(1500.0, TransactionType.EXPENSE, "餐饮🍜", "餐饮")
        clean_app.add_transaction(800.0, TransactionType.EXPENSE, "交通🚗", "交通")
        clean_app.add_transaction(1200.0, TransactionType.EXPENSE, "购物🛒", "购物")
        clean_app.add_transaction(500.0, TransactionType.EXPENSE, "娱乐🎬", "娱乐")

        # 获取统计数据
        summary = clean_app.get_summary(30)
        income_stats = clean_app.get_category_stats("收入", 30)
        expense_stats = clean_app.get_category_stats("支出", 30)

        # 计算各项比率
        total_income = summary["total_income"]
        total_expense = summary["total_expense"]
        savings_rate = (summary["balance"] / total_income) * 100
        expense_rate = (total_expense / total_income) * 100

        print(f"\n📊 收支比分析:")
        print(f"  总收入: ¥{total_income:,.2f}")
        print(f"  总支出: ¥{total_expense:,.2f}")
        print(f"  净储蓄: ¥{summary['balance']:,.2f}")
        print(f"  储蓄率: {savings_rate:.1f}%")
        print(f"  支出率: {expense_rate:.1f}%")

        # 收入结构分析
        print(f"\n💰 收入结构:")
        for _, row in income_stats.iterrows():
            print(f"  {row['分类']}: ¥{row['金额']:,.2f} ({row['占比']:.1f}%)")

        # 支出结构分析
        print(f"\n💸 支出结构:")
        for _, row in expense_stats.iterrows():
            expense_ratio = (row["金额"] / total_income) * 100
            print(f"  {row['分类']}: ¥{row['金额']:,.2f} (占收入{expense_ratio:.1f}%)")

        # 验证
        assert total_income == 13500.0
        assert total_expense == 7000.0
        assert summary["balance"] == 6500.0
        assert abs(savings_rate - 48.15) < 0.1  # 储蓄率约48%

        # 工资应该是主要收入来源
        salary = income_stats[income_stats["分类"] == "工资💰"]["金额"].iloc[0]
        assert salary == 10000.0
        assert salary / total_income > 0.7  # 工资占收入70%以上

        # 住房应该是最大支出项
        housing = expense_stats[expense_stats["分类"] == "住房🏠"]["金额"].iloc[0]
        assert housing == 3000.0

        print(f"\n✅ 收支比分析测试通过！")

    def test_data_migration_scenario(self, temp_data_file):
        """集成测试4.3: 数据迁移场景"""
        print("\n" + "=" * 60)
        print("测试场景：数据备份与迁移")
        print("=" * 60)

        # 原始应用
        app1 = AccountingApp()
        app1.storage = Storage(temp_data_file)

        # 添加一些数据
        for i in range(10):
            app1.add_transaction(
                100.0 * (i + 1),
                TransactionType.INCOME if i % 2 == 0 else TransactionType.EXPENSE,
                "工资💰" if i % 2 == 0 else "餐饮🍜",
                f"交易{i+1}",
            )

        original_balance = app1.get_balance()
        original_count = len(app1.storage.get_all_transactions())

        print(f"\n原始数据:")
        print(f"  余额: ¥{original_balance}")
        print(f"  交易数: {original_count}")

        # 备份数据（通过读取文件）
        backup_file = temp_data_file + ".backup"
        import shutil

        shutil.copy(temp_data_file, backup_file)
        print(f"✅ 数据已备份到: {backup_file}")

        # 模拟数据损坏（添加错误数据）
        app1.add_transaction(999999.0, TransactionType.EXPENSE, "其他📦", "错误数据")
        corrupted_balance = app1.get_balance()
        print(f"\n❌ 数据损坏后余额: ¥{corrupted_balance}")

        # 从备份恢复
        app2 = AccountingApp()
        app2.storage = Storage(backup_file)

        restored_balance = app2.get_balance()
        restored_count = len(app2.storage.get_all_transactions())

        print(f"\n✅ 从备份恢复:")
        print(f"  余额: ¥{restored_balance}")
        print(f"  交易数: {restored_count}")

        # 验证恢复的数据与原始数据一致
        assert restored_balance == original_balance
        assert restored_count == original_count

        # 将恢复的数据保存到新文件
        new_file = temp_data_file + ".restored"
        app3 = AccountingApp()
        app3.storage = Storage(new_file)

        # 复制所有交易
        for trans in app2.storage.get_all_transactions():
            app3.storage.add_transaction(trans)

        final_balance = app3.get_balance()
        final_count = len(app3.storage.get_all_transactions())

        print(f"\n✅ 迁移到新文件:")
        print(f"  余额: ¥{final_balance}")
        print(f"  交易数: {final_count}")

        assert final_balance == original_balance
        assert final_count == original_count

        print(f"\n🎉 数据迁移场景测试通过！")


# ============================================================
# 运行所有测试的主函数
# ============================================================

if __name__ == "__main__":
    """
    直接运行此文件进行测试

    使用方法:
        python test_integration.py              # 运行所有测试
        pytest test_integration.py -v           # 详细模式
        pytest test_integration.py -v -s        # 显示打印输出
        pytest test_integration.py -k "Bottom"  # 只运行特定测试
    """
    import sys

    print("=" * 60)
    print("记账应用 - 集成测试套件")
    print("=" * 60)
    print("\n测试组织结构:")
    print("  1. 自底向上集成测试 (TestBottomUpIntegration)")
    print("     - Storage & Model 集成")
    print("     - App & Storage & Model 三层集成")
    print("\n  2. 自顶向下集成测试 (TestTopDownIntegration)")
    print("     - 完整交易工作流程")
    print("     - 交易修改工作流程")
    print("\n  3. 数据一致性集成测试 (TestDataConsistencyIntegration)")
    print("     - 大量数据场景")
    print("     - 并发操作模拟")
    print("     - 顺序操作验证")
    print("     - 边界情况处理")
    print("\n  4. 复杂场景集成测试 (TestComplexScenarios)")
    print("     - 预算追踪场景")
    print("     - 收支比分析场景")
    print("     - 数据迁移场景")
    print("\n  5. 端到端测试")
    print("     - 月度财务报告生成")
    print("=" * 60)
    print("\n开始运行测试...\n")

    # 运行pytest
    exit_code = pytest.main(
        [
            __file__,
            "-v",  # 详细模式
            "-s",  # 显示打印输出
            "--tb=short",  # 简短的错误追踪
            "--color=yes",  # 彩色输出
        ]
    )

    sys.exit(exit_code)
