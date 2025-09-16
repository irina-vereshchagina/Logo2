# services/payment_service.py
from __future__ import annotations

import os
import logging
from uuid import uuid4
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from yookassa import Configuration, Payment

# 1) Загружаем .env
load_dotenv()

# 2) Берём КЛЮЧИ МАГАЗИНА (приём платежей), НЕ ключи выплат
SHOP_ID = (os.getenv("YOOKASSA_SHOP_ID") or "").strip()
SECRET  = (os.getenv("YOOKASSA_SECRET_KEY") or "").strip()
if not SHOP_ID or not SECRET:
    raise RuntimeError("YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY не заданы в .env")

# 3) Форсим Basic Auth (без OAuth)
Configuration.account_id = SHOP_ID
Configuration.secret_key = SECRET
Configuration.access_token = None

def _amount_str(amount: float | int | str) -> str:
    """Нормализуем сумму к строке '999.00'."""
    try:
        return f"{Decimal(str(amount)):.2f}"
    except (InvalidOperation, ValueError):
        raise ValueError(f"Некорректная сумма: {amount!r}")

def create_payment(amount: float | int | str, description: str, return_url: str) -> tuple[str, str]:
    """Создаёт платёж. Возвращает (confirmation_url, payment_id)."""
    payload = {
        "amount": {"value": _amount_str(amount), "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": description,
        "metadata": {"env": "test"},
    }
    try:
        payment = Payment.create(payload, idempotence_key=str(uuid4()))
        return payment.confirmation.confirmation_url, payment.id
    except Exception:
        logging.exception("YooKassa create_payment failed (проверьте ключи магазина)")
        raise

def check_payment(payment_id: str) -> bool:
    """True, если платёж успешно завершён."""
    try:
        p = Payment.find_one(payment_id)
        return getattr(p, "status", "") == "succeeded"
    except Exception:
        logging.exception("YooKassa check_payment failed")
        return False
