import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import THEORY_DATA_PATH


def load_theory_data():
    """Загружает теоретический материал из JSON файла"""
    try:
        with open(THEORY_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {THEORY_DATA_PATH} не найден!")
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка чтения JSON из {THEORY_DATA_PATH}")
        return {}


async def _send_image(context, chat_id, path):
    """Отправляет картинку с учётом расширения.
    .gif  → animation (сохраняет анимацию)
    .webp → document (send_photo не всегда принимает webp)
    .png/.jpg → photo
    Возвращает объект Message или None при ошибке."""
    ext = os.path.splitext(path)[1].lower()
    with open(path, 'rb') as f:
        if ext == '.gif':
            return await context.bot.send_animation(chat_id=chat_id, animation=f)
        elif ext == '.webp':
            return await context.bot.send_document(chat_id=chat_id, document=f)
        else:
            return await context.bot.send_photo(chat_id=chat_id, photo=f)


async def cleanup_topic_images(context, chat_id):
    """Удаляет ранее отправленные картинки текущей темы.
    Можно вызывать из других обработчиков (например, при выходе в главное меню)."""
    msg_ids = context.user_data.pop('topic_image_ids', [])
    for mid in msg_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception as e:
            # Сообщение могло быть уже удалено или старше 48ч — не критично
            print(f"Не удалось удалить картинку {mid}: {e}")


async def theory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Теоретический материал'"""
    query = update.callback_query
    await query.answer()

    # Чистим картинки предыдущей темы, если они есть
    await cleanup_topic_images(context, query.message.chat_id)

    data = load_theory_data()
    if not data:
        await query.edit_message_text("Теоретический материал временно недоступен.")
        return

    sections = list(data.keys())
    text = "📚 *Выберите раздел для изучения теоретического материала:*"

    from keyboards.inline_keyboards import get_sections_menu
    await query.edit_message_text(
        text,
        reply_markup=get_sections_menu(sections, 'main'),
        parse_mode='Markdown'
    )


async def section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора раздела / возврата к списку тем."""
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    # 1) Удаляем картинки текущей темы (если пользователь вернулся из темы)
    await cleanup_topic_images(context, chat_id)

    # 2) Удаляем сообщение с темой (на котором нажали кнопку)
    try:
        await query.message.delete()
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")

    section = query.data.replace('section_', '')
    data = load_theory_data()

    if section not in data:
        await context.bot.send_message(chat_id=chat_id, text=f"Раздел '{section}' не найден.")
        return

    topics = data.get(section, [])

    # 3) Отправляем новый список тем
    if not topics:
        text = f"📖 *Раздел: {section}*\n\nПока нет доступных тем в этом разделе."
        keyboard = [
            [InlineKeyboardButton("🔢 Перейти к задачам", callback_data=f'problems_section_{section}')],
            [InlineKeyboardButton("🔙 Назад", callback_data='theory_back')]
        ]
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return

    text = f"📖 *Раздел: {section}*\n\n*Выберите тему:*"

    from keyboards.inline_keyboards import get_theory_topics_menu
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=get_theory_topics_menu(topics, section, 'theory_back'),
        parse_mode='Markdown'
    )


async def _show_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, section: str, index: int):
    """Отправляет тему: сначала картинки, затем текст с формулами и кнопками."""
    query = update.callback_query
    chat_id = query.message.chat_id

    data = load_theory_data()

    if section not in data or index >= len(data[section]):
        await context.bot.send_message(chat_id=chat_id, text="Тема не найдена.")
        return

    topic = data[section][index]

    # Формируем текст темы
    text = f"📚 *{topic['title']}*\n\n{topic['content']}"
    if topic.get('formulas'):
        text += "\n\n📝 *Ключевые формулы:*\n"
        for formula in topic['formulas']:
            text += f"• `{formula}`\n"

    keyboard = [
        [InlineKeyboardButton("🔢 Перейти к решению задач", callback_data=f'problems_section_{section}')],
        [InlineKeyboardButton("🔙 Назад к темам", callback_data=f'section_{section}')]
    ]
    markup = InlineKeyboardMarkup(keyboard)

    # На случай, если пользователь открыл тему без возврата — чистим старые картинки
    await cleanup_topic_images(context, chat_id)

    # Удаляем сообщение-меню, с которого пришли
    try:
        await query.message.delete()
    except Exception as e:
        print(f"Не удалось удалить сообщение: {e}")

    # Отправляем картинки и запоминаем их message_id, чтобы потом удалить
    image_msg_ids = []
    for img_path in topic.get('images', []) or []:
        if not os.path.exists(img_path):
            print(f"⚠️ Картинка не найдена: {img_path}")
            continue
        try:
            msg = await _send_image(context, chat_id, img_path)
            if msg:
                image_msg_ids.append(msg.message_id)
        except Exception as e:
            print(f"⚠️ Ошибка отправки картинки {img_path}: {e}")

    context.user_data['topic_image_ids'] = image_msg_ids

    # Отправляем текст с кнопками
    MAX_LEN = 4000
    if len(text) <= MAX_LEN:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=markup,
            parse_mode='Markdown'
        )
    else:
        parts = []
        current = ""
        for chunk in text.split("\n\n"):
            if len(current) + len(chunk) + 2 > MAX_LEN:
                parts.append(current)
                current = chunk
            else:
                current = (current + "\n\n" + chunk) if current else chunk
        if current:
            parts.append(current)

        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            await context.bot.send_message(
                chat_id=chat_id,
                text=part,
                reply_markup=markup if is_last else None,
                parse_mode='Markdown'
            )


async def topic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора темы теории"""
    query = update.callback_query
    await query.answer()

    parts = query.data.split('_')
    if len(parts) != 3:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Ошибка в данных темы."
        )
        return

    section = parts[1]
    try:
        index = int(parts[2])
    except ValueError:
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Ошибка в индексе темы."
        )
        return

    await _show_topic(update, context, section, index)


async def topic_studied_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение изучения темы (для совместимости)."""
    query = update.callback_query
    await query.answer("✅ Информация сохранена!")

    parts = query.data.split('_')
    if len(parts) < 4:
        return

    section = parts[2]
    try:
        index = int(parts[3])
    except ValueError:
        return

    await _show_topic(update, context, section, index)