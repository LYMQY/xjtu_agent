from langchain.tools import tool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import DBTrip
from datetime import datetime, timedelta
from thread_local import get_current_username
import json

engine = create_engine("sqlite:///./users.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@tool
def save_trip(
    destination: str,
    days: int,
    budget: float,
    style: str = "comfortable",
    people: int = 1,
    start_date: str = None,
    itinerary: dict = None
) -> str:
    """
    保存旅行计划。
    
    参数:
        destination: 目的地
        days: 天数
        budget: 预算（元）
        style: 出行方式 (budget/comfortable/luxury)
        people: 人数
        start_date: 出发日期 YYYY-MM-DD
        itinerary: 行程详情（字典）
    
    返回:
        成功消息
    """
    user_id = get_current_username()
    if not user_id:
        return "错误：未获取到用户信息，请先登录"
    
    db = SessionLocal()
    try:
        end_date = None
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = (start + timedelta(days=days-1)).strftime("%Y-%m-%d")
        
        new_trip = DBTrip(
            user_id=user_id,
            destination=destination,
            days=days,
            people=people,
            budget=int(budget * 100),
            style=style,
            start_date=start_date,
            end_date=end_date,
            itinerary=json.dumps(itinerary) if itinerary else None,
            status="planning"
        )
        db.add(new_trip)
        db.commit()
        
        return f"成功保存 {destination} {days}日旅行计划，预算 ¥{budget}"
    finally:
        db.close()

@tool
def get_my_trips(status: str = None) -> str:
    """
    获取用户的旅行计划列表。
    
    参数:
        status: 状态筛选 (planning/upcoming/completed/cancelled)
    
    返回:
        JSON格式的旅行计划列表
    """
    user_id = get_current_username()
    if not user_id:
        return "错误：未获取到用户信息，请先登录"
    
    db = SessionLocal()
    try:
        query = db.query(DBTrip).filter(DBTrip.user_id == user_id)
        if status:
            query = query.filter(DBTrip.status == status)
        
        trips = query.order_by(DBTrip.created_at.desc()).all()
        
        result = [
            {
                "id": t.id,
                "destination": t.destination,
                "days": t.days,
                "start_date": t.start_date,
                "end_date": t.end_date,
                "status": t.status,
                "budget": t.budget / 100
            } for t in trips
        ]
        return f"查询到 {len(result)} 个旅行计划：{result}"
    finally:
        db.close()
