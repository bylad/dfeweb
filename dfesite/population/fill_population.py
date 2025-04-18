import camelot
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
SEARCH_ZAGS_LIST = ["Родившиеся", "Умершие", "браков", "разводов"]


# Функции добавления в БД
def add_migrhead(title, news_href, date):
    MigrationHead.objects.get_or_create(migration_title=title, href=news_href, pub_date=date)
    current_migrhead = MigrationHead.objects.get(migration_title=title)
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


def search_webdata(idx, search_text):
    """
    Поиск новости news_text
    :param idx: номер новости на веб-странице
    :param search_text: искомый текст
    :return: [news_count, title, href, pub_date, file]
    """
    app_dir = 'population'
    webpage = 'https://29.rosstat.gov.ru/population111'
    # 0-количество, 1-заголовок, 2-ссылка, 3-дата, 4-файл (docx)
    population_info = []
    print(f"\nsearch_webdata: idx={idx}, search_text='{search_text}', webpage={webpage}, HEADER={HEADER}\n")
    stat = PopulationStat(idx, search_text, webpage, HEADER)
    if stat.div_count:
        stat_href = stat.www + stat.get_href()
        stat_title = stat.get_title()
        year = re.search(r'\d{4}', stat_title).group()
        file_name = os.path.split(stat_href)[1]
        file_requests = requests.get(stat_href, verify=False)
        stat_file = WebFile(file_requests, MEDIA, app_dir, year, file_name)
        stat_file.download_file()

        # Если PDF, то указываем путь к файлу, иначе возращаем тип object (файл DOCX)
        if os.path.splitext(file_name)[1] == '.pdf':
            file = stat_file.file_path
        else:
            file = DocxFile(MEDIA, app_dir, year, file_name).get_docx()

        population_info.append(stat.div_count)
        population_info.append(stat_title)
        population_info.append(stat_href)
        population_info.append(stat.get_pub_date())
        population_info.append(file)
        return population_info
    return None


def data_docx(doc, doc_name):
    tdata = []
    table = doc.tables[0]
    if len(doc.tables) > 1:
        print('Внимание! Изменилось количество таблиц. Проверьте исходный файл.')
        print('Обрабатывается только первая таблица...')
    if SEARCH_MIGRATION in doc_name:
        for i, row in enumerate(table.rows):
            if i == 1:  # обработка 2-ой строки
                try:
                    text = [" ".join(cell.text.split()) for cell in row.cells]
                    # в таблице за январь 2024 меньше элементов. Изменил условие, где данные идут после типов string
                    # .lstrip("-") удаляет знак "-" в отрицательных числах для прохождения условия isdigit()
                    tdata = [int(ele) for ele in text if ele.lstrip("-").isdigit()]
                except Exception:
                    print('Внимание! Изменилась структура таблицы. Проверьте исходный файл')
    else:
        for i, col in enumerate(table.columns):
            if i == 1:  # обработка 2-го столбца
                try:
                    text = [" ".join(cell.text.split()) for cell in col.cells]
                    # в таблице за январь 2024 меньше элементов. Изменил условие, где данные идут после типов string
                    # .lstrip("-") удаляет знак "-" в отрицательных числах для прохождения условия isdigit()
                    tdata = [int(ele) for ele in text if ele.lstrip("-").isdigit()]
                    del tdata[2]  # удаляем элемент с индексом 2 (прирост)
                except Exception:
                    print('Внимание! Изменилась структура таблицы. Проверьте исходный файл')
    return tdata


def get_pdf_table(pdf_file):
    tables = camelot.read_pdf(pdf_file)
    if tables.n > 0:
        df = tables[0].df
        df1 = df[df[0].str.contains("(?i)|".join(SEARCH_ZAGS_LIST))]
        return df1[1].to_list()
    return None


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
    if srch_txt == SEARCH_MIGRATION:
        head = MigrationHead
    else:
        head = ZagsHead
    db_last = head.objects.last()
    db_head = head.objects.filter(pub_date__year=f"{db_last.pub_date.year}").order_by('-pub_date')
    db_dates = [obj.pub_date for obj in db_head]

    info = search_webdata(0, srch_txt)  # находим количество искомого
    # [news_count, title, href, pub_date, file]
    if info:
        news_count = info[0]  # фиксируем количество новостей после 1-го поиска
        if news_count > 5:  # ограничиваем количество обрабатываемых новостей
            news_count = 5
    else:
        news_count = 0

    for i in range(news_count - 1):
        if info[3] in db_dates:
            info = search_webdata(i + 1, srch_txt)
            continue
        # выполняем обработку таблицы загруженного файла
        if type(info[4]) is str:
            data_list = get_pdfdf(info[4])
        else:
            data_list = data_docx(info[4], info[1])

        if srch_txt == SEARCH_MIGRATION:
            migrhead_pk = add_migr(info, data_list)  # добавляем миграционные данные в БД
        else:
            add_zags(info, data_list)

        info = search_webdata(i+1, srch_txt)

    if migrhead_pk:
        send_msg.sending('population', migrhead_pk, info[1])  # данные по миграции поступают позже ЗАГС


@transaction.atomic
def populate():
    srch_list = [SEARCH_MIGRATION, SEARCH_ZAGS]
    print("-----------------------POPULATION BEGIN--------------------------")
    for look in srch_list:
        putto_db(look)
    print("-----------------------POPULATION END--------------------------")

