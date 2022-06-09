from logging import log
import time
import datetime
import socket
import uuid


def create_timestamp() -> int:
    """
    Creates a timestamp.
    @return: number of milliseconds since the epoch (UTC).
    """
    return datetime.datetime.utcnow().timestamp() * 1000


def timestamp_to_date(t: int) -> str:
    return str(datetime.datetime.utcfromtimestamp(t / 1000.0))


def check_connection(url: str, logger=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(20)
    result = sock.connect_ex((url.split(':')[0], int(url.split(':')[1])))
    if result != 0:
        if logger != None:
            logger.error(f"Can't connect to address: {url}")
        raise ConnectionError(f"Can't connect to address: {url}")
    sock.close()


def wait_until_server_is_online(url, logger, sleep_time: int = 2, retries: int = 15) -> None:
    for _ in range(retries):
        try:
            check_connection(url, logger)
        except ConnectionError as e:
            time.sleep(sleep_time)
            if logger != None:
                logger.info(f"Try again to reconnect to server {url}")


def generate_unique_id():
    return str(uuid.uuid4())
