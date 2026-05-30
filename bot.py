import asyncio
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
import asyncpg

# ===== КОНФИГУРАЦИЯ =====
BOT_TOKEN = "8824407853:AAHq_BcojLt6FnzKdLgdd6LnuGySb6M2His"
WEB_APP_URL = "https://kyratov.github.io/P2P/"  # Твоя ссылка на Mini App

# Данные для подключения к PostgreSQL (из bothost)
DB_HOST = "node1.pghost.ru"
DB_PORT = "15736"
DB_NAME = "bothost_db_821628b3592e"
DB_USER = "bothost_db_821628b3592e"
DB_PASS = "5SUexoM1XABN7JOEIId61G1R2uGQ6btC8ow-53G-HNnM"  # Твой пароль

# ===== ИНИЦИАЛИЗАЦИЯ =====
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Глобальный пул подключений к БД
db_pool = None


# ===== РАБОТА С БАЗОЙ ДАННЫХ =====
async def init_db():
    """Создаёт пул подключений и таблицы"""
    global db_pool
    db_pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        min_size=1,
        max_size=10
    )
    
    # Создаём таблицу для сделок
    async with db_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                deal_id BIGINT NOT NULL,
                type VARCHAR(10) NOT NULL,
                amount_paid DECIMAL(15,2) NOT NULL,
                usdt_amount DECIMAL(15,2) NOT NULL,
                price_per_usdt DECIMAL(15,2),
                counterparty TEXT,
                deal_number TEXT,
                comment TEXT,
                custom_date TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        # Индекс для быстрого поиска
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_deals_user_id ON deals(user_id)
        ''')
        
        # Уникальный индекс для deal_id (чтобы не было дублей)
        await conn.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_deals_unique ON deals(user_id, deal_id)
        ''')
    
    print("✅ База данных подключена, таблицы готовы")


async def save_deals_to_db(user_id: int, deals: list):
    """Сохраняет все сделки пользователя в БД (синхронизация)"""
    async with db_pool.acquire() as conn:
        # Сначала удаляем старые сделки пользователя
        await conn.execute('DELETE FROM deals WHERE user_id = $1', user_id)
        
        # Сохраняем новые
        for deal in deals:
            await conn.execute('''
                INSERT INTO deals (user_id, deal_id, type, amount_paid, usdt_amount, 
                                   price_per_usdt, counterparty, deal_number, comment, custom_date)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ''', user_id, deal.get('id'), deal.get('type'), deal.get('amountPaid'),
                deal.get('usdtAmount'), deal.get('pricePerUsdt'), deal.get('counterparty'),
                deal.get('dealNumber'), deal.get('comment'), deal.get('customDate'))
    
    print(f"✅ Сохранено {len(deals)} сделок для user_id={user_id}")


async def load_deals_from_db(user_id: int) -> list:
    """Загружает сделки пользователя из БД"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT deal_id as id, type, amount_paid as "amountPaid", 
                   usdt_amount as "usdtAmount", price_per_usdt as "pricePerUsdt",
                   counterparty, deal_number as "dealNumber", comment, custom_date as "customDate"
            FROM deals 
            WHERE user_id = $1 
            ORDER BY created_at DESC
        ''', user_id)
        
        deals = []
        for row in rows:
            deals.append({
                'id': row['id'],
                'type': row['type'],
                'amountPaid': float(row['amountPaid']),
                'usdtAmount': float(row['usdtAmount']),
                'pricePerUsdt': float(row['pricePerUsdt']) if row['pricePerUsdt'] else None,
                'counterparty': row['counterparty'],
                'dealNumber': row['dealNumber'],
                'comment': row['comment'],
                'customDate': row['customDate']
            })
        
        print(f"📥 Загружено {len(deals)} сделок для user_id={user_id}")
        return deals


# ===== КЛАВИАТУРЫ =====
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 ОТКРЫТЬ ПРИЛОЖЕНИЕ", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text="📈 Мои сделки", callback_data="stats"),
         InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
        [InlineKeyboardButton(text="🔄 Синхронизация", callback_data="sync"),
         InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/KyratovVD")]
    ])


def back_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])


def back_with_open_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Открыть приложение", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_main")]
    ])


# ===== ОБРАБОТЧИКИ КОМАНД =====
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "друг"
    
    # Проверяем, есть ли у пользователя сохранённые сделки
    deals = await load_deals_from_db(user_id)
    
    if len(deals) == 0:
        # Новый пользователь
        await message.answer_photo(
            photo="https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
            caption=f"👋 Привет, {name}!\n\n"
                    f"📊 P2P Tracker Pro — считай прибыль от сделок.\n\n"
                    f"▸ Добавляй покупки и продажи USDT\n"
                    f"▸ Смотри график роста капитала\n"
                    f"▸ Синхронизация между устройствами\n\n"
                    f"👇 Нажми кнопку, чтобы начать",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 НАЧАТЬ УЧЁТ", web_app=WebAppInfo(url=WEB_APP_URL))],
                [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
            ])
        )
    else:
        # Пользователь с сохранёнными сделками
        total_buy = sum(d['amountPaid'] for d in deals if d['type'] == 'buy')
        total_sell = sum(d['amountPaid'] for d in deals if d['type'] == 'sell')
        total_deals = len(deals)
        
        await message.answer(
            f"📊 С возвращением, {name}!\n\n"
            f"📝 Всего сделок: {total_deals}\n"
            f"💰 Сумма покупок: {total_buy:.2f} ₽\n"
            f"💸 Сумма продаж: {total_sell:.2f} ₽\n\n"
            f"Выбери действие:",
            reply_markup=main_keyboard()
        )


# ===== ОБРАБОТКА ДАННЫХ ИЗ MINI APP =====
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    """Принимает данные из Mini App и сохраняет в БД"""
    user_id = message.from_user.id
    
    try:
        # Получаем данные из Web App
        data = json.loads(message.web_app_data.data)
        deals = data.get('deals', [])
        
        # Сохраняем в базу данных
        await save_deals_to_db(user_id, deals)
        
        await message.answer(
            f"✅ Синхронизация выполнена!\n"
            f"📊 Сохранено {len(deals)} сделок.\n\n"
            f"Теперь твои данные доступны на всех устройствах.",
            reply_markup=main_keyboard()
        )
    except Exception as e:
        print(f"Ошибка синхронизации: {e}")
        await message.answer(
            "❌ Ошибка синхронизации. Попробуй ещё раз.",
            reply_markup=main_keyboard()
        )


# ===== CALLBACK ОБРАБОТЧИКИ =====
@dp.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "❓ ЧТО УМЕЕТ ПРИЛОЖЕНИЕ\n\n"
        "▸ Добавлять покупки и продажи USDT\n"
        "▸ Автоматически считать маржу\n"
        "▸ Показывать общую прибыль\n"
        "▸ Строить график роста капитала\n"
        "▸ Искать сделки по истории\n"
        "▸ Экспортировать отчёты в PDF/Excel\n"
        "▸ Синхронизация между устройствами\n\n"
        "📊 Все данные хранятся в облаке и на твоём телефоне",
        reply_markup=back_with_open_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "stats")
async def show_stats(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    deals = await load_deals_from_db(user_id)
    
    if not deals:
        await callback.message.edit_text(
            "📈 У вас пока нет сделок.\n\n"
            "Откройте приложение и добавьте первую сделку!",
            reply_markup=back_with_open_keyboard()
        )
        await callback.answer()
        return
    
    total_buy = sum(d['amountPaid'] for d in deals if d['type'] == 'buy')
    total_sell = sum(d['amountPaid'] for d in deals if d['type'] == 'sell')
    total_buy_usdt = sum(d['usdtAmount'] for d in deals if d['type'] == 'buy')
    total_sell_usdt = sum(d['usdtAmount'] for d in deals if d['type'] == 'sell')
    profit = total_sell - total_buy
    
    await callback.message.edit_text(
        f"📈 МОЯ СТАТИСТИКА\n\n"
        f"📝 Всего сделок: {len(deals)}\n"
        f"🟢 Покупок: {len([d for d in deals if d['type'] == 'buy'])}\n"
        f"🔴 Продаж: {len([d for d in deals if d['type'] == 'sell'])}\n\n"
        f"💰 Сумма покупок: {total_buy:.2f} ₽\n"
        f"💸 Сумма продаж: {total_sell:.2f} ₽\n"
        f"📊 Объём покупок: {total_buy_usdt:.2f} USDT\n"
        f"📉 Объём продаж: {total_sell_usdt:.2f} USDT\n\n"
        f"🏆 Прибыль: {profit:.2f} ₽",
        reply_markup=back_with_open_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "sync")
async def show_sync_info(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔄 СИНХРОНИЗАЦИЯ\n\n"
        "Твои сделки автоматически сохраняются в облаке.\n\n"
        "Чтобы синхронизировать данные между устройствами:\n"
        "1️⃣ Открой приложение на новом устройстве\n"
        "2️⃣ Нажми кнопку «Открыть приложение»\n"
        "3️⃣ Данные загрузятся автоматически\n\n"
        "📌 Все изменения сохраняются мгновенно!",
        reply_markup=back_with_open_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "back_main")
async def back_to_main(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    deals = await load_deals_from_db(user_id)
    total_deals = len(deals)
    total_buy = sum(d['amountPaid'] for d in deals if d['type'] == 'buy')
    total_sell = sum(d['amountPaid'] for d in deals if d['type'] == 'sell')
    
    await callback.message.edit_text(
        f"📊 P2P Tracker Pro\n\n"
        f"📝 Сделок: {total_deals}\n"
        f"💰 Покупки: {total_buy:.2f} ₽\n"
        f"💸 Продажи: {total_sell:.2f} ₽\n\n"
        f"Выбери действие:",
        reply_markup=main_keyboard()
    )
    await callback.answer()


@dp.message()
async def unknown_message(message: types.Message):
    await message.answer(
        "❓ Неизвестная команда\n\nНажми /start или используй кнопки меню",
        reply_markup=main_keyboard()
    )


async def set_bot_commands():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="📊 Главное меню"),
    ])


# ===== ЗАПУСК БОТА =====
async def main():
    # Инициализируем базу данных
    await init_db()
    
    # Устанавливаем команды
    await set_bot_commands()
    
    print("✅ Бот P2P Tracker Pro запущен!")
    print(f"📱 Mini App: {WEB_APP_URL}")
    print(f"🗄️ База данных: {DB_NAME}")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())