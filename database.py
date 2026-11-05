# database.py
import sqlite3
import os
from datetime import datetime

DB_PATH = 'data/users.db'

# ── Настройки системы баллов ──
POINTS = {'easy': 5, 'medium': 10, 'hard': 20}
WRONG_PENALTY = -3
CORRECT_STREAK_TO_UP = 2
DIFFICULTY_ORDER = ['easy', 'medium', 'hard']


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        points INTEGER DEFAULT 0,
        total_correct INTEGER DEFAULT 0,
        total_wrong INTEGER DEFAULT 0,
        created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_sections (
        user_id INTEGER,
        section TEXT,
        difficulty TEXT DEFAULT 'easy',
        correct_streak INTEGER DEFAULT 0,
        total_correct INTEGER DEFAULT 0,
        total_wrong INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, section))''')
    c.execute('''CREATE TABLE IF NOT EXISTS answers_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        section TEXT,
        difficulty TEXT,
        is_correct INTEGER,
        timestamp TEXT)''')
    conn.commit()
    conn.close()


def _conn():
    return sqlite3.connect(DB_PATH)


def get_or_create_user(user_id, username='', first_name=''):
    conn = _conn()
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    if c.fetchone() is None:
        c.execute(
            'INSERT INTO users (user_id, username, first_name, created_at) VALUES (?, ?, ?, ?)',
            (user_id, username, first_name, datetime.now().isoformat())
        )
    else:
        c.execute(
            'UPDATE users SET username=?, first_name=? WHERE user_id=?',
            (username, first_name, user_id)
        )
    conn.commit()
    conn.close()


def get_user(user_id):
    conn = _conn()
    c = conn.cursor()
    c.execute(
        'SELECT user_id, username, first_name, points, total_correct, total_wrong, created_at '
        'FROM users WHERE user_id=?', (user_id,)
    )
    r = c.fetchone()
    conn.close()
    if not r:
        return None
    return {
        'user_id': r[0],
        'username': r[1],
        'first_name': r[2],
        'points': r[3],
        'total_correct': r[4],
        'total_wrong': r[5],
        'created_at': r[6]
    }


def get_section_state(user_id, section):
    conn = _conn()
    c = conn.cursor()
    c.execute(
        'SELECT difficulty, correct_streak, total_correct, total_wrong '
        'FROM user_sections WHERE user_id=? AND section=?',
        (user_id, section)
    )
    r = c.fetchone()
    if not r:
        c.execute(
            'INSERT INTO user_sections (user_id, section) VALUES (?, ?)',
            (user_id, section)
        )
        conn.commit()
        conn.close()
        return {'difficulty': 'easy', 'correct_streak': 0, 'total_correct': 0, 'total_wrong': 0}
    conn.close()
    return {'difficulty': r[0], 'correct_streak': r[1], 'total_correct': r[2], 'total_wrong': r[3]}


def record_answer(user_id, section, difficulty, is_correct):
    state = get_section_state(user_id, section)
    new_streak = state['correct_streak']
    new_diff = state['difficulty']
    new_correct = state['total_correct']
    new_wrong = state['total_wrong']

    if is_correct:
        points_delta = POINTS.get(difficulty, 5)
        new_streak += 1
        new_correct += 1
        if new_streak >= CORRECT_STREAK_TO_UP and difficulty != 'hard':
            new_diff = DIFFICULTY_ORDER[DIFFICULTY_ORDER.index(difficulty) + 1]
            new_streak = 0
    else:
        points_delta = WRONG_PENALTY
        new_streak = 0
        new_wrong += 1
        if difficulty != 'easy':
            new_diff = DIFFICULTY_ORDER[DIFFICULTY_ORDER.index(difficulty) - 1]

    conn = _conn()
    c = conn.cursor()
    c.execute(
        '''UPDATE user_sections
           SET difficulty=?, correct_streak=?, total_correct=?, total_wrong=?
           WHERE user_id=? AND section=?''',
        (new_diff, new_streak, new_correct, new_wrong, user_id, section)
    )
    if is_correct:
        c.execute(
            'UPDATE users SET points=points+?, total_correct=total_correct+1 WHERE user_id=?',
            (points_delta, user_id)
        )
    else:
        c.execute(
            'UPDATE users SET points=MAX(0, points+?), total_wrong=total_wrong+1 WHERE user_id=?',
            (points_delta, user_id)
        )
    c.execute(
        'INSERT INTO answers_log (user_id, section, difficulty, is_correct, timestamp) '
        'VALUES (?, ?, ?, ?, ?)',
        (user_id, section, difficulty, 1 if is_correct else 0, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return {'points_delta': points_delta, 'new_difficulty': new_diff}


def get_weak_sections(user_id, threshold=2):
    conn = _conn()
    c = conn.cursor()
    c.execute(
        '''SELECT section, total_correct, total_wrong
           FROM user_sections
           WHERE user_id=? AND total_wrong >= ?
           ORDER BY (total_wrong * 1.0 / MAX(1, total_correct + total_wrong)) DESC''',
        (user_id, threshold)
    )
    rows = c.fetchall()
    conn.close()
    return [{'section': r[0], 'correct': r[1], 'wrong': r[2]} for r in rows]


def get_top_sections(user_id):
    conn = _conn()
    c = conn.cursor()
    c.execute(
        '''SELECT section, total_correct
           FROM user_sections
           WHERE user_id=? AND total_correct >= 3
           ORDER BY total_correct DESC LIMIT 3''',
        (user_id,)
    )
    rows = c.fetchall()
    conn.close()
    return [{'section': r[0], 'correct': r[1]} for r in rows]


def reset_user_progress(user_id):
    conn = _conn()
    c = conn.cursor()
    c.execute('UPDATE users SET points=0, total_correct=0, total_wrong=0 WHERE user_id=?', (user_id,))
    c.execute('DELETE FROM user_sections WHERE user_id=?', (user_id,))
    c.execute('DELETE FROM answers_log WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()