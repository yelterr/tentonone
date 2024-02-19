from google.cloud.sql.connector import Connector
import numpy as np

from my_creds import SQL_Creds
credentials = SQL_Creds()

connector = Connector()

def create_db_connection(instance_conn_name, user_name, user_password, db_name):
    conn = connector.connect(
        instance_conn_name,
        "pytds",
        user=user_name,
        password=user_password,
        db=db_name
    )
    return conn


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
        return True
    except:
        print(f"Error: 'execution error'")
        return False

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except:
        print(f"Error: 'read error'")

# Only needs filename and rating since the rest can be derived otherwise
def add_rating(connection, filename, rating):
    pop_ratings = f"INSERT INTO ratings (filename, rating) VALUES {(filename, rating)}"
    result = execute_query(connection, pop_ratings)
    if result:
        return True
    else:
        return False

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