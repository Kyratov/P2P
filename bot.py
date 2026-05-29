import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, FSInputFile
from aiogram.utils.markdown import hbold, hitalic

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = "8824407853:AAHq_BcojLt6FnzKdLgdd6LnuGySb6M2His"  # Вставь сюда свой токен!
WEB_APP_URL = "https://kyratov.github.io/P2P/"  # Твоя ссылка на Mini App

# Создаём бота и диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Папка для логов (если нужно)
os.makedirs("logs", exist_ok=True)


# ===== КОМАНДА /start =====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name or "друг"
    
    # Красивая клавиатура с кнопкой Mini App
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📊 Открыть приложение", 
            web_app=WebAppInfo(url=WEB_APP_URL)
        )],
        [
            InlineKeyboardButton(text="📖 Гид", callback_data="guide"),
            InlineKeyboardButton(text="📈 Моя статистика", callback_data="stats")
        ],
        [
            InlineKeyboardButton(text="🛟 Поддержка", url="https://t.me/KyratovVD"),
            InlineKeyboardButton(text="📎 Экспорт PDF", callback_data="export_guide")
        ]
    ])
    
    await message.answer_photo(
        photo="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
        caption=f"""👋 *Привет, {user_name}!*

📊 *P2P Tracker Pro* — твой умный помощник для учёта сделок

✨ *Что умеет приложение:*
• 💰 Автоматический расчёт прибыли и маржи
• 📈 График роста капитала
• 🔍 История с поиском и фильтрами
• 📎 Экспорт отчётов в PDF
• 🌙 Тёмная тема

👇 *Нажми на кнопку ниже, чтобы начать учёт!*

➖➖➖➖➖➖➖➖➖➖
💡 *Совет:* Записывай каждую сделку — так ты увидишь реальную прибыль!
""",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ===== КОМАНДА /help =====
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        f"""📖 *Гид по P2P Tracker Pro*

*1️⃣ Главный экран*
Прибыль, курсы валют, статистика и график роста

*2️⃣ Создать сделку*
Укажи тип (покупка/продажа), сумму в ₽, количество USDT и цену

*3️⃣ История сделок*
Все твои сделки с поиском и фильтрами

*4️⃣ Калькулятор*
Конвертируй RUB → USDT по своему курсу

*5️⃣ Прочее*
• PDF отчёт — скачай историю
• Гид — повторное обучение
• Поддержка — связь с разработчиком

➖➖➖➖➖➖➖➖➖➖
❓ *Вопросы?* Пиши в поддержку: @KyratovVD
""",
        parse_mode="Markdown"
    )


# ===== ОБРАБОТКА КНОПОК (callback) =====
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    user_name = callback.from_user.first_name or "пользователь"
    
    if callback.data == "guide":
        await callback.message.answer(
            f"""📖 *Гид по приложению*

👋 *Привет, {user_name}!*

🗺 *Навигация:*
• *Главная* — твоя прибыль, курсы валют, график
• *Создать* — добавь новую сделку
• *История* — ищи и фильтруй сделки
• *Калькулятор* — конвертируй RUB в USDT
• *Прочее* — экспорт PDF, гид, поддержка

📈 *Совет:* Регулярно записывай сделки — увидишь реальную картину!

🔧 *Нужна помощь?* @KyratovVD
""",
            parse_mode="Markdown"
        )
        await callback.answer()
    
    elif callback.data == "stats":
        # Здесь можно добавить статистику из базы данных
        # Пока отправляем заглушку
        await callback.message.answer(
            f"""📊 *Твоя статистика*

📝 *Всего сделок:* — (открой приложение, чтобы увидеть)

💡 *Совет:* Открой приложение и добавь первые сделки!
Статистика появится автоматически.

👇 *Нажми кнопку ниже, чтобы открыть трекер*
""",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))]
            ])
        )
        await callback.answer()
    
    elif callback.data == "export_guide":
        await callback.message.answer(
            f"""📎 *Как экспортировать PDF отчёт*

1️⃣ Открой приложение через кнопку ниже
2️⃣ Перейди во вкладку *«Прочее»*
3️⃣ Нажми *«Скачать PDF»*
4️⃣ Готово! Отчёт сохранится на твой телефон

📄 В отчёт входят:
• Все сделки с датами
• Суммы в ₽ и USDT
• Итоговая прибыль

👇 *Открыть приложение*
""",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))]
            ])
        )
        await callback.answer()
    
    else:
        await callback.answer("⚡ Действие в разработке!")


# ===== КОМАНДА /about (о проекте) =====
@dp.message(Command("about"))
async def cmd_about(message: types.Message):
    await message.answer(
        f"""ℹ️ *О проекте*

*P2P Tracker Pro* — это твой личный помощник для учёта P2P сделок.

*Разработчик:* @KyratovVD
*Версия:* 2.0.0

*Функции:*
✅ Авторасчёт прибыли
✅ График роста капитала
✅ История с поиском
✅ Экспорт PDF
✅ Тёмная тема

*Технологии:* Telegram Mini App, HTML/CSS/JS, aiogram 3.x

📱 *Приложение работает полностью офлайн — твои данные в безопасности!*
""",
        parse_mode="Markdown"
    )


# ===== КОМАНДА /feedback (обратная связь) =====
@dp.message(Command("feedback"))
async def cmd_feedback(message: types.Message):
    await message.answer(
        f"""💬 *Обратная связь*

У тебя есть идеи или нашёл баг?

✍️ Напиши нам в поддержку:
👉 @KyratovVD

📝 *Что можно написать:*
• Предложения по новым функциям
• Сообщения об ошибках
• Вопросы по использованию

Спасибо, что помогаешь делать приложение лучше! 🙏
""",
        parse_mode="Markdown"
    )


# ===== ОБРАБОТКА НЕИЗВЕСТНЫХ СООБЩЕНИЙ =====
@dp.message()
async def handle_unknown(message: types.Message):
    await message.answer(
        f"""🤖 *Я умный бот, но не понимаю эту команду*

Используй кнопки меню или команды:

/start — Главное меню
/help — Помощь и гид
/about — О проекте
/feedback — Обратная связь

👇 *Или просто нажми на кнопку ниже, чтобы открыть приложение!*""",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))]
        ])
    )


# ===== ЗАПУСК БОТА =====
async def main():
    print("🤖 Бот P2P Tracker Pro запущен!")
    print(f"📊 Mini App URL: {WEB_APP_URL}")
    print("✅ Бот готов к работе!")
    
    # Устанавливаем команды для меню бота
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🚀 Главное меню"),
        types.BotCommand(command="help", description="📖 Помощь и гид"),
        types.BotCommand(command="about", description="ℹ️ О проекте"),
        types.BotCommand(command="feedback", description="💬 Обратная связь"),
    ])
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())