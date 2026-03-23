import polars as pl
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import polars as pl
from queries import treatment_team_query, emrn_query
import time
import os

def wake_up_azure(db_pwd=None):
    if db_pwd is None:
        db_pwd = os.getenv('AZURE_DB_PASSWORD')

    azure_server = os.getenv('AZURE_DB_SERVER')
    azure_database = os.getenv('AZURE_DB_NAME')
    azure_user = os.getenv('AZURE_DB_USER')

    connection_string_write = 'Driver={ODBC Driver 17 for SQL Server};' \
                              f'Server={azure_server};' \
                              f'Database={azure_database};' \
                              f'UID={azure_user};' \
                              'PWD=' + str(db_pwd)
    connection_string = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string_write})
    retries = 3
    delay = 60  # seconds
    
    for attempt in range(1, retries + 1):
        try:
            engine = create_engine(connection_string)
            # Test the connection
            with engine.connect() as connection:
                print(f"Connected to SQL Server on attempt {attempt}")
                engine.dispose()
                return None
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Failed to connect after 3 attempts")
                raise

def extractAzureData(query):
    azure_server = os.getenv('AZURE_DB_SERVER')
    azure_database = os.getenv('AZURE_DB_NAME')
    azure_user = os.getenv('AZURE_DB_USER')
    azure_password = os.getenv('AZURE_DB_PASSWORD')

    connection_string = 'Driver={ODBC Driver 17 for SQL Server};' \
                              f'Server={azure_server};' \
                              f'Database={azure_database};' \
                              f'UID={azure_user};' \
                              f'PWD={azure_password}'
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    engine = create_engine(connection_url)
    
    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = result.fetchall()
        columns = result.keys()

    df = pl.DataFrame(rows, schema=columns)
    return df

def fetch_treatment_team(encounters_and_dates=None):
    if encounters_and_dates == None:
        return "Needs list of encounters and dates."

    clarity_server = os.getenv('CLARITY_DB_SERVER')
    clarity_database = os.getenv('CLARITY_DB_NAME')

    connection_string = 'Driver={ODBC Driver 17 for SQL Server};' \
                        f'Server={clarity_server};' \
                        f'Database={clarity_database};' \
                        'Trusted_Connection=yes;'
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    engine = create_engine(connection_url)

    with engine.connect() as connection:
        rows = []
        for (encounter_id, alert_date) in encounters_and_dates:
            result = connection.execute(
                text(treatment_team_query),
                {"encounter_id": encounter_id, "alert_date": alert_date}
            )
            rows += result.fetchall()
        columns = result.keys()

    df = pl.DataFrame(rows, schema=columns)

    return df

def fetch_emrns(encounters=None):
    if encounters == None:
        return "Needs list of encounters."

    clarity_server = os.getenv('CLARITY_DB_SERVER')
    clarity_database = os.getenv('CLARITY_DB_NAME')

    connection_string = 'Driver={ODBC Driver 17 for SQL Server};' \
                        f'Server={clarity_server};' \
                        f'Database={clarity_database};' \
                        'Trusted_Connection=yes;'
    connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
    engine = create_engine(connection_url)

    with engine.connect() as connection:
        rows = []
        for encounter_id in encounters:
            result = connection.execute(
                text(emrn_query),
                {"encounter_id": encounter_id}
            )
            rows += result.fetchall()
        columns = result.keys()

    df = pl.DataFrame(rows, schema=columns)

    return df