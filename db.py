import psycopg2
from decouple import config

def get_db_conn(): 
    conn = psycopg2.connect(
            host=config("DB_HOST"),
            port=config("DB_PORT"),
            database=config("DB_NAME"),
            user=config("DB_USERNAME"),
            password=config("DB_PASSWORD")
    )
    conn.set_session(autocommit=True)

    return conn

def get_cursor():
    conn = get_db_conn()
    cur = conn.cursor()

    return cur

def get_data_as_dict(query, *args):
    conn = get_db_conn()
    cur = get_cursor()

    cur.execute(query=query, vars=args)
    
    result = cur.fetchall()
    count = cur.rowcount

    cur.close()
    conn.close()
    
    return count, result

def insert_data(query, *args):
    conn = get_db_conn()
    cur = get_cursor()

    cur.execute(query, (args))

    count = cur.rowcount
    result = cur.fetchone()
    
    cur.close()
    conn.close()

    return count, result