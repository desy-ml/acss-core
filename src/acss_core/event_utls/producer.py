import time
import typing

import confluent_kafka

from ..config import KAFKA_SERVER_URL
from ..messages.message import Headers
from ..topics import NUM_OF_PARTITION


class Producer:
    def __init__(self, event_server_url=KAFKA_SERVER_URL):
        self._producer = confluent_kafka.Producer({'bootstrap.servers': event_server_url,
                                                   'topic.metadata.refresh.interval.ms': 10,
                                                   'message.max.bytes': 52428800})  # Because of slow on first message. 1.7.0 should fix it but its still there. https://github.com/confluentinc/confluent-kafka-dotnet/issues/701
        #self._producer = confluent_kafka.Producer({'bootstrap.servers': event_server_url, 'message.max.bytes': 52428800})

    def _produce(self, topic, value, headers: Headers, is_async=False):

        self._producer.produce(topic, value=value, headers=headers.to_kafka_headers())
        if is_async:
            self._producer.poll(1)
        else:
            self._producer.flush()

    def async_produce(self, topic, value, headers):
        self._produce(topic, value, headers=headers, is_async=True)

    def all_partitions_produce(self, topic, value, headers):
        for p_id in range(NUM_OF_PARTITION):
            self._producer.produce(topic, partition=p_id, value=value, headers=headers.to_kafka_headers())
        self._producer.poll(1)

    def sync_produce(self, topic, value, headers):
        self._produce(topic, value, headers=headers, is_async=False)

    def get_existing_topics(self) -> typing.List[str]:
        metadata = self._producer.list_topics()
        self._producer.flush()
        return [key for key, _ in metadata.topics.items()]

    def is_topic_created(self, topic):
        metadata = self._producer.list_topics(topic=topic)
        self._producer.flush()
        # there is just one topic in topics
        topic_metadata = metadata.topics.get(topic)
        if not topic_metadata:
            return False
        else:
            return metadata.topics[topic].error

    def get_search_for_topic(self, topic) -> typing.List[str]:
        metadata = self._producer.list_topics(topic=topic)
        self._producer.flush()

        res = {key: value.error for key, value in metadata.topics.items()}
        for topic, error in res.items():
            print(f"Error messages from topic '{topic}': {error}")
        return res

    def wait_until_topics_created(self, topics, poll_time=0.5, max_iterations=0):
        # Wait for full metadata state for topics
        # https://github.com/confluentinc/confluent-kafka-python/issues/524
        all_topics_created = False
        iter_count = 0
        while not all_topics_created and iter_count <= max_iterations:
            all_topics_created = True
            for topic in topics:
                existing_topics = self.get_search_for_topic(topic=topic)
                if existing_topics.get(topic) and existing_topics[topic]:
                    all_topics_created = False
                    time.sleep(poll_time)
                    break
            if max_iterations != 0:
                iter_count += 1

        if max_iterations < iter_count:
            raise TimeoutError
