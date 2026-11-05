# handlers/profile.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import database as db


async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать профиль (из кнопки меню)."""
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    db.get_or_create_user(user.id, user.username or '', user.first_name or '')
    await _render(update)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /profile."""
    user = update.effective_user
    db.get_or_create_user(user.id, user.username or '', user.first_name or '')
    user_data = db.get_user(user.id)
    weak = db.get_weak_sections(user.id)
    top = db.get_top_sections(user.id)
    text, keyboard = _build_profile_text(user_data, weak, top)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')


async def _render(update: Update):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    weak = db.get_weak_sections(user_id)
    top = db.get_top_sections(user_id)
    text, keyboard = _build_profile_text(user_data, weak, top)
    await update.callback_query.edit_message_text(
        text, reply_markup=keyboard, parse_mode='Markdown'
    )


def _build_profile_text(user, weak, top):
    name = user['first_name'] or user['username'] or "Пользователь"
    total = user['total_correct'] + user['total_wrong']
    accuracy = (user['total_correct'] / total * 100) if total > 0 else 0.0

    text = f"👤 *Профиль: {name}*\n\n"
    text += f"💰 Баллы: *{user['points']}*\n"
    text += f"✅ Верных ответов: {user['total_correct']}\n"
    text += f"❌ Ошибок: {user['total_wrong']}\n"
    text += f"🎯 Точность: {accuracy:.1f}%\n"

    if weak:
        text += "\n⚠️ *Что стоит подтянуть:*\n"
        for w in weak[:5]:
            text += f"• *{w['section']}* — ошибок {w['wrong']}, верных {w['correct']}\n"
    else:
        text += "\n✨ Слабых тем не найдено — так держать!\n"

    if top:
        text += "\n🏆 *Сильные темы:*\n"
        for t in top:
            text += f"• {t['section']} ({t['correct']} верных)\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Сбросить прогресс", callback_data='reset_progress')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main')]
    ])
    return text, keyboard


async def reset_progress_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Прогресс сброшен")
    db.reset_user_progress(update.effective_user.id)
    await _render(update)