# keyboards/inline_keyboards.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu():
    """Главное меню бота."""
    keyboard = [
        [InlineKeyboardButton("📚 Теоретический материал", callback_data='theory')],
        [InlineKeyboardButton("📝 Формулы", callback_data='formulas')],
        [InlineKeyboardButton("🔢 Решение задач", callback_data='problems')],
        [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')],
        [InlineKeyboardButton("❓ Помощь и поддержка", callback_data='help')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_sections_menu(sections, back_callback='main'):
    """Меню выбора разделов (общее)."""
    keyboard = []
    for section in sections:
        keyboard.append([InlineKeyboardButton(section, callback_data=f'section_{section}')])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=back_callback)])
    return InlineKeyboardMarkup(keyboard)


def get_theory_topics_menu(topics, section, back_callback='theory_back'):
    """Меню выбора тем теории."""
    keyboard = []
    for i, topic in enumerate(topics):
        keyboard.append([InlineKeyboardButton(
            topic['title'],
            callback_data=f'topic_{section}_{i}'
        )])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=back_callback)])
    return InlineKeyboardMarkup(keyboard)


def get_formulas_sections_menu(sections, back_callback='main'):
    """Меню выбора разделов формул."""
    keyboard = []
    for section in sections:
        keyboard.append([InlineKeyboardButton(
            section,
            callback_data=f'formulas_section_{section}'
        )])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=back_callback)])
    return InlineKeyboardMarkup(keyboard)


def get_problems_sections_menu(sections, back_callback='main'):
    """Меню выбора разделов задач."""
    keyboard = []
    for section in sections:
        keyboard.append([InlineKeyboardButton(
            section,
            callback_data=f'problems_section_{section}'
        )])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data=back_callback)])
    return InlineKeyboardMarkup(keyboard)