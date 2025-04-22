import psycopg2
from config.config import DB_CONFIG

def conectar():
    return psycopg2.connect(**DB_CONFIG)
