import os
import asyncio
import httpx
import threading
import time
from fastapi import FastAPI, Depends, HTTPException, Form, Query
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
from pydantic import BaseModel
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse





# Загружаем URL базы из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не установлен")

# Исправляем URL, если он начинается с "postgres://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Настройки БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Создаем экземпляр FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены или указать конкретные
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все HTTP методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# Определяем путь к собранному фронтенду
frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print("⚠️ Папка frontend/dist не найдена! Запустите `npm run build` в папке frontend.")

# Определение моделей SQLAlchemy
class DeviceData(Base):
    __tablename__ = "device_data"
    id = Column(Integer, primary_key=True, index=True)
    tds = Column(Float, nullable=False)
    ph = Column(Float, nullable=False)
    main_liquid = Column(String, nullable=False)
    components = Column(String, nullable=False)
    ph_level = Column(String, nullable=False)
    water_level = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Settings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    max_tds = Column(Float, nullable=False)
    min_tds = Column(Float, nullable=False)
    max_ph = Column(Float, nullable=False)
    min_ph = Column(Float, nullable=False)

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

# Функция для работы с БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic модели
class DeviceDataBase(BaseModel):
    tds: float
    ph: float
    main_liquid: str
    components: str
    ph_level: str
    water_level: str
    timestamp: Optional[datetime.datetime] = None

class DeviceDataCreate(DeviceDataBase):
    pass

class DeviceDataResponse(BaseModel):
    id: int
    tds: float
    ph: float
    water_level: float
    timestamp: str

    class Config:
        from_attributes = True  

class SettingsBase(BaseModel):
    max_tds: float
    min_tds: float
    max_ph: float
    min_ph: float

class SettingsResponse(SettingsBase):
    id: int
    class Config:
        from_attributes = True

# API маршруты
@app.get("/")
def read_root():
    return {"message": "API is running"}

@app.get("/login")
async def login(request: Request):
    username = request.query_params.get('username')
    password = request.query_params.get('password')
    
    # Проверка логина и пароля
    if username == "gidro" and password == "gidro":
        return JSONResponse(content={"message": "Login successful!"}, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/data", response_model=List[DeviceDataResponse])
def get_data(db: Session = Depends(get_db)):
    return db.query(DeviceData).order_by(DeviceData.timestamp.desc()).limit(7).all()
@app.post("/login")
async def login(username: str, password: str):
    print(f"Received login attempt with username={username} and password={password}")

@app.post("/data", response_model=DeviceDataResponse)
def save_data(data: DeviceDataCreate, db: Session = Depends(get_db)):
    db_data = DeviceData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@app.get("/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

@app.post("/settings", response_model=SettingsResponse)
def update_settings(settings: SettingsBase, db: Session = Depends(get_db)):
    existing_settings = db.query(Settings).first()
    if existing_settings:
        for key, value in settings.dict().items():
            setattr(existing_settings, key, value)
    else:
        existing_settings = Settings(**settings.dict())
        db.add(existing_settings)

    db.commit()
    db.refresh(existing_settings)
    return existing_settings

# Keep-alive процесс
DOMAIN = "https://gidro-2.onrender.com"

async def keep_alive():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await client.get(DOMAIN)
            except Exception as e:
                print("Ошибка keep-alive:", e)
            await asyncio.sleep(300)

@app.on_event("startup")
async def start_keep_alive():
    asyncio.create_task(keep_alive())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
