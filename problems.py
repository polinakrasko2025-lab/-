# handlers/problems.py
import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import PROBLEMS_DATA_PATH
import database as db

OPTION_LABELS = ['A', 'B', 'C', 'D']
DIFF_LABEL = {'easy': '🟢 Лёгкая', 'medium': '🟡 Средняя', 'hard': '🔴 Сложная'}


def load_problems_data():
    """Загружает задачи из JSON."""
    try:
        with open(PROBLEMS_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {PROBLEMS_DATA_PATH} не найден!")
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка чтения JSON из {PROBLEMS_DATA_PATH}")
        return {}


def _difficulty_of(section, index, total):
    """Автоматически определяет сложность по позиции в списке.
    Первая треть — easy, вторая — medium, последняя — hard."""
    if total <= 1:
        return 'easy'
    r = index / total
    if r < 0.34:
        return 'easy'
    if r < 0.67:
        return 'medium'
    return 'hard'


def _problems_by_difficulty(section, difficulty, data):
    problems = data.get(section, [])
    total = len(problems)
    return [(i, p) for i, p in enumerate(problems)
            if _difficulty_of(section, i, total) == difficulty]


def _build_options(problems, index):
    """Собирает 4 варианта ответа: 1 правильный + 3 дистрактора."""
    correct = problems[index]['answer']

    # Если в JSON заданы свои варианты — используем их
    if problems[index].get('options'):
        opts = list(problems[index]['options'])
        if correct in opts:
            random.shuffle(opts)
            return opts, opts.index(correct)

    # Иначе собираем дистракторы из ответов других задач этого раздела
    pool = [p['answer'] for i, p in enumerate(problems)
            if i != index and p['answer'] != correct]
    random.shuffle(pool)

    distractors = []
    for d in pool:
        if d not in distractors:
            distractors.append(d)
        if len(distractors) >= 3:
            break
    while len(distractors) < 3:
        distractors.append(f"— вариант {len(distractors) + 1} —")

    options = [correct] + distractors[:3]
    random.shuffle(options)
    return options, options.index(correct)


# ─────────── Обработчики ───────────

async def problems_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка 'Решение задач' в главном меню."""
    query = update.callback_query
    await query.answer()

    data = load_problems_data()
    if not data:
        await query.edit_message_text("Задачи временно недоступны.")
        return

    user = update.effective_user
    db.get_or_create_user(user.id, user.username or '', user.first_name or '')

    from keyboards.inline_keyboards import get_problems_sections_menu
    await query.edit_message_text(
        "🔢 *Выберите раздел для решения задач:*\n_Сложность подбирается автоматически под вас._",
        reply_markup=get_problems_sections_menu(list(data.keys()), 'main'),
        parse_mode='Markdown'
    )


async def problem_section_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пользователь выбрал раздел задач."""
    query = update.callback_query
    await query.answer()
    section = query.data.replace('problems_section_', '')
    await show_adaptive_problem(update, context, section)


async def next_problem_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кнопка 'Следующая задача'."""
    query = update.callback_query
    await query.answer()
    section = query.data.replace('next_problem_', '')
    await show_adaptive_problem(update, context, section)


async def show_adaptive_problem(update: Update, context: ContextTypes.DEFAULT_TYPE, section: str):
    """Показывает задачу, подобранную под текущий уровень пользователя."""
    query = update.callback_query
    user_id = update.effective_user.id

    data = load_problems_data()
    if section not in data:
        await query.edit_message_text("Раздел не найден.")
        return

    state = db.get_section_state(user_id, section)
    difficulty = state['difficulty']
    candidates = _problems_by_difficulty(section, difficulty, data)

    # Фолбэк, если в текущей сложности нет задач
    if not candidates:
        for d in ['medium', 'easy', 'hard']:
            candidates = _problems_by_difficulty(section, d, data)
            if candidates:
                difficulty = d
                break

    if not candidates:
        await query.edit_message_text("В этом разделе пока нет задач.")
        return

    index, problem = random.choice(candidates)
    options, correct_idx = _build_options(data[section], index)

    # Сохраняем контекст текущей задачи
    context.user_data['current_problem'] = {
        'section': section,
        'index': index,
        'difficulty': difficulty,
        'correct_idx': correct_idx,
        'options': options
    }

    user = db.get_user(user_id)
    text = f"📝 *Задача — {section}*\n"
    text += f"Сложность: {DIFF_LABEL[difficulty]}\n"
    text += f"💰 Ваш баланс: *{user['points']}* баллов\n\n"
    text += f"{problem['problem']}\n\n"
    text += "*Выберите вариант ответа:*"

    keyboard = []
    for i, opt in enumerate(options):
        short = opt if len(opt) < 60 else opt[:57] + "..."
        keyboard.append([InlineKeyboardButton(
            f"{OPTION_LABELS[i]}) {short}",
            callback_data=f'answer_{i}'
        )])
    keyboard.append([InlineKeyboardButton("🔙 К разделам", callback_data='problems_back')])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пользователь выбрал вариант ответа."""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    ctx = context.user_data.get('current_problem')

    if not ctx:
        await query.edit_message_text(
            "Сессия устарела. Начните заново.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 К разделам", callback_data='problems_back')
            ]])
        )
        return

    selected = int(query.data.replace('answer_', ''))
    is_correct = (selected == ctx['correct_idx'])

    result = db.record_answer(user_id, ctx['section'], ctx['difficulty'], is_correct)
    user = db.get_user(user_id)
    data = load_problems_data()
    problem = data[ctx['section']][ctx['index']]

    if is_correct:
        header = f"✅ *Правильно!* +{result['points_delta']} баллов"
    else:
        right = ctx['options'][ctx['correct_idx']]
        header = (f"❌ *Неправильно.* {result['points_delta']} баллов\n"
                  f"Правильный ответ: *{right}*")

    diff_note = ""
    if result['new_difficulty'] != ctx['difficulty']:
        if result['new_difficulty'] == 'hard':
            diff_note = "\n\n🚀 Сложность повышена до *сложной*!"
        elif result['new_difficulty'] == 'medium':
            if ctx['difficulty'] == 'hard':
                diff_note = "\n\n⬇️ Сложность понижена до *средней*."
            else:
                diff_note = "\n\n📈 Сложность повышена до *средней*!"
        else:
            diff_note = "\n\n⬇️ Сложность понижена до *лёгкой*. Стоит повторить теорию."

    text = f"{header}\n\n"
    text += f"*Решение:*\n{problem['solution']}\n\n"
    text += f"*Ответ:* {problem['answer']}{diff_note}\n\n"
    text += f"💰 Баланс: *{user['points']}* баллов"

    keyboard = [
        [InlineKeyboardButton("➡️ Следующая задача", callback_data=f'next_problem_{ctx["section"]}')],
        [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')],
        [InlineKeyboardButton("🔙 К разделам", callback_data='problems_back')]
    ]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )


# ── Alias для обратной совместимости со старым кодом ──
async def show_problem(update, context, section, index=0):
    await show_adaptive_problem(update, context, section)