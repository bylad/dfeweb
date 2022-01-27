from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Проверка https://arhangelskstat.gks.ru/news и добавление данных в БД'

    def handle(self, *args, **options):
        from subsidy import fill_subsidy
        fill_subsidy.populate()
