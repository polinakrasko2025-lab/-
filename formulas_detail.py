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

async def formulas_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик детального изучения формулы"""
    query = update.callback_query
    await query.answer()
    
    # Разбираем callback_data: formula_detail_{section}_{index}
    parts = query.data.split('_')
    if len(parts) != 4:
        await query.edit_message_text("Ошибка в данных формулы.")
        return
    
    section = parts[2]
    try:
        index = int(parts[3])
    except ValueError:
        await query.edit_message_text("Ошибка в индексе формулы.")
        return
    
    data = load_formulas_data()
    
    if section not in data or index >= len(data[section]):
        await query.edit_message_text("Формула не найдена.")
        return
    
    formula = data[section][index]
    
    text = f"📐 *Изучение формулы*\n\n"
    text += f"*Раздел:* {section}\n\n"
    text += f"*Название:* {formula['name']}\n\n"
    text += f"*Формула:* `{formula['formula']}`\n\n"
    text += f"*Описание:* {formula['description']}\n\n"
    
    # Добавляем дополнительные сведения в зависимости от формулы
    additional_info = get_additional_formula_info(section, formula['name'])
    if additional_info:
        text += f"*Дополнительные сведения:*\n{additional_info}\n\n"
    
    # Добавляем примеры применения
    examples = get_formula_examples(section, formula['name'])
    if examples:
        text += f"*Примеры применения:*\n{examples}\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton("📝 Формулы раздела", callback_data=f'formulas_section_{section}'),
            InlineKeyboardButton("📚 Назад к разделам", callback_data='formulas_back')
        ],
        [InlineKeyboardButton("🔙 Главное меню", callback_data='main')]
    ]
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

def get_additional_formula_info(section: str, formula_name: str) -> str:
    """Возвращает дополнительную информацию о формуле"""
    info = {
        "Механика": {
            "Второй закон Ньютона": "• В инерциальных системах отсчета\n• Сила измеряется в ньютонах (Н)\n• Ускорение всегда сонаправлено с силой",
            "Закон сохранения энергии": "• Справедлив для замкнутых систем\n• При наличии трения механическая энергия переходит во внутреннюю",
            "Сила Архимеда": "• Действует на погруженное в жидкость или газ тело\n• Приложена к центру тяжести вытесненного объема"
        },
        "Электродинамика": {
            "Закон Ома для участка цепи": "• Справедлив для металлов и электролитов\n• Не выполняется для газов и полупроводников",
            "Сила Лоренца": "• Не совершает работы (перпендикулярна скорости)\n• Меняет направление скорости, но не ее модуль"
        }
    }
    
    return info.get(section, {}).get(formula_name, "")

def get_formula_examples(section: str, formula_name: str) -> str:
    """Возвращает примеры применения формулы"""
    examples = {
        "Механика": {
            "Второй закон Ньютона": "• Расчет ускорения автомобиля\n• Определение силы натяжения нити\n• Расчет перегрузок при старте ракеты",
            "Закон сохранения энергии": "• Расчет скорости в нижней точке маятника\n• Определение высоты подъема тела\n• Расчет КПД механизмов"
        },
        "Электродинамика": {
            "Закон Ома для участка цепи": "• Расчет тока в цепи\n• Определение напряжения на участке\n• Расчет сопротивления проводника",
            "Сила Ампера": "• Расчет силы взаимодействия проводников\n• Определение момента сил в электродвигателе\n• Расчет отклонения стрелки гальванометра"
        }
    }
    
    return examples.get(section, {}).get(formula_name, "")