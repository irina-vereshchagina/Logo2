import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN
from handlers import start, info, prompt, generation, vectorize, buy
from handlers.check import check_payment_command  # импортируем /check
from utils.user_state import get_user_state, STATE_GENERATE, STATE_VECTORIZE, STATE_MENU
from utils.user_roles import load_db
from utils.payments import load_payments  # импорт загрузки платежей

# Настройка логов
logging.basicConfig(level=logging.INFO)
logging.getLogger("aiogram.event").setLevel(logging.DEBUG)

# Создание бота и диспетчера
defaults = DefaultBotProperties(parse_mode=ParseMode.HTML)
bot = Bot(token=TELEGRAM_BOT_TOKEN, default=defaults)
dp = Dispatcher(storage=MemoryStorage())

def is_generate_text(message):
    return (
        message.text
        and not message.text.startswith("/")
        and get_user_state(message.from_user.id) == STATE_GENERATE
    )

def is_vectorization_photo(message):
    return (
        message.photo
        and get_user_state(message.from_user.id) == STATE_VECTORIZE
    )

# Универсальная кнопка "назад" / "в меню"
def is_back(m):
    t = (m.text or "").replace("\uFE0F", "").strip()  # убираем вариационный селектор эмодзи
    return t in ("⬅️ В меню", "⬅️ Назад", "Назад")

# Регистрация хендлеров
dp.message.register(start.start, CommandStart())
dp.message.register(start.setrole_command, Command(commands=["setrole"]))
dp.message.register(start.start, is_back)  # ← заменили точечный фильтр на универсальный
dp.message.register(info.info, lambda m: m.text == "ℹ️ Информация")
dp.message.register(prompt.prompt_for_idea, lambda m: m.text == "🎨 Генерация логотипа")
dp.message.register(vectorize.ask_for_image, lambda m: m.text == "🖼 Векторизация")
dp.message.register(vectorize.handle_vectorization_image, is_vectorization_photo)
dp.message.register(generation.handle_idea, is_generate_text)
# выбор тарифа
dp.message.register(buy.buy_menu, lambda m: m.text and "Купить тариф" in m.text)
# конкретная покупка BASIC/PRO
dp.message.register(
    buy.handle_buy,
    lambda m: m.text and ("BASIC" in m.text or "PRO" in m.text)
)
# проверка оплаты
dp.message.register(check_payment_command, Command(commands=["check"]))

@dp.message()
async def fallback_handler(message):
    state = get_user_state(message.from_user.id)
    if state == STATE_MENU:
        await message.answer(
            "❗️Вы сейчас в главном меню. Пожалуйста, выберите действие кнопкой ниже."
        )
    elif state == STATE_GENERATE:
        await message.answer("❗️Ожидается текстовая идея логотипа.")
    elif state == STATE_VECTORIZE:
        await message.answer("❗️Ожидается изображение (фото) для векторизации.")
    else:
        await message.answer("❓ Непонятное состояние. Нажмите '⬅️ В меню'.")

if __name__ == "__main__":
    load_db()        # загрузка базы пользователей
    load_payments()  # загрузка ожидающих платежей
    asyncio.run(dp.start_polling(bot))
