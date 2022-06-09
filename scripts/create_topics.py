from src.acss_core.topics import *
from src.acss_core.event_utls.producer import Producer
from src.acss_core.config import KAFKA_SERVER_URL
from confluent_kafka.admin import AdminClient, NewTopic
from src.acss_core.utils.utils import wait_until_server_is_online
from src.acss_core.logger import logging
from src.acss_core.topics import NUM_OF_PARTITION

_logger = logging.getLogger(__name__)


def sync_create_topics(admin, producer, topics):
    existing_topics = producer.get_existing_topics()
    new_topics = []
    for topic in topics:
        if topic not in new_topics and topic not in existing_topics:
            new_topics.append(topic)
    if new_topics:
        futures = admin.create_topics(
            [NewTopic(topic=topic, num_partitions=NUM_OF_PARTITION, replication_factor=1) for topic in new_topics])
        # Wait for operation to finish.
        for topic, f in futures.items():
            try:
                f.result()  # The result itself is None
            except Exception as e:
                raise Exception(f"Failed to create topic {topic}: {e}")


if __name__ == "__main__":
    wait_until_server_is_online(url=KAFKA_SERVER_URL, logger=_logger)
    admin = AdminClient(
        {'bootstrap.servers': KAFKA_SERVER_URL, 'debug': "admin,broker"})
    producer = Producer()

    topics = [CONTROL_TOPIC, SERVICE_INPUT_TOPIC, SERVICE_OUTPUT_TOPIC,
              SERVICE_OBSERVE_TOPIC, MACHINE_EVENTS, SIMULATION_EVENTS, RECONFIG_TOPIC, PROPOSAL_TOPIC,
              IS_ALIVE, ACTIVE_SERVICES_UPDATED_TOPIC, AGENT_EVENTS]
    print("create topics.")
    sync_create_topics(admin, producer, topics)
    print("wait until topics are created.")
    producer.wait_until_topics_created(topics, max_iterations=10)
    print("topics created.")
