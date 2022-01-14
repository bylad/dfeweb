from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Проверка https://arhangelskstat.gks.ru/population111 и добавление данных в БД'

    def handle(self, *args, **options):
        from population import fill_population
        fill_population.populate()
