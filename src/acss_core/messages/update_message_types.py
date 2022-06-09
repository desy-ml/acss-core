import dataclasses
from typing import List
from xmlrpc.client import Boolean

from .message import Message


@dataclasses.dataclass
class UpdateMessage(Message):
    source: str
    updated: List[str]


@dataclasses.dataclass
class WriteCommand():
    channel: str
    device_name: str
    property: str
    params: dict


@dataclasses.dataclass
class SetMachineMessage(Message):
    is_last_message: Boolean
    write_commands: List[WriteCommand]
