from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand

from ...worker import main


class Command(BaseCommand):
    help = "Runs the worker process for handling tasks."

    
    def handle(self, *args, **options):
        try:
            async_to_sync(main)()
            self.stdout.write(self.style.SUCCESS("Worker process started successfully."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error starting worker: {e}"))