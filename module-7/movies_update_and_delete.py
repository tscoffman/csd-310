import mysql.connector
from mysql.connector import errorcode
from dotenv import dotenv_values

secrets = dotenv_values("..env")

config = {
    "user": secrets["USER"],
    "password": secrets["PASSWORD"],
    "host": secrets["HOST"],
    "database": secrets["DATABASE"],
    "raise_on_warnings": True
}

try:
    # Connect to the MySQL database
    db = mysql.connector.connect(**config)
    cursor = db.cursor()

    print(
        "\n  Database user {} connected to MySQL on host {} with database {}".format(
            config["user"], config["host"], config["database"]
        )
    )

    # Function to display selected film info
    def show_films(cursor, title):
        query = """
            SELECT 
                film.film_name AS Name,
                film.film_director AS Director,
                genre.genre_name AS Genre,
                studio.studio_name AS Studio
            FROM film
            INNER JOIN genre ON film.genre_id = genre.genre_id
            INNER JOIN studio ON film.studio_id = studio.studio_id
        """
        cursor.execute(query)
        films = cursor.fetchall()

        print("\n-- {} --".format(title))
        for film in films:
            print("Film Name: {}".format(film[0]))
            print("Director: {}".format(film[1]))
            print("Genre Name ID: {}".format(film[2]))
            print("Studio Name: {}".format(film[3]))
            print("")

    # Display all films before changes
    show_films(cursor, "DISPLAYING FILMS")

    # INSERT a new film
    cursor.execute("""
        INSERT INTO film (film_name, film_releaseDate, film_runtime, film_director, studio_id, genre_id)
        VALUES ('The Matrix', 1999, 136, 'The Wachowskis', 1, 2)
    """)
    db.commit()
    show_films(cursor, "DISPLAYING FILMS AFTER INSERT")

    # UPDATE 'Alien' to be a Horror film
    cursor.execute("""
        UPDATE film
        SET genre_id = 1
        WHERE film_name = 'Alien'
    """)
    db.commit()
    show_films(cursor, "DISPLAYING FILMS AFTER UPDATE")

    # DELETE the film 'Gladiator'
    cursor.execute("""
        DELETE FROM film
        WHERE film_name = 'Gladiator'
    """)
    db.commit()
    show_films(cursor, "DISPLAYING FILMS AFTER DELETE")

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
