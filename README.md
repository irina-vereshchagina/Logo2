# Logo2


🚀 Как запустить проект локально
1️⃣ Установи Python и клонируй репозиторий
Открой терминал и выполни:
# если Python ещё не установлен — скачай 3.11+ с python.org
git clone https://github.com/irina-vereshchagina/Logo2.git
cd Logo2
💡 Проверь:
python --version
должно быть Python 3.11 или 3.12
2️⃣ Создай и активируй виртуальное окружение
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate
3️⃣ Установи зависимости
Если есть requirements.txt — выполни:
pip install -r requirements.txt
Если файла нет — установи вручную нужные пакеты (для aiogram и YooKassa):
pip install aiogram==3.3.0 python-dotenv yookassa requests
4️⃣ Создай файл .env
В корне проекта (Logo2/) создай файл .env со следующими строками:
# токен твоего телеграм-бота
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNopQRstuVWxyz

# ключи YooKassa (можно оставить заглушки, если не тестируешь оплату)
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# API-ключ OpenAI (если используешь генерацию)
OPENAI_API_KEY=your_openai_key

# можно оставить, если хочешь тестировать без OpenAI
USE_PLACEHOLDER=true
⚠️ Важное: если ключи YooKassa не заданы — бот выдаст ошибку
"YOOKASSA_SHOP_ID / YOOKASSA_SECRET_KEY не заданы".
Для теста можно временно закомментировать raise в services/payment_service.py.
5️⃣ Запусти бота
python bot.py
После запуска ты должен увидеть в консоли что-то вроде:
INFO:aiogram.event:Polling started
Теперь в Telegram открой своего бота и проверь /start.
6️⃣ Проверка “Назад” и меню
✅ /start — показывает 4 кнопки
✅ “💰 Купить тариф” — открывает меню с тарифами
✅ “⬅️ В меню” — возвращает в главное меню
✅ “✅ Я оплатил” — проверяет статус платежа (если есть реальные ключи)
7️⃣ (опционально) — автоперезапуск при изменениях
Чтобы не перезапускать вручную при изменении кода:
pip install watchdog
watchmedo auto-restart -d . -p "*.py" -- python bot.py
