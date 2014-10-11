from django.core.management.base import BaseCommand, CommandError
from criticalsyncing.core.models import Source, Article


class Command(BaseCommand):
    args = '<Source Name> | all'

    def handle(self, *args, **options):
        name = args[0] if args else "all"
        if name == 'all':
            sources = Source.objects.all()
        else:
            sources = Source.objects.filter(name=name)
        for source in sources:
            pass
