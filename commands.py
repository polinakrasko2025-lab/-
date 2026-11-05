# handlers/commands.py
from telegram import Update
from telegram.ext import ContextTypes
import database as db


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    user = update.effective_user
    db.get_or_create_user(user.id, user.username or '', user.first_name or '')

    welcome_text = """
    🎓 *Добро пожаловать в Физика PRO100!*

    *Возможности бота:*
    📚 Теоретический материал по всем разделам
    📝 Формулы с подробным описанием
    🔢 Адаптивное решение задач — сложность подстраивается под вас
    👤 Личный профиль с баллами и слабыми темами
    ❓ Помощь и поддержка

    *Система баллов:*
    🟢 Лёгкая задача — +5 баллов
    🟡 Средняя задача — +10 баллов
    🔴 Сложная задача — +20 баллов
    ❌ Неправильный ответ — −3 балла
    """

    from keyboards.inline_keyboards import get_main_menu
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode='Markdown'
    )