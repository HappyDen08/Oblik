from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session, Student, Transaction, Attendance

app = FastAPI(title="Моніторинг Занять API")

async def get_db():
    async with async_session() as session:
        yield session

@app.get("/")
def read_root():
    return {"message": "API працює. Перейдіть на /docs для перегляду ендпоінтів."}

@app.get("/students")
async def get_students(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student))
    students = result.scalars().all()
    return [{"id": s.id, "first_name": s.first_name, "last_name": s.last_name, "balance": s.balance_lessons} for s in students]

@app.get("/transactions")
async def get_transactions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction).order_by(Transaction.date.desc()).limit(50))
    transactions = result.scalars().all()
    return transactions

@app.get("/attendances")
async def get_attendances(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Attendance).order_by(Attendance.date.desc()).limit(50))
    attendances = result.scalars().all()
    return attendances
