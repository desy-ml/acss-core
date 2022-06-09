from time import time


def check_if_sql_db_table_exists(connection, tablename):
    cursor = connection.cursor()

    sql_query = f"select COUNT(*) from information_schema.tables where TABLE_NAME='{tablename}'"
    cursor.execute(sql_query)
    table_count = cursor.fetchone()[0]
    connection.commit()
    if table_count == 1:
        cursor.close()
        return True
    cursor.close()
    return False


def check_if_sql_table_is_filled(connection, tablename):
    cursor = connection.cursor()

    sql_query = f"select COUNT(*) from {tablename}"
    cursor.execute(sql_query)
    count = cursor.fetchone()[0]
    connection.commit()
    if count > 0:
        cursor.close()
        return True
    cursor.close()
    return False
