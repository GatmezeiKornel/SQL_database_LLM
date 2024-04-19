import psycopg2
import pandas as pd

def connect_to_db(host: str, dbname: str, user: str, password: str):
    """Connecting to azure postgreSQL database
    
    Parameters:
    - host: Azure Server Name
    - dbname: The name of the database being connected to in the postgreSQL resource
    - user: The username of the connection
    - password: The password associated with the user

    Returns:
    - conn: psycopg2 connection variable used to create a cursor for database queries
    """
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, "require")
    conn = psycopg2.connect(conn_string) 
    print("Connection established")
    return conn

def create_table(table: str, attr: str, conn):
    """Creating postgreSQL table using psycopg2 connection variable
    
    Parameters:
    - table: the name of the table being created
    - attr: the attributes of the table being created. The format is the following: (attr1 [constraintsOfAttr1], attr2 [constraintsOfAttr2], ...)
    - conn: psycopg2 connection variable
    """
    cursor = conn.cursor()
    # cursor.execute(f"DROP TABLE IF EXISTS {table};")
    # print("Finished dropping table (if existed)")

    cursor.execute(f"CREATE TABLE {table} {attr};")
    print("Finished creating table")

def insert_item(table: str, attr: str, row: str, conn):
    """Inserting to a postgreSQL table using psycopg2 connection variable
    
    Parameters:
    - table: the name of the target table being inserted into
    - attr: the attributes of the target table. The format is the following: (attr1, attr2, ...)
    - row: the values of the row being inserted. The format is the following: (value1, value2, ...)
    - conn: psycopg2 connection variable
    """
    cursor = conn.cursor()
    placeholder = ", ".join(["%s" for i in range(len(row))])
    cursor.execute(f"INSERT INTO {table} {attr} VALUES ({placeholder});", row)

def read_db(query: str, conn) -> pd.DataFrame:
    """Querying postgreSQL database using psycopg2 connection variable
    
    Parameters:
    - query: the query being used in the database
    - conn: psycopg2 connection variable

    Returns:
    - the result of the query in pandas Dataframe format
    """
    cursor = conn.cursor()
    cursor.execute(f"{query};")
    rows = cursor.fetchall()
    
    return pd.DataFrame(rows)

def close_connection(conn):
    """Close the connection to the database"""
    conn.commit()
    conn.cursor().close()
    conn.close()