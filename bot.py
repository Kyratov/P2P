import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ===== КОНФИГ =====
BOT_TOKEN = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"
WEB_APP_URL = "https://kyratov.github.io/P2P/"

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


# ===== КЛАВИАТУРЫ =====
def main_menu():
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text="📈 Статистика", callback_data="stats"),
         InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        [InlineKeyboardButton(text="📎 Экспорт PDF", callback_data="export"),
         InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/KyratovVD")]
    ])


def back_button():
    """Кнопка назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
    ])


# ===== ПРИВЕТСТВИЕ (только при первом запуске) =====
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Проверяем, первый ли раз
    if not await is_first_visit(user_id):
        # Повторный вход — короткое меню
        await message.answer(
            "📊 P2P Tracker Pro\n\nВыбери действие:",
            reply_markup=main_menu()
        )
        return
    
    # Первый раз — приветствие
    await set_visited(user_id)
    await message.answer_photo(
        photo="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
        caption=f"""👋 Привет, {message.from_user.first_name}!

P2P Tracker Pro — учёт сделок с авторасчётом прибыли.

▸ Добавляй сделки
▸ Смотри график роста
▸ Экспортируй PDF

👇 Нажми кнопку, чтобы начать""",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Начать учёт", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
        ])
    )


# ===== ПРОСТАЯ БАЗА ДЛЯ ПЕРВЫХ ВИЗИТОВ =====
# (в реальном проекте замени на БД)
first_visits = set()

async def is_first_visit(user_id):
    return user_id not in first_visits

async def set_visited(user_id):
    first_visits.add(user_id)


# ===== КОМАНДА /help =====
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📋 Что умеет приложение?\n\n"
        "▸ Добавлять покупки и продажи USDT\n"
        "▸ Считать маржу и общую прибыль\n"
        "▸ Показывать график роста капитала\n"
        "▸ Искать сделки по истории\n"
        "▸ Экспортировать отчёты в PDF\n\n"
        "📊 Открой приложение и начни учёт",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
        ])
    )


# ===== СТАТИСТИКА =====
@dp.callback_query(F.data == "stats")
async def show_stats(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📈 Статистика доступна в приложении\n\n"
        "Открой трекер, чтобы увидеть:\n"
        "▸ Общую прибыль\n"
        "▸ График роста\n"
        "▸ Количество сделок\n"
        "▸ Среднюю маржу",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
        ])
    )
    await callback.answer()


# ===== ЭКСПОРТ PDF =====
@dp.callback_query(F.data == "export")
async def show_export(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📎 Как скачать PDF-отчёт\n\n"
        "1. Открой приложение\n"
        "2. Перейди в раздел «Прочее»\n"
        "3. Нажми «Скачать PDF»\n\n"
        "Отчёт сохранится на телефон",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
        ])
    )
    await callback.answer()


# ===== ПОМОЩЬ (callback) =====
@dp.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📋 Что умеет приложение?\n\n"
        "▸ Добавлять покупки и продажи USDT\n"
        "▸ Считать маржу и общую прибыль\n"
        "▸ Показывать график роста капитала\n"
        "▸ Искать сделки по истории\n"
        "▸ Экспортировать отчёты в PDF\n\n"
        "📊 Открой приложение и начни учёт",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_main")]
        ])
    )
    await callback.answer()


# ===== КНОПКА НАЗАД =====
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📊 P2P Tracker Pro\n\nВыбери действие:",
        reply_markup=main_menu()
    )
    await callback.answer()


# ===== НЕИЗВЕСТНЫЕ СООБЩЕНИЯ =====
@dp.message()
async def unknown_message(message: types.Message):
    await message.answer(
        "❓ Неизвестная команда\n\n"
        "Используй /start или кнопки меню",
        reply_markap=main_menu()
    )


# ===== КОМАНДЫ ДЛЯ МЕНЮ БОТА =====
async def set_commands():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="Главное меню"),
    ])


# ===== ЗАПУСК =====
async def main():
    await set_commands()
    print("🤖 Бот запущен!")
    print(f"📱 Mini App: {WEB_APP_URL}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())