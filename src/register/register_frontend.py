import http
import time

from flask import Flask, request, make_response
from flaskext.mysql import MySQL

from src.acss_core.logger import init_logger
from src.acss_core.config import MYSQL_USER, MYSQL_PW
from src.acss_core.config import MYSQL_PW, MYSQL_USER
from src.acss_core.utils.sql_utils import check_if_sql_db_table_exists

_logger = init_logger(__name__)


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response


def create_app():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    return app


app = create_app()
# connect to mysql
app.config['MYSQL_DATABASE_HOST'] = "register_database"
app.config['MYSQL_DATABASE_USER'] = MYSQL_USER
app.config['MYSQL_DATABASE_PASSWORD'] = MYSQL_PW
app.config['MYSQL_DATABASE_DB'] = 'services'
mysql = MySQL(app)


@app.route('/')
def is_alive():
    return "I'm alive\n"


def wait_until_table_created(table_name):
    max_retries = 50
    connection = None
    for _ in range(max_retries):
        try:
            connection = mysql.get_db()
        except:
            _logger.debug("Connect to sql db failed. Try to reconnect in 0.25s")
            time.sleep(0.25)
        if connection is not None:
            break
    if connection is None:
        raise Exception("Table 'info' doesn't exists. Connection timeout reached.")

    is_table_available = False
    for _ in range(max_retries):
        is_table_available = check_if_sql_db_table_exists(mysql.get_db(), table_name)
        if is_table_available:
            break
        _logger.debug("Table 'info' doesn't exists. Retry in 0.25s.")
        time.sleep(0.25)
    if not is_table_available:
        raise Exception("Connection established but table 'info' doesn't exists. Timeout reached.")


def find_service_query(name):
    print("mysql.get_db().cursor()")
    cursor = mysql.get_db().cursor()
    cursor.execute(f"SELECT name, status, timestamp FROM info where name = '{name}'")
    result = cursor.fetchall()
    mysql.get_db().commit()
    cursor.close()
    if len(result) == 0:
        return {}
    else:
        print(f"--->>> result: {result}")
        return{"name": result[0][0], "status": result[0][1], "timestamp": result[0][2]}


@app.route('/services/find/<name>', methods=['GET', 'OPTIONS'])
def find_service(name):
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        res = find_service_query(name)
        if not res:
            return {}, http.HTTPStatus.OK
        else:
            return res, http.HTTPStatus.OK


@app.route('/register/<name>', methods=['GET', 'OPTIONS'])
def register(name):
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        wait_until_table_created('info')
        res = find_service_query(name)
        if res:
            return {"message": f"Service with name {name} already exists."}, http.HTTPStatus.CONFLICT

        return {}, http.HTTPStatus.OK


@app.route('/services/', methods=['GET', 'OPTIONS'])
def get_services():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        wait_until_table_created('info')
        cursor = mysql.get_db().cursor()
        cursor.execute(f"SELECT name, info, type, status, category FROM info")
        result = cursor.fetchall()
        mysql.get_db().commit()
        cursor.close()
        return {"services": {res[0]: {'info': res[1], 'type': res[2], 'status': res[3], 'cat': res[4]} for res in result}}, http.HTTPStatus.OK, {'Content-Type': 'application/json; charset=utf-8', "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"} 


if __name__ == '__main__':
    app.run(debug=True, port=5004, host='0.0.0.0')
