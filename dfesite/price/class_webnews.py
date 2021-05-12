import os
import re, requests
from bs4 import BeautifulSoup
from transliterate import translit
from dateparser import parse


class NewsLocate:
    def __init__(self, web, header):
        self.request = requests.get(web, headers=header, verify=False)
        self.soup = BeautifulSoup(self.request.content, 'html.parser')
        crop_end = web.find('/', 8, len(web))
        self.www = web[:crop_end]


class NewsStat(NewsLocate):
    def __init__(self, idx, txt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_a = self.soup.findAll('a', text=re.compile(txt))
        self.acount = len(all_a)
        # print(f"tag A count = {self.acount}")
        if self.acount == 0:
            self.atag = None
        else:
            self.atag = all_a[idx]

    def get_title(self):
        return self.atag.text

    def get_href(self):
        return self.atag.get('href')

    def get_pub_date(self):
        if self.atag is not None:
            atag_parent = self.atag.parent.parent
        else:
            return None
        try:
            news_date = translit(atag_parent.find('div', class_='news-card__data').text, 'ru')
        except AttributeError:
            news_date = '9 сентября 1999'
            print("Attribute Error! News date was dropped!")
        return parse(news_date)


class NewsStatDetail(NewsLocate):
    def __init__(self, txt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        div_a = self.soup.find('div', {'class': 'content'}).find('a', text=re.compile(txt))
        self.path, self.file_name = os.path.split(self.www + div_a.get('href'))
        self.file_href = requests.get(self.www + div_a.get('href'))

class NewsUrals(NewsLocate):
    def __init__(self, txt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.web = web
        self.atag = self.soup.find('a', title=re.compile(txt))

    def get_title(self):
        return self.atag.span.text

    def get_href(self):
        return self.www + self.atag.get('href')

    def get_pub_date(self):
        try:
            news_date = translit(self.atag.find(class_='e-date').text,'ru')
        except AttributeError:
            news_date = '9 сентября 1999'
            print("Attribute Error! News date was dropped!")
        return parse(news_date)

class NewsUralsDetail(NewsLocate):
    def __init__(self, txt,*args, **kwargs):
        super().__init__(*args, **kwargs)
        p = self.soup.find('p', text=re.compile(txt))
        self.price_str = re.findall(r'\d+\,\d+', p.text)[0]

    def get_price(self):
        return float(re.sub(',', '.', self.price_str))
