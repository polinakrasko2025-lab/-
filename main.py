# main.py
import logging
import warnings
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TOKEN
import database as db

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Игнорируем предупреждение о pkg_resources
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")


async def handle_text_messages(update: Update, context):
    """Обработка текстовых сообщений."""
    text = update.message.text.lower()

    if any(word in text for word in ['привет', 'hello', 'hi', 'start']):
        await update.message.reply_text(
            "👋 Привет! Используйте /start для начала работы или /help для помощи."
        )
    elif any(word in text for word in ['спасибо', 'thanks', 'thank you']):
        await update.message.reply_text(
            "🙏 Пожалуйста! Рад помочь в подготовке к экзамену по физике!"
        )
    elif any(word in text for word in ['помощь', 'help', 'как пользоваться']):
        from handlers.help_handler import help_command
        await help_command(update, context)
    elif any(word in text for word in ['профиль', 'profile', 'баллы', 'очки']):
        from handlers.profile import profile_command
        await profile_command(update, context)
    else:
        await update.message.reply_text(
            "🤖 Я бот, который поможет подготовиться к экзамену по физике. "
            "Используйте меню для навигации.\n"
            "Доступные команды:\n"
            "/start - Главное меню\n"
            "/help - Помощь и инструкции\n"
            "/profile - Личный профиль и баллы",
            parse_mode='Markdown'
        )


async def handle_back_buttons(update: Update, context):
    """Обработчик кнопок 'Назад'."""
    query = update.callback_query
    await query.answer()

    callback_data = query.data

    if callback_data == 'main':
        from keyboards.inline_keyboards import get_main_menu
        await query.edit_message_text(
            "🎓 *Главное меню бота Физика PRO100*\n\nВыберите, с чего бы хотели начать изучение:",
            reply_markup=get_main_menu(),
            parse_mode='Markdown'
        )
    elif callback_data == 'theory_back':
        from handlers.theory import theory_callback
        await theory_callback(update, context)
    elif callback_data == 'formulas_back':
        from handlers.formulas import formulas_callback
        await formulas_callback(update, context)
    elif callback_data == 'problems_back':
        from handlers.problems import problems_callback
        await problems_callback(update, context)


def main():
    # Инициализация БД
    db.init_db()

    # Создание приложения
    application = Application.builder().token(TOKEN).build()

    # Импорты обработчиков
    from handlers.commands import start_command
    from handlers.theory import theory_callback, section_callback, topic_callback, topic_studied_callback
    from handlers.formulas import formulas_callback, formulas_section_callback
    from handlers.formulas_detail import formulas_detail_callback
    from handlers.problems import (
        problems_callback,
        problem_section_callback,
        show_problem,
        next_problem_callback,
        handle_answer,
    )
    from handlers.profile import profile_callback, profile_command, reset_progress_callback
    from handlers.help_handler import help_command, help_callback, faq_callback, contact_callback

    # Команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))

    # Главное меню
    application.add_handler(CallbackQueryHandler(theory_callback, pattern='^theory$'))
    application.add_handler(CallbackQueryHandler(formulas_callback, pattern='^formulas$'))
    application.add_handler(CallbackQueryHandler(problems_callback, pattern='^problems$'))
    application.add_handler(CallbackQueryHandler(profile_callback, pattern='^profile$'))
    application.add_handler(CallbackQueryHandler(reset_progress_callback, pattern='^reset_progress$'))
    application.add_handler(CallbackQueryHandler(help_callback, pattern='^help$'))
    application.add_handler(CallbackQueryHandler(contact_callback, pattern='^contact$'))
    application.add_handler(CallbackQueryHandler(faq_callback, pattern='^faq$'))

    # Теория
    application.add_handler(CallbackQueryHandler(section_callback, pattern='^section_'))
    application.add_handler(CallbackQueryHandler(topic_callback, pattern='^topic_'))
    application.add_handler(CallbackQueryHandler(topic_studied_callback, pattern='^topic_studied_'))

    # Формулы
    application.add_handler(CallbackQueryHandler(formulas_section_callback, pattern='^formulas_section_'))
    application.add_handler(CallbackQueryHandler(formulas_detail_callback, pattern='^formula_detail_'))

    # Задачи (адаптивные)
    application.add_handler(CallbackQueryHandler(problem_section_callback, pattern='^problems_section_'))
    application.add_handler(CallbackQueryHandler(next_problem_callback, pattern='^next_problem_'))
    application.add_handler(CallbackQueryHandler(handle_answer, pattern='^answer_'))

    # Кнопки "Назад"
    application.add_handler(CallbackQueryHandler(
        handle_back_buttons,
        pattern='^(main|theory_back|formulas_back|problems_back)$'
    ))

    # Текстовые сообщения
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_messages
    ))

    # Обработчик ошибок
    async def error_handler(update: Update, context):
        logging.error(f"Ошибка при обработке обновления: {update}")
        if context.error:
            logging.error(f"Контекст ошибки: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ Произошла ошибка. Попробуйте еще раз или используйте /help для помощи.",
                parse_mode='Markdown'
            )

    application.add_error_handler(error_handler)

    # Запуск
    print("✅ Бот запущен и ожидает сообщений...")
    print("🔗 Ссылка на бота: https://t.me/PhysicsPRO100bot")
    print("📚 Доступные разделы: Теория, Формулы, Задачи, Профиль, Помощь")

    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == '__main__':
    main()