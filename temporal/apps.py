import asyncio
import threading
from django.apps import AppConfig


class TemporalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "temporal"
    _worker_thread = None

    def ready(self):
        # Avoid running on reloader thread
        import os

        if os.environ.get("RUN_MAIN") and not self._worker_thread:
            from temporal.worker import main

            def run_worker():
                asyncio.run(main())

            # Start the worker in a separate thread
            self._worker_thread = threading.Thread(target=run_worker, daemon=True)
            self._worker_thread.start()
