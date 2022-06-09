from src.acss_core.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PW
from adapter.petra.PetraSimDatabase import PetraSimDatabase


if not MYSQL_PORT:
    MYSQL_PORT = '3306'

if MYSQL_USER == None:
    raise Exception(f"Environment Value SIM_SQL_USER isn't set. Please set the value in .env file.")

if MYSQL_PW == None:
    raise Exception(f"Environment Value SIM_SQL_PW isn't set. Please set the value in .env file.")

if MYSQL_HOST == None:
    raise Exception(f"Environment Value SIM_SQL_HOST isn't set. Please set the value in .env file.")


print(f"Environment MYSQL_HOST: {MYSQL_HOST}")


if __name__ == "__main__":

    db = PetraSimDatabase()
    db.create_petra_tables()
    print("Database filled.")
