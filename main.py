from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
import os

# 📌 Получаем данные БД из переменных среды (Railway автоматически задаст их)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:iqctUHZDSblHxNmMqBNvoaqndDbxEyhl@postgres.railway.internal:5432/railway")

# Подключение к БД
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# 📌 Модель данных
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

# 📌 Создаем таблицы, если их нет
Base.metadata.create_all(bind=engine)

# 📌 Функция получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📌 Авторизация
@app.get("/login")
def login(username: str, password: str):
    if username == "gidro" and password == "gidro":
        return {"message": "Success"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# 📌 Получение данных
@app.get("/data")
def get_data(db: Session = Depends(get_db)):
    data = db.query(DeviceData).order_by(DeviceData.timestamp.desc()).limit(7).all()
    return data

# 📌 Сохранение данных от устройства
@app.post("/data")
def save_data(data: DeviceData, db: Session = Depends(get_db)):
    db.add(data)
    db.commit()
    return {"message": "Data saved"}

# 📌 Получение настроек
@app.get("/settings")
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(Settings).first()
    return settings

# 📌 Обновление настроек
@app.post("/settings")
def update_settings(settings: Settings, db: Session = Depends(get_db)):
    db.query(Settings).update(settings.dict())
    db.commit()
    return {"message": "Settings updated"}
