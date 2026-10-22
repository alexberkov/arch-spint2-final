from datetime import datetime

from pydantic import BaseModel


class UserEventInput(BaseModel):
    user_id: int
    username: str
    email: str | None = None
    action: str
    timestamp: datetime


class MovieEventInput(BaseModel):
    movie_id: int
    user_id: int
    title: str
    action: str
    rating: float | None = None
    genres: list[str] | None = None
    description: str | None = None


class PaymentEventInput(BaseModel):
    user_id: int
    payment_id: int
    amount: float
    status: str
    method_type: str
    timestamp: datetime
