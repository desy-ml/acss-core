import typing

from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient

from src.config import KAFKA_SERVER_URL


def get_existing_topics(kafka_producer) -> typing.List[str]:
    metadata = kafka_producer.list_topics()
    kafka_producer.flush()
    return list(filter(lambda topic: topic[:2] != "__", [key for key, _ in metadata.topics.items()]))


if __name__ == "__main__":
    producer = Producer({'bootstrap.servers': KAFKA_SERVER_URL})
    admin = AdminClient({'bootstrap.servers': KAFKA_SERVER_URL})
    r = get_existing_topics(producer)
    print(r)
    admin.delete_topics(r)
