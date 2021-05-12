from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Проверка https://arhangelskstat.gks.ru/news и добавление новости в БД'

    def handle(self, *args, **options):
        from industry import fill_stat_news
        fill_stat_news.populate()
