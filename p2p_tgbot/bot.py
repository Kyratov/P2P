import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

# === КОНФИГУРАЦИЯ ===
BOT_TOKEN = "8824407853:AAHq_BcojLt6FnzKdLgdd6LnuGySb6M2His"  # Замени на свой токен
WEBAPP_URL = "https://p2-p-sand.vercel.app/"  # URL твоего Mini App

# === ИНИЦИАЛИЗАЦИЯ ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === КОМАНДА /start ===
@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Создаём клавиатуру с WebApp кнопкой
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🚀 Открыть P2P трекер",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )],
        [InlineKeyboardButton(
            text="📊 Моя статистика",
            callback_data="my_stats"
        )],
        [InlineKeyboardButton(
            text="❓ Помощь",
            callback_data="help"
        )]
    ])
    
    await message.answer(
        "📊 *P2P Tracker Pro*\n\n"
        "Добро пожаловать в умный учёт P2P сделок!\n\n"
        "✅ Автоматический расчёт прибыли\n"
        "✅ Курсы валют в реальном времени\n"
        "✅ История сделок с поиском\n\n"
        "👇 *Нажми на кнопку ниже, чтобы открыть приложение*",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# === КОМАНДА /stats ===
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📊 Открыть статистику",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "📈 *Ваша статистика P2P*\n\n"
        "Для просмотра подробной статистики откройте приложение:\n"
        "• Общая прибыль\n"
        "• Куплено/продано USDT\n"
        "• Остаток в кошельке\n"
        "• История всех сделок",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# === КОМАНДА /help ===
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "❓ *Помощь по P2P Tracker Pro*\n\n"
        "📌 *Основные функции:*\n"
        "• Добавление сделок (покупка/продажа)\n"
        "• Автоматический расчёт прибыли\n"
        "• Отслеживание курсов USD, EUR, CNY\n"
        "• Поиск и фильтрация сделок\n\n"
        "📌 *Как добавить сделку:*\n"
        "1. Нажми 'Создать'\n"
        "2. Укажи тип операции\n"
        "3. Введи сумму, количество и цену\n"
        "4. Добавь контрагента и номер сделки\n\n"
        "📌 *Вопросы и предложения:*\n"
        "👤 @KyratovVD",
        parse_mode="Markdown"
    )

# === ОБРАБОТКА CALLBACK ===
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    if callback.data == "my_stats":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📊 Открыть статистику",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )]
        ])
        await callback.message.edit_text(
            "📊 *Ваша статистика*\n\n"
            "Откройте приложение для детального просмотра:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    elif callback.data == "help":
        await callback.message.edit_text(
            "❓ *Помощь*\n\n"
            "📌 *Как добавить сделку:*\n"
            "1. Нажми 'Создать'\n"
            "2. Укажи тип операции\n"
            "3. Введи сумму и количество USDT\n"
            "4. Укажи цену за 1 USDT\n\n"
            "📌 *Вопросы:* @KyratovVD",
            parse_mode="Markdown"
        )
    
    await callback.answer()

# === ЗАПУСК БОТА ===
async def main():
    logging.basicConfig(level=logging.INFO)
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())