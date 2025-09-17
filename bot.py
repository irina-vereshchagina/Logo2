# handlers/buy.py
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging

from services.payment_service import create_payment
from utils.user_state import set_user_state, STATE_MENU
from utils.payments import add_payment

# Меню тарифов (как в остальных разделах: "⬅️ В меню")
async def buy_menu(message: types.Message):
    set_user_state(message.from_user.id, STATE_MENU)
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Купить BASIC — 999 ₽")],
            [KeyboardButton(text="Купить PRO — 1999 ₽")],
            [KeyboardButton(text="⬅️ В меню")],   # одинаково с другими разделами
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Тарифы:\n"
        "• BASIC — 10 генераций, 1 SVG\n"
        "• PRO — 20 генераций, 2 SVG\n\n"
        "Выберите тариф:",
        reply_markup=kb
    )

# Покупка
async def handle_buy(message: types.Message):
    if "BASIC" in (message.text or ""):
        amount, role = 999, "user_basic"
    elif "PRO" in (message.text or ""):
        amount, role = 1999, "user_pro"
    else:
        await message.answer("❌ Такой тариф не найден")
        return

    try:
        url, payment_id = create_payment(
            amount,
            f"Покупка {role}",
            return_url="https://t.me/your_bot"  # при необходимости смените на @имя_вашего_бота
        )
    except Exception:
        logging.exception("Ошибка создания платежа")
        await message.answer("❌ Не удалось создать платёж. Проверьте настройки ЮKassa и попробуйте ещё раз.")
        return

    # сохраняем платёж
    add_payment(message.from_user.id, payment_id, role)

    # клавиатура как в остальных разделах: есть "⬅️ В меню" + кнопка подтверждения
    confirm_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Я оплатил")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True,
    )

    await message.answer(f"Для оплаты перейдите по ссылке: {url}")
    await message.answer("После успешной оплаты нажмите «✅ Я оплатил».", reply_markup=confirm_kb)
