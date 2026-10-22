from datetime import datetime

from fastapi import APIRouter, status, Request, Depends
from fastapi.responses import JSONResponse

from schemas.events import Event
from schemas.response.events import EventResponse
from schemas.request.events import (
    UserEventInput, MovieEventInput, PaymentEventInput
)

from services.events import EventService

router = APIRouter()


def get_event_service(request: Request) -> EventService:
    return request.app.state.event_service


@router.get('/health', status_code=status.HTTP_200_OK, summary='Health check')
async def health_check():
    return JSONResponse(status_code=status.HTTP_200_OK, content={'status': True})


@router.post('/movie', response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             summary='Movie event', description='Process movie event.',
             response_description='Movie event information.')
async def process_movie_event(
        event_info: MovieEventInput,
        service: EventService = Depends(get_event_service)
) -> EventResponse:
    event: Event = Event(
        id=f'movie-{event_info.movie_id}-viewed',
        type='movie', timestamp=datetime.now()
    )
    await service.produce_event(event)
    return EventResponse(status='success', partition='1', offset='0', event=event)


@router.post('/user', response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             summary='User event', description='Process user event.',
             response_description='User event information.')
async def process_user_event(
        event_info: UserEventInput,
        service: EventService = Depends(get_event_service)
) -> EventResponse:
    event: Event = Event(
        id=f'user-{event_info.user_id}-registered',
        type='user', timestamp=event_info.timestamp
    )
    await service.produce_event(event)
    return EventResponse(status='success', partition='1', offset='0', event=event)


@router.post('/payment', response_model=EventResponse, status_code=status.HTTP_201_CREATED,
             summary='Payment event', description='Process payment event.',
             response_description='Payment event information.')
async def process_payment_event(
        event_info: PaymentEventInput,
        service: EventService = Depends(get_event_service)
) -> EventResponse:
    event: Event = Event(
        id=f'payment-{event_info.payment_id}-completed',
        type='payment', timestamp=event_info.timestamp
    )
    await service.produce_event(event)
    return EventResponse(status='success', partition='1', offset='0', event=event)
