import dataclasses
import typing
import numpy as np

from confluent_kafka import TIMESTAMP_CREATE_TIME
from src.acss_core.utils.utils import create_timestamp
from src.acss_core.messages.message import Message, Headers


class KafkaMessageMock:
    def __init__(self, serialized_message, headers: Headers):
        self.byte_msg = bytes(serialized_message,
                              'utf-8') if serialized_message else None
        self.kafka_headers_dict = headers.to_kafka_headers() if headers else None

    def value(self):
        return self.byte_msg

    def headers(self):
        return [(key, value) for key, value in self.kafka_headers_dict.items()]

    def timestamp(self):
        return TIMESTAMP_CREATE_TIME, create_timestamp()


def test_message_serialize_deserialize():
    msg = Message()
    serialized_msg = msg.serialize()

    kafka_msg = KafkaMessageMock(
        serialized_msg, Headers(source='service_name'))

    deserialized_msg = Message.deserialize([kafka_msg])

    assert msg == deserialized_msg


def test_message_serialize_deserialize_with_np_array():
    @dataclasses.dataclass
    class MessageWithNumpyArray(Message):
        arr: np.ndarray

        def __eq__(self, other):
            are_base_attr_eql = super().__eq__(other)
            are_all_close = np.allclose(other.arr, self.arr)
            return are_base_attr_eql and are_all_close

    msg = MessageWithNumpyArray(arr=np.random.randint(1, 100, [10, 20]))

    serialized_msg = msg.serialize()

    kafka_msg = KafkaMessageMock(
        serialized_msg, Headers(source='service_name'))

    deserialized_msg = MessageWithNumpyArray.deserialize([kafka_msg])

    assert msg == deserialized_msg


def test_message_serialize_deserialize_with_list_of_dataclass():
    @dataclasses.dataclass
    class MyDataClass():
        cmd: str
        params: list

        def __eq__(self, other):
            return self.cmd == other.cmd and self.params == other.params

    @dataclasses.dataclass
    class MessageWithListOfDataclass(Message):
        cmds: typing.List[MyDataClass]

    msg = MessageWithListOfDataclass(cmds=[MyDataClass('get', [1, 2]), MyDataClass('set', [3, 4])])

    serialized_msg = msg.serialize()

    kafka_msg = KafkaMessageMock(
        serialized_msg, Headers(source='service_name'))

    deserialized_msg = MessageWithListOfDataclass.deserialize([kafka_msg])

    assert msg.cmds == deserialized_msg.cmds


def test_message_serialize_deserialize_with_np_array_in_dict():
    @dataclasses.dataclass
    class MessageWithNumpyArrayInDict(Message):
        param: dict

        def __eq__(self, other):
            are_base_attr_eql = super().__eq__(other)
            is_param_eql = True
            for key, value in self.param.items():
                other_val = other.param.get(key, None)
                if other_val is None or type(value) != type(other_val):
                    is_param_eql = False
                    break
                elif isinstance(value, np.ndarray):
                    are_all_close = np.allclose(value, other_val)
                    if not are_all_close:
                        is_param_eql = False
                        break
                else:
                    if not value == other_val:
                        is_param_eql = False
                        break

            return are_base_attr_eql and is_param_eql

    msg = MessageWithNumpyArrayInDict(param={'arr': np.random.randint(1, 100, [10, 20]), 'info': 'info'})

    serialized_msg = msg.serialize()

    kafka_msg = KafkaMessageMock(
        serialized_msg, Headers(source='service_name'))

    deserialized_msg = MessageWithNumpyArrayInDict.deserialize([kafka_msg])

    assert msg == deserialized_msg
