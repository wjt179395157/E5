# storage.py - 数据存储
"""
数据持久化
"""
import json
import os
from typing import List
from models import Transaction, TransactionType


class Storage:
    """JSON文件存储"""
    
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.data = self._load()
    
    def _load(self):
        """加载数据"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'transactions': [], 'balance': 0.0}
    
    def _save(self):
        """保存数据"""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def add_transaction(self, transaction: Transaction):
        """添加交易"""
        self.data['transactions'].append(transaction.to_dict())
        
        if transaction.type == TransactionType.INCOME:
            self.data['balance'] += transaction.amount
        else:
            self.data['balance'] -= transaction.amount
        
        self._save()
    
    def get_all_transactions(self) -> List[Transaction]:
        """获取所有交易"""
        return [Transaction.from_dict(t) for t in self.data['transactions']]
    
    def get_balance(self) -> float:
        """获取余额"""
        return self.data['balance']
    
    def delete_transaction(self, transaction_id: str) -> bool:
        """删除交易"""
        for i, t in enumerate(self.data['transactions']):
            if t['id'] == transaction_id:
                trans = Transaction.from_dict(t)
                if trans.type == TransactionType.INCOME:
                    self.data['balance'] -= trans.amount
                else:
                    self.data['balance'] += trans.amount
                
                del self.data['transactions'][i]
                self._save()
                return True
        return False
