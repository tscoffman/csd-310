import mysql.connector
from mysql.connector import errorcode
from dotenv import dotenv_values

secrets = dotenv_values("..env")

config = {
    "user": secrets["USER"],                # root or other user
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],                # localhost
    "database": secrets["DATABASE"],        # wilson_financial
    "raise_on_warnings": True
}

try:
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    print(
        "\n  Database user {} connected to MySQL on host {} with database {}".format(
            config["user"], config["host"], config["database"]
        )
    )

    def show_employees_table(cursor, title):
        query = "SELECT * FROM employees"

        cursor.execute(query)
        employees = cursor.fetchall()

        print("\n" + title)
        for employee in employees:
            print("Employee ID: {}".format(employee[0]))
            print("First Name: {}".format(employee[1]))
            print("Last Name: {}".format(employee[2]))
            print("Role: {}".format(employee[3]))
            print("Date Hired: {}".format(employee[4]))
            print("Active: {}".format("Yes" if employee[5] == 1 else "No"))
            print("")

    def show_clients_table(cursor, title):
        query = "SELECT * FROM clients"

        cursor.execute(query)
        clients = cursor.fetchall()

        print("\n" + title)
        for client in clients:
            print("Client ID: {}".format(client[0]))
            print("Advisor ID: {}".format(client[1]))
            print("First Name: {}".format(client[2]))
            print("Last Name: {}".format(client[3]))
            print("Email: {}".format(client[4]))
            print("Phone Number: {}".format(client[5]))
            print("Date Joined: {}".format(client[6]))
            print("Active: {}".format("Yes" if client[7] == 1 else "No"))
            print("")

    def show_accounts_table(cursor, title):
        query = "SELECT * FROM accounts"

        cursor.execute(query)
        accounts = cursor.fetchall()

        print("\n" + title)
        for account in accounts:
            print("Account ID: {}".format(account[0]))
            print("Client ID: {}".format(account[1]))
            print("Account Type: {}".format(account[2]))
            print("Date Opened: {}".format(account[3]))
            print("Active: {}".format("Yes" if account[4] == 1 else "No"))
            print("")

    def show_assets_table(cursor, title):
        query = "SELECT * FROM assets"

        cursor.execute(query)
        assets = cursor.fetchall()

        print("\n" + title)
        for asset in assets:
            print("Asset ID: {}".format(asset[0]))
            print("Symbol: {}".format(asset[1] if asset[1] is not None else "N/A"))
            print("Asset Name: {}".format(asset[2]))
            print("Asset Type: {}".format(asset[3] if asset[3] is not None else "N/A"))
            print("")

    def show_holdings_table(cursor, title):
        query = "SELECT * FROM holdings"

        cursor.execute(query)
        holdings = cursor.fetchall()

        print("\n" + title)
        for holding in holdings:
            print("Holding ID: {}".format(holding[0]))
            print("Account ID: {}".format(holding[1]))
            print("Asset ID: {}".format(holding[2]))
            print("Quantity: {}".format("{0:g}".format(float(holding[3])) if holding[3] is not None else "N/A"))
            print("Value: ${}".format(str(holding[4]) + " as of " + str(holding[5])))
            print("")

    def show_transactions_table(cursor, title):
        query = "SELECT * FROM transactions"

        cursor.execute(query)
        transactions = cursor.fetchall()

        print("\n" + title)
        for transaction in transactions:
            print("Transaction ID: {}".format(transaction[0]))
            print("Account ID: {}".format(transaction[1]))
            print("Transaction Date: {}".format(transaction[2]))
            print("Transaction Type: {}".format(transaction[3]))
            print("Transaction Amount: ${}".format(transaction[4]))
            print("Description: {}".format(transaction[5] if transaction[5] is not None else "N/A"))
            print("")

    def show_tables():
        show_employees_table(cursor, "---Employees---")
        show_clients_table(cursor, "---Clients---")
        show_accounts_table(cursor, "---Accounts---")
        show_assets_table(cursor, "---Assets---")
        show_holdings_table(cursor, "---Holdings---")
        show_transactions_table(cursor, "---Transactions---")

    show_tables()

except mysql.connector.Error as err:
    # Handle errors
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("  The supplied username or password are invalid")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("  The specified database does not exist")
    else:
        print(err)

finally:
    # Close the database connection
    if 'db' in locals() and db.is_connected():
        db.close()
