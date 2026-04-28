import os
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from app.database import Student

def get_main_keyboard(user_id: int = None):
    keyboard_layout = [
        [KeyboardButton(text="Внести транзакцію")],
        [KeyboardButton(text="Внести відвідування")],
        [KeyboardButton(text="Інформація по учню")],
        [KeyboardButton(text="Редагувати баланс")]
    ]
    
    admin_id = os.getenv("ADMIN_ID")
    if admin_id and str(user_id) == str(admin_id):
        keyboard_layout.append([KeyboardButton(text="Бекап бази")])

    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_layout,
        resize_keyboard=True
    )
    return keyboard

def get_cancel_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Скасувати")]],
        resize_keyboard=True
    )
    return keyboard

def get_students_inline_keyboard(students: list[Student]):
    buttons = []
    for s in students:
        buttons.append([InlineKeyboardButton(text=f"{s.last_name} {s.first_name}", callback_data=f"student_{s.id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_attendance_status_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Була (-1 урок)")],
            [KeyboardButton(text="Не була (перенесено)")],
            [KeyboardButton(text="Не була (списано)")],
            [KeyboardButton(text="Скасувати")]
        ],
        resize_keyboard=True
    )
    return keyboard
def get_confirmation_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Так, все вірно")],
            [KeyboardButton(text="Скасувати")]
        ],
        resize_keyboard=True
    )
    return keyboard
