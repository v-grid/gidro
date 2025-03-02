import os
import threading
import time
import requests
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
from pydantic import BaseModel
from typing import List, Optional
from fastapi.staticfiles import StaticFiles

# Определяем путь к собранному фронтенду
frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print("⚠️ Папка frontend/dist не найдена! Запустите `npm run build` в папке frontend.")





# Загружаем URL базы из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не установлен")

# Настройки БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Создаем экземпляр FastAPI
app = FastAPI()

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

# Создание таблиц в БД (если их нет)
Base.metadata.create_all(bind=engine)

# Функция для работы с БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic модели для сериализации данных
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

class DeviceDataResponse(DeviceDataBase):
    id: int

    class Config:
        orm_mode = True

class SettingsBase(BaseModel):
    max_tds: float
    min_tds: float
    max_ph: float
    min_ph: float

class SettingsResponse(SettingsBase):
    id: int

    class Config:
        orm_mode = True

# Добавляем обработчик корневого маршрута
@app.get("/")
def read_root():
    return {"message": "API is running"}

# Авторизация
@app.get("/login")
def login(username: str, password: str):
    if username == "gidro" and password == "gidro":
        return {"message": "Success"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Получение последних 7 записей с устройства
@app.get("/data", response_model=List[DeviceDataResponse])
def get_data(db: Session = Depends(get_db)):
    data = db.query(DeviceData).order_by(DeviceData.timestamp.desc()).limit(7).all()
    return data

# Сохранение новых данных от устройства
@app.post("/data", response_model=DeviceDataResponse)
def save_data(data: DeviceDataCreate, db: Session = Depends(get_db)):
    db_data = DeviceData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

# Получение текущих настроек
@app.get("/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# Обновление настроек
@app.post("/settings", response_model=SettingsResponse)
def update_settings(settings: SettingsBase, db: Session = Depends(get_db)):
    existing_settings = db.query(Settings).first()
    if existing_settings:
        db.delete(existing_settings)
        db.commit()
    
    db_settings = Settings(**settings.dict())
    db.add(db_settings)
    db.commit()
    return db_settings

# Фоновая задача для поддержания активности сервера
DOMAIN = "https://gidro-2.onrender.com"

def keep_alive():
    while True:
        try:
            requests.get(DOMAIN)
            print("Keep-alive ping sent")
        except Exception as e:
            print("Ошибка keep-alive:", e)
        time.sleep(300)  # Раз в 5 минут

@app.on_event("startup")
def start_keep_alive():
    thread = threading.Thread(target=keep_alive, daemon=True)
    thread.start()