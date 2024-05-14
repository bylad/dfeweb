import camelot
import re
import sys

import urllib3

from django.db import transaction
from django.conf import settings  # correct way for access BASE_DIR, MEDIA_DIR...
from pathlib import Path
from price.class_webnews import NewsStat, NewsStatDetail, PriceStat
from price.class_filehandle import WebFile, DocxFile
# from transliterate import translit

from industry import send_msg
from dfesite.constants import HEADER
from subsidy.models import NewsHead, SubsidyData, BenefitData


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
MEDIA = settings.MEDIA_DIR
SEARCH_TEXT = 'предоставление гражданам субсидий и социальной поддержки'
SUBSIDY_TITLE = 'Предоставление гражданам субсидий на оплату жилого помещения и коммунальных услуг'
BENEFIT_TITLE = 'Предоставление гражданам социальной поддержки (льгот) по оплате жилого помещения и коммунальных услуг'
WEBPAGE_SUBSIDY = 'https://29.rosstat.gov.ru/housing111'

# Функции добавления в БД
def add_newshead(title, news_href, date, news_period):
    NewsHead.objects.get_or_create(news_title=title, href=news_href, pub_date=date, subsidy_period=news_period)
    current_newshead = NewsHead.objects.get(news_title=title)
    return current_newshead.id

def add_subsidydata(ind, name, value):
    SubsidyData.objects.get_or_create(newshead_id=ind, subsidy_name=name, subsidy_value=value)

def add_benefitdata(ind, name, value):
    BenefitData.objects.get_or_create(newshead_id=ind, benefit_name=name, benefit_value=value)
# ------------------------

# ---Добавление данных с сайта---
def search_subsidy(idx, news_text):
    """
    Поиск новости news_text
    :param idx: номер новости на веб-странице
    :param news_text: искомая новость
    :return: list[news_count, title, href, pub_date, file]
    """
    # nao = 'Ненецком'
    nao = 'Ненецкий'
    app_dir = 'subsidy'
    news = []
    # 0-количество новостей, 1-заголовок, 2-ссылка, 3-дата, 4-файл
    stat = PriceStat(idx, news_text, WEBPAGE_SUBSIDY, HEADER)
    print()
    if stat.div_count:
        news.append(stat.div_count)
        news.append(stat.get_title())
        news.append(stat.webfile_link)
        news.append(stat.get_pub_date())
        # Если дата новости с сайта < или = дате последней новости из БД, то обработку прекращаем
        try:
            if news[3] <= NewsHead.objects.last().pub_date:
                print("Новость была добавлена ранее.")
                return "Exist"
        except AttributeError:
            print("Добавляем данные в БД")

        year = re.findall(r'\d{4}', stat.get_title())[0]
        stat_file = WebFile(stat.webfile_href, MEDIA, app_dir, year, stat.webfile_name)
        stat_file.download_file()
        news.append(stat_file.file_path)
        return news
    return None



def search_news(idx, page, news_text):
    """
    Поиск новости news_text
    :param idx: номер новости на веб-странице
    :param page: номер страницы с новостями статистики
    :param news_text: искомая новость
    :return: list[news_count, title, href, pub_date, file]
    """
    nao = 'Ненецкий'
    app_dir = 'subsidy'
    webpage = 'https://29.rosstat.gov.ru/news?page=' + str(page)
    news = []
    # 0-количество новостей, 1-заголовок, 2-ссылка, 3-дата, 4-файл (путь к pdf)
    stat = NewsStat(idx, news_text, webpage, HEADER)
    if stat.acount:
        news.append(stat.acount)
        news.append(stat.get_title())
        print(f"Стр.{page}, {stat.get_title()}")
        news.append(stat.get_href())
        news.append(stat.get_pub_date())

        # Если дата новости с сайта < или = дате последней новости из БД, то обработку прекращаем
        try:
            if news[3] <= NewsHead.objects.last().pub_date:
                print("Новость была добавлена ранее.")
                return "Exist"
        except AttributeError:
            print("Добавляем данные в БД")

        stat_detail = NewsStatDetail(nao, stat.get_href(), HEADER)
        year = re.findall(r'\d{4}', stat.get_title())[0]
        if stat_detail.file_href.status_code == 404:
            print("Файл недоступен! Статус запрашиваемой ссылки - 404.")
            return 404
        else:
            stat_file = WebFile(stat_detail.file_href, MEDIA, app_dir, year, stat_detail.file_name)
            stat_file.download_file()
#            file = DocxFile(MEDIA, app_dir, year, Path(stat_file.file_path).name).get_docx()
            news.append(stat_file.file_path)
            return news
    return None
# ------------------------

def get_table_data(table):
    data = []
    for i, row in enumerate(table.rows):
        if i == 0:
            continue
        text = (re.sub(r'\s+', ' ', cell.text.strip()) for cell in row.cells)
        data.append(tuple(text))
    return data


def data_docx(doc):
    tdata = []
    if len(doc.tables) > 3:
        print('Внимание! Изменилась структура файла, проверьте его.')
    for t in range(2):
        tdata.append(get_table_data(doc.tables[t]))
    if tdata:
        return tdata  # 0 - таблица с субсидиями, 1 - таблица со льготами
    return None


def get_pdf_table(list_txt):
    data_list = list()
    is_num = 0
    number_txt = ''
    string_buffer = ''
    for txt in list_txt:
        if txt[:1].isupper():
            if string_buffer and is_num:
                data_list.append((string_buffer, number_txt))
                string_buffer = ''
                is_num = 0
            string_buffer = txt
        elif txt[:1].isdigit():
            number_txt = txt
            is_num = 1
            if number_txt == list_txt[-1]:
                data_list.append((string_buffer, number_txt))
        else:
            if is_num:
                data_list.append((f"{string_buffer} {txt}", number_txt))
                string_buffer = ''
                is_num = 0
            else:
                string_buffer = f"{string_buffer} {txt}"
    return data_list


def extract_table(pdf_path):
    tables = camelot.read_pdf(pdf_path)
    pdf_tables = list()
    for idx in range(tables.n):
        tdata = tables[idx].data
        tdata_text = tdata[1][0]  # tdata[0] = ['январь-март 2022 года']
        tdata_stripped_list = [txt.strip() for txt in tdata_text.splitlines()]
        tdata_tuple_list = get_pdf_table(tdata_stripped_list)
        tdata_tuple_list.insert(0, ('', tdata[0][0]))
        pdf_tables.append(tdata_tuple_list)
    return pdf_tables


def data_todb(datalist, news_pk, idx):
    """ Добавление данных из списка в таблицы: SubsidyData, BenefitData
    :param datalist: список с данными
    :param news_pk: ID (или pk-primary key) новости
    :param idx: 0 - данные с субсидиями, 1 - данные со льготами
    """
    for ele in datalist:
        if ele[0] == '':  # пропуск первой пары вида ('', 'Январь-сентябрь 2020 года')
            continue
        if idx:
            add_benefitdata(news_pk, ele[0], float(re.sub(',', '.', ele[1])))
        else:
            add_subsidydata(news_pk, ele[0], float(re.sub(',', '.', ele[1])))


@transaction.atomic
def populate():
    print("-----------------------SUBSIDY BEGIN--------------------------")
    found = search_subsidy(0, SEARCH_TEXT)  # 0-кол. новостей, 1-заголовок, 2-ссылка, 3-дата, 4-файл(docx)
    if found == 404 or found == "Exist":
        print("-----------------------SUBSIDY END--------------------------")
        return
    elif found is not None:
        try:  # период - 'январь-июнь 2021'
            period = re.search(r"[яфмаисонд][а-я]+[ьйт]\s*-\s*[яфмаисонд][а-я]+[ьйт]\s*\d{4}", found[1]).group()
        except AttributeError:
            period = re.search(r"\d{4}", found[1]).group()  # период за год - '2021'
        news_id = add_newshead(found[1], found[2], found[3], period.strip())

        data_list = extract_table(found[4])
        for i, data in enumerate(data_list):
            data_todb(data, news_id, i)
    added = NewsHead.objects.get(id=news_id)
    send_msg.sending('subsidy', news_id, added.news_title)
    print("-----------------------SUBSIDY END--------------------------")

