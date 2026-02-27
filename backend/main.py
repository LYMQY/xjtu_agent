# -*- coding: utf-8 -*-
"""
FastAPI 交小荣智能教务后端
"""

from models import DBUser, Base, DBSchedule, DBExpense, DBBudget, DBHealthCheckin, DBTrip
from sqlalchemy import DateTime, create_engine, Column, String, Boolean, Text, Integer, Float, func
from sqlalchemy.orm import sessionmaker, Session
from config import config
from crypto_utils import crypto 
import os
from datetime import datetime, timedelta
import uuid
import logging
from scheduler import start_scheduler

current_user_context = {}
# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库初始化单例
class DatabaseInitializer:
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if not cls._initialized:
            # 创建所有表
            Base.metadata.create_all(bind=engine)
            # 插入初始用户（直接使用 DBUser 模型）
            cls._insert_default_user()
            
            cls._initialized = True
    
    @classmethod
    def _insert_default_user(cls):
        db = UserSessionLocal()
        try:
            if not db.query(DBUser).first():
                # 直接创建 DBUser 实例，绕过 UserCreate
                default_user = DBUser(
                    username="2021000000",
                    email="default@example.com",
                    # 使用 crypto 工具加密密码
                    encrypted_password=crypto.encrypt("default_password")
                )
                db.add(default_user)
                db.commit()
            if not db.query(DBSchedule).first():
                # 创建默认日程
                default_schedule = DBSchedule(
                    id=str(uuid.uuid4()),  # 使用 UUID 生成唯一 ID
                    user_id="2021000000",
                    name="默认日程",
                    start_time=datetime.fromisoformat("2023-10-01T08:00:00Z"),
                    end_time=datetime.fromisoformat("2023-10-01T09:00:00Z"),
                    color="#2097f3",
                    remark="这是一个默认日程"
                )
                db.add(default_schedule)
                db.commit()
        finally:
            db.close()

# 立即初始化数据库（在任何导入前）
DatabaseInitializer.initialize()

import json
import time
import uuid
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import FastAPI, HTTPException, Query, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator, Field
import redis
from passlib.context import CryptContext
from agents.demo_rag import EhallAgent  
from thread_local import set_current_username, get_current_username


# ---------- 数据库配置（用户表） ----------
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"  # 数据库文件存在本地的backend目录
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------- JWT和密码加密配置 ----------
SECRET_KEY = config.get_secret_key() or "your-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ---------- Pydantic模型（接口入参/出参） ----------
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator('username')
    def username_must_be_digits(cls, v):
        if not v.isdigit():
            raise ValueError('学号必须为数字')
        return v

# ---------- 新增日程相关Pydantic模型 ----------
class ScheduleCreate(BaseModel):
    name: str
    start_time: str  # ISO格式字符串
    end_time: str    # ISO格式字符串
    color: Optional[str] = "#2097f3"
    remark: Optional[str] = ""
    
    @field_validator('start_time', 'end_time')
    def validate_datetime(cls, v):
        try:
            # 尝试解析ISO格式
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError('日期时间格式错误，应为ISO 8601格式（如YYYY-MM-DDTHH:mm:ss）')


class ScheduleResponse(BaseModel):
    id: str
    name: str
    start_time: str
    end_time: str
    color: str
    remark: Optional[str]
    schedule_calendar: dict

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------- 预算管理 Pydantic 模型 ----------
class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="金额")
    category: str = Field(..., description="分类: food/transport/shopping/entertainment/study/living/other")
    description: Optional[str] = Field(None, description="描述")
    date: str = Field(..., description="日期 YYYY-MM-DD")

class ExpenseResponse(BaseModel):
    id: str
    amount: float
    category: str
    description: Optional[str]
    date: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class BudgetSet(BaseModel):
    total_budget: float = Field(..., gt=0, description="月预算金额")
    month: str = Field(..., description="月份 YYYY-MM")

class BudgetStats(BaseModel):
    total_budget: float
    total_spent: float
    remaining: float
    percentage: float
    category_breakdown: dict

# 消费分类映射
EXPENSE_CATEGORIES = {
    "food": "餐饮",
    "transport": "交通",
    "shopping": "购物",
    "entertainment": "娱乐",
    "study": "学习",
    "living": "住宿",
    "other": "其他"
}

# ---------- 健康打卡 Pydantic 模型 ----------
class HealthCheckinCreate(BaseModel):
    date: str = Field(..., description="日期 YYYY-MM-DD")
    sleep_time: Optional[str] = Field(None, description="入睡时间 HH:MM")
    wake_time: Optional[str] = Field(None, description="起床时间 HH:MM")
    exercise: str = Field("none", description="运动状态: none/light/medium/heavy")
    steps: int = Field(0, ge=0, description="步数")
    health_status: str = Field("good", description="健康状况: excellent/good/minor/bad")
    weight: Optional[float] = Field(None, gt=0, description="体重 kg")
    remark: Optional[str] = Field(None, description="备注")

class HealthStats(BaseModel):
    total_checkins: int
    consecutive_days: int
    avg_sleep: float
    avg_steps: float
    exercise_rate: float
    health_score: int

# 健康分类映射
HEALTH_STATUS_MAP = {
    "excellent": "非常健康",
    "good": "健康",
    "minor": "轻微不适",
    "bad": "身体不适"
}

EXERCISE_MAP = {
    "none": "未运动",
    "light": "轻度运动",
    "medium": "中度运动",
    "heavy": "剧烈运动"
}

# ---------- 旅游规划 Pydantic 模型 ----------
class TripCreate(BaseModel):
    destination: str = Field(..., description="目的地")
    days: int = Field(..., ge=1, le=30, description="天数")
    people: int = Field(1, ge=1, le=20, description="人数")
    budget: float = Field(..., gt=0, description="预算（元）")
    style: str = Field("comfortable", description="出行方式")
    start_date: Optional[str] = Field(None, description="出发日期 YYYY-MM-DD")
    itinerary: Optional[List[Dict]] = Field(None, description="行程详情")

class TripGenerateRequest(BaseModel):
    destination: str
    days: int = Field(..., ge=1, le=30)
    budget: float
    style: str = "comfortable"
    people: int = 1

# ---------- 工具函数（密码、Token、数据库操作） ----------
def get_user_db():
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

def get_db_user(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()

def get_db_email(db: Session, email: str):
    return db.query(DBUser).filter(DBUser.email == email).first()

def create_db_user(db: Session, user: UserCreate):
    db_user = DBUser(
        username=user.username,
        email=user.email,
        encrypted_password=crypto.encrypt(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_db_user(db, username)
    decrypted_password = crypto.decrypt(user.encrypted_password)
    if password != decrypted_password:
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_user_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_db_user(db, username)
    if user is None:
        raise credentials_exception
    return user



# 配置日志系统（保持不变）
os.makedirs(config.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=config.get_log_level(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.get_log_file_path(), encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# 应用配置（保持不变）
app = FastAPI(
    title=config.APP_NAME,
    description="基于FastAPI、LangChain和DeepSeek的智能教务系统",
    version=config.APP_VERSION
)
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# Redis连接配置（保持不变）
try:
    redis_client = redis.Redis(**config.get_redis_config())
    redis_client.ping()
    logger.info(f"Redis连接成功 - 主机: {config.REDIS_HOST}:{config.REDIS_PORT}")
    REDIS_AVAILABLE = True
except Exception as e:
    logger.error(f"Redis连接失败: {e}")
    logger.warning("应用将在没有Redis的情况下运行，会话数据将不会持久化")
    redis_client = None
    REDIS_AVAILABLE = False

# 初始化LangChain的DeepSeek模型
try:
    # 初始化LangChain的DeepSeek聊天模型
    kb_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend/data", "通识选课2.csv")
    ehall_agent = EhallAgent(verbose=False, knowledge_base_path=kb_path)
    logger.info("LangChain DeepSeek模型初始化成功")
except Exception as e:
    logger.error(f"LangChain初始化失败: {e}")
    raise

# 数据模型、AI角色配置、工具函数
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: float

class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    session_id: str
    message: str
    timestamp: float

MAX_HISTORY_MESSAGES = config.MAX_HISTORY_MESSAGES
MAX_MESSAGE_LENGTH = config.MAX_MESSAGE_LENGTH
CONVERSATION_EXPIRE_TIME = config.CONVERSATION_EXPIRE_TIME
SESSION_EXPIRE_TIME = config.SESSION_EXPIRE_TIME

MEMORY_STORAGE = {
    "conversations": {},
    "sessions": {}
}

def generate_session_id() -> str:
    session_id = str(uuid.uuid4())
    logger.info(f"生成新会话ID: {session_id}")
    return session_id

def get_conversation_key(user_id: str, session_id: str) -> str:
    return f"conversation:{user_id}:{session_id}"

def get_user_sessions_key(user_id: str) -> str:
    return f"user_sessions:{user_id}"

async def save_message_to_redis(user_id: str, session_id: str, message: ChatMessage):
    """将消息保存到Redis或内存"""
    try:
        message_data = {
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp
        }
        
        if REDIS_AVAILABLE and redis_client:
            # 使用Redis存储
            conversation_key = get_conversation_key(user_id, session_id)
            
            # 将消息添加到对话历史
            redis_client.lpush(conversation_key, json.dumps(message_data))
            
            # 设置过期时间
            redis_client.expire(conversation_key, config.CONVERSATION_EXPIRE_TIME)
            
            # 更新用户会话列表
            sessions_key = get_user_sessions_key(user_id)
            session_info = {
                "session_id": session_id,
                "last_message": message.content[:config.MAX_MESSAGE_LENGTH] + "..." if len(message.content) > config.MAX_MESSAGE_LENGTH else message.content,
                "last_timestamp": message.timestamp
            }
            redis_client.hset(sessions_key, session_id, json.dumps(session_info))
            redis_client.expire(sessions_key, config.SESSION_EXPIRE_TIME)
            
            logger.info(f"消息已保存到Redis - 用户: {user_id}, 会话: {session_id[:8]}..., 角色: {message.role}, 内容长度: {len(message.content)}")
        else:
            # 使用内存存储
            if user_id not in MEMORY_STORAGE["conversations"]:
                MEMORY_STORAGE["conversations"][user_id] = {}
            if session_id not in MEMORY_STORAGE["conversations"][user_id]:
                MEMORY_STORAGE["conversations"][user_id][session_id] = []
            
            MEMORY_STORAGE["conversations"][user_id][session_id].append(message_data)
            
            # 更新会话信息
            if user_id not in MEMORY_STORAGE["sessions"]:
                MEMORY_STORAGE["sessions"][user_id] = {}
            
            MEMORY_STORAGE["sessions"][user_id][session_id] = {
                "session_id": session_id,
                "last_message": message.content[:config.MAX_MESSAGE_LENGTH] + "..." if len(message.content) > config.MAX_MESSAGE_LENGTH else message.content,
                "last_timestamp": message.timestamp
            }
            
            logger.info(f"消息已保存到内存 - 用户: {user_id}, 会话: {session_id[:8]}..., 角色: {message.role}, 内容长度: {len(message.content)}")
            
    except Exception as e:
        logger.error(f"保存消息失败 - 用户: {user_id}, 会话: {session_id[:8]}..., 错误: {e}")
        raise

async def get_conversation_history(user_id: str, session_id: str) -> List[Dict[str, Any]]:
    """从Redis或内存获取对话历史"""
    try:
        if REDIS_AVAILABLE and redis_client:
            # 从Redis获取
            conversation_key = get_conversation_key(user_id, session_id)
            messages = redis_client.lrange(conversation_key, 0, -1)
            
            # 反转消息顺序（Redis中是倒序存储的）
            messages.reverse()
            
            history = [json.loads(msg) for msg in messages]
            logger.info(f"从Redis获取对话历史 - 用户: {user_id}, 会话: {session_id[:8]}..., 消息数量: {len(history)}")
            return history
        else:
            # 从内存获取
            if (user_id in MEMORY_STORAGE["conversations"] and 
                session_id in MEMORY_STORAGE["conversations"][user_id]):
                history = MEMORY_STORAGE["conversations"][user_id][session_id]
                logger.info(f"从内存获取对话历史 - 用户: {user_id}, 会话: {session_id[:8]}..., 消息数量: {len(history)}")
                return history
            else:
                logger.info(f"对话历史为空 - 用户: {user_id}, 会话: {session_id[:8]}...")
                return []
    except Exception as e:
        logger.error(f"获取对话历史失败 - 用户: {user_id}, 会话: {session_id[:8]}..., 错误: {e}")
        return []

async def generate_ai_response(messages: List[Dict[str, Any]]) -> str:
    """调用EhallAgent生成响应"""
    try:
        logger.info(f"生成AI响应 - 消息数量: {len(messages)}")
        
        # 转换历史消息为EhallAgent需要的格式: 列表 of (role, content) 元组
        chat_history = []
        for msg in messages[-MAX_HISTORY_MESSAGES:]:
            if msg["role"] == "user":
                chat_history.append(("human", msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(("ai", msg["content"]))
        
        # 提取最新用户消息
        user_message = messages[-1]["content"] if messages and messages[-1]["role"] == "user" else "请回答"
        
        # 调用EhallAgent（同步方法，无需await）
        start_time = time.time()
        response = ehall_agent.run(
            user_input=user_message,
            chat_history=chat_history
        )
        latency = time.time() - start_time
        logger.info(f"AI响应生成成功 - 耗时: {latency:.2f}s, 长度: {len(response)}")
        return response
        
    except Exception as e:
        logger.error(f"生成AI响应失败: {e}")
        return "抱歉，处理请求时出现错误，请稍后再试。"
    
async def generate_streaming_response(user_id: str, session_id: str, user_message: str, role: str = "assistant", provider: Optional[str] = None, model: Optional[str] = None):
    """生成流式响应"""


try:
    scheduler = start_scheduler()
    logger.info("日程提醒功能已启用")
except Exception as e:
    logger.error(f"启动日程提醒调度器失败：{e}")

# ---------- 新增接口（注册、登录） ----------
@app.post("/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_user_db)):
    db_user = get_db_user(db, user.username)
    db_emali = get_db_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "username", "msg": "学号已被注册"}
        )
    
    if db_emali:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": "email", "msg": "邮箱已被注册"}  # 返回错误字段和信息
        )
    
    create_db_user(db, user)
    return {"message": "注册成功，请登录"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_user_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# API接口（保持不变，与前端交互逻辑不受影响）
@app.get("/")
async def root():
    logger.info("访问根路径，重定向到聊天界面")
    return RedirectResponse(url="/static/index.html")

@app.get("/api")
async def api_info():
    return {"message": "FastAPI LangChain DeepSeek聊天应用演示", "version": "1.0.0"}

@app.post("/chat/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_id = request.user_id.strip()
    session_id = request.session_id or generate_session_id()
    user_message = request.message.strip()
    
    set_current_username(user_id)

    # 可选：添加 user_id 格式校验（如是否为数字）
    if not user_id.isdigit():
        raise HTTPException(status_code=400, detail="用户ID必须为数字")
    
    if not user_message:
        raise HTTPException(status_code=400, detail="消息内容不能为空")
    
    logger.info(f"用户 {user_id} 发起聊天 - 会话: {session_id[:8]}..., 消息: {user_message[:50]}...")
    
    # 保存用户消息
    user_msg = ChatMessage(role="user", content=user_message, timestamp=time.time())
    await save_message_to_redis(user_id, session_id, user_msg)
    
    # 获取对话历史
    history = await get_conversation_history(user_id, session_id)
    
    # 生成AI响应
    ai_response = await generate_ai_response(history)
    
    # 保存AI响应
    ai_msg = ChatMessage(role="assistant", content=ai_response, timestamp=time.time())
    await save_message_to_redis(user_id, session_id, ai_msg)
    set_current_username(None)
    return ChatResponse(
        session_id=session_id,
        message=ai_response,
        timestamp=ai_msg.timestamp
    )

# ---------- 新增日程相关工具函数 ----------
def schedule_to_dict(schedule: DBSchedule) -> dict:
    """将数据库日程对象转换为前端需要的字典格式"""
    return {
        "id": schedule.id,
        "name": schedule.name,
        "start_time": schedule.start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end_time": schedule.end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "color": schedule.color,
        "remark": schedule.remark,
        "schedule_calendar": {
            "color": schedule.color,
            "name": "默认日历"
        }
    }


def get_schedule_by_id(db: Session, schedule_id: str, user_id: str):
    """获取指定用户的指定日程"""
    return db.query(DBSchedule).filter(
        DBSchedule.id == schedule_id,
        DBSchedule.user_id == user_id
    ).first()


def create_schedule(db: Session, schedule: ScheduleCreate, user_id: str):
    """创建新日程"""
    try:
        start_time = datetime.fromisoformat(schedule.start_time.replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(schedule.end_time.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="日期时间格式错误")
    
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")
    
    db_schedule = DBSchedule(
        user_id=user_id,
        name=schedule.name,
        start_time=start_time,
        end_time=end_time,
        color=schedule.color,
        remark=schedule.remark
    )
    
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# ---------- 新增日历API接口 ----------
@app.get("/api/schedules/", response_model=List[dict])
def get_schedules(
    start: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户的日程列表（支持日期范围筛选）"""
    query = db.query(DBSchedule).filter(DBSchedule.user_id == current_user.username)
    
    # 日期筛选
    if start and end:
        try:
            # 将输入的日期字符串转换为datetime对象，时间部分设为00:00:00
            start_date = datetime.strptime(start, "%Y-%m-%d")
            # 结束日期设为当天的23:59:59，覆盖一整天
            end_date = datetime.strptime(end, "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)
            
            # 查询条件：日程的结束时间晚于开始日期，且日程的开始时间早于结束日期
            query = query.filter(
                DBSchedule.end_time >= start_date,
                DBSchedule.start_time <= end_date
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，应为YYYY-MM-DD")

    return [schedule_to_dict(s) for s in query.all()]

@app.post("/api/schedules/", response_model=dict)
def create_schedule_api(
    schedule: ScheduleCreate,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """创建新日程（仅当前用户可见）"""
    try:
        # 验证时间逻辑
        start_time = datetime.fromisoformat(schedule.start_time.replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(schedule.end_time.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="日期时间格式错误，应为ISO 8601格式")
    
    if start_time >= end_time:
        raise HTTPException(status_code=400, detail="开始时间必须早于结束时间")
    
    # 创建日程，关联当前用户
    new_schedule = create_schedule(db, schedule, current_user.username)
    return schedule_to_dict(new_schedule)


@app.delete("/api/schedules/{schedule_id}", response_model=dict)
def delete_schedule(
    schedule_id: str,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """删除当前用户的日程"""
    schedule = get_schedule_by_id(db, schedule_id, current_user.username)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="日程不存在或无权访问")
    
    db.delete(schedule)
    db.commit()
    return {"message": "日程已成功删除", "id": schedule_id}


@app.get("/api/schedules/search/", response_model=List[dict])
def search_schedules(
    keyword: str = Query(..., description="搜索关键词"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """搜索当前用户的日程（按标题或描述）"""
    schedules = db.query(DBSchedule).filter(
        DBSchedule.user_id == current_user.username,
        (DBSchedule.name.contains(keyword)) | 
        (DBSchedule.remark.contains(keyword))
    ).all()
    logger.info("f{schedules} schedules found for keyword '{keyword}'")
    
    return [schedule_to_dict(s) for s in schedules]

@app.get("/api/schedules/last-updated/", response_model=dict)
def get_last_schedule_update(
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户最后更新的日程时间戳"""
    # 查询当前用户所有日程中最新的更新时间
    last_updated = db.query(
        func.max(func.julianday(DBSchedule.end_time)).label('max_time')
    ).filter(DBSchedule.user_id == current_user.username).scalar()
    
    # 如果没有日程，返回当前时间戳
    if not last_updated:
        timestamp = datetime.now().timestamp()
    else:
        # 将Julian日期转换为Unix时间戳
        # SQLite的julianday从公元前4714年11月24日开始，需要转换偏移量
        timestamp = (last_updated - 2440587.5) * 86400
    
    return {
        "timestamp": str(int(timestamp)),  # 转为整数时间戳字符串
        "user_id": current_user.username
    }

# ==================== 预算管理 API ====================

@app.get("/api/expenses/", response_model=list)
def get_expenses(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    category: Optional[str] = Query(None, description="分类筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户的消费记录"""
    query = db.query(DBExpense).filter(DBExpense.user_id == current_user.username)
    
    # 日期筛选
    if start_date:
        query = query.filter(DBExpense.date >= start_date)
    if end_date:
        query = query.filter(DBExpense.date <= end_date)
    # 分类筛选
    if category:
        query = query.filter(DBExpense.category == category)
    
    # 分页
    offset = (page - 1) * page_size
    expenses = query.order_by(DBExpense.date.desc()).offset(offset).limit(page_size).all()
    
    return [
        {
            "id": e.id,
            "amount": e.amount / 100,  # 转换为元
            "category": e.category,
            "category_name": EXPENSE_CATEGORIES.get(e.category, e.category),
            "description": e.description,
            "date": e.date,
            "created_at": e.created_at.isoformat() if e.created_at else None
        } for e in expenses
    ]

@app.post("/api/expenses/", response_model=dict)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """添加新的消费记录"""
    # 金额转为分存储
    new_expense = DBExpense(
        user_id=current_user.username,
        amount=int(expense.amount * 100),
        category=expense.category,
        description=expense.description,
        date=expense.date
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return {
        "id": new_expense.id,
        "amount": new_expense.amount / 100,
        "category": new_expense.category,
        "description": new_expense.description,
        "date": new_expense.date,
        "message": "添加成功"
    }

@app.delete("/api/expenses/{expense_id}", response_model=dict)
def delete_expense(
    expense_id: str,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """删除消费记录"""
    expense = db.query(DBExpense).filter(
        DBExpense.id == expense_id,
        DBExpense.user_id == current_user.username
    ).first()
    
    if not expense:
        raise HTTPException(status_code=404, detail="记录不存在或无权访问")
    
    db.delete(expense)
    db.commit()
    return {"message": "删除成功", "id": expense_id}

@app.get("/api/expenses/stats/", response_model=BudgetStats)
def get_expense_stats(
    month: Optional[str] = Query(None, description="月份 YYYY-MM，默认当月"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取消费统计"""
    if not month:
        month = datetime.now().strftime("%Y-%m")
    
    # 获取当月预算
    budget = db.query(DBBudget).filter(
        DBBudget.user_id == current_user.username,
        DBBudget.month == month
    ).first()
    
    total_budget = budget.total_budget / 100 if budget else 1500
    start_date = f"{month}-01"
    end_date = f"{month}-31"
    
    # 获取当月消费
    expenses = db.query(DBExpense).filter(
        DBExpense.user_id == current_user.username,
        DBExpense.date >= start_date,
        DBExpense.date <= end_date
    ).all()
    
    total_spent = sum(e.amount for e in expenses) / 100
    
    # 分类统计
    category_breakdown = {}
    for e in expenses:
        cat = e.category
        cat_name = EXPENSE_CATEGORIES.get(cat, cat)
        category_breakdown[cat_name] = category_breakdown.get(cat_name, 0) + e.amount / 100
    
    return BudgetStats(
        total_budget=round(total_budget, 2),
        total_spent=round(total_spent, 2),
        remaining=round(total_budget - total_spent, 2),
        percentage=round(total_spent / total_budget * 100, 1) if total_budget > 0 else 0,
        category_breakdown=category_breakdown
    )

@app.get("/api/budget/", response_model=dict)
def get_budget(
    month: Optional[str] = Query(None, description="月份 YYYY-MM，默认当月"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户预算"""
    if not month:
        month = datetime.now().strftime("%Y-%m")
    
    budget = db.query(DBBudget).filter(
        DBBudget.user_id == current_user.username,
        DBBudget.month == month
    ).first()
    
    return {
        "total_budget": budget.total_budget / 100 if budget else 1500,
        "month": month
    }

@app.post("/api/budget/", response_model=dict)
def set_budget(
    budget: BudgetSet,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """设置月度预算"""
    existing = db.query(DBBudget).filter(
        DBBudget.user_id == current_user.username,
        DBBudget.month == budget.month
    ).first()
    
    if existing:
        existing.total_budget = int(budget.total_budget * 100)
    else:
        new_budget = DBBudget(
            user_id=current_user.username,
            total_budget=int(budget.total_budget * 100),
            month=budget.month
        )
        db.add(new_budget)
    
    db.commit()
    return {"message": "预算设置成功", "month": budget.month, "total_budget": budget.total_budget}

# ==================== 健康打卡 API ====================

@app.get("/api/health/checkins/", response_model=list)
def get_health_checkins(
    start_date: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(31, ge=1, le=100),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户的健康打卡记录"""
    query = db.query(DBHealthCheckin).filter(
        DBHealthCheckin.user_id == current_user.username
    )
    
    if start_date:
        query = query.filter(DBHealthCheckin.date >= start_date)
    if end_date:
        query = query.filter(DBHealthCheckin.date <= end_date)
    
    offset = (page - 1) * page_size
    checkins = query.order_by(DBHealthCheckin.date.desc()).offset(offset).limit(page_size).all()
    
    return [
        {
            "id": c.id,
            "date": c.date,
            "sleep_time": c.sleep_time,
            "wake_time": c.wake_time,
            "sleep_duration": c.sleep_duration,
            "exercise": c.exercise,
            "exercise_text": EXERCISE_MAP.get(c.exercise, c.exercise),
            "steps": c.steps,
            "health_status": c.health_status,
            "health_status_text": HEALTH_STATUS_MAP.get(c.health_status, c.health_status),
            "weight": c.weight,
            "remark": c.remark,
            "created_at": c.created_at.isoformat() if c.created_at else None
        } for c in checkins
    ]

@app.post("/api/health/checkins/", response_model=dict)
def create_or_update_health_checkin(
    checkin: HealthCheckinCreate,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """添加或更新健康打卡记录"""
    # 计算睡眠时长
    sleep_duration = None
    if checkin.sleep_time and checkin.wake_time:
        try:
            sleep_t = datetime.strptime(checkin.sleep_time, "%H:%M")
            wake_t = datetime.strptime(checkin.wake_time, "%H:%M")
            diff = (wake_t - sleep_t).total_seconds() / 3600
            if diff < 0:
                diff += 24  # 跨天
            sleep_duration = round(diff, 1)
        except:
            pass
    
    # 检查是否已存在
    existing = db.query(DBHealthCheckin).filter(
        DBHealthCheckin.user_id == current_user.username,
        DBHealthCheckin.date == checkin.date
    ).first()
    
    if existing:
        # 更新
        existing.sleep_time = checkin.sleep_time
        existing.wake_time = checkin.wake_time
        existing.sleep_duration = sleep_duration
        existing.exercise = checkin.exercise
        existing.steps = checkin.steps
        existing.health_status = checkin.health_status
        existing.weight = checkin.weight
        existing.remark = checkin.remark
        db.commit()
        db.refresh(existing)
        return {"id": existing.id, "date": existing.date, "message": "更新成功"}
    else:
        # 新增
        new_checkin = DBHealthCheckin(
            user_id=current_user.username,
            date=checkin.date,
            sleep_time=checkin.sleep_time,
            wake_time=checkin.wake_time,
            sleep_duration=sleep_duration,
            exercise=checkin.exercise,
            steps=checkin.steps,
            health_status=checkin.health_status,
            weight=checkin.weight,
            remark=checkin.remark
        )
        db.add(new_checkin)
        db.commit()
        db.refresh(new_checkin)
        return {"id": new_checkin.id, "date": new_checkin.date, "message": "打卡成功"}

@app.get("/api/health/checkins/{date}", response_model=dict)
def get_health_checkin_by_date(
    date: str,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取指定日期的打卡记录"""
    checkin = db.query(DBHealthCheckin).filter(
        DBHealthCheckin.user_id == current_user.username,
        DBHealthCheckin.date == date
    ).first()
    
    if not checkin:
        return {"date": date, "checked": False}
    
    return {
        "id": checkin.id,
        "date": checkin.date,
        "sleep_time": checkin.sleep_time,
        "wake_time": checkin.wake_time,
        "sleep_duration": checkin.sleep_duration,
        "exercise": checkin.exercise,
        "steps": checkin.steps,
        "health_status": checkin.health_status,
        "weight": checkin.weight,
        "remark": checkin.remark,
        "checked": True
    }

@app.delete("/api/health/checkins/{date}", response_model=dict)
def delete_health_checkin(
    date: str,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """删除打卡记录"""
    checkin = db.query(DBHealthCheckin).filter(
        DBHealthCheckin.user_id == current_user.username,
        DBHealthCheckin.date == date
    ).first()
    
    if not checkin:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    db.delete(checkin)
    db.commit()
    return {"message": "删除成功", "date": date}

@app.get("/api/health/stats/", response_model=HealthStats)
def get_health_stats(
    days: int = Query(30, ge=7, le=90, description="统计天数"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取健康统计数据"""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    checkins = db.query(DBHealthCheckin).filter(
        DBHealthCheckin.user_id == current_user.username,
        DBHealthCheckin.date >= start_date,
        DBHealthCheckin.date <= end_date
    ).all()
    
    total_checkins = len(checkins)
    
    # 计算连续打卡天数
    consecutive_days = 0
    check_dates = set(c.date for c in checkins)
    current_date = datetime.now()
    while True:
        date_str = current_date.strftime("%Y-%m-%d")
        if date_str in check_dates:
            consecutive_days += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # 计算平均值
    sleep_values = [c.sleep_duration for c in checkins if c.sleep_duration]
    avg_sleep = round(sum(sleep_values) / len(sleep_values), 1) if sleep_values else 0
    
    steps_values = [c.steps for c in checkins if c.steps]
    avg_steps = round(sum(steps_values) / len(steps_values)) if steps_values else 0
    
    # 运动率
    exercised = len([c for c in checkins if c.exercise != "none"])
    exercise_rate = round(exercised / total_checkins * 100, 1) if total_checkins > 0 else 0
    
    # 健康评分
    health_score = 60
    if avg_sleep >= 7:
        health_score += 10
    if avg_steps >= 6000:
        health_score += 10
    if exercise_rate >= 50:
        health_score += 10
    if total_checkins >= days * 0.8:
        health_score += 10
    
    return HealthStats(
        total_checkins=total_checkins,
        consecutive_days=consecutive_days,
        avg_sleep=avg_sleep,
        avg_steps=avg_steps,
        exercise_rate=exercise_rate,
        health_score=min(100, health_score)
    )

@app.get("/api/health/calendar/", response_model=dict)
def get_health_calendar(
    year: int = Query(None, description="年份"),
    month: int = Query(None, description="月份"),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取某年月的打卡日历数据"""
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    
    checkins = db.query(DBHealthCheckin).filter(
        DBHealthCheckin.user_id == current_user.username,
        DBHealthCheckin.date >= start_date,
        DBHealthCheckin.date < end_date
    ).all()
    
    calendar_data = {}
    for c in checkins:
        calendar_data[c.date] = {
            "checked": True,
            "health_status": c.health_status,
            "exercise": c.exercise,
            "steps": c.steps
        }
    
    return {"year": year, "month": month, "data": calendar_data}

# ==================== 旅游规划 API ====================

@app.get("/api/trips/", response_model=dict)
def get_trips(
    status: Optional[str] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取当前用户的旅行计划列表"""
    import json
    
    query = db.query(DBTrip).filter(DBTrip.user_id == current_user.username)
    
    if status:
        query = query.filter(DBTrip.status == status)
    
    total = query.count()
    offset = (page - 1) * page_size
    trips = query.order_by(DBTrip.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "trips": [
            {
                "id": t.id,
                "destination": t.destination,
                "days": t.days,
                "people": t.people,
                "budget": t.budget / 100,
                "style": t.style,
                "start_date": t.start_date,
                "end_date": t.end_date,
                "status": t.status,
                "cover_image": t.cover_image,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in trips
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }

@app.post("/api/trips/", response_model=dict)
def create_trip(
    trip: TripCreate,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """创建新的旅行计划"""
    import json
    
    end_date = None
    if trip.start_date:
        try:
            start = datetime.strptime(trip.start_date, "%Y-%m-%d")
            end_date = (start + timedelta(days=trip.days - 1)).strftime("%Y-%m-%d")
        except:
            pass
    
    itinerary_json = None
    if trip.itinerary:
        itinerary_json = json.dumps(trip.itinerary)
    
    new_trip = DBTrip(
        user_id=current_user.username,
        destination=trip.destination,
        days=trip.days,
        people=trip.people,
        budget=int(trip.budget * 100),
        style=trip.style,
        start_date=trip.start_date,
        end_date=end_date,
        itinerary=itinerary_json,
        status="planning"
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    
    return {
        "id": new_trip.id,
        "destination": new_trip.destination,
        "days": new_trip.days,
        "message": "旅行计划创建成功"
    }

@app.get("/api/trips/{trip_id}", response_model=dict)
def get_trip_detail(
    trip_id: str,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """获取旅行计划详情"""
    import json
    
    trip = db.query(DBTrip).filter(
        DBTrip.id == trip_id,
        DBTrip.user_id == current_user.username
    ).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="旅行计划不存在")
    
    itinerary = None
    if trip.itinerary:
        try:
            itinerary = json.loads(trip.itinerary)
        except:
            pass
    
    return {
        "id": trip.id,
        "destination": trip.destination,
        "days": trip.days,
        "people": trip.people,
        "budget": trip.budget / 100,
        "style": trip.style,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "status": trip.status,
        "itinerary": itinerary,
        "cover_image": trip.cover_image,
        "created_at": trip.created_at.isoformat() if trip.created_at else None
    }

@app.put("/api/trips/{trip_id}", response_model=dict)
def update_trip(
    trip_id: str,
    trip_update: TripCreate,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """更新旅行计划"""
    import json
    
    trip = db.query(DBTrip).filter(
        DBTrip.id == trip_id,
        DBTrip.user_id == current_user.username
    ).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="旅行计划不存在")
    
    trip.destination = trip_update.destination
    trip.days = trip_update.days
    trip.people = trip_update.people
    trip.budget = int(trip_update.budget * 100)
    trip.style = trip_update.style
    
    if trip_update.start_date:
        try:
            trip.start_date = trip_update.start_date
            trip.end_date = (datetime.strptime(trip_update.start_date, "%Y-%m-%d") + timedelta(days=trip_update.days - 1)).strftime("%Y-%m-%d")
        except:
            pass
    
    if trip_update.itinerary:
        trip.itinerary = json.dumps(trip_update.itinerary)
    
    db.commit()
    return {"message": "更新成功", "id": trip_id}

@app.delete("/api/trips/{trip_id}", response_model=dict)
def delete_trip(
    trip_id: str,
    db: Session = Depends(get_user_db),
    current_user: DBUser = Depends(get_current_user)
):
    """删除旅行计划"""
    trip = db.query(DBTrip).filter(
        DBTrip.id == trip_id,
        DBTrip.user_id == current_user.username
    ).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="旅行计划不存在")
    
    db.delete(trip)
    db.commit()
    return {"message": "删除成功", "id": trip_id}

@app.post("/api/trips/generate", response_model=dict)
def generate_itinerary(
    request: TripGenerateRequest
):
    """AI 生成行程规划"""
    activities_pool = [
        {"time": "08:00", "name": "酒店早餐", "desc": "享用早餐", "cost": 0, "duration": "1小时"},
        {"time": "09:00", "name": "景点游览", "desc": "参观主要景点", "cost": 5000, "duration": "3小时"},
        {"time": "12:00", "name": "午餐", "desc": "当地特色美食", "cost": 3000, "duration": "1小时"},
        {"time": "14:00", "name": "下午活动", "desc": "继续游览", "cost": 3000, "duration": "2小时"},
        {"time": "17:00", "name": "自由活动", "desc": "购物或休息", "cost": 0, "duration": "2小时"},
        {"time": "19:00", "name": "晚餐", "desc": "特色晚餐", "cost": 4000, "duration": "1.5小时"},
        {"time": "21:00", "name": "返回酒店", "desc": "休息", "cost": 0, "duration": "30分钟"}
    ]
    
    themes = ["历史文化探秘", "美食之旅", "自然风光欣赏", "城市漫步", "休闲度假"]
    itinerary = []
    
    for i in range(request.days):
        day_activities = activities_pool[:4 + (i % 3)]
        total_cost = sum(a["cost"] for a in day_activities)
        
        itinerary.append({
            "day": i + 1,
            "theme": themes[i % len(themes)],
            "activities": day_activities,
            "meals": {"breakfast": "酒店自助", "lunch": "当地美食", "dinner": "特色餐厅"},
            "tips": "注意保管好个人物品" if i == 0 else None,
            "dayCost": total_cost
        })
    
    return {
        "destination": request.destination,
        "days": request.days,
        "people": request.people,
        "budget": request.budget,
        "style": request.style,
        "itinerary": itinerary,
        "totalCost": sum(d["dayCost"] for d in itinerary)
    }