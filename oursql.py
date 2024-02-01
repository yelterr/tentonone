import mysql.connector
from mysql.connector import Error
import pandas as pd

from my_creds import SQL_Creds
credentials = SQL_Creds()


def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful.")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully.")
    except Error as err:
        print(f"Error: '{err}'")

# Modified create_server_connection(). It connects directly to a DB
def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

# Only needs filename and rating since the rest can be derived otherwise
def add_row(connection, filename, rating):
    pop_ratings = f"INSERT INTO ratings (filename, rating) VALUES {(filename, rating)}"
    execute_query(connection, pop_ratings)

# Clears the ratings table
# I kept the delete and recreate just in case I want to change "ratings"
def reset_ratings(db_connection):
    delete_query = "DROP TABLE ratings;"
    execute_query(db_connection, delete_query)
    new_ratings_query = """
    CREATE TABLE ratings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(70) NOT NULL,
        rating DECIMAL(7, 5) NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        quality BOOL DEFAULT 1
    );
    """
    execute_query(db_connection, new_ratings_query)


    clear_query = "TRUNCATE TABLE ratings;"
    execute_query(db_connection, clear_query)
    print("Table 'ratings' reset successfully.")

# Same thing as reset_ratings(), but for names
def reset_names(db_connection):
    #delete_query = "DROP TABLE names;"
    #execute_query(db_connection, delete_query)
    new_names_query = """
    CREATE TABLE names (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(40) NOT NULL,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(40) NOT NULL
    );
    """
    #execute_query(db_connection, new_names_query)

    clear_query = "TRUNCATE TABLE names;"
    execute_query(db_connection, clear_query)
    print("Table 'names' reset successfully.")

# Retrieves the average rating of a specified filename
def get_current_rating(db_connection, filename):
    avg_query = f"SELECT AVG(rating) FROM ratings WHERE filename = '{filename}';"
    result = read_query(db_connection, avg_query)

    if result[0][0] == None:
        return -1

    return round(result[0][0], 5)

# Retrieves a list of tuples structured (filename, amt_raters, avg_rating)
def get_all_average_ratings(db_connection):
    all_filenames_query = "SELECT DISTINCT filename FROM ratings"
    all_filenames = read_query(db_connection, all_filenames_query)

    ratings = []
    for filename in all_filenames:
        filename = filename[0]
        rating = get_current_rating(db_connection, filename)
        get_count_query = f"SELECT COUNT(*) AS filename FROM ratings WHERE filename = '{filename}';"
        amt_raters = read_query(db_connection, get_count_query)[0][0]
        ratings.append((filename, amt_raters, rating))

    return ratings

def get_ranking(db_connection, filename):
    rankings = sorted(get_all_average_ratings(db_connection), key=(lambda x : x[2]))[::-1]

    try:
        index = next(index for index, sublist in enumerate(rankings) if filename in sublist)
        return index + 1
    except StopIteration:
        pass

    return "[Error: please tell us about this]"

def get_count(db_connection, filename):
    q = f"SELECT COUNT(*) AS filename FROM ratings WHERE filename = '{filename}';"
    amt_raters = read_query(db_connection, q)[0][0]
    return amt_raters

# A testing tool
def print_all_rows(db_connection):
    get_all_query = "SELECT * FROM ratings"
    result = read_query(db_connection, get_all_query)
    for row in result:
        print(row)

#db = "hotornot"
#db_connection = create_db_connection(credentials.host, credentials.username, credentials.passwd, db)


# ----- TESTS -----

#      Adding rows
#reset_ratings(db_connection)
#filename = "elon_musk.jpg"
#rating = 5.6
#add_row(db_connection, filename, rating)
#print_all_rows(db_connection)