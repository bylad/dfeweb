from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Проверка https://arhangelskstat.gks.ru/news и добавление новости в БД'

    def handle(self, *args, **options):
        from salary import fill_salary
        fill_salary.populate()
