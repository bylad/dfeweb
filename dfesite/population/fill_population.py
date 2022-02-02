import os
import re
import requests
import urllib3

from django.db import transaction
from django.conf import settings  # correct way for access BASE_DIR, MEDIA_DIR...

from price.class_webnews import PopulationStat
from price.class_filehandle import WebFile, DocxFile
from transliterate import translit

from dfesite.constants import HEADER, MONTHE
from industry import send_msg
from population.models import MigrationHead, MigrationData, ZagsHead, ZagsData

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
MEDIA = settings.MEDIA_DIR
NAO = "Ненецкий автономный округ"
SEARCH_MIGRATION = 'О числе прибывших, выбывших'
SEARCH_ZAGS = 'О числе зарегистрированных родившихся'

# Функции добавления в БД
def add_migrhead(title, news_href, date):
    MigrationHead.objects.get_or_create(migration_title=title, href=news_href, pub_date=date)
    current_migrhead = MigrationHead.objects.get(migration_title=title)
    # send_msg.sending('price', current_news.id, current_news.title)  # здесь срабатывала ложно
    return current_migrhead.id

def add_migrdata(ind, count_in, count_out, up_down):
    MigrationData.objects.get_or_create(migrationhead_id=ind, arrived=count_in, departed=count_out, gain=up_down)
    # return tovar

def add_zagshead(title, href, date):
    ZagsHead.objects.get_or_create(zags_title=title, href=href, pub_date=date)
    current_zagshead = ZagsHead.objects.get(zags_title=title)
    return current_zagshead.id

def add_zagsdata(ind, born, died, wedd, divorce):
    ZagsData.objects.get_or_create(zagshead_id=ind, born=born, died=died, wedd=wedd, divorce=divorce)
# ------------------------

def search_webdata(idx, search_text):
    """
    Поиск новости news_text
    :param idx: номер новости на веб-странице
    :param search_text: искомый текст
    :return: [news_count, title, href, pub_date, file]
    """
    app_dir = 'population'
    webpage = 'https://arhangelskstat.gks.ru/population111'
    # 0-количество, 1-заголовок, 2-ссылка, 3-дата, 4-файл (docx)
    population_info = []
    stat = PopulationStat(idx, search_text, webpage, HEADER)
    if stat.div_count:
        stat_href = stat.www + stat.get_href()
        stat_title = stat.get_title()
        year = re.search(r'\d{4}', stat_title).group()
        file_name = os.path.split(stat_href)[1]
        file_requests = requests.get(stat_href)
        stat_file = WebFile(file_requests, MEDIA, app_dir, year, file_name)
        stat_file.download_file()
        file = DocxFile(MEDIA, app_dir, year, file_name).get_docx()

        population_info.append(stat.div_count)
        population_info.append(stat_title)
        population_info.append(stat_href)
        population_info.append(stat.get_pub_date())
        population_info.append(file)
        return population_info
    return None


def data_docx(doc):
    tdata = []
    table = doc.tables[0]
    if len(doc.tables) > 1:
        print('Внимание! Изменилось количество таблиц. Проверьте исходный файл.')
        print('Обрабатывается только первая таблица...')
    for i, row in enumerate(table.rows):
        if i == 1:
            try:
                text = [" ".join(cell.text.split()) for cell in row.cells]
                tdata = [int(ele) for j, ele in enumerate(text) if j > 0]
            except Exception:
                print('Внимание! Изменилась структура таблицы. Проверьте исходный файл')
    return tdata


def add_migr(wwwdata, docdata):
    migrhead_id = add_migrhead(wwwdata[1], wwwdata[2], wwwdata[3].date())
    add_migrdata(migrhead_id, docdata[0], docdata[1], docdata[2])
    return migrhead_id


def add_zags(wwwdata, docdata):
    zagshead_id = add_zagshead(wwwdata[1], wwwdata[2], wwwdata[3].date())
    add_zagsdata(zagshead_id, docdata[0], docdata[1], docdata[2], docdata[3])


def putto_db(srch_txt):
    """ Функция выполняет проверку на наличие новых данных и в случае отсутствия добавляет в БД
    :param srch_txt: искомый текст
    """
    migrhead_pk = None
    try:
        db_migrhead = MigrationHead.objects.all().order_by('pub_date')
        db_zagshead = ZagsHead.objects.all().order_by('pub_date')
    except Exception as e:
        db_migrhead = None
        db_zagshead = None
        if hasattr(e, 'message'):
            print("Exception's message:", e.message)
        else:
            print('Exception:', e)

    info = search_webdata(0, srch_txt)  # находим количество искомого
    # [news_count, title, href, pub_date, file]
    if info:
        if db_migrhead.last().migration_title == info[1]:
            return None
        data_list = data_docx(info[4])
        if srch_txt == SEARCH_MIGRATION and db_migrhead:  # если ищем мигр.данные и они есть в БД
            for db in db_migrhead:
                if info[3] == db.pub_date:
                    continue
                else:
                    migrhead_pk = add_migr(info, data_list)  # добавляем миграционные данные в БД
        elif srch_txt == SEARCH_ZAGS and db_zagshead:  # если ищем мигр.данные и они есть в БД
            for db in db_zagshead:
                if info[3] == db.pub_date:
                    continue
                else:  # добавляем данные из реестра ЗАГС в БД
                    add_zags(info, data_list)
    return migrhead_pk


@transaction.atomic
def populate():
    srch_list = [SEARCH_MIGRATION, SEARCH_ZAGS]
    print("-----------------------POPULATION BEGIN--------------------------")
    for look in srch_list:
        migrtitle_id = putto_db(look)
        if migrtitle_id:
            current = MigrationHead.objects.get(id=migrtitle_id)
            print(f'current_migr.id={current.id}')
            send_msg.sending('population', current.id, current.migration_title)
    print("-----------------------POPULATION END--------------------------")

