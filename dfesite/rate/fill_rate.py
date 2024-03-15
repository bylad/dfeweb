import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from transliterate import translit
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateparser import parse
from decimal import Decimal
from pycbrf.toolbox import ExchangeRates
from django.db.models import Avg
from .models import Daily, Monthly
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

class NewsLocate:
    def __init__(self, web, header, txt):
        self.web = web
        self.request = requests.get(web, headers=header, verify=False)
        self.soup = BeautifulSoup(self.request.content, 'html.parser')
        # self.atag = self.soup.find('a', title=re.compile(txt))
        self.atag_all = self.soup.findAll('a', title=re.compile(txt))

    def get_title(self, index):
        return self.atag_all[index].span.text

    def get_href(self, index):
        crop_end = self.web.find('/', 8, len(self.web))
        www = self.web[:crop_end]
        return www + self.atag_all[index].get('href')

    def get_pub_date(self, index):
        if self.atag_all is not None:
            try:
                news_date = translit(self.atag_all[index].small.text,'ru')
            except AttributeError:
                news_date = '9 сентября 1999'
                print("Attribute Error! News date was dropped!")
            return parse(news_date)


class NewsDetail:
    def __init__(self, web, header, txt):
        request = requests.get(web, headers=header, verify=False).content
        news_soup = BeautifulSoup(request, 'html.parser')
        p = news_soup.find('p', text=re.compile(txt))
        self.price_str = re.findall(r'\d+\,?\d+', p.text)[0]

    def get_price(self):
        return float(re.sub(',', '.', self.price_str))


def fill_daily(rate_date, rate_usd):
    Daily.objects.get_or_create(date=rate_date, usd=rate_usd)


def fill_monthly(rate_date, rate_oil, rate_usd):
    Monthly.objects.get_or_create(date=rate_date, oil=rate_oil, usd=rate_usd)


#def usd_rates(today):
#     """ Курс доллара на дату (today) в формате %Y-%m-%d 
#         Запрос выполняется с помощью API pycbrf
#     """
#    print(f"usd_rates({today})")
#    rates = ExchangeRates(today)
#    print(rates['USD'].value)
#    return rates['USD'].value

def usd_rates(today):
    """ Курс доллара на дату (today) 
        Запрос выполняется с помощью XML запроса
        API запрос падает с ошибкой 
    """
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={datetime.strftime(today, "%d/%m/%Y")}&VAL_NM_RQ=R01235'
    df = pd.read_xml(url, encoding='cp1251')
    s = df.loc[df['ID'] == 'R01235']['Value'].item()
    return Decimal(s.replace(',', '.'))


def yemo(input_date):
    """ Возвращает дату 2021-03-15 в виде целого числа 202103 """
    return int(str(input_date.year) + str(input_date.month).zfill(2))


# def news_data(year_int, month_int, last_month):
def news_data(last_month):
    web_page = 'https://www.economy.gov.ru/material/departments/d12/konyunktura_mirovyh_tovarnyh_rynkov/'
    head = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    news_txt = 'сорта «Юралс»'
    p_txt = 'долл. США'
    news = NewsLocate(web_page, head, news_txt)
    if news.atag_all is not None:
        date = last_month + relativedelta(months=1)
        for ind in range(len(news.atag_all)-1, -1, -1):
            news_date = news.get_pub_date(ind)
            # print(f'yemo(news_date)={yemo(news_date)}')
            # print(f'yemo(date)={yemo(date)}')
            if yemo(news_date) > yemo(date):
                oil_price = NewsDetail(news.get_href(ind), head, p_txt).get_price()
                avg_usd = Daily.objects.filter(date__year__exact=date.year,
                                               date__month__exact=date.month).aggregate(Avg('usd'))
                # Заносим данные в БД
                fill_monthly(date, oil_price, round(avg_usd['usd__avg'], 4))
                date += relativedelta(months=1)
    return


def populate():
    print('============== rate.populate ===============')
    today = datetime.today().date()
    db_day = Daily.objects.first().date
    # Заполнение ежедневного курса $
    print(f'today={today}')
    print(f'db_day={db_day}')
    while today > db_day:
        db_day += relativedelta(days=1)
        print(f'dbday+={db_day}')
        usd = usd_rates(db_day)
        print('Function usd_rates() done!')
        fill_daily(db_day, usd)

    db_last_date = Monthly.objects.last().date
    print(f"db_last_date={db_last_date}, {yemo(db_last_date)}")
    print(f"today={today}, {yemo(today)}")

    # Заполнение ежедневного курса $
    # if yemo(db_last_date) < yemo(today):
    if news_data(db_last_date) is not None:
        news_data(db_last_date)
    print('Процедура fill_rate выполнена')

