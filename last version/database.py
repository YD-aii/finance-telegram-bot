import sqlite3

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # Таблица для доходов с учетом месяца
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')

    # Таблица для расходов с учетом месяца
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Добавление дохода с указанием месяца
def add_income(user_id, month, name, amount):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO incomes (user_id, month, name, amount)
        VALUES (?, ?, ?, ?)
    ''', (user_id, month, name, amount))
    conn.commit()
    conn.close()

# Добавление расхода с указанием месяца
def add_expense(user_id, month, name, amount):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO expenses (user_id, month, name, amount)
        VALUES (?, ?, ?, ?)
    ''', (user_id, month, name, amount))
    conn.commit()
    conn.close()

# Получение доходов за выбранный месяц
def get_incomes(user_id, month):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, amount FROM incomes WHERE user_id = ? AND month = ?', (user_id, month))
    incomes = cursor.fetchall()
    conn.close()
    return incomes

# Получение расходов за выбранный месяц
def get_expenses(user_id, month):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, amount FROM expenses WHERE user_id = ? AND month = ?', (user_id, month))
    expenses = cursor.fetchall()
    conn.close()
    return expenses

# Удаление всех доходов за выбранный месяц
def delete_all_incomes(user_id, month):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM incomes WHERE user_id = ? AND month = ?', (user_id, month))
    conn.commit()
    conn.close()

# Удаление всех расходов за выбранный месяц
def delete_all_expenses(user_id, month):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE user_id = ? AND month = ?', (user_id, month))
    conn.commit()
    conn.close()

def create_user_table():
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT
                )''')
    conn.commit()
    conn.close()

def is_user_registered(user_id):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def register_user(user_id, username, first_name):
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
              (user_id, username, first_name))
    conn.commit()
    conn.close()


# Получение баланса за выбранный месяц
def get_balance(user_id, month):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute('SELECT SUM(amount) FROM incomes WHERE user_id = ? AND month = ?', (user_id, month))
    total_income = cursor.fetchone()[0] or 0

    cursor.execute('SELECT SUM(amount) FROM expenses WHERE user_id = ? AND month = ?', (user_id, month))
    total_expense = cursor.fetchone()[0] or 0

    conn.close()
    return total_income - total_expense

# Инициализация базы данных
init_db()

def get_all_users():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

# Получение всех транзакций пользователя
def get_all_transactions(user_id):
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    # Получим доходы
    cursor.execute('SELECT month, "Доход", name, amount FROM incomes WHERE user_id = ?', (user_id,))
    incomes = cursor.fetchall()

    # Получим расходы
    cursor.execute('SELECT month, "Расход", name, amount FROM expenses WHERE user_id = ?', (user_id,))
    expenses = cursor.fetchall()

    conn.close()

    # Объединяем и сортируем по месяцу (при желании можно и по дате, если она будет)
    return sorted(incomes + expenses, key=lambda x: x[0])
create_user_table()


