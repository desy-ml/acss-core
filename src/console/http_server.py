import http

from flask import Flask, request, make_response
from src.acss_core.logger import init_logger
from src.console.compose_client import DockerComposeClient
from src.acss_core.client.kafka_client import KafkaPipeClient


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
pipe_client = KafkaPipeClient()

global compose_client
compose_client = DockerComposeClient(64)


@app.route('/')
def is_alive():
    return "I'm alive\n"


@app.route('/start/services', methods=['GET', 'OPTIONS'])
def get_service():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        services = compose_client.get_services()
        print(services)
        return {'services': services}, http.HTTPStatus.OK, {'Content-Type': 'application/json; charset=utf-8', "Access-Control-Allow-Origin": "*"}


@app.route('/start/<name>/<service_type>/<mode>', methods=['GET', 'OPTIONS'])
def start_service(name, service_type, mode):
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        services = compose_client.get_services()
        print(services)
        if service_type not in services:
            return f"service type '{service_type}' does not exists.", http.HTTPStatus.BAD_REQUEST, {'Content-Type': 'application/json; charset=utf-8', "Access-Control-Allow-Origin": "*"}

        compose_client.run_service(name=name, service_type=service_type, mode=mode)
        return '', http.HTTPStatus.OK, {'Content-Type': 'application/json; charset=utf-8', "Access-Control-Allow-Origin": "*"}


@app.route('/stop/<name>', methods=['GET', 'OPTIONS'])
def stop_service(name):
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        pipe_client.stop_service(name)

        return '', http.HTTPStatus.OK, {'Content-Type': 'application/json; charset=utf-8', "Access-Control-Allow-Origin": "*"}


@app.route('/services', methods=['GET', 'OPTIONS'])
def get_running_services():
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_prelight_response()
    else:
        res = pipe_client.get_running_service_info()
        return {'services': res}, http.HTTPStatus.OK, {'Content-Type': 'application/json; charset=utf-8', "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "*"}


if __name__ == '__main__':
    app.run(debug=True, port=5002, host='0.0.0.0')
