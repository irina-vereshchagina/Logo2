import os
import base64
import requests
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

# === Флаги и ключи ===
USE_PLACEHOLDER = os.getenv("USE_PLACEHOLDER", "false").strip().lower() == "true"

# Ключ и базовый URL OpenRouter (приоритет у OpenRouter, иначе можно оставить OPENAI_API_KEY)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or ""
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip()

# Доп. заголовки (необязательно, но рекомендуются OpenRouter для аналитики)
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Logo2 Bot")

# Модели можно переопределить в .env
# для текста (рефайн промпта) и для картинок
TEXT_MODEL = os.getenv("OPENROUTER_TEXT_MODEL", "openai/gpt-4.1-mini")
IMAGE_MODEL = os.getenv("OPENROUTER_IMAGE_MODEL", "openai/gpt-image-1")


def _placeholder_image() -> BytesIO:
    """Картинка-заглушка, если ключей нет или включён режим разработки."""
    url = "https://placehold.co/1024x1024/png?text=Logo"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return BytesIO(resp.content)


async def generate_image(user_prompt: str) -> BytesIO:
    """
    Генерация изображения логотипа.
      • Если USE_PLACEHOLDER=true или нет ключа — вернёт плейсхолдер.
      • Иначе: 1) уточнит промпт через /v1/responses (TEXT_MODEL),
               2) сгенерирует картинку через Images API (IMAGE_MODEL).
    Возвращает BytesIO с PNG/JPEG.
    """
    if USE_PLACEHOLDER or not OPENROUTER_API_KEY:
        return _placeholder_image()

    from openai import OpenAI

    # Заголовки OpenRouter (опционально)
    default_headers = {}
    if OPENROUTER_SITE_URL:
        default_headers["HTTP-Referer"] = OPENROUTER_SITE_URL
    if OPENROUTER_APP_NAME:
        default_headers["X-Title"] = OPENROUTER_APP_NAME

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
        default_headers=default_headers or None,
    )

    # 1) Уточняем/сжимаем промпт (новый endpoint: /v1/responses)
    try:
        refine = client.responses.create(
            model=TEXT_MODEL,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise logo prompt refiner. "
                        "Return a short, English, single-sentence prompt for generating a logo. "
                        "No extra commentary."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
        )
        refined_prompt = (refine.output_text or "").strip() or user_prompt
    except Exception:
        refined_prompt = user_prompt

    # 2) Генерация изображения (Images API).
    # OpenRouter для openai-совместимых моделей отдаёт либо url, либо b64_json.
    try:
        img = client.images.generate(
            model=IMAGE_MODEL,
            prompt=refined_prompt,
            n=1,
            size="1024x1024",
        )
    except Exception:
        return _placeholder_image()

    data0 = img.data[0]

    # Вариант с URL
    if getattr(data0, "url", None):
        resp = requests.get(data0.url, timeout=60)
        resp.raise_for_status()
        return BytesIO(resp.content)

    # Вариант с base64
    b64 = getattr(data0, "b64_json", None)
    if b64:
        raw = base64.b64decode(b64)
        return BytesIO(raw)

    # На всякий случай — плейсхолдер
    return _placeholder_image()
