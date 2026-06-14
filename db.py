import psycopg2

def get_connection():

    return psycopg2.connect(
        host="localhost",
        database="smart_meter",
        user="postgres",
        password="Bachi@21389"
    )