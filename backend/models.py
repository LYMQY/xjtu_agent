# models.py
from sqlalchemy import Column, String, Boolean, Text, Integer, DateTime, Float
import uuid
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# ---------- 数据库模型（用户表） ----------
class DBUser(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)  # 学号
    email = Column(String, unique=True, index=True)
    encrypted_password = Column(String)  # 改为可逆加密的密码
    is_active = Column(Boolean, default=True)

class DBSchedule(Base):
    __tablename__ = "schedules"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)  # 关联到用户
    name = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    color = Column(String, default="#2097f3")
    remark = Column(Text, nullable=True)
    calendar_id = Column(Integer, default=1)  # 日历分类ID
    reminder_sent = Column(Boolean, default=False) # 是否已发送提醒

# ---------- 预算管理模型 ----------
class DBExpense(Base):
    __tablename__ = "expenses"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)  # 关联用户
    amount = Column(Integer, nullable=False)  # 金额（分）
    category = Column(String, nullable=False)  # 分类
    description = Column(String, nullable=True)  # 描述
    date = Column(String, nullable=False)  # 日期 YYYY-MM-DD
    created_at = Column(DateTime, default=datetime.utcnow)

class DBBudget(Base):
    __tablename__ = "budgets"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)  # 关联用户
    total_budget = Column(Integer, default=150000)  # 月预算（分）
    month = Column(String, nullable=False)  # 月份 YYYY-MM
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ---------- 健康打卡模型 ----------
class DBHealthCheckin(Base):
    __tablename__ = "health_checkins"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)  # 关联用户
    date = Column(String, nullable=False)  # 日期 YYYY-MM-DD（每天一条）
    
    # 睡眠数据
    sleep_time = Column(String, nullable=True)  # 入睡时间 HH:MM
    wake_time = Column(String, nullable=True)  # 起床时间 HH:MM
    sleep_duration = Column(Float, nullable=True)  # 睡眠时长（小时）
    
    # 运动数据
    exercise = Column(String, default="none")  # 运动状态: none/light/medium/heavy
    steps = Column(Integer, default=0)  # 步数
    
    # 健康数据
    health_status = Column(String, default="good")  # 健康状况: excellent/good/minor/bad
    weight = Column(Float, nullable=True)  # 体重（kg）
    
    # 其他
    remark = Column(Text, nullable=True)  # 备注
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ---------- 旅游规划模型 ----------
class DBTrip(Base):
    __tablename__ = "trips"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, index=True, nullable=False)  # 关联用户
    destination = Column(String, nullable=False)  # 目的地
    days = Column(Integer, nullable=False)  # 天数
    people = Column(Integer, default=1)  # 人数
    budget = Column(Integer, nullable=False)  # 预算（分）
    style = Column(String, default="comfortable")  # 出行方式
    start_date = Column(String, nullable=True)  # 出发日期
    end_date = Column(String, nullable=True)  # 结束日期
    status = Column(String, default="planning")  # planning/upcoming/completed/cancelled
    itinerary = Column(Text, nullable=True)  # JSON 行程详情
    cover_image = Column(String, nullable=True)  # 封面图路径
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
