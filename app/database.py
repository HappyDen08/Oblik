import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum, Float
import enum
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", os.getenv("POSTGRES_USER", "postgres"))
DB_PASS = os.getenv("DB_PASS", os.getenv("POSTGRES_PASSWORD", "postgres"))
DB_HOST = os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "localhost"))
DB_PORT = os.getenv("DB_PORT", os.getenv("POSTGRES_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", os.getenv("POSTGRES_DB", "monitoring_db"))
DB_TYPE = os.getenv("DB_TYPE", "postgres") # 'postgres' or 'mysql'

if DB_TYPE == "mysql":
    DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Overwrite if full URL is provided
DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    ABSENT_RESCHEDULED = "absent_rescheduled"
    ABSENT_CHARGED = "absent_charged"

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    balance_lessons: Mapped[float] = mapped_column(Float, default=0.0)

    transactions = relationship("Transaction", back_populates="student", cascade="all, delete")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete")

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    amount: Mapped[int] = mapped_column(Integer)
    lessons_added: Mapped[float] = mapped_column(Float)

    student = relationship("Student", back_populates="transactions")

class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus))
    balance_impact: Mapped[float] = mapped_column(Float, default=0.0)

    student = relationship("Student", back_populates="attendances")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # Ручна перевірка та додавання колонки, якщо вона відсутня (для існуючих баз)
        def add_column_if_missing(connection):
            from sqlalchemy import inspect, text
            inspector = inspect(connection)
            columns = [c['name'] for c in inspector.get_columns('attendances')]
            if 'balance_impact' not in columns:
                connection.execute(text('ALTER TABLE attendances ADD COLUMN balance_impact FLOAT DEFAULT 0.0'))
        
        await conn.run_sync(add_column_if_missing)
