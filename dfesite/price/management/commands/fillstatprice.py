from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Проверка https://arhangelskstat.gks.ru/news и добавление новости в БД'

    def handle(self, *args, **options):
        from price import fill_price
        fill_price.populate()
