import http

from flask import Flask, request, make_response
from flask_pymongo import PyMongo

from src.acss_core.logger import init_logger
from src.acss_core.config import PIPE_EVENT_DB_URL, PIPE_EVENT_DB_PW, PIPE_EVENT_DB_USER

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
# TODO: Why do I have to use authSource=admin for authentication https://stackoverflow.com/questions/37945262/authentication-failed-when-using-flask-pymongo
app.config["MONGO_URI"] = f"mongodb://{PIPE_EVENT_DB_USER}:{PIPE_EVENT_DB_PW}@{PIPE_EVENT_DB_URL}:27017/service_data?authSource=admin"
mongo = PyMongo(app)


@app.route('/')
def is_alive():
    return "I'm alive\n"


@app.route('/find/<ids>/<service_type>', methods=['GET', 'OPTIONS'])
def get_service(ids, service_type):
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        split_ids = ids.split(',')
        query = {"id": {"$in": split_ids}, "service_type": service_type}, {'_id': False}
        _logger.debug(f"query: {query}")
        doc_stream = mongo.db.service_data.find({"id": {"$in": split_ids}, "service_type": service_type}, {'_id': False})
        docs = []
        found_ids = set()
        for doc in doc_stream:
            docs.append(doc['data'])
            found_ids.add(doc['id'])

        _logger.debug(docs)

        if len(split_ids) == len(found_ids):
            return {'data': docs}, http.HTTPStatus.OK, {'Content-Type': 'application/json; charset=utf-8', "Access-Control-Allow-Origin": "*"}
        else:
            return {}, http.HTTPStatus.ACCEPTED, {'Content-Type': 'application/json; charset=utf-8', "Access-Control-Allow-Origin": "*"}


if __name__ == '__main__':
    app.run(debug=True, port=5003, host='0.0.0.0')
