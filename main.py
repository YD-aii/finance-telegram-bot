from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import database as db
from config import BOT_TOKEN

from database import is_user_registered, register_user
from config import AUTH_CODE
from config import ADMIN_IDS
from database import get_all_users
from telegram.ext import ContextTypes
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# Состояния для выбора месяца и ввода данных
CHOOSING_MONTH, ADDING_INCOME_NAME, ADDING_INCOME_AMOUNT = range(3)
ADDING_EXPENSE_NAME, ADDING_EXPENSE_AMOUNT = range(3, 5)

# Доступные месяцы
MONTHS = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
          "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]


async def open_app(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url="https://your-deployed-url.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Нажмите кнопку ниже, чтобы открыть мини-приложение:", reply_markup=reply_markup)

async def open_app(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Открыть мини-приложение", web_app=WebAppInfo(url="https://yourdomain.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📱 Нажмите кнопку ниже, чтобы открыть приложение:", reply_markup=reply_markup)


async def universal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or ""
    first_name = user.first_name or ""

    # Проверка регистрации
    if not db.is_user_registered(user_id):
        if context.user_data.get("awaiting_code"):
            if update.message.text == AUTH_CODE:
                db.register_user(user_id, username, first_name)
                context.user_data["awaiting_code"] = False
                await update.message.reply_text("✅ Регистрация успешна!")
                await start(update, context)
            else:
                await update.message.reply_text("❌ Неверный код. Попробуйте снова.")
        else:
            context.user_data["awaiting_code"] = True
            await update.message.reply_text("🔐 Введите код доступа для регистрации:")
        return

    # Пользователь зарегистрирован — продолжаем
    # Здесь можно переадресовать на команду, или просто игнорировать
    await update.message.reply_text("🤖 Используйте кнопки или команды.")




# Главное меню после выбора месяца
def get_main_menu():
    keyboard = [
        ["Добавить доход", "Добавить расход"],
        ["Показать таблицу"],
        ["Удалить все доходы", "Удалить все расходы"],
        ["Сменить месяц"]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)


# Команда /start
async def start(update: Update, context):
    keyboard = [["Выбрать месяц"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Добро пожаловать в финансовый бот!", reply_markup=reply_markup)


# Обработка выбора месяца
async def choose_month(update: Update, context):
    keyboard = [[month] for month in MONTHS]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("🗓Выберите месяц:", reply_markup=reply_markup)
    return CHOOSING_MONTH


# Сохранение выбранного месяца
async def handle_month_choice(update: Update, context):
    month = update.message.text
    if month not in MONTHS:
        await update.message.reply_text("Пожалуйста, выберите месяц из списка.")
        return CHOOSING_MONTH

    context.user_data["month"] = month  # Сохраняем месяц
    await update.message.reply_text(f"Вы выбрали месяц: {month}. Теперь вы можете редактировать финансы.",
                                    reply_markup=get_main_menu())
    return ConversationHandler.END


# Добавление дохода
async def add_income(update: Update, context):
    if "month" not in context.user_data:
        await update.message.reply_text("Сначала выберите месяц.")
        return ConversationHandler.END
    await update.message.reply_text("Введите название дохода:")
    return ADDING_INCOME_NAME


# Ввод названия дохода
async def handle_income_name(update: Update, context):
    context.user_data["income_name"] = update.message.text
    await update.message.reply_text("Введите сумму дохода:")
    return ADDING_INCOME_AMOUNT


# Ввод суммы дохода
async def handle_income_amount(update: Update, context):
    user_id = update.message.from_user.id
    month = context.user_data["month"]
    income_name = context.user_data["income_name"]
    income_amount = float(update.message.text)

    db.add_income(user_id, month, income_name, income_amount)

    await update.message.reply_text(f"✅ Доход '{income_name}' ({income_amount}₽) добавлен в {month}!",
                                    reply_markup=get_main_menu())
    return ConversationHandler.END


# Добавление расхода
async def add_expense(update: Update, context):
    if "month" not in context.user_data:
        await update.message.reply_text("Сначала выберите месяц.")
        return ConversationHandler.END
    await update.message.reply_text("Введите название расхода:")
    return ADDING_EXPENSE_NAME


# Ввод названия расхода
async def handle_expense_name(update: Update, context):
    context.user_data["expense_name"] = update.message.text
    await update.message.reply_text("Введите сумму расхода:")
    return ADDING_EXPENSE_AMOUNT


# Ввод суммы расхода
async def handle_expense_amount(update: Update, context):
    user_id = update.message.from_user.id
    month = context.user_data["month"]
    expense_name = context.user_data["expense_name"]
    expense_amount = float(update.message.text)

    db.add_expense(user_id, month, expense_name, expense_amount)

    await update.message.reply_text(f"✅ Расход '{expense_name}' ({expense_amount}₽) добавлен в {month}!",
                                    reply_markup=get_main_menu())
    return ConversationHandler.END


# Показ таблицы расходов и доходов
async def show_table(update: Update, context):
    if "month" not in context.user_data:
        await update.message.reply_text("Сначала выберите месяц.")
        return

    user_id = update.message.from_user.id
    month = context.user_data["month"]

    incomes = db.get_incomes(user_id, month)
    expenses = db.get_expenses(user_id, month)

    response = f"📊 Финансы за {month}:\n\n"
    response += "Доходы:\n" if incomes else "Доходов нет.\n"
    for id, name, amount in incomes:
        response += f"• {name}: {amount}₽\n"

    response += "\nРасходы:\n" if expenses else "\nРасходов нет.\n"
    for id, name, amount in expenses:
        response += f"• {name}: {amount}₽\n"

    balance = db.get_balance(user_id, month)
    response += f"\n💰 Итоговый баланс: {balance}₽"

    await update.message.reply_text(response, reply_markup=get_main_menu())


# Удаление всех доходов
async def delete_all_incomes(update: Update, context):
    if "month" not in context.user_data:
        await update.message.reply_text("Сначала выберите месяц.")
        return

    user_id = update.message.from_user.id
    month = context.user_data["month"]

    db.delete_all_incomes(user_id, month)
    await update.message.reply_text(f"❌ Все доходы за {month} удалены!", reply_markup=get_main_menu())


# Удаление всех расходов
async def delete_all_expenses(update: Update, context):
    if "month" not in context.user_data:
        await update.message.reply_text("Сначала выберите месяц.")
        return

    user_id = update.message.from_user.id
    month = context.user_data["month"]

    db.delete_all_expenses(user_id, month)
    await update.message.reply_text(f"❌ Все расходы за {month} удалены!", reply_markup=get_main_menu())


# Смена месяца
async def change_month(update: Update, context):
    return await choose_month(update, context)
async def admin_panel(update: Update, context):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 У вас нет доступа к этой команде.")
        return

    users = get_all_users()
    if not users:
        await update.message.reply_text("Нет зарегистрированных пользователей.")
        return

    text = "👥 Зарегистрированные пользователи:\n\n"
    for uid, username, first_name in users:
        name = first_name or "Без имени"
        login = f"@{username}" if username else "(нет username)"
        text += f"• {name} — {login} (ID: {uid})\n"

    await update.message.reply_text(text)

# Основная функция
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик выбора месяца
    month_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text(["Выбрать месяц", "Сменить месяц"]), choose_month)],
        states={CHOOSING_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_month_choice)]},
        fallbacks=[]
    )

    # Обработчики доходов и расходов
    income_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("Добавить доход"), add_income)],
        states={ADDING_INCOME_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_income_name)],
                ADDING_INCOME_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_income_amount)]},
        fallbacks=[]
    )

    expense_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Text("Добавить расход"), add_expense)],
        states={ADDING_EXPENSE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense_name)],
                ADDING_EXPENSE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_expense_amount)]},
        fallbacks=[]
    )

    application.add_handler(month_handler)
    application.add_handler(income_handler)
    application.add_handler(expense_handler)
    application.add_handler(MessageHandler(filters.Text("Показать таблицу"), show_table))
    application.add_handler(MessageHandler(filters.Text("Удалить все доходы"), delete_all_incomes))
    application.add_handler(MessageHandler(filters.Text("Удалить все расходы"), delete_all_expenses))
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, universal_handler))
    application.add_handler(CommandHandler("app", open_app))
    application.add_handler(CommandHandler("app", open_app))

    application.run_polling()


if __name__ == "__main__":
    main()
