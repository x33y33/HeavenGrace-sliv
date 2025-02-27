import sqlite3

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users
(id INTEGER PRIMARY KEY AUTOINCREMENT, 
username TEXT DEFAULT 'Не установлен',
city TEXT DEFAULT 'Не выбрано',
currency TEXT DEFAULT 'RUB',
count_orders INTEGER DEFAULT 0,
referral INTEGER DEFAULT 0,
referral_count INTEGER DEFAULT 0)
''')

conn.commit()

conn.close()

def connect():
    return sqlite3.connect('database.db')

def add_referral(telegram_id, referrer_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET referral = ? WHERE id = ?', (referrer_id, telegram_id))
    conn.commit()

def increment_referral_count(referrer_id):
    conn = connect()
    cursor = conn.cursor()  
    cursor.execute('UPDATE users SET referral_count = referral_count + 1 WHERE id = ?', (referrer_id,))
    conn.commit()

def get_count_ref(telegram_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT referral_count FROM users WHERE id = ?', (telegram_id,))
    return cursor.fetchone()[0]

def get_referral(telegram_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT referral FROM users WHERE id = ?', (telegram_id,))
    return cursor.fetchone()[0]

def add_user(telegram_id, username):
    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (id, username) VALUES (?, ?)', (telegram_id, username))
    conn.commit()

def add_city(telegram_id, city):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET city = ? WHERE id = ?', (city, telegram_id))
    conn.commit()

def add_count_orders(telegram_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET count_orders = count_orders + 1 WHERE id = ?', (telegram_id,))
    conn.commit()

def user_exists(telegram_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (telegram_id,))
    return cursor.fetchone() is not None

def add_currency(telegram_id, currency):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET currency = ? WHERE id = ?', (currency, telegram_id))
    conn.commit()

def user_check(telegram_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (telegram_id,))
    return cursor.fetchone()  # Вернет None, если пользователя нет
