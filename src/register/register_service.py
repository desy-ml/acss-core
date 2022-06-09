import json
from collections import OrderedDict
import time
import threading

from src.acss_core.topics import ACTIVE_SERVICES_UPDATED_TOPIC
from src.acss_core.logger import init_logger
from src.acss_core.config import KAFKA_SERVER_URL
from src.acss_core.event_utls.consumer import consume
from src.acss_core.topics import IS_ALIVE
from acss_core.messages.update_message_types import *
from src.acss_core.messages.message import AliveMessage, Headers
from src.acss_core.utils.SqlDBConnector import SqlDBConnector
from src.acss_core.config import MYSQL_USER, MYSQL_PW
from src.acss_core.event_utls.producer import Producer
from src.acss_core.utils.TimerThread import TimerThread

_logger = init_logger(__name__)


class RegisterService():
    def __init__(self, heartbeat_time, db_connector):
        self.heartbeat_time = heartbeat_time
        self.db_connector = db_connector
        self.create_table_if_not_exists("info")
        self.producer = Producer()
        self.garbage_coll_thread = TimerThread(self.heartbeat_time, self._delete_unhealthy_services)
        self.lock = threading.RLock()

    def create_table_if_not_exists(self, table):
        if not self.db_connector.check_if_sql_db_table_exists(table):
            cursor = self.db_connector.sql_con.cursor()
            cursor.execute(f"CREATE TABLE info (name varchar(255) PRIMARY KEY, status varchar(255), timestamp DOUBLE, info varchar(255), type varchar(255), category varchar(255))")
            self.db_connector.sql_con.commit()
            cursor.close()

    def start(self):
        self.producer.wait_until_topics_created([IS_ALIVE], poll_time=1, max_iterations=30)
        self.garbage_coll_thread.start()
        for msg in consume([IS_ALIVE], timeout_poll=0.1, group_id='register', bootstrap_server=KAFKA_SERVER_URL):
            self.health_check(msg)

    def _remove_service_from_database(self, name):
        with self.lock:
            cursor = self.db_connector.sql_con.cursor()
            _logger.debug(f"remove {name} from db")
            cursor.execute(f"DELETE FROM info WHERE name='{name}'")
            self.db_connector.sql_con.commit()
            cursor.close()

    def _delete_unhealthy_services(self):
        current_timestamp = time.time()
        timestamp_service_pairs = self.get_stored_services()
        unhealthy_services = []
        for timestamp, service in timestamp_service_pairs:
            if (current_timestamp - timestamp) > self.heartbeat_time:
                unhealthy_services.append(service)
        for service in unhealthy_services:
            self._remove_service_from_database(service)

    def get_stored_services(self):
        with self.lock:
            cursor = self.db_connector.sql_con.cursor()
            cursor.execute(f"SELECT name, timestamp FROM info")
            result = cursor.fetchall()
            self.db_connector.sql_con.commit()
            cursor.close()
            res_list = [(res[1], res[0]) for res in result]
            res_list.sort()
            return res_list

    def health_check(self, msg):
        _, timestamp = msg.timestamp()
        headers = Headers.from_kafka_headers(msg.headers())
        alive_msg = AliveMessage.deserialize([msg])
        self.update_database(headers.source, alive_msg.status, timestamp/1000.0, alive_msg.info, alive_msg.type, alive_msg.category)
        # self.active_services_updated_event()

    def active_services_updated_event(self):
        self.producer.sync_produce(ACTIVE_SERVICES_UPDATED_TOPIC, json.dumps(self.services), Headers(package_id=None, source='register'))

    def update_database(self, service_name, status, timestamp, info, type, cat):
        with self.lock:
            cursor = self.db_connector.sql_con.cursor()
            cursor.execute(
                f"INSERT INTO info (name, status, timestamp, info, type, category) values ('{service_name}', '{status}', {timestamp}, '{info}', '{type}', '{cat}') ON DUPLICATE KEY UPDATE timestamp={timestamp}, status='{status}'")
            self.db_connector.sql_con.commit()
            cursor.close()


if __name__ == "__main__":
    obs = RegisterService(heartbeat_time=2.0, db_connector=SqlDBConnector(user=MYSQL_USER, pw=MYSQL_PW, host="register_database", port=3306, database='services'))
    obs.start()
