from aiogram import types
import logging

from services.payment_service import create_payment, check_payment
from utils.user_state import set_user_state, STATE_MENU
from utils.payments import add_payment, get_payment, remove_payment
from utils.user_roles import set_user_role
from keyboards import (
    get_payment_keyboard,
    get_confirm_payment_keyboard,
    get_main_keyboard,
    get_back_keyboard,
)

log = logging.getLogger(__name__)


# Меню выбора тарифа
async def buy_menu(message: types.Message):
    """
    Открывает меню с тарифами. Возврат в главное меню — кнопкой «⬅️ В меню».
    """
    set_user_state(message.from_user.id, STATE_MENU)
    await message.answer(
        "Тарифы:\n"
        "• BASIC — 10 генераций, 1 SVG\n"
        "• PRO — 20 генераций, 2 SVG\n\n"
        "Выберите тариф:",
        reply_markup=get_payment_keyboard(),
    )


# Обработка клика по тарифу (создание платежа)
async def handle_buy(message: types.Message):
    text = (message.text or "")

    if "BASIC" in text:
        amount, role = 999, "user_basic"
    elif "PRO" in text:
        amount, role = 1999, "user_pro"
    else:
        await message.answer("❌ Такой тариф не найден", reply_markup=get_back_keyboard())
        return

    try:
        url, payment_id = create_payment(
            amount,
            f"Покупка {role}",
            # при желании замените на ссылку вашего бота
            return_url="https://t.me/Logozavod_Bot",
        )
    except Exception:
        log.exception("Ошибка создания платежа")
        await message.answer(
            "❌ Не удалось создать платёж. Проверьте настройки ЮKassa и попробуйте ещё раз.",
            reply_markup=get_back_keyboard(),
        )
        return

    # Сохраняем платёж и показываем клавиатуру подтверждения
    add_payment(message.from_user.id, payment_id, role)

    await message.answer(f"Для оплаты перейдите по ссылке: {url}")
    await message.answer(
        "После успешной оплаты нажмите «✅ Я оплатил».",
        reply_markup=get_confirm_payment_keyboard(),
    )


# Подтверждение оплаты (меняем роль и возвращаемся в главное меню)
async def confirm_payment(message: types.Message):
    if (message.text or "").strip() != "✅ Я оплатил":
        return

    user_id = message.from_user.id
    data = get_payment(user_id)

    if not data:
        await message.answer(
            "❌ Активный платёж не найден.",
            reply_markup=get_main_keyboard(),
        )
        return

    payment_id = data["payment_id"]
    new_role = data["role"]

    try:
        ok = check_payment(payment_id)
    except Exception:
        log.exception("Ошибка проверки платежа")
        ok = False

    if ok:
        set_user_role(user_id, new_role)
        remove_payment(user_id)
        await message.answer(
            f"✅ Оплата подтверждена. Ваша роль обновлена: <b>{new_role}</b>",
            reply_markup=get_main_keyboard(),
        )
    else:
        await message.answer(
            "⏳ Платёж ещё не подтверждён. Проверьте оплату и попробуйте ещё раз.",
            reply_markup=get_confirm_payment_keyboard(),
        )
