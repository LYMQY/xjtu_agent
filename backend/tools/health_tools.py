from langchain.tools import tool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import DBHealthCheckin
from datetime import datetime, timedelta
from thread_local import get_current_username

engine = create_engine("sqlite:///./users.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@tool
def health_checkin(
    date: str = None,
    sleep_time: str = None,
    wake_time: str = None,
    exercise: str = "none",
    steps: int = 0,
    health_status: str = "good",
    weight: float = None,
    remark: str = ""
) -> str:
    """
    健康打卡。
    
    参数:
        date: 日期，格式 YYYY-MM-DD，默认今天
        sleep_time: 入睡时间 HH:MM
        wake_time: 起床时间 HH:MM
        exercise: 运动状态 (none/light/medium/heavy)
        steps: 步数
        health_status: 健康状况 (excellent/good/minor/bad)
        weight: 体重(kg)
        remark: 备注
    
    返回:
        成功/更新消息
    """
    user_id = get_current_username()
    if not user_id:
        return "错误：未获取到用户信息，请先登录"
    
    db = SessionLocal()
    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # 计算睡眠时长
        sleep_duration = None
        if sleep_time and wake_time:
            try:
                s = datetime.strptime(sleep_time, "%H:%M")
                w = datetime.strptime(wake_time, "%H:%M")
                diff = (w - s).total_seconds() / 3600
                if diff < 0:
                    diff += 24
                sleep_duration = round(diff, 1)
            except:
                pass
        
        # 检查是否已存在
        existing = db.query(DBHealthCheckin).filter(
            DBHealthCheckin.user_id == user_id,
            DBHealthCheckin.date == date
        ).first()
        
        if existing:
            existing.sleep_time = sleep_time
            existing.wake_time = wake_time
            existing.sleep_duration = sleep_duration
            existing.exercise = exercise
            existing.steps = steps
            existing.health_status = health_status
            existing.weight = weight
            existing.remark = remark
            msg = f"更新了 {date} 的健康打卡"
        else:
            new_checkin = DBHealthCheckin(
                user_id=user_id,
                date=date,
                sleep_time=sleep_time,
                wake_time=wake_time,
                sleep_duration=sleep_duration,
                exercise=exercise,
                steps=steps,
                health_status=health_status,
                weight=weight,
                remark=remark
            )
            db.add(new_checkin)
            msg = f"成功完成 {date} 健康打卡"
        
        db.commit()
        return msg
    finally:
        db.close()

@tool
def get_health_records(days: int = 30) -> str:
    """
    获取健康打卡记录。
    
    参数:
        days: 查询天数，默认30
    
    返回:
        JSON格式的记录列表
    """
    user_id = get_current_username()
    if not user_id:
        return "错误：未获取到用户信息，请先登录"
    
    db = SessionLocal()
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        records = db.query(DBHealthCheckin).filter(
            DBHealthCheckin.user_id == user_id,
            DBHealthCheckin.date >= start_date,
            DBHealthCheckin.date <= end_date
        ).order_by(DBHealthCheckin.date.desc()).all()
        
        result = [
            {
                "date": r.date,
                "sleep_duration": r.sleep_duration,
                "exercise": r.exercise,
                "steps": r.steps,
                "health_status": r.health_status
            } for r in records
        ]
        return f"查询到 {len(result)} 条健康记录：{result}"
    finally:
        db.close()

@tool
def get_health_stats(days: int = 30) -> str:
    """
    获取健康统计数据。
    
    参数:
        days: 统计天数，默认30
    
    返回:
        JSON格式的统计数据
    """
    user_id = get_current_username()
    if not user_id:
        return "错误：未获取到用户信息，请先登录"
    
    db = SessionLocal()
    try:
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        records = db.query(DBHealthCheckin).filter(
            DBHealthCheckin.user_id == user_id,
            DBHealthCheckin.date >= start_date,
            DBHealthCheckin.date <= end_date
        ).all()
        
        if not records:
            return f"暂无 {days} 天内的健康数据"
        
        total_days = len(records)
        avg_sleep = sum(r.sleep_duration for r in records if r.sleep_duration) / total_days if total_days else 0
        avg_steps = sum(r.steps for r in records) / total_days if total_days else 0
        exercise_days = sum(1 for r in records if r.exercise and r.exercise != "none")
        
        status_counts = {}
        for r in records:
            if r.health_status:
                status_counts[r.health_status] = status_counts.get(r.health_status, 0) + 1
        
        best_status = max(status_counts, key=status_counts.get) if status_counts else "unknown"
        
        result = {
            "period": f"{start_date} 至 {end_date}",
            "total_records": total_days,
            "avg_sleep_hours": round(avg_sleep, 1),
            "avg_steps": int(avg_steps),
            "exercise_days": exercise_days,
            "exercise_rate": f"{round(exercise_days / total_days * 100, 1)}%" if total_days else "0%",
            "main_health_status": best_status,
            "status_breakdown": status_counts
        }
        
        return f"健康统计 ({days}天)：平均睡眠 {result['avg_sleep_hours']} 小时，日均步数 {result['avg_steps']} 步，运动 {result['exercise_days']} 天({result['exercise_rate']})，主要健康状况: {result['main_health_status']}"
    finally:
        db.close()
