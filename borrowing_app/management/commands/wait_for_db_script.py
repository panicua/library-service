import time
from django.core.management.base import BaseCommand
from django.db import connections, OperationalError


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        attempts = 0
        max_attempts = 20

        while attempts < max_attempts:
            try:
                db_conn = connections["default"]
                c = db_conn.cursor()
                c.execute("SELECT 1;")
                self.stdout.write(self.style.SUCCESS("Database available!"))
                return
            except OperationalError:
                attempts += 1
                self.stdout.write(
                    f"Database unavailable, waiting {attempts} second(s)..."
                )
                time.sleep(1)

        raise Exception("Database unavailable after waiting for 20 seconds")
