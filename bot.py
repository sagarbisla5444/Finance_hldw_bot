# =========================================================
# SMALL FINANCE TELEGRAM BOT
# COMPLETE RAILWAY READY CODE
# =========================================================
#
# FEATURES:
#
# ✅ Admin password login
# ✅ Duplicate customer names
# ✅ Customer ID system
# ✅ Daily / Weekly / Monthly installment
# ✅ Auto overdue tracking
# ✅ Daily reminder at 6:10 PM
# ✅ Railway cloud compatible
# ✅ Pending notifications daily
# ✅ Total finance summary
# ✅ Customer management
#
# =========================================================

import os
import sqlite3

from datetime import (
    datetime,
    timedelta,
    time
)

from telegram import Update

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# =========================================================
# ENV VARIABLES
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "12345"
)

# YOUR TELEGRAM USER ID
ADMIN_CHAT_ID = int(
    os.getenv("ADMIN_CHAT_ID", "123456789")
)

# =========================================================
# LOGIN SESSION
# =========================================================

logged_in_users = set()

# =========================================================
# DATABASE
# =========================================================

conn = sqlite3.connect(
    "/tmp/finance.db",
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

    next_due_date TEXT,

    overdue_days INTEGER DEFAULT 0,

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
# LOGIN
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
# LOGOUT
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
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = """
🏦 SMALL FINANCE BOT

━━━━━━━━━━━━━━━━━━
📌 COMMANDS
━━━━━━━━━━━━━━━━━━

/login PASSWORD

/logout

/add NAME MOBILE LOAN RETURN TYPE INSTALLMENTS

/pay CUSTOMER_ID AMOUNT

/customer CUSTOMER_ID

/list

/total

/pending

/delete CUSTOMER_ID

━━━━━━━━━━━━━━━━━━

📆 TYPES:
• daily
• weekly
• monthly

━━━━━━━━━━━━━━━━━━

EXAMPLE:

/add Ramesh 9876543210 10000 12000 weekly 12

/pay 1 1000
"""

    await update.message.reply_text(text)

# =========================================================
# HELP
# =========================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await start(update, context)

# =========================================================
# ADD CUSTOMER
# =========================================================

async def add_customer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Login required.\nUse:\n/login PASSWORD"
        )

        return

    try:

        args = context.args

        if len(args) < 6:

            await update.message.reply_text(
                "❌ Wrong Syntax\n\n"
                "/add NAME MOBILE LOAN RETURN TYPE INSTALLMENTS"
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

        today = datetime.now()

        # NEXT DUE DATE
        if installment_type == "daily":

            next_due_date = (
                today + timedelta(days=1)
            ).strftime("%Y-%m-%d")

        elif installment_type == "weekly":

            next_due_date = (
                today + timedelta(days=7)
            ).strftime("%Y-%m-%d")

        elif installment_type == "monthly":

            next_due_date = (
                today + timedelta(days=30)
            ).strftime("%Y-%m-%d")

        else:

            next_due_date = today.strftime("%Y-%m-%d")

        # INSERT
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
            next_due_date,
            created_date

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (

            name,
            mobile,
            loan_amount,
            return_amount,
            installment_type,
            total_installments,
            installment_amount,
            pending_amount,
            next_due_date,
            created_date
        ))

        conn.commit()

        customer_id = cursor.lastrowid

        profit = return_amount - loan_amount

        msg = f"""
✅ CUSTOMER ADDED

🆔 ID: {customer_id}

👤 Name: {name}

📱 Mobile: {mobile}

💰 Loan: ₹{loan_amount}

💵 Return: ₹{return_amount}

📈 Profit: ₹{profit}

📆 Type: {installment_type}

💳 Installment: ₹{installment_amount:.2f}

📅 Next Due:
{next_due_date}
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

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Login required."
        )

        return

    try:

        args = context.args

        if len(args) < 2:

            await update.message.reply_text(
                "❌ Use:\n/pay CUSTOMER_ID AMOUNT"
            )

            return

        customer_id = int(args[0])

        amount = float(args[1])

        # GET CUSTOMER
        cursor.execute("""
        SELECT
            name,
            paid_amount,
            pending_amount,
            installment_type
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

        installment_type = customer[3]

        today = datetime.now()

        # NEXT DUE DATE
        if installment_type == "daily":

            next_due_date = (
                today + timedelta(days=1)
            ).strftime("%Y-%m-%d")

        elif installment_type == "weekly":

            next_due_date = (
                today + timedelta(days=7)
            ).strftime("%Y-%m-%d")

        elif installment_type == "monthly":

            next_due_date = (
                today + timedelta(days=30)
            ).strftime("%Y-%m-%d")

        else:

            next_due_date = today.strftime("%Y-%m-%d")

        # UPDATE
        cursor.execute("""
        UPDATE customers
        SET
            paid_amount=?,
            pending_amount=?,
            next_due_date=?,
            overdue_days=0
        WHERE id=?
        """, (
            paid_amount,
            pending_amount,
            next_due_date,
            customer_id
        ))

        payment_date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # PAYMENT HISTORY
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

🆔 ID: {customer_id}

👤 Name: {customer_name}

💵 Paid: ₹{amount}

✅ Total Paid: ₹{paid_amount}

📉 Pending: ₹{pending_amount}

📅 Next Due:
{next_due_date}
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

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Login required."
        )

        return

    try:

        if len(context.args) < 1:

            await update.message.reply_text(
                "❌ Use:\n/customer CUSTOMER_ID"
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

💰 Loan: ₹{data[3]}

💵 Return: ₹{data[4]}

📆 Type: {data[5]}

🔁 Installments: {data[6]}

💳 Installment:
₹{data[7]:.2f}

✅ Paid:
₹{data[8]}

📉 Pending:
₹{data[9]}

📅 Next Due:
{data[10]}

⚠️ Overdue Days:
{data[11]}
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

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Login required."
        )

        return

    cursor.execute("""
    SELECT
        id,
        name,
        pending_amount,
        next_due_date,
        overdue_days
    FROM customers
    ORDER BY id DESC
    """)

    customers = cursor.fetchall()

    if not customers:

        await update.message.reply_text(
            "❌ No customers."
        )

        return

    msg = "📋 CUSTOMER LIST\n\n"

    for customer in customers:

        msg += (
            f"🆔 {customer[0]}\n"
            f"👤 {customer[1]}\n"
            f"📉 ₹{customer[2]}\n"
            f"📅 {customer[3]}\n"
            f"⚠️ {customer[4]} days\n\n"
        )

    await update.message.reply_text(msg)

# =========================================================
# TOTAL
# =========================================================

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Login required."
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

    returns = data[1] or 0

    collected = data[2] or 0

    pending = data[3] or 0

    profit = returns - invested

    msg = f"""
📊 TOTAL SUMMARY

💰 Invested:
₹{invested}

💵 Expected Return:
₹{returns}

✅ Collected:
₹{collected}

📉 Pending:
₹{pending}

📈 Profit:
₹{profit}
"""

    await update.message.reply_text(msg)

# =========================================================
# PENDING
# =========================================================

async def pending(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Login required."
        )

        return

    cursor.execute("""
    SELECT
        id,
        name,
        pending_amount,
        overdue_days
    FROM customers
    WHERE pending_amount > 0
    ORDER BY overdue_days DESC
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
            f"🆔 {row[0]}\n"
            f"👤 {row[1]}\n"
            f"💰 ₹{row[2]}\n"
            f"⚠️ {row[3]} days overdue\n\n"
        )

    await update.message.reply_text(msg)

# =========================================================
# DELETE
# =========================================================

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):

        await update.message.reply_text(
            "🔒 Login required."
        )

        return

    try:

        if len(context.args) < 1:

            await update.message.reply_text(
                "❌ Use:\n/delete CUSTOMER_ID"
            )

            return

        customer_id = int(context.args[0])

        cursor.execute("""
        DELETE FROM customers
        WHERE id=?
        """, (customer_id,))

        conn.commit()

        await update.message.reply_text(
            f"🗑 Customer deleted.\nID: {customer_id}"
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{str(e)}"
        )

# =========================================================
# DAILY REMINDER
# =========================================================

async def daily_reminder(context):

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    cursor.execute("""
    SELECT
        id,
        name,
        installment_amount,
        pending_amount,
        next_due_date,
        overdue_days
    FROM customers
    WHERE pending_amount > 0
    """)

    customers = cursor.fetchall()

    if not customers:

        return

    msg = "📢 INSTALLMENT REMINDER\n\n"

    found = False

    for customer in customers:

        customer_id = customer[0]

        name = customer[1]

        installment = customer[2]

        pending = customer[3]

        due_date = customer[4]

        overdue_days = customer[5]

        # OVERDUE CHECK
        if due_date <= today:

            found = True

            overdue_days += 1

            # UPDATE OVERDUE
            cursor.execute("""
            UPDATE customers
            SET overdue_days=?
            WHERE id=?
            """, (
                overdue_days,
                customer_id
            ))

            conn.commit()

            msg += (
                f"🆔 ID: {customer_id}\n"
                f"👤 Name: {name}\n"
                f"💳 Installment: ₹{installment}\n"
                f"📉 Pending: ₹{pending}\n"
                f"⚠️ Overdue: {overdue_days} days\n"
                f"📅 Due: {due_date}\n\n"
            )

    if found:

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=msg
        )

# =========================================================
# MAIN
# =========================================================

def main():

    app = ApplicationBuilder().token(
        BOT_TOKEN
    ).build()

    # COMMANDS
    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        CommandHandler("help", help_command)
    )

    app.add_handler(
        CommandHandler("login", login)
    )

    app.add_handler(
        CommandHandler("logout", logout)
    )

    app.add_handler(
        CommandHandler("add", add_customer)
    )

    app.add_handler(
        CommandHandler("pay", pay)
    )

    app.add_handler(
        CommandHandler("customer", customer)
    )

    app.add_handler(
        CommandHandler("list", list_customers)
    )

    app.add_handler(
        CommandHandler("total", total)
    )

    app.add_handler(
        CommandHandler("pending", pending)
    )

    app.add_handler(
        CommandHandler("delete", delete)
    )

    # =====================================================
    # DAILY REMINDER 6:10 PM
    # =====================================================

    job_queue = app.job_queue

    job_queue.run_daily(
        daily_reminder,
        time=time(hour=18, minute=10)
    )

    print("✅ BOT RUNNING...")

    app.run_polling()

# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()
