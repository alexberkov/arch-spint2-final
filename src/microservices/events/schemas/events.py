from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class EventType(Enum):
    user = 'user'
    payment = 'payment'
    movie = 'movie'


class Event(BaseModel):
    id: str
    type: EventType
    timestamp: datetime
    payload: dict = dict()
