import time
from ..logger import init_logger
from ..utils.sql_utils import check_if_sql_db_table_exists, check_if_sql_table_is_filled
import mysql.connector
_logger = init_logger(__name__)


class SqlDBConnector():
    def __init__(self, user, pw, host, port, database):
        self.sql_con = self.connect_to_db(user, pw, host, port, database)

    def check_if_sql_db_table_exists(self, tablename):
        return check_if_sql_db_table_exists(self.sql_con, tablename)

    def check_if_sql_table_is_filled(self, tablename):
        return check_if_sql_table_is_filled(self.sql_con, tablename)

    def connect_to_db(self, user, pw, host, port, database):
        while(True):
            try:
                cnx = mysql.connector.connect(user=user, password=pw, host=host, port=port, database=database)
                break
            except Exception as e:
                if e.errno == mysql.connector.errorcode.CR_UNKNOWN_HOST or e.errno == mysql.connector.errorcode.CR_CONN_HOST_ERROR:
                    time.sleep(0.5)
                    _logger.debug(f"Try to connect again. error: {e}")
                    continue
                else:
                    raise e
        return cnx

    def wait_until_table_is_created(self, table: str):
        while(True):
            try:                
                if self.check_if_sql_db_table_exists(table) and self.check_if_sql_table_is_filled(table):
                    return
            except mysql.connector.errors.ProgrammingError as mysql_error:
                if mysql_error.errno == mysql.connector.errorcode.ER_NO_SUCH_TABLE:                
                    _logger.warning(f"Table {table} doesn't exists.")
                    time.sleep(0.5)