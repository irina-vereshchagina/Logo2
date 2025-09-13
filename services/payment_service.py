from yookassa import Configuration, Payment
import os

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")

def create_payment(amount: int, description: str, return_url: str):
    payment = Payment.create({
        "amount": {"value": f"{amount}", "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": return_url},
        "capture": True,
        "description": description
    })
    return payment.confirmation.confirmation_url, payment.id

def check_payment(payment_id: str) -> bool:
    payment = Payment.find_one(payment_id)
    return payment.status == "succeeded"
