# handlers/help_handler.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь из главного меню."""
    query = update.callback_query
    await query.answer()

    help_text = """
    🤖 *Физика PRO100 - Помощь*

    *Основные возможности бота:*

    📚 *Теоретический материал*
    • Полная теория по всем разделам физики
    • Структурировано по темам
    • Ключевые формулы в каждой теме

    📝 *Формулы*
    • Сборник всех основных формул
    • Подробные объяснения каждой формулы
    • Разделено по темам для удобства

    🔢 *Решение задач (адаптивное)*
    • Задачи подбираются под ваш уровень
    • 4 варианта ответа к каждой задаче
    • Сложность растёт при правильных ответах
    • Сложность снижается при ошибках

    👤 *Личный профиль*
    • Баланс баллов
    • Список слабых тем
    • Точность ответов

    *Система баллов:*
    🟢 Лёгкая задача: +5 баллов
    🟡 Средняя задача: +10 баллов
    🔴 Сложная задача: +20 баллов
    ❌ Ошибка: −3 балла

    *Основные команды:*
    /start — Начать работу с ботом
    /help — Показать это сообщение
    /profile — Личный профиль и баллы

    *Как пользоваться ботом:*
    1. Нажмите /start для начала работы
    2. Выберите нужный раздел в меню
    3. Переходите по разделам и темам
    4. Используйте кнопку "Назад" для возврата
    """

    keyboard = [
        [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')],
        [InlineKeyboardButton("❓ Часто задаваемые вопросы", callback_data='faq')],
        [InlineKeyboardButton("📞 Связь с разработчиком", callback_data='contact')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main')]
    ]

    await query.edit_message_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help."""
    help_text = """
    *Физика PRO100 - Команды и помощь*

    *Доступные команды:*
    /start — Запустить бота и показать главное меню
    /help — Показать это сообщение справки
    /profile — Личный профиль (баллы, слабые темы)

    *Основные разделы бота:*
    • Теория — теоретический материал по всем темам
    • Формулы — сборник формул с пояснениями
    • Задачи — адаптивные задачи с вариантами ответов
    • Профиль — личные баллы и статистика

    *Советы по подготовке к экзамену:*
    1. Начинайте с теоретического материала
    2. Изучайте формулы с пониманием
    3. Решайте задачи от простых к сложным
    4. Следите за слабыми темами в профиле
    """

    keyboard = [
        [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')],
        [InlineKeyboardButton("❓ Часто задаваемые вопросы", callback_data='faq')],
        [InlineKeyboardButton("📞 Связь с разработчиком", callback_data='contact')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main')]
    ]

    await update.message.reply_text(
        help_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def faq_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """FAQ."""
    query = update.callback_query
    await query.answer()

    faq_text = """
    ❓ *Часто задаваемые вопросы*

    *Q: Как работает адаптивная сложность?*
    A: Задачи подбираются автоматически. Решите 2 задачи подряд правильно — сложность повысится. Ошибётесь — понизится.

    *Q: Сколько баллов я могу получить?*
    A: 🟢 за лёгкую +5, 🟡 за среднюю +10, 🔴 за сложную +20 баллов.

    *Q: За что снимаются баллы?*
    A: За неправильный ответ −3 балла. Баланс не уходит в минус.

    *Q: Как посмотреть слабые темы?*
    A: Нажмите /profile или кнопку "Мой профиль".

    *Q: Бот бесплатный?*
    A: Да, полностью бесплатный.

    *Q: Как сообщить об ошибке?*
    A: Через кнопку "Связь с разработчиком".
    """

    keyboard = [
        [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')],
        [InlineKeyboardButton("🔙 Назад", callback_data='help')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main')]
    ]

    await query.edit_message_text(
        faq_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def contact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Связь с разработчиком."""
    query = update.callback_query
    await query.answer()

    contact_text = """
    📞 *Связь с разработчиком*

    Если вы нашли ошибку, у вас есть предложения или вопросы:

    *Email:* polinakrasko2025@gmail.com
    *Telegram:* @Mjoer

    *Что сообщать при обращении:*
    1. Ваш username в Telegram
    2. Описание проблемы
    3. Шаги для воспроизведения ошибки
    4. Скриншоты (если есть)

    *Время ответа:* 1-2 рабочих дня

    Спасибо за обратную связь! ✨
    """

    keyboard = [
        [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')],
        [InlineKeyboardButton("🔙 Назад в помощь", callback_data='help')],
        [InlineKeyboardButton("🏠 Главное меню", callback_data='main')]
    ]

    await query.edit_message_text(
        contact_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )