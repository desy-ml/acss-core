import dataclasses

from .message import Message

PETRA_III_COMMAND_TOPIC = 'petra_III_command_topic'


@dataclasses.dataclass
class Command(Message):
    command: str
    parameter: dict
