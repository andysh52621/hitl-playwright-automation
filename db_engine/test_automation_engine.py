import logging
import os
import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

hitlLogger = logging.getLogger("HitlLogger")


def get_test_db_engine():
    server = 'vzn-eastus2-hitl-task-manager-dev-sql-01.database.windows.net'
    database = 'HITLDB'

    # 🔐 Securely load SQL login credentials
    sql_username = "HITL-DB-USER"  # SQL user name
    sql_password = os.environ.get("SANDBOX_DB_PASS")  # SQL user password

    if not sql_username or not sql_password:
        raise EnvironmentError("Missing SQL credentials (HITL_DB_USER / HITL_DB_USER_PASSWORD)")

    # 🔧 No 'Authentication' needed for SQL logins
    params = urllib.parse.quote_plus(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={sql_username};'
        f'PWD={sql_password};'
    )

    return create_engine(f'mssql+pyodbc:///?odbc_connect={params}')


def get_app_db_engine(test_user):
    server = f'vzn-eastus2-hitl-task-manager-{test_user.test_env}-sql-01.database.windows.net'
    database = 'HITLDB'

    # 🔐 Securely load SQL login credentials
    sql_username = "HITL-DB-USER"  # SQL user name
    sql_password = os.environ.get("DYNAMIC_DB_PASS")  # SQL user password

    if not sql_username or not sql_password:
        raise EnvironmentError("Dynamic DB Pass Missing SQL credentials (HITL_DB_USER / HITL_DB_USER_PASSWORD)")

    # 🔧 No 'Authentication' needed for SQL logins
    params = urllib.parse.quote_plus(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={sql_username};'
        f'PWD={sql_password};'
    )
    # hitlLogger.info(f"params= {params}")
    return create_engine(f'mssql+pyodbc:///?odbc_connect={params}')


def get_app_db_session(test_user):
    engine = get_app_db_engine(test_user)
    Session = sessionmaker(bind=engine)
    return Session()


def get_test_db_session():
    engine = get_test_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()
