import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN', '8240699418:AAF4x6fnPglosNjE8c0PQhW8ReQEiubByuI')

# Пути к файлам с данными
THEORY_DATA_PATH = 'data/theory.json'
FORMULAS_DATA_PATH = 'data/formulas.json'
PROBLEMS_DATA_PATH = 'data/problems.json'