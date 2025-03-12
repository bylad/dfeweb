import os
import re
import requests

from bs4 import BeautifulSoup
from dateparser import parse
from transliterate import translit


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
    def __init__(self, txt='Ненецкий', *args, **kwargs):
        super().__init__(*args, **kwargs)
#        div_a = self.soup.find('div', {'class': 'content'}).find('a', text=re.compile(txt))
        div_desc = self.soup.find('div', {'class': 'document-list__item-title'}, text=re.compile(txt)).parent
        div_atag = div_desc.find_previous_sibling().find('a')
        self.pub_date = parse(re.search(r'\d{2}.\d{2}.\d{4}', str(div_desc)).group(), date_formats=['%d.%m.%Y'])
        self.path, self.file_name = os.path.split(self.www + div_atag.get('href'))
        self.file_href = requests.get(self.www + div_atag.get('href'), verify=False)


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
            news_date = translit(self.atag.find(class_='e-date').text, 'ru')
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


class PriceStat(NewsLocate):
    def __init__(self, idx, txt, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print(self.request)

        all_divs = self.soup.findAll('div', attrs={"class": "document-list__item"})
        div_list = create_mydiv_list(all_divs, txt)
        self.div_count = len(div_list)
        if self.div_count == 0:
            self.div_tag, self.webfile_link, self.webfile_href, self.webfile_path, self.webfile_name = None, None, None, None, None
        else:
            self.div_tag = div_list[idx]
            self.webfile_link = self.www + self.div_tag.findChild('div', attrs={"class": "document-list__item-link"}).findChild('a').get('href')
            self.webfile_href = requests.get(self.webfile_link, verify=False)
            self.webfile_path, self.webfile_name = os.path.split(self.webfile_link)

    def get_title(self):
        return self.div_tag.findChild('div', attrs={"class": "document-list__item-title"}).text.strip()

    def get_href(self):
        return self.div_tag.findChild('a').get('href')

    def get_pub_date(self):
        try:
            pub_text = self.div_tag.findChild(class_='document-list__item-info').text
            pub_date = re.search(r'(\d{2}.\d{2}.\d{4})', pub_text).group()
        except AttributeError:
            pub_date = '9 сентября 1999'
            print("Attribute Error! News date was dropped!")
        return parse(pub_date, date_formats=['%d.%m.%Y'])


class PopulationStat(NewsLocate):
    def __init__(self, idx, txt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_divs = self.soup.findAll('div', attrs={"class": "document-list__item"})
        div_list = create_mydiv_list(all_divs, txt)
        self.div_count = len(div_list)
        if self.div_count == 0:
            self.div_tag = None
        else:
            self.div_tag = div_list[idx]

    def get_title(self):
        return self.div_tag.findChild('div', attrs={"class": "document-list__item-title"}).text.strip()

    def get_href(self):
        return self.div_tag.findChild('a').get('href')

    def get_pub_date(self):
        try:
            pub_text = self.div_tag.findChild(class_='document-list__item-info').text
            pub_date = re.search(r'(\d{2}.\d{2}.\d{4})', pub_text).group()
        except AttributeError:
            pub_date = '9 сентября 1999'
            print("Attribute Error! News date was dropped!")
        return parse(pub_date)


def create_mydiv_list(alldivs, find_string):
    mydiv_list = []
    for div in alldivs:
        try:
            if find_string in div.findChild('div', attrs={"class": "document-list__item-title"}).text:
                mydiv_list.append(div)
        except Exception as e:
            if hasattr(e, 'message'):
                print("Exception's message:", e.message)
            else:
                print('Exception:', e)
    return mydiv_list
