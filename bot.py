import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage

# ===== КОНФИГ =====
BOT_TOKEN = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"
WEB_APP_URL = "https://kyratov.github.io/P2P/"

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# База для первых визитов (в продакшене замени на БД)
first_visits = set()


# ===== КЛАВИАТУРЫ (дизайн) =====

def main_keyboard():
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 ОТКРЫТЬ ПРИЛОЖЕНИЕ", web_app=WebAppInfo(url=WEB_APP_URL))],
        [
            InlineKeyboardButton(text="📈 Мои сделки", callback_data="stats"),
            InlineKeyboardButton(text="❓ Помощь", callback_data="help")
        ],
        [
            InlineKeyboardButton(text="📎 Экспорт PDF", callback_data="export"),
            InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/KyratovVD")
        ]
    ])


def back_keyboard(to="main"):
    """Универсальная кнопка назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data=f"back_{to}")]
    ])


def back_with_open_keyboard():
    """Назад + кнопка открыть приложение"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])


# ===== ПРИВЕТСТВИЕ (только первый раз) =====

async def is_first_visit(user_id: int) -> bool:
    return user_id not in first_visits

async def mark_visited(user_id: int):
    first_visits.add(user_id)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "друг"
    
    if await is_first_visit(user_id):
        await mark_visited(user_id)
        # Первый раз — развёрнутое приветствие
        await message.answer_photo(
            photo="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
            caption=f"👋 Привет, {name}!\n\n"
                    f"P2P Tracker Pro — считай прибыль от сделок.\n\n"
                    f"▸ Добавляй покупки и продажи USDT\n"
                    f"▸ Смотри график роста капитала\n"
                    f"▸ Экспортируй отчёты в PDF\n\n"
                    f"👇 Нажми кнопку, чтобы начать",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 НАЧАТЬ УЧЁТ", web_app=WebAppInfo(url=WEB_APP_URL))],
                [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
            ])
        )
    else:
        # Повторный вход — краткое меню
        await message.answer(
            f"📊 С возвращением, {name}!\n\nВыбери действие:",
            reply_markup=main_keyboard()
        )


# ===== ПОМОЩЬ =====

@dp.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "❓ ЧТО УМЕЕТ ПРИЛОЖЕНИЕ\n\n"
        "▸ Добавлять покупки и продажи USDT\n"
        "▸ Автоматически считать маржу\n"
        "▸ Показывать общую прибыль\n"
        "▸ Строить график роста капитала\n"
        "▸ Искать сделки по истории\n"
        "▸ Экспортировать отчёты в PDF\n\n"
        "📊 Все данные хранятся на твоём телефоне",
        reply_markup=back_with_open_keyboard()
    )
    await callback.answer()


# ===== СТАТИСТИКА =====

@dp.callback_query(F.data == "stats")
async def show_stats(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📈 МОЯ СТАТИСТИКА\n\n"
        "Вся аналитика доступна в приложении:\n"
        "▸ Общая прибыль\n"
        "▸ График роста капитала\n"
        "▸ Количество сделок\n"
        "▸ Средняя маржа\n"
        "▸ Лучший метод оплаты\n\n"
        "📊 Открой приложение, чтобы увидеть цифры",
        reply_markup=back_with_open_keyboard()
    )
    await callback.answer()


# ===== ЭКСПОРТ PDF =====

@dp.callback_query(F.data == "export")
async def show_export(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📎 КАК СКАЧАТЬ PDF\n\n"
        "1️⃣ Открой приложение\n"
        "2️⃣ Перейди в раздел «Прочее»\n"
        "3️⃣ Нажми «Скачать PDF»\n\n"
        "📄 Отчёт сохранится на твой телефон.\n"
        "В нём будут все сделки и итоговая прибыль.",
        reply_markup=back_with_open_keyboard()
    )
    await callback.answer()


# ===== КНОПКИ НАЗАД =====

@dp.callback_query(F.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📊 P2P Tracker Pro\n\nВыбери действие:",
        reply_markup=main_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "back_help")
async def back_to_help(callback: types.CallbackQuery):
    await show_help(callback)


@dp.callback_query(F.data == "back_stats")
async def back_to_stats(callback: types.CallbackQuery):
    await show_stats(callback)


@dp.callback_query(F.data == "back_export")
async def back_to_export(callback: types.CallbackQuery):
    await show_export(callback)


# ===== НЕИЗВЕСТНЫЕ СООБЩЕНИЯ =====

@dp.message()
async def unknown_message(message: types.Message):
    await message.answer(
        "❓ Неизвестная команда\n\nНажми /start или используй кнопки меню",
        reply_markup=main_keyboard()
    )


# ===== КОМАНДЫ БОТА =====

async def set_bot_commands():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="📊 Главное меню"),
    ])


# ===== ЗАПУСК =====

async def main():
    await set_bot_commands()
    print("✅ Бот P2P Tracker Pro запущен!")
    print(f"📱 Mini App: {WEB_APP_URL}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())