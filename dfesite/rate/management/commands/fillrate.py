from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Добавление курса доллара'

    def handle(self, *args, **options):
        from rate import fill_rate
        fill_rate.populate()
