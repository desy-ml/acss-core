import sys
from typing import Union, List

from confluent_kafka import Consumer, KafkaError, KafkaException, TopicPartition

from ..config import KAFKA_SERVER_URL


def consume(topics: Union[List[str], List[TopicPartition]], group_id: str, timeout_poll: int = 0.1, max_session: int = 0,
            consumer_started_hook=None, all_msg_hook=None, stop_hook=None, bootstrap_server=KAFKA_SERVER_URL):
    """        
    Returns a message, when a new message is available in subscribed topics.
    @param topics: Topics that will be consumed. Can be a List of strings with the topic names or a list of TopicPartitions
    @param group_id: Consumer's group_id
    @param timeout_poll: Maximal waiting time for a new message.
    @param max_session: Maximum iterations, when the maximum is reached a TimeoutError exception will be thrown.
    @param consumer_started_hook: A function that is called after the consumer is initialized and is conusming the topic.
    @param all_msg_hook: A function that is called after the consumer.poll function.
    @param stop_hook: A function that returns bool. If the functions returns true, consuming will be stopped.
    @return: Message of type KafkaMessage.        
    """
    settings = {
        'bootstrap.servers': bootstrap_server,
        'group.id': group_id,
        'auto.offset.reset': 'latest',
        'enable.partition.eof': True if consumer_started_hook else False
    }

    print(f"consumer settings: {settings}")

    consumer = Consumer(settings)

    if all(isinstance(x, str) for x in topics):
        consumer.subscribe(topics)
    else:
        consumer.assign(topics)
    session = 0
    message_published = False
    while True:
        if stop_hook and stop_hook():
            break
        msg = consumer.poll(timeout_poll)
        if all_msg_hook:
            all_msg_hook(msg)
        if max_session and session > max_session:
            raise TimeoutError
        if msg is None:
            session += 1
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # https://github.com/confluentinc/confluent-kafka-python/issues/156
                # https://github.com/confluentinc/confluent-kafka-python/issues/581
                if not message_published and consumer_started_hook:
                    consumer_started_hook()
                    message_published = True
                # End of partition event
                sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                 (msg.topic(), msg.partition(), msg.offset()))
            elif msg.error():
                # https://github.com/edenhill/librdkafka/issues/1987
                if msg.error().code() == KafkaError._TRANSPORT:
                    sys.stderr.write(
                        'GroupCoordinator response error: Local: Broker transport failure')
                else:
                    raise KafkaException(msg.error())
        yield msg
    consumer.close()
