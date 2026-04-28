import asyncio
import json
import os
from datetime import datetime
from sqlalchemy import select
from app.database import async_session, Student, Transaction, Attendance, AttendanceStatus, init_db

LESSON_PRICE = float(os.getenv("LESSON_PRICE", 250))

async def get_or_create_student(session, name):
    # Normalize name: split by space or underscore
    # Convention: first part is last_name, rest is first_name
    name = name.replace("_", " ")
    parts = name.split(maxsplit=1)
    last_name = parts[0]
    first_name = parts[1] if len(parts) > 1 else ""
    
    result = await session.execute(
        select(Student).where(Student.last_name == last_name, Student.first_name == first_name)
    )
    student = result.scalars().first()
    
    if not student:
        student = Student(last_name=last_name, first_name=first_name, balance_lessons=0.0)
        session.add(student)
        await session.flush()
        print(f"Created student: {last_name} {first_name}")
    return student

async def load_data(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    async with async_session() as session:
        # Transactions
        for t_data in data["transactions"]:
            student = await get_or_create_student(session, t_data["student_name"])
            date = datetime.fromisoformat(t_data["date"])
            amount = float(t_data["amount"])
            lessons_added = amount / LESSON_PRICE
            
            transaction = Transaction(
                student_id=student.id,
                date=date,
                amount=amount,
                lessons_added=lessons_added
            )
            session.add(transaction)
            student.balance_lessons += lessons_added
            
        # Attendances
        for a_data in data["attendances"]:
            student = await get_or_create_student(session, a_data["student_name"])
            date = datetime.fromisoformat(a_data["date"])
            status_str = a_data["status"]
            
            # Map status string to Enum
            try:
                status = AttendanceStatus(status_str)
            except ValueError:
                status = AttendanceStatus.PRESENT # Default
                
            balance_impact = -1.0 if status in [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT_CHARGED] else 0.0
            
            attendance = Attendance(
                student_id=student.id,
                date=date,
                status=status,
                balance_impact=balance_impact
            )
            session.add(attendance)
            student.balance_lessons += balance_impact
            
        await session.commit()
        print("Data loaded successfully!")

if __name__ == "__main__":
    import sys
    asyncio.run(init_db())
    json_path = sys.argv[1] if len(sys.argv) > 1 else "data_dump.json"
    if os.path.exists(json_path):
        asyncio.run(load_data(json_path))
    else:
        print(f"File {json_path} not found")
