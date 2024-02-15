import mysql.connector
from mysql.connector import Error
import numpy as np

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
        return True
    except Error as err:
        print(f"Error: '{err}'")
        return False

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
def add_rating(connection, filename, rating):
    pop_ratings = f"INSERT INTO ratings (filename, rating) VALUES {(filename, rating)}"
    result = execute_query(connection, pop_ratings)
    if result:
        return True
    else:
        return False

def add_name(connection, name, gender, filename, og_filename, source):
    add_name_q = f"INSERT INTO names (name, gender, filename, og_filename, source) VALUES {(name, gender, filename, og_filename, source)}"
    result = execute_query(connection, add_name_q)
    if result:
        return True
    else:
        return False

def edit_name(connection, original_name, new_name=None, new_gender=None, new_filename=None, new_og_filename=None, new_source=None):
    condition = f"WHERE name = '{original_name}';"
    changes = [new_name, new_gender, new_filename, new_og_filename, new_source]
    corrosponding_stat = ["name", "gender", "filename", "og_filename", "source"]
    commands = []

    for i, change in enumerate(changes):
        if change:
            command = f"{corrosponding_stat[i]} = '{change}'"
            commands.append(command)

    print(commands)

    for command in commands:
        update_query = f"UPDATE names SET {command} {condition}"
        result = execute_query(connection, update_query)
        if result:
            print(f"{original_name} successfully updated.")
        else:
            print(f"There was an error updating the information of {original_name}")

# Clears the ratings table
def reset_ratings(db_connection):
    #delete_query = "DROP TABLE ratings;"
    #execute_query(db_connection, delete_query)
    new_ratings_query = """
    CREATE TABLE ratings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(70) NOT NULL,
        rating DECIMAL(7, 5) NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        quality BOOL DEFAULT 1
    );
    """
    #execute_query(db_connection, new_ratings_query)


    #clear_query = "TRUNCATE TABLE ratings;"
    #execute_query(db_connection, clear_query)
    print("Table 'ratings' reset successfully.")

# Same thing as reset_ratings(), but for names
def reset_names(db_connection):
    #delete_query = "DROP TABLE names;"
    #execute_query(db_connection, delete_query)
    new_names_query = """
    CREATE TABLE names (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(40) NOT NULL,
        gender VARCHAR(5) NOT NULL,
        filename VARCHAR(70) NOT NULL,
        og_filename VARCHAR(100),
        source VARCHAR(500) NOT NULL
    );
    """
    #execute_query(db_connection, new_names_query)

    #clear_query = "TRUNCATE TABLE names;"
    #execute_query(db_connection, clear_query)
    print("Table 'names' reset successfully.")

# Retrieves the average rating of a specified filename
def get_current_rating(db_connection, filename):
    avg_query = f"SELECT AVG(rating) FROM ratings WHERE filename = \"{filename}\";"
    result = read_query(db_connection, avg_query)

    if not result:
        return -1

    return round(result[0][0], 5)

# Retrieves a list of tuples structured (filename, amt_raters, avg_rating)
def get_all_average_ratings(db_connection):
    my_query = '''
    SELECT filename,
    COUNT(filename) as amt_raters,
    AVG(rating) AS average_rating
    FROM ratings
    GROUP BY filename;
    '''
    results = read_query(db_connection, my_query)

    return results

def get_ranking(db_connection, filename):
    rankings = sorted(get_all_average_ratings(db_connection), key=(lambda x : x[2]))[::-1]
    rankings = np.array(rankings)

    try:
        filenames = rankings[:, 0]
        index = np.where(filenames == filename)
        return int(index[0][0] + 1)
    except StopIteration:
        pass

    return "[Error: please tell us about this]"

def get_count(db_connection, filename):
    q = f"SELECT COUNT(*) AS filename FROM ratings WHERE filename = \"{filename}\";"
    amt_raters = read_query(db_connection, q)[0][0]
    return amt_raters

def get_individual_info(connection, filename):
    search_query = f"SELECT * FROM names WHERE filename = \"{filename}\""
    results = read_query(connection, search_query)
    return results

# A testing tool
def print_all_rows(db_connection):
    get_all_query = "SELECT * FROM ratings"
    result = read_query(db_connection, get_all_query)
    for row in result:
        print(row)

# ----- TESTS -----

#db = "hotornot"
#db_connection = create_db_connection(credentials.host, credentials.username, credentials.passwd, db)

#edit_name(db_connection, original_name="Eminem", new_source="https://people.com/music/super-bowl-2022-eminem-says-his-performance-is-nerve-wracking/")
#print(get_individual_info(db_connection, "Eminem.jpg"))

#      Adding rows
#reset_ratings(db_connection)
#filename = "elon_musk.jpg"
#rating = 5.6
#add_row(db_connection, filename, rating)
#print_all_rows(db_connection)