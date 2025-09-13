from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.payment_service import create_payment, check_payment
from utils.user_roles import set_user_role
from utils.user_state import set_user_state, STATE_MENU

# меню выбора тарифа
async def buy_menu(message: types.Message):
    set_user_state(message.from_user.id, STATE_MENU)  # оставить в меню
    buttons = [
        [KeyboardButton("Купить BASIC — 999 ₽")],
        [KeyboardButton("Купить PRO — 1999 ₽")],
        [KeyboardButton("⬅️ Назад")],
    ]
    kb = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Выберите тариф для покупки:", reply_markup=kb)

# обработка покупки
async def handle_buy(message: types.Message):
    if "BASIC" in message.text:
        amount, role = 999, "user_basic"
    elif "PRO" in message.text:
        amount, role = 1999, "user_pro"
    else:
        await message.answer("❌ Такой тариф не найден")
        return

    url, payment_id = create_payment(amount, f"Покупка {role}", return_url="https://t.me/your_bot")
    await message.answer(f"Для оплаты перейдите по ссылке: {url}")
