from typing import Optional
from django.conf import settings
from temporalio.client import Client
from temporalio.worker import Worker
from temporal.workflows import KaironWorkflow
from temporal.activities import (
    update_task_status_activity,
    update_execution_status_activity,
    send_email_activity,
)


class TemporalWorker:
    _instance: Optional["TemporalWorker"] = None
    _worker: Optional[Worker] = None
    _client: Optional[Client] = None
    _is_running: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._is_running:
            return

    async def start(self):
        if self._is_running:
            return
        
        self._client = await Client.connect(settings.TEMPORAL_CLIENT_ADDRESS, namespace=settings.TEMPORAL_CLIENT_NAMESPACE)
        self._worker = Worker(
            self._client,
            task_queue=settings.TEMPORAL_TASK_QUEUE_NAME,
            workflows=[KaironWorkflow],
            activities=[
                update_task_status_activity,
                update_execution_status_activity,
                send_email_activity,
            ],
        )
        self._is_running = True
        await self._worker.run()

    async def stop(self):
        if self._worker and self._is_running:
            await self._worker.shutdown()
            self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def client(self) -> Optional[Client]:
        return self._client


async def main():
    worker = TemporalWorker()
    await worker.start()
