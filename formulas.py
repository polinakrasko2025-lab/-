import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import FORMULAS_DATA_PATH

def load_formulas_data():
    """Загружает формулы из JSON файла"""
    try:
        with open(FORMULAS_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {FORMULAS_DATA_PATH} не найден!")
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка чтения JSON из {FORMULAS_DATA_PATH}")
        return {}

async def formulas_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Формулы'"""
    query = update.callback_query
    await query.answer()
    
    data = load_formulas_data()
    if not data:
        await query.edit_message_text("Формулы временно недоступны.")
        return
    
    sections = list(data.keys())
    
    text = "📝 *Выберите раздел для изучения формул:*"
    
    from keyboards.inline_keyboards import get_formulas_sections_menu
    await query.edit_message_text(
        text,
        reply_markup=get_formulas_sections_menu(sections, 'main'),
        parse_mode='Markdown'
    )

async def formulas_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора раздела формул"""
    query = update.callback_query
    await query.answer()
    
    section = query.data.replace('formulas_section_', '')
    data = load_formulas_data()
    
    if section not in data:
        await query.edit_message_text(f"Раздел '{section}' не найден.")
        return
    
    formulas = data.get(section, [])
    
    if not formulas:
        text = f"📐 *Раздел: {section}*\n\nВ этом разделе пока нет формул."
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='formulas_back')]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        return
    
    text = f"📐 *Формулы раздела: {section}*\n\n"
    text += "*Выберите формулу для изучения:*\n\n"
    
    # Создаем кнопки для каждой формулы
    keyboard = []
    for i, formula in enumerate(formulas):
        # Обрезаем длинные названия
        formula_name = formula['name']
        if len(formula_name) > 30:
            formula_name = formula_name[:27] + "..."
        
        keyboard.append([InlineKeyboardButton(
            f"{i+1}. {formula_name}",
            callback_data=f'formula_detail_{section}_{i}'
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад к разделам", callback_data='formulas_back')])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )