import yaml
import logging
import os

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


PATH_TO_ACSS_SERVICES_ROOT = os.environ.get('PATH_TO_ACSS_SERVICES_ROOT')

ACSS_CONFIG_FILEPATH = os.environ.get('ACSS_CONFIG_FILEPATH', 'ml-pipe-config.yaml')

with open(ACSS_CONFIG_FILEPATH, 'r') as file:
    pipe_conf = yaml.load(file, Loader=yaml.FullLoader)

msg_bus_settings = pipe_conf.get('msg_bus')
if msg_bus_settings is None:
    raise ValueError(f"Message bus is not configured. Please add msg_bus key to config file.")
else:
    broker_urls = msg_bus_settings.get("broker_urls")
    if broker_urls != None:
        brokers = [b.strip() for b in broker_urls.split(',')]
        KAFKA_SERVER_URL = brokers[0]
    if KAFKA_SERVER_URL == None:
        raise ValueError(f"No broker is set.")

sim_settings = pipe_conf.get('simulation')
if sim_settings is None:
    raise ValueError(f"Simulation is not configured. Please add simulation key to config file.")
MYSQL_USER = sim_settings.get("sim_db_usr")
if MYSQL_USER == None:
    raise ValueError("sim_db_usr key is not set in config.")
MYSQL_PW = sim_settings.get("sim_db_pw")
if MYSQL_PW == None:
    raise ValueError("sim_db_pw key is not set in config.")
MYSQL_HOST, MYSQL_PORT = sim_settings.get('sim_db_url').strip().split(':')
if MYSQL_HOST == None:
    raise ValueError("sim_db_url key is not set in config.")

obs_settings = pipe_conf.get("observer")
if obs_settings is None:
    raise ValueError(f"Observer is not configured. Please add observer key to config file.")
OBSERVER_URL = obs_settings.get('url')
if OBSERVER_URL is None:
    raise ValueError("url key for observer frontend is not set in config.")
PIPE_EVENT_DB_USER = obs_settings.get("event_db_usr")
if PIPE_EVENT_DB_USER == None:
    raise ValueError("event_db_usr key is not set in config.")
PIPE_EVENT_DB_PW = obs_settings.get("event_db_pw")
if PIPE_EVENT_DB_PW == None:
    raise ValueError("event_db_pw key is not set in config.")
PIPE_EVENT_DB_URL = obs_settings.get("event_db_url", "observer_database")

register_settings = pipe_conf.get("register")
if obs_settings is None:
    raise ValueError(f"Register is not configured. Please add register key to config file.")
REGISTER_URL = register_settings.get('url')

if REGISTER_URL is None:
    raise ValueError("url key for register frontend is not set in config.")


LOGSTASH_SERVER_URL = None
LOGSTASH_PORT = None
logging_settings = pipe_conf.get("logging")
if logging_settings is not None:
    logstash_url = logging_settings.get("logstash_url")
    if logstash_url is not None:
        LOGSTASH_SERVER_URL, LOGSTASH_PORT = logstash_url.strip().split(':')

_logger.info(f"KAFKA_SERVER_URL={KAFKA_SERVER_URL}")
_logger.info(f"MYSQL_HOST={MYSQL_HOST}")
_logger.info(f"MYSQL_PORT={MYSQL_PORT}")
_logger.info(f"MYSQL_USER={MYSQL_USER}")
