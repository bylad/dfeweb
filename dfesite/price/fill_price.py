import os
import sys
import re
import xlrd
import docx
import openpyxl
import dateparser
from datetime import timedelta

from django.db import transaction
from django.conf import settings # correct way for access BASE_DIR, MEDIA_DIR...
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dfesite.settings')
# import django
# django.setup()

from .class_webnews import NewsStat, NewsStatDetail
from .class_filehandle import WebFile, DocxFile
from .models import PriceNews, PriceData, PricePetrolHead, PricePetrolData
from industry import send_msg

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MEDIA = settings.MEDIA_DIR

MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля',
          'августа', 'сентября', 'октября', 'ноября', 'декабря']

HEADER = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
          AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 \
          Safari/537.36'}

SEARCH_TXT1 = 'Ненецкий автономный округ'
SEARCH_TXT2 = 'Нарьян-Мар'
CUT_NM = ' и г.Нарьян-Мару'

# Функции добавления в БД
def add_news(title, news_href, date):
    PriceNews.objects.get_or_create(title=title, href=news_href, pub_date=date)
    current_news = PriceNews.objects.get(title=title)
    send_msg.sending('price', current_news.id, current_news.title)  # здесь срабатывала ложно
    return current_news.id


def add_data(ind, tovar, sale_price):
    PriceData.objects.get_or_create(pricenews_id=ind, product=tovar, price=sale_price)
    return tovar


def add_pethead(ptitle, phref, pdate):
    PricePetrolHead.objects.get_or_create(petrol_title=ptitle, href=phref, pub_date=pdate)
    current_pethead = PricePetrolHead.objects.get(petrol_title=ptitle)
    return current_pethead.id


def add_petdata(ind, toplivo, sale_price):
    PricePetrolData.objects.get_or_create(pricepetrolhead_id=ind, petrol=toplivo, price=sale_price)
# ------------------------


def cut_date(txt):
    """
    Из заголовка вычленяем дату. Например из текста (txt):
        "Средние  цены на отдельные потребительские товары (услуги)
         по Ненецкому автономному округу на 13 января 2020 года"
    получим "13 января 2020". Ф-я возвращает эту строку в формате дата.
    """
    regex = re.compile('\d{1,2}\s[яфмаисонд][а-я]+[а|я]\s\d{4}')
    return dateparser.parse(re.search(regex, txt).group())


# Функции обработки файлов DOCX, XLS(X)
def data_docx(doc):
    pet_price = [0.0] * 3
    pet_name = [''] * 3
    ben_i = 1000
    j = 0
    ben = ['Бензин автомобильный марки АИ-92']
    if len(doc.tables) > 1:
        print('Внимание! Изменилось количество таблиц. Проверьте исходный файл.')
        print('Обрабатывается только первая таблица...')
    for i, row in enumerate(doc.tables[0].rows):
        for cell in row.cells:  # поиск строки с необх. данными
            if any(x in cell.text for x in ben):
                ben_i = i
                break
        if ben_i <= i < len(doc.tables[0].rows):
            pet_name[j] = doc.tables[0].cell(i, 0).text
            pet_price[j] = float(re.sub(',', '.', doc.tables[0].cell(i, 1).text))
            j += 1
    pet_head = doc.tables[0].cell(0, 0).text.replace(CUT_NM, '')
    print(pet_head)
    # print(pet_name)
    # print(pet_price)
    print('Обработка таблицы DOCX файла успешно завершена.\n')
    # sys.exit()
    return pet_head, pet_name, pet_price


def data_xls(xls):  # предыдущая версия data_xls(xls, search_txt)
    j = 0
    data_begin = 0
    data_end = 0
    wb = xlrd.open_workbook(xls)
    ws = wb.sheet_by_index(0)

    # удаляем из заголовка все лишние пробелы, символы новой строки и подстроку CUT_NM
    xls_title = re.sub('\s+', ' ', ws.cell_value(0, 0)).replace(CUT_NM, '')
    for i in range(ws.nrows):
        if re.search(SEARCH_TXT1, ws.cell_value(i, 0)):
            data_begin = i
        if re.search(SEARCH_TXT2, ws.cell_value(i, 0)):
            data_end = i
    if not data_begin:
        print(f'Ошибка!\nНе найден заголовок, содержащий слова "{SEARCH_TXT1}". Проверьте файл!\nПрограмма завершена.')
        sys.exit()

    # rows_count = ws.nrows - data_i
    rows_count = data_end - (data_begin + 1)  # начало: data_begin+1
    col_name = [''] * rows_count
    col_price = [0.0] * rows_count

    for i in range(data_begin+1, data_end):
        col_name[j] = ws.cell_value(i, 0)
        col_price[j] = ws.cell_value(i, 1)
        j += 1

    print('Обработка Excel файла успешно завершена.\n')
    # print(f'Заголовок:\n{xls_title}\n')
    # print(f'{col_name}\n')
    # print(f'{col_price}\n')
    # sys.exit()
    return xls_title, col_name, col_price
#--------------------------------


def data_openpyxl(xlsx, search_txt):
    j = 0
    data_i = 0
    petrol_list = ['Бензин автомобильный марки АИ-92', 'Бензин автомобильный марки АИ-95', 'Дизельное топливо']
    regex = re.compile(search_txt)
    wb = openpyxl.load_workbook(xlsx)
    ws = wb.worksheets[0]
    xls_title = re.sub('\s+', ' ', ws.cell(row=1, column=1).value)  # удаляем все лишние пробелы, символы новой строки
    for i in range(1, ws.max_row):
        if re.search(regex, ws.cell(row=i, column=1).value):
            data_i = i
            print(f'data_i={data_i}')
            break
    if not data_i:
        print('Ошибка!\nНе найден заголовок "Товар". Проверьте файл!\nПрограмма завершена.')
        sys.exit()

    rows_count = ws.max_row - data_i
    col_name = [''] * rows_count
    col_price = [0.0] * rows_count

    # NEW ADD BEGIN
    if search_txt == 'Нарьян-Мар':
        col_name = [''] * 3
        col_price = [0.0] * 3

        for i in range(data_i+1, ws.max_row):  # итерируем цены для Нарьян-Мара
            if any(ext in ws.cell(row=i, column=1).value for ext in petrol_list):
                idx = [petrol_list.index(s) for s in petrol_list if s in ws.cell(row=i, column=1).value]
                col_name[idx[0]] = ws.cell(row=i, column=1).value
                col_price[idx[0]] = ws.cell(row=i, column=4).value
        print('Обработка Excel файла успешно завершена.\n')
        return col_name, col_price
    # NEW ADD END

    for i in range(data_i+1, ws.max_row):
        col_name[j] = ws.cell_value(i, 0)
        col_price[j] = ws.cell_value(i, 1)
        j += 1

    print('Обработка Excel файла успешно завершена.\n')
    return xls_title, col_name, col_price
#--------------------------------


def check_db(news_date, is_petrol):
    """ Проверка наличия данных в базе (0 - нет, 1 - есть)
    is_petrol: цены на бензин (0 - нет, 1 - да)
    """
    data_exists = 1
    if is_petrol:
        db_data = PricePetrolHead.objects.all()
    else:
        db_data = PriceNews.objects.all()
    for i in range(len(db_data)):
        if news_date.date() == db_data[i].pub_date.date():
            data_exists = 1
            print(f'Данные уже в базе!')
            break
        else:
            data_exists = 0
    return data_exists


# ---Добавление данных с сайта---
def search_news(idx, page, news_text):
    """
    Поиск новости news_text
    :param idx: номер новости на веб-странице
    :param page: номер страницы с новостями статистики
    :param news_text: искомая новость
    :return: list[news_count, title, href, pub_date, file]
    """
    nao = 'Ненецком'
    app_dir = 'price'
    webpage = 'https://arhangelskstat.gks.ru/news?page=' + str(page)
    news = []
    # 0-количество новостей, 1-заголовок, 2-ссылка, 3-дата, 4-файл (либо путь к xl, либо объект docx)
    stat = NewsStat(idx, news_text, webpage, HEADER)
    if stat.acount:
        news.append(stat.acount)
        news.append(stat.get_title())
        news.append(stat.get_href())
        news.append(stat.get_pub_date())
        stat_detail = NewsStatDetail(nao, stat.get_href(), HEADER)
        year = re.findall(r'\d{4}', stat.get_title())[0]
        stat_file = WebFile(stat_detail.file_href, MEDIA, app_dir, year, stat_detail.file_name)
        stat_file.download_file()
        file = stat_file.file_path
        filename, file_extension = os.path.splitext(file)
        if news_text == 'О потребительских ценах на бензин':
            if file_extension.lower() == '.docx' or file_extension.lower() == '.doc':
                file = DocxFile(MEDIA, app_dir, year, stat_detail.file_name).get_docx()
        news.append(file)
        return news
    return None


def mid_news(news_num, page):
    """
    Поиск новости 'Средние цены и их изменение на отдельные потребительские товары' по вхождению слова 'потребительские'
    с индексом (news_num) на веб странице 'https://arhangelskstat.gks.ru/news?page=' + str(page)
    Добавление найденных данных в БД
    Возвращает количество найденных новостей на странице
    0-количество новостей, 1-заголовок, 2-ссылка, 3-дата, 4-файл (либо путь к xl, либо объект docx)
    """
    newsdata = search_news(news_num, page, 'потребительские')
    all_news = PriceNews.objects.all().order_by('-pub_date')
    for news in all_news:  # добавлена проверка, т.к. на сайте статистики м.б. ошибочная дата в заголовке
        if news.title == newsdata[1] and news.pub_date != newsdata[3]:
            previous_news = news.get_previous_by_pub_date()
            pattern = re.compile('\d{1,2}\s[яфмаисонд][а-я]+[а|я]\s\d{4}')
            previous_news_title_date = dateparser.parse(re.search(pattern, previous_news.title).group())
            # т.к. данные обновляются еженедельно, то к предыдущей дате добавляем 7 дней
            newsdate = previous_news_title_date + timedelta(days=7)
            new_date = f"{newsdate.day - 2} {MONTHS[newsdate.month - 1]} {newsdate.year}"
            newsdata[1] = re.sub(pattern, new_date, newsdata[1])
        elif news.title == newsdata[1] and news.pub_date == newsdata[3]:
            data_in = 1
            return newsdata[0], data_in, 0  # news_id=0, т.к. новость уже существует

    data_in = check_db(newsdata[3], 0)
    if data_in == 0:
        # определяем ID новости, к нему будут привязаны данные
        news_id = add_news(newsdata[1], newsdata[2], newsdata[3])
        xls_file = newsdata[4]
        xl_title, products, prices = data_xls(xls_file)
        for p in range(len(products)):  # кол-во строк с ценами на товары
            add_data(news_id, products[p], prices[p])
    return newsdata[0], data_in, news_id


def pet_news(news_num, page):
    """
    Поиск новости 'О потребительских ценах на бензин')
    с индексом (news_num) на веб странице 'https://arhangelskstat.gks.ru/news?page=' + str(page)
    Добавление найденных данных в БД
    Возвращает количество найденных новостей на странице
    """
    # [0] количество новостей, [1] заголовок, [2] ссылка, [3] дата, [4] файл
    newsdata = search_news(news_num, page, 'О потребительских ценах на бензин')
    if newsdata is not None:
        data_in = check_db(newsdata[3], 1)
        if data_in == 0:
            pethead_id = add_pethead(newsdata[1], newsdata[2], newsdata[3])
            if not isinstance(newsdata[4], str):
                print('============== pet_news: DOC FILE ===============')
                pet_title, pet_name, pet_price = data_docx(newsdata[4])

                for p in range(len(pet_name)):  # кол-во строк с ценами на товары
                    add_petdata(pethead_id, pet_name[p], pet_price[p])
            else:
                print('============== pet_news: XLSX FILE ===============')
                pet_name, pet_price = data_openpyxl(newsdata[4], 'Нарьян-Мар')
                for p in range(len(pet_name)):  # кол-во строк с ценами на товары
                    add_petdata(pethead_id, pet_name[p], pet_price[p])
        return newsdata[0]
    return 0


def from_web(page):
    mid_num = 0
    mid_count = 1
    pet_num = 0
    pet_count = 1
    data_in_db = 0

    while mid_num < mid_count:
        print('mid_news RUNNING...')
        mid_count, data_in_db, midnews_id = mid_news(mid_num, page)
        # if data_in_db == 1:  # при
        #     return data_in_db
        mid_num += 1

    while pet_num < pet_count:
        print('pet_news RUNNING...')
        pet_count = pet_news(pet_num, page)
        pet_num += 1
    return data_in_db, midnews_id
#--------------------------------
# 2020. Загрузка данных из ранее скачанных файлов
def from_xlsdocx(path):
    for filename in os.listdir(path):
        # print(os.path.join(path, filename))
        if filename.endswith(".xls") or filename.endswith(".xlsx"):
            xl_title, products, prices = data_xls(os.path.join(path, filename))
            xl_date = cut_date(xl_title)
            data_in = check_db(xl_date, 0)
            if data_in == 0:
                news_id = add_news(xl_title, '', xl_date)
                for p in range(len(products)):  # кол-во строк с ценами на товары
                    add_data(news_id, products[p], prices[p])
        elif filename.endswith(".docx"):
            doc_title, products, prices = data_docx(docx.Document(os.path.join(path, filename)))
            doc_date = cut_date(doc_title)
            data_in = check_db(doc_date, 1)
            if data_in == 0:
                news_id = add_pethead(doc_title, '', doc_date)
                for p in range(len(products)):  # кол-во строк с ценами на товары
                    add_petdata(news_id, products[p], prices[p])
        else:
            continue
#----------------------------------------------------
# 2019-2018. Загрузка данных из ранее скачанных файлов
def data_xlsm(xls, product_column):
    """
    Обработка старых XLSM файлов
    :param xls: полный путь к файлу Excel
    :param product_column: колонка 0(A) - бензин, колонка 4(E) - товар
    :return: заголовок, товар, цена
    """
    j = 0
    i_begin = 0
    i_end = 0
    regex_nao = re.compile('в том числе Ненецкий')
    regex_arh = re.compile('без Ненецкого')
    regex_milk = re.compile('Молоко питьевое')
    wb = xlrd.open_workbook(xls)
    ws = wb.sheet_by_index(0)

    if product_column:
        title = re.sub('\s+', ' ', ws.cell_value(0, 4)) + ' ' + re.sub('\s+', ' ', ws.cell_value(1, 4))
    else:
        title = re.sub('\s+', ' ', ws.cell_value(0, 0)) + ' ' + re.sub('\s+', ' ', ws.cell_value(1, 0))[:-2]

    for i in range(ws.nrows):
        if re.search(regex_nao, ws.cell_value(i, product_column)):
            i_begin = i
        if re.search(regex_arh, ws.cell_value(i, product_column)):
            i_end = i
            break
    if not i_begin:
        print('Ошибка структуры файла!\nПрограмма завершена.')
        sys.exit()

    rows_count = i_end - i_begin - 1
    col_name = [''] * rows_count
    col_price = [0.0] * rows_count
    for i in range(i_begin+1, i_end):
        if re.search(regex_milk, ws.cell_value(i, product_column)):
            col_name[j] = f"{ws.cell_value(i, product_column)} {ws.cell_value(i + 1, product_column)}"
            try:
                col_price[j] = float(re.sub(r',', '.', ws.cell_value(i, product_column+1)))
            except TypeError:
                col_price[j] = ws.cell_value(i, product_column+1)
            j += 1
            continue
        elif ws.cell_value(i, product_column) != '' and ws.cell_value(i, product_column+1) != '':
            col_name[j] = ws.cell_value(i, product_column)
            try:
                col_price[j] = float(re.sub(r',', '.', ws.cell_value(i, product_column+1)))
            except TypeError:
                col_price[j] = ws.cell_value(i, product_column+1)
            j += 1
            continue
        elif ws.cell_value(i, product_column) != '' and ws.cell_value(i, product_column+1) == '' \
                and product_column == 0:
            col_name[j] = ws.cell_value(i, product_column)
            try:
                col_price[j] = float(re.sub(r',', '.', ws.cell_value(i+1, product_column+1)))
            except TypeError:
                col_price[j] = ws.cell_value(i+1, product_column+1)
            j += 1
            continue
    excess = rows_count - j  # излишне созданные данные в списке
    print('Обработка Excel файла успешно завершена.\n')
    return title.strip(), col_name[:-excess], col_price[:-excess]


def from_xlsm(path):
    column_list = [0, 4]
    for filename in os.listdir(path):
        if filename.endswith(".xlsm"):
            for column in column_list:
                xl_title, products, prices = data_xlsm(os.path.join(path, filename), column)
                xl_date = cut_date(xl_title)
                if column:  # колонка не равна 0, т.е. не бензин
                    data_in = check_db(xl_date, 0)
                    if data_in == 0:
                        news_id = add_news(xl_title, '', xl_date)
                        for p in range(len(products)):  # кол-во строк с ценами на товары
                            add_data(news_id, products[p], prices[p])
                else:  # добавляем в базу данные по бензину
                    data_in = check_db(xl_date, 1)
                    if data_in == 0:
                        news_id = add_pethead(xl_title, '', xl_date)
                        for p in range(len(products)):  # кол-во строк с ценами на товары
                            add_petdata(news_id, products[p], prices[p])
#----------------------------------------------------
# Добавление данных из файлов xls, docx (2020)
# files_dir = "d:/code/python/study/djangoproject/dfesite/media/price/__source/2020"
# from_xlsdocx(files_dir)

#----------------------------------------------------
# Добавление данных из файлов xlsm (2019)
# files_dir = "d:/code/python/study/djangoproject/dfesite/media/price/__source/2019"
# from_xlsm(files_dir)

#----------------------------------------------------
# Добавление данных с сайта

@transaction.atomic
def populate():
    page_num = 1
    print('============== price.populate ===============')
    while page_num < 5:
        print(f'page={page_num}')
        data_exist, mnews_id = from_web(page_num)
        if data_exist == 1:
            print('===========PRICE DATA EXIST===========')
            break
        page_num += 1
        current_news = PriceNews.objects.get(id=mnews_id)
        print(f'current_news.id={current_news.id}')
    print('Процедура выполнена')

# if __name__ == "__main__":
#     populate()
