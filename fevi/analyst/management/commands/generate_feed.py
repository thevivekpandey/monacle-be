from django.core.management.base import BaseCommand
from analyst.tasks import generate_feed_card


class Command(BaseCommand):
    help = 'Executes to generate feed for pending tasks'

    def handle(self, *args, **kwargs):
        self.stdout.write('generating card job')
        generate_feed_card()
