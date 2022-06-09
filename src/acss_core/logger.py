import logging
import sys
import os
import logstash

from .utils.utils import wait_until_server_is_online
from .config import LOGSTASH_SERVER_URL, LOGSTASH_PORT


def init_logger(logger_name, log_lvl=logging.DEBUG):
    _logger = logging.getLogger(logger_name)
    _logger.setLevel(log_lvl)
    if LOGSTASH_SERVER_URL != None and LOGSTASH_PORT != None:
        wait_until_server_is_online(LOGSTASH_SERVER_URL + ":" + LOGSTASH_PORT, logger=_logger)
        _logger.addHandler(logstash.TCPLogstashHandler(LOGSTASH_SERVER_URL, LOGSTASH_PORT, version=1))
        _logger.info(f"Logging is set to logstash")
    else:
        _logger.warning(f"Environment value LOGSTASH_SERVER_URL isn't set. Service will not log in central Log DB only to stdout.")
        _logger.info("Logging is set to stdout.")

    return _logger


path_to_logfile = os.environ.get('MPY_ML_PIPE_KAFKA_LOG_FILE_PATH')

if path_to_logfile:
    logging.basicConfig(
        filename=path_to_logfile,
        format='[%(asctime)s.%(msecs)03d] %(levelname)-4s  %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(
        stream=sys.stdout,
        format='[%(asctime)s.%(msecs)03d] %(levelname)-4s  %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
