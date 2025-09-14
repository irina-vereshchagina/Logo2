# utils/payments.py
import json
import os
from threading import Lock

DB_FILE = "payments_db.json"
payments: dict[str, dict[str, str]] = {}
_lock = Lock()

def load_payments():
    """Считывает ожидающие платежи из файла."""
    global payments
    if os.path.exists(DB_FILE):
        with _lock:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                payments = json.load(f)
    else:
        payments = {}

def save_payments():
    """Сохраняет ожидающие платежи в файл."""
    with _lock:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(payments, f, ensure_ascii=False, indent=2)

def add_payment(user_id: int, payment_id: str, role: str):
    """Сохраняет payment_id и роль для пользователя."""
    payments[str(user_id)] = {"payment_id": payment_id, "role": role}
    save_payments()

def get_payment(user_id: int):
    """Возвращает данные платежа для пользователя или None."""
    return payments.get(str(user_id))

def remove_payment(user_id: int):
    """Удаляет данные платежа (когда оплата завершилась)."""
    if str(user_id) in payments:
        del payments[str(user_id)]
        save_payments()
