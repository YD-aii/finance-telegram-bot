from flask import Flask, send_from_directory, request, jsonify
import sqlite3

app = Flask(__name__, static_folder=".", static_url_path="")

DB = "finance.db"

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/data")
def get_data():
    user_id = request.args.get("user_id")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT name, amount FROM incomes WHERE user_id = ?", (user_id,))
    incomes = cur.fetchall()
    cur.execute("SELECT name, amount FROM expenses WHERE user_id = ?", (user_id,))
    expenses = cur.fetchall()

    transactions = [{"type": "Доход", "name": n, "amount": a} for n, a in incomes] + \
                   [{"type": "Расход", "name": n, "amount": a} for n, a in expenses]

    balance = sum(a for _, a in incomes) - sum(a for _, a in expenses)

    conn.close()
    return jsonify({"balance": round(balance, 2), "transactions": transactions})

@app.route("/api/add", methods=["POST"])
def add_data():
    data = request.json
    user_id = data["user_id"]
    type_ = data["type"]
    name = data["name"]
    amount = float(data["amount"])

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    if type_ == "income":
        cur.execute("INSERT INTO incomes (user_id, month, name, amount) VALUES (?, 'WebApp', ?, ?)", (user_id, name, amount))
    else:
        cur.execute("INSERT INTO expenses (user_id, month, name, amount) VALUES (?, 'WebApp', ?, ?)", (user_id, name, amount))

    conn.commit()
    conn.close()
    return "✅ Добавлено!"

if __name__ == "__main__":
    app.run(port=8000)
