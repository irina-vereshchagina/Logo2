from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from services.payment_service import create_payment
from utils.user_state import set_user_state, STATE_MENU
from utils.payments import add_payment  # новый импорт

# меню выбора тарифа
async def buy_menu(message: types.Message):
    set_user_state(message.from_user.id, STATE_MENU)  # оставить в меню
    buttons = [
        [KeyboardButton(text="Купить BASIC — 999 ₽")],
        [KeyboardButton(text="Купить PRO — 1999 ₽")],
        [KeyboardButton(text="⬅️ Назад")],
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

    # создаём платёж и получаем id
    url, payment_id = create_payment(
        amount,
        f"Покупка {role}",
        return_url="https://t.me/your_bot"
    )
    # сохраняем payment_id и роль для последующей проверки
    add_payment(message.from_user.id, payment_id, role)

    # отправляем ссылку на оплату
    await message.answer(f"Для оплаты перейдите по ссылке: {url}")
