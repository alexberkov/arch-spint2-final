import asyncio
import json
import logging
import os

from dotenv import load_dotenv
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from schemas.events import Event, EventType

load_dotenv()

KAFKA_HOST = os.getenv("KAFKA_HOST", "kafka")
KAFKA_PORT = os.getenv("KAFKA_PORT", "9092")
KAFKA_BROKERS = [f'{KAFKA_HOST}:{KAFKA_PORT}']


class EventService:

    def __init__(self):
        self.topics: list[str] = [f'{elem.value}-events' for elem in EventType]

        self.producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BROKERS)

        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=KAFKA_BROKERS, auto_offset_reset='earliest', enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.consumer.subscribe(topics=self.topics)

        self.log = logging.getLogger(self.__class__.__name__)

        self.consume_task: asyncio.Task = None

    async def start(self) -> None:
        await self.producer.start()
        await self.consumer.start()

        self.consume_task = asyncio.create_task(self.consume_events())

    async def stop(self):
        if self.consume_task:
            self.consume_task.cancel()
            await asyncio.gather(self.consume_task, return_exceptions=True)

        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

    async def produce_event(self, event: Event) -> None:
        await self.producer.send(
            topic=f'{event.type.value}-events', key=str(event.id).encode(),
            value=event.model_dump_json().encode()
        )
        self.log.info(f"Produced event: {event.model_dump_json()}")
        await self.producer.flush()

    async def consume_events(self) -> None:
        try:
            async for msg in consumer:
                try:
                    event: Event = Event(**msg)
                    self.log.info(f'Processed message from Kafka: {event.model_dump_json()}')
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.log.error(f'Error processing message: {e}')
        except asyncio.CancelledError:
            self.log.info(f'Kafka consumer stop requested')
