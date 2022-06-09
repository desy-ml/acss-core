import json
import dataclasses
import typing
import time
import datetime
import numpy as np
from io import BytesIO

import dacite
import confluent_kafka

from ..utils.utils import generate_unique_id


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, np.ndarray):
            memfile = BytesIO()
            np.save(memfile, o)
            memfile.seek(0)
            serialized = json.dumps(memfile.read().decode('latin-1'))
            return serialized
        return super().default(o)


class Headers:
    MSG_TYPE_REGISTER = "register"
    MSG_TYPE_DEREGISTER = "deregister"
    MSG_TYPE_INFO = "info"

    def __init__(self,  source: str, package_id=None,  only_for: typing.List[str] = None, msg_type=None,
                 execution_loc=None):
        self.package_id = generate_unique_id() if package_id == None else package_id
        self.source = source
        self.only_for = only_for
        self.msg_type = msg_type  # used by the communication between scheduler and services
        self.execution_loc = execution_loc

    def to_kafka_headers(self) -> typing.Dict[str, bytes]:
        headers = {'source': bytes(self.source, encoding='utf-8')}
        if self.package_id:
            headers['package_id'] = bytes(self.package_id, encoding='utf-8')
        if self.only_for:
            headers['only_for'] = bytes(','.join(self.only_for), encoding='utf-8')
        if self.msg_type:
            headers['msg_type'] = bytes(self.msg_type, encoding='utf-8')
        if self.execution_loc:
            headers['execution_loc'] = bytes(self.execution_loc, encoding='utf-8')

        return headers

    def is_source(self, service_name):
        if self.source:
            return self.source == service_name
        return False

    def is_message_for(self, service_name):
        if self.only_for:
            return service_name in self.only_for
        return False

    def __str__(self):
        return f'Header:[ source: {self.source}, package_id: {self.package_id}, only_for: {",".join(self.only_for) if self.only_for else "None"}, ' \
               f'msg_type: {self.msg_type if self.msg_type else "None"}, execution_log: {self.execution_loc} ]'

    @classmethod
    def from_kafka_headers(cls, headers: typing.List[typing.Tuple[str, bytes]]) -> 'Headers':
        param = {}
        for key, value in headers:
            if key == "only_for":
                param[key] = value.decode('utf-8').split(',') if b',' else [value.decode('utf-8')]
            else:
                param[key] = value.decode('utf-8')
        return cls(**param)


@dataclasses.dataclass
class Message:
    def serialize(self) -> str:
        return json.dumps(self, cls=EnhancedJSONEncoder)

    @classmethod
    def deserialize(cls, messages: typing.Union[typing.List[confluent_kafka.Message], typing.List[bytes]]) -> 'Message':
        """
        Deserialize the message to the specific message data class.
        @param messages: Message received by the Kafa which type is List[confluent_kafka.Message] or by the http client
        which type is List[bytes]
        @return: A dataclass from the specific message
        """
        cls = Message._deserialize(class_type=cls, messages=messages)
        return cls

    @classmethod
    def from_byte_string(cls, byte_str):
        message_dict = json.loads(byte_str)
        return Message._from_dict_to_dataclass(cls, message_dict)


    @staticmethod
    def _deserialize_ndarray(serialized_array):
        memfile = BytesIO()
        memfile.write(json.loads(serialized_array).encode('latin-1'))
        memfile.seek(0)
        return np.load(memfile)

    @staticmethod
    def _deserialize_dict(serialized_dict):
        for key, value in serialized_dict.items():
            # is value a numpy array decoded string?
            if isinstance(value, str) and value[:12] == r'"\u0093NUMPY':
                serialized_dict[key] = Message._deserialize_ndarray(value)
        return serialized_dict

    @staticmethod
    def _from_dict_to_dataclass(class_type: 'Message', message_dict):
        return dacite.from_dict(data_class=class_type, data=message_dict,
                                config=dacite.Config(type_hooks={np.ndarray: Message._deserialize_ndarray,
                                                                 dict: Message._deserialize_dict}))

    @staticmethod
    def _deserialize(class_type: 'Message',
                     messages: typing.Union[typing.List[confluent_kafka.Message], typing.List[bytes]]):

        merged_message_values = ''
        for message in messages:
            merged_message_values += message.decode('utf-8') if type(message) == bytes else message.value().decode(
                'utf-8')

        return class_type.from_byte_string(merged_message_values)

    def get_readable_timestamp(self, fmt: str = '%Y-%m-%d %H:%M:%S') -> str:
        return datetime.datetime.strftime(time.localtime(self.timestamp), fmt)


@dataclasses.dataclass
class AliveMessage(Message):
    info: str
    type: str
    status: str
    category: str


@dataclasses.dataclass
class ControlMessage(Message):
    name: str
    command: str
