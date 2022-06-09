import dataclasses
from typing import Optional

from .message import Message


@dataclasses.dataclass
class SimpleServiceMessage(Message):
    params: Optional[dict]
