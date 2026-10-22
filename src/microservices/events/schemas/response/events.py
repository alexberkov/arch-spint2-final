from pydantic import BaseModel

from schemas.events import Event


class EventResponse(BaseModel):
    status: str
    partition: int
    offset: int
    event: Event
