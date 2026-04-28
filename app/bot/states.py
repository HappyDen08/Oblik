from aiogram.fsm.state import State, StatesGroup

class TransactionState(StatesGroup):
    waiting_for_student = State()
    waiting_for_amount = State()
    waiting_for_date = State()
    waiting_for_confirmation = State()

class AttendanceState(StatesGroup):
    waiting_for_student = State()
    waiting_for_status = State()
    waiting_for_date = State()
    waiting_for_confirmation = State()

class InfoState(StatesGroup):
    waiting_for_student = State()

class EditBalanceState(StatesGroup):
    waiting_for_student = State()
    waiting_for_amount = State()
    waiting_for_confirmation = State()
