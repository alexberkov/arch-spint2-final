import os

from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI

from services.events import EventService
from api import events

load_dotenv()

EVENTS_HOST = os.getenv("EVENTS_HOST", "http://127.0.0.1")
EVENTS_PORT = os.getenv("PORT", "8082")


@asynccontextmanager
async def lifespan(app: FastAPI):
    service = EventService()
    await service.start()
    app.state.event_service = service
    yield
    await service.stop()


app = FastAPI(
    lifespan=lifespan,
    title='Events Service',
    description='Produce & consume events using AIOKafka',
    servers=[
        {"url": f"{EVENTS_HOST}:{EVENTS_PORT}"}
    ],
)


app.include_router(events.router, prefix='/api/events', tags=['events'])
