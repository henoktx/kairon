from typing import Optional

from django.conf import settings
from temporalio.client import Client


class TemporalClientSingleton:
    _instance: Optional[Client] = None

    @classmethod
    async def get_client(cls) -> Client:
        if cls._instance is None:
            cls._instance = await Client.connect(
                settings.TEMPORAL_CLIENT_ADDRESS,
                namespace=settings.TEMPORAL_CLIENT_NAMESPACE,
            )
        return cls._instance


async def get_temporal_client() -> Client:
    return await TemporalClientSingleton.get_client()
