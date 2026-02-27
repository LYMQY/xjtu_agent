from langchain.tools import tool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import DBExpense, DBBudget
from datetime import datetime
from thread_local import get_current_username

# 数据库连接
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ========== Tool 1: 查询消费记录 ==========
@tool
def get_expenses(
    start_date: str = None,
    end_date: str = None,
    category: str = None,
    page: int = 1,
    page_size: int = 20
) -> str:
    """
    查询用户的消费记录。
    
    参数:
        start_date: 开始日期，格式 YYYY-MM-DD
        end_date: 结束日期，格式 YYYY-MM-DD
        category: 消费分类 (food/transport/shopping/entertainment/study/living/other)
        page: 页码，默认1
        page_size: 每页数量，默认20
    
    返回:
        JSON格式的消费记录列表
    """
    user_id = get_current_username()
    if not user_id:
        return "错误：未获取到用户信息，请先登录"
    
    db = SessionLocal()
    try:
        query = db.query(DBExpense).filter(DBExpense.user_id == user_id)
        
        if start_date:
            query = query.filter(DBExpense.date >= start_date)
        if end_date:
            query = query.filter(DBExpense.date <= end_date)
        if category:
            query = query.filter(DBExpense.category == category)
        
        offset = (page - 1) * page_size
        expenses = query.order_by(DBExpense.date.desc()).offset(offset).limit(page_size).all()
        
        result = [
            {
                "id": e.id,
                "date": e.date,
                "amount": e.amount / 100,  # 分转元
                "category": e.category,
                "description": e.description
            } for e in expenses
        ]
        return f"查询到 {len(result)} 条消费记录：{result}"
    finally:
        db.close()

# ========== Tool 2: 获取预算统计 ==========
@tool
def get_budget_stats(user_id: str, month: str = None) -> str:
    """
    获取月度预算统计。
    
    参数:
        user_id: 用户ID（学号）
        month: 月份，格式 YYYY-MM，默认当前月
    
    返回:
        JSON格式的统计数据
    """
    db = SessionLocal()
    try:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        # 获取预算
        budget = db.query(DBBudget).filter(
            DBBudget.user_id == user_id,
            DBBudget.month == month
        ).first()
        total_budget = budget.total_budget / 100 if budget else 1500
        
        # 获取消费
        start_date = f"{month}-01"
        expenses = db.query(DBExpense).filter(
            DBExpense.user_id == user_id,
            DBExpense.date >= start_date
        ).all()
        
        total_spent = sum(e.amount for e in expenses) / 100
        
        # 分类统计
        category_breakdown = {}
        for e in expenses:
            cat = e.category
            category_breakdown[cat] = category_breakdown.get(cat, 0) + e.amount / 100
        
        result = {
            "month": month,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": total_budget - total_spent,
            "percentage": round(total_spent / total_budget * 100, 1) if total_budget > 0 else 0,
            "category_breakdown": category_breakdown
        }
        return f"本月预算统计：{result}"
    finally:
        db.close()

# ========== Tool 3: 添加消费记录 ==========
@tool
def add_expense(
    user_id: str,
    amount: float,
    category: str,
    date: str = None,
    description: str = ""
) -> str:
    """
    添加消费记录。
    
    参数:
        user_id: 用户ID（学号）
        amount: 金额（元）
        category: 消费分类
        date: 日期，格式 YYYY-MM-DD，默认今天
        description: 描述
    
    返回:
        成功消息
    """
    db = SessionLocal()
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        new_expense = DBExpense(
            user_id=user_id,
            amount=int(amount * 100),  # 元转分
            category=category,
            description=description,
            date=date
        )
        db.add(new_expense)
        db.commit()
        return f"成功添加消费记录：{description or category}，金额 ¥{amount}"
    finally:
        db.close()

# ========== Tool 4: 设置预算 ==========
@tool
def set_budget(user_id: str, amount: float, month: str = None) -> str:
    """
    设置月度预算。
    
    参数:
        user_id: 用户ID（学号）
        amount: 预算金额（元）
        month: 月份，格式 YYYY-MM，默认当前月
    
    返回:
        成功消息
    """
    db = SessionLocal()
    try:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        
        existing = db.query(DBBudget).filter(
            DBBudget.user_id == user_id,
            DBBudget.month == month
        ).first()
        
        if existing:
            existing.total_budget = int(amount * 100)
        else:
            new_budget = DBBudget(
                user_id=user_id,
                total_budget=int(amount * 100),
                month=month
            )
            db.add(new_budget)
        
        db.commit()
        return f"成功设置 {month} 月预算：¥{amount}"
    finally:
        db.close()
