from django.core.management.base import BaseCommand
from .dummy_account_setup import generate_demo_data


class Command(BaseCommand):
    help = 'Displays current time'

    def add_arguments(self, parser):
        parser.add_argument('-w', '--workspace', type=str,
                            help='Please provide workspace')

        parser.add_argument('-l', '--local', action='store_true',
                            help='Please provide enviroment')

    def handle(self, *args, **kwargs):
        workspace = kwargs['workspace']
        local = kwargs['local']
        self.stdout.write("creating workspace `%s` in `%s`" % (workspace, 'localhost' if local else 'production'))
        generate_demo_data(workspace=workspace, local=local)
