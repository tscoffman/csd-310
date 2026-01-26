import mysql.connector
from mysql.connector import errorcode
from dotenv import dotenv_values

# Load secrets from the .env file
secrets = dotenv_values("..env")

config = {
    "user": secrets["USER"],
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],
    "database": secrets["DATABASE"],
    "raise_on_warnings": True  # Not in .env file
}

try:
    # Connect to the MySQL database
    db = mysql.connector.connect(**config)

    # Output the connection status
    print(
        "\n  Database user {} connected to MySQL on host {} with database {}".format(
            config["user"], config["host"], config["database"]
        )
    )

    input("\n\n  Press any key to continue...")

except mysql.connector.Error as err:
    # Handle errors
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("  The supplied username or password are invalid")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("  The specified database does not exist")
    else:
        print(err)

finally:
    # Close the connection to MySQL
    if 'db' in locals() and db.is_connected():
        db.close()
