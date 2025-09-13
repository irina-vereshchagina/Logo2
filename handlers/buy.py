from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from services.payment_service import create_payment, check_payment
from utils.user_roles import set_user_role

# меню выбора тарифа
async def buy_menu(message: types.Message):
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
    # TODO: сохранить payment_id и выбранный тариф (например, в файл или БД)
    await message.answer(f"Для оплаты перейдите по ссылке: {url}")

    # ⚡ вариант авто-проверки (по команде /check или через background-job)
    # if check_payment(payment_id):
    #     set_user_role(message.from_user.id, role)
    #     await message.answer(f"✅ Оплата успешна! Тариф {role} активирован.")
