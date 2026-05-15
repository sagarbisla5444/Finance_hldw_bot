# =========================================================
# SMALL FINANCE TELEGRAM BOT
# COMPLETE READY-TO-RUN CODE
# ADMIN LOGIN + DUPLICATE NAMES + FINANCE SYSTEM
# =========================================================

# INSTALL:
# pip install python-telegram-bot==20.7

# RUN:
# python bot.py

# =========================================================

import sqlite3
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# =========================================================
# BOT CONFIG
# =========================================================

BOT_TOKEN = "TOKEN"

# =========================================================
# ADMIN PASSWORD
# =========================================================

ADMIN_PASSWORD = "12345"

# Logged-in admin users
logged_in_users = set()

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "finance.db",
    check_same_thread=False
)

cursor = conn.cursor()

# =========================================================
# CUSTOMERS TABLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    mobile TEXT,

    loan_amount REAL,

    return_amount REAL,

    installment_type TEXT,

    total_installments INTEGER,

    installment_amount REAL,

    paid_amount REAL DEFAULT 0,

    pending_amount REAL,

    created_date TEXT
)
""")

# =========================================================
# PAYMENTS TABLE
# =========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    customer_id INTEGER,

    customer_name TEXT,

    amount REAL,

    payment_date TEXT
)
""")

conn.commit()

# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(user_id):

    return user_id in logged_in_users

# =========================================================
# LOGIN COMMAND
# =========================================================

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        if len(context.args) < 1:

            await update.message.reply_text(
                "❌ Use:\n/login PASSWORD"
            )

            return

        password = context.args[0]

        if password == ADMIN_PASSWORD:

            user_id = update.effective_user.id

            logged_in_users.add(user_id)

            await update.message.reply_text(
                "✅ Admin login successful."
            )

        else:

            await update.message.reply_text(
                "❌ Wrong password."
            )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )

# =========================================================
# LOGOUT COMMAND
# =========================================================

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id in logged_in_users:

        logged_in_users.remove(user_id)

        await update.message.reply_text(
            "✅ Logged out successfully."
        )

    else:

        await update.message.reply_text(
            "❌ You are not logged in."
        )

# =========================================================
# START COMMAND
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🏦 SMALL FINANCE BOT

━━━━━━━━━━━━━━━━━━
📌 AVAILABLE COMMANDS
━━━━━━━━━━━━━━━━━━

1️⃣ LOGIN

Syntax:
<code>/login PASSWORD</code>

Example:
<code>/login 12345</code>

━━━━━━━━━━━━━━━━━━

2️⃣ LOGOUT

Syntax:
<code>/logout</code>

━━━━━━━━━━━━━━━━━━

3️⃣ ADD CUSTOMER

Syntax:
<code>/add NAME MOBILE LOAN RETURN TYPE INSTALLMENTS</code>

Example:
<code>/add Ramesh 9876543210 10000 12000 weekly 12</code>

━━━━━━━━━━━━━━━━━━

4️⃣ ADD PAYMENT

Syntax:
<code>/pay CUSTOMER_ID AMOUNT</code>

Example:
<code>/pay 1 1000</code>

━━━━━━━━━━━━━━━━━━

5️⃣ CUSTOMER DETAILS

Syntax:
<code>/customer CUSTOMER_ID</code>

Example:
<code>/customer 1</code>

━━━━━━━━━━━━━━━━━━

6️⃣ CUSTOMER LIST

Syntax:
<code>/list</code>

━━━━━━━━━━━━━━━━━━

7️⃣ TOTAL SUMMARY

Syntax:
<code>/total</code>

━━━━━━━━━━━━━━━━━━

8️⃣ PENDING CUSTOMERS

Syntax:
<code>/pending</code>

━━━━━━━━━━━━━━━━━━

9️⃣ DELETE CUSTOMER

Syntax:
<code>/delete CUSTOMER_ID</code>

Example:
<code>/delete 1</code>

━━━━━━━━━━━━━━━━━━

📆 Installment Types:
• daily
• weekly
• monthly

━━━━━━━━━━━━━━━━━━
"""

    await update.message.reply_text(
        text,
        parse_mode="HTML"
    )

# =========================================================
# HELP COMMAND
# =========================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await start(update, context)

# =========================================================
# ADD CUSTOMER
# =========================================================

async def add_customer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ADMIN CHECK
    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Admin login required.\n\nUse:\n/login PASSWORD"
        )

        return

    try:

        args = context.args

        if len(args) < 6:

            await update.message.reply_text(
                "❌ Wrong Syntax\n\n"
                "Use:\n"
                "/add NAME MOBILE LOAN RETURN TYPE INSTALLMENTS\n\n"
                "Example:\n"
                "/add Ramesh 9876543210 10000 12000 weekly 12"
            )

            return

        name = args[0]

        mobile = args[1]

        loan_amount = float(args[2])

        return_amount = float(args[3])

        installment_type = args[4].lower()

        total_installments = int(args[5])

        installment_amount = (
            return_amount / total_installments
        )

        pending_amount = return_amount

        created_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # INSERT CUSTOMER
        cursor.execute("""
        INSERT INTO customers (

            name,
            mobile,
            loan_amount,
            return_amount,
            installment_type,
            total_installments,
            installment_amount,
            pending_amount,
            created_date

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            name,
            mobile,
            loan_amount,
            return_amount,
            installment_type,
            total_installments,
            installment_amount,
            pending_amount,
            created_date
        ))

        conn.commit()

        customer_id = cursor.lastrowid

        profit = return_amount - loan_amount

        msg = f"""
✅ CUSTOMER ADDED

🆔 Customer ID: {customer_id}

👤 Name: {name}

📱 Mobile: {mobile}

💰 Loan Amount: ₹{loan_amount}

💵 Return Amount: ₹{return_amount}

📈 Profit: ₹{profit}

📆 Installment Type: {installment_type}

🔁 Installments: {total_installments}

💳 Installment Amount: ₹{installment_amount:.2f}

📉 Pending Amount: ₹{pending_amount}
"""

        await update.message.reply_text(msg)

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )

# =========================================================
# PAYMENT
# =========================================================

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ADMIN CHECK
    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Admin login required.\n\nUse:\n/login PASSWORD"
        )

        return

    try:

        args = context.args

        if len(args) < 2:

            await update.message.reply_text(
                "❌ Wrong Syntax\n\n"
                "Use:\n"
                "/pay CUSTOMER_ID AMOUNT\n\n"
                "Example:\n"
                "/pay 1 1000"
            )

            return

        customer_id = int(args[0])

        amount = float(args[1])

        # GET CUSTOMER
        cursor.execute("""
        SELECT
            name,
            paid_amount,
            pending_amount
        FROM customers
        WHERE id=?
        """, (customer_id,))

        customer = cursor.fetchone()

        if not customer:

            await update.message.reply_text(
                "❌ Customer not found."
            )

            return

        customer_name = customer[0]

        paid_amount = customer[1] + amount

        pending_amount = customer[2] - amount

        # UPDATE CUSTOMER
        cursor.execute("""
        UPDATE customers
        SET
            paid_amount=?,
            pending_amount=?
        WHERE id=?
        """, (
            paid_amount,
            pending_amount,
            customer_id
        ))

        payment_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # INSERT PAYMENT
        cursor.execute("""
        INSERT INTO payments (

            customer_id,
            customer_name,
            amount,
            payment_date

        )

        VALUES (?, ?, ?, ?)
        """, (
            customer_id,
            customer_name,
            amount,
            payment_date
        ))

        conn.commit()

        msg = f"""
✅ PAYMENT ADDED

🆔 Customer ID: {customer_id}

👤 Name: {customer_name}

💵 Payment: ₹{amount}

✅ Total Paid: ₹{paid_amount}

📉 Pending: ₹{pending_amount}
"""

        await update.message.reply_text(msg)

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )

# =========================================================
# CUSTOMER DETAILS
# =========================================================

async def customer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ADMIN CHECK
    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Admin login required.\n\nUse:\n/login PASSWORD"
        )

        return

    try:

        if len(context.args) < 1:

            await update.message.reply_text(
                "❌ Wrong Syntax\n\n"
                "Use:\n"
                "/customer CUSTOMER_ID\n\n"
                "Example:\n"
                "/customer 1"
            )

            return

        customer_id = int(context.args[0])

        cursor.execute("""
        SELECT *
        FROM customers
        WHERE id=?
        """, (customer_id,))

        data = cursor.fetchone()

        if not data:

            await update.message.reply_text(
                "❌ Customer not found."
            )

            return

        msg = f"""
👤 CUSTOMER DETAILS

🆔 ID: {data[0]}

👤 Name: {data[1]}

📱 Mobile: {data[2]}

💰 Loan Amount: ₹{data[3]}

💵 Return Amount: ₹{data[4]}

📆 Installment Type: {data[5]}

🔁 Total Installments: {data[6]}

💳 Installment Amount: ₹{data[7]:.2f}

✅ Paid Amount: ₹{data[8]}

📉 Pending Amount: ₹{data[9]}

📅 Created:
{data[10]}
"""

        await update.message.reply_text(msg)

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )

# =========================================================
# LIST CUSTOMERS
# =========================================================

async def list_customers(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ADMIN CHECK
    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Admin login required.\n\nUse:\n/login PASSWORD"
        )

        return

    cursor.execute("""
    SELECT
        id,
        name,
        pending_amount
    FROM customers
    ORDER BY id DESC
    """)

    customers = cursor.fetchall()

    if not customers:

        await update.message.reply_text(
            "❌ No customers found."
        )

        return

    msg = "📋 CUSTOMER LIST\n\n"

    for customer in customers:

        msg += (
            f"🆔 ID: {customer[0]}\n"
            f"👤 Name: {customer[1]}\n"
            f"📉 Pending: ₹{customer[2]}\n\n"
        )

    await update.message.reply_text(msg)

# =========================================================
# TOTAL SUMMARY
# =========================================================

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ADMIN CHECK
    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Admin login required.\n\nUse:\n/login PASSWORD"
        )

        return

    cursor.execute("""
    SELECT

        SUM(loan_amount),

        SUM(return_amount),

        SUM(paid_amount),

        SUM(pending_amount)

    FROM customers
    """)

    data = cursor.fetchone()

    invested = data[0] or 0

    expected_return = data[1] or 0

    collected = data[2] or 0

    pending = data[3] or 0

    profit = expected_return - invested

    msg = f"""
📊 TOTAL SUMMARY

💰 Total Invested:
₹{invested}

💵 Expected Return:
₹{expected_return}

✅ Collected:
₹{collected}

📉 Pending:
₹{pending}

📈 Expected Profit:
₹{profit}
"""

    await update.message.reply_text(msg)

# =========================================================
# PENDING CUSTOMERS
# =========================================================

async def pending(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ADMIN CHECK
    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Admin login required.\n\nUse:\n/login PASSWORD"
        )

        return

    cursor.execute("""
    SELECT
        id,
        name,
        pending_amount
    FROM customers
    WHERE pending_amount > 0
    ORDER BY pending_amount DESC
    """)

    rows = cursor.fetchall()

    if not rows:

        await update.message.reply_text(
            "✅ No pending customers."
        )

        return

    msg = "📉 PENDING CUSTOMERS\n\n"

    for row in rows:

        msg += (
            f"🆔 ID: {row[0]}\n"
            f"👤 Name: {row[1]}\n"
            f"💰 Pending: ₹{row[2]}\n\n"
        )

    await update.message.reply_text(msg)

# =========================================================
# DELETE CUSTOMER
# =========================================================

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ADMIN CHECK
    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Admin login required.\n\nUse:\n/login PASSWORD"
        )

        return

    try:

        if len(context.args) < 1:

            await update.message.reply_text(
                "❌ Wrong Syntax\n\n"
                "Use:\n"
                "/delete CUSTOMER_ID\n\n"
                "Example:\n"
                "/delete 1"
            )

            return

        customer_id = int(context.args[0])

        cursor.execute("""
        DELETE FROM customers
        WHERE id=?
        """, (customer_id,))

        conn.commit()

        await update.message.reply_text(
            f"🗑 Customer deleted.\n\n"
            f"🆔 ID: {customer_id}"
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )

# =========================================================
# MAIN
# =========================================================

def main():

    app = ApplicationBuilder().token(
        BOT_TOKEN
    ).build()

    # COMMANDS
    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("help", help_command))

    app.add_handler(CommandHandler("login", login))

    app.add_handler(CommandHandler("logout", logout))

    app.add_handler(CommandHandler("add", add_customer))

    app.add_handler(CommandHandler("pay", pay))

    app.add_handler(CommandHandler("customer", customer))

    app.add_handler(CommandHandler("list", list_customers))

    app.add_handler(CommandHandler("total", total))

    app.add_handler(CommandHandler("pending", pending))

    app.add_handler(CommandHandler("delete", delete))

    print("✅ BOT RUNNING...")

    app.run_polling()

# =========================================================
# START BOT
# =========================================================

if __name__ == "__main__":

    main()
