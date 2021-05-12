import os
import re
# from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from . import models
from . import create_pptx


# Create your views here.
class PriceListView(ListView):
    context_object_name = 'news_list'
    model = models.PriceNews
    paginate_by = 8
    ordering = ['-pub_date']
    template_name = 'price/pricenews_list.html'

class PriceDetailView(DetailView):
    model = models.PriceNews
    template_name = 'price/price_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        all_petrolnews = models.PricePetrolHead.objects.all()
        # Определяем id заголовка новости
        current_pricenews = self.model.objects.get(id=self.kwargs['pk'])
        for i in range(len(all_petrolnews)):
            if current_pricenews.pub_date == all_petrolnews[i].pub_date:
                current_petrol = all_petrolnews[i]

        context = {'price_detail': current_pricenews,
                   'price_list': current_pricenews.products.all(),
                   'petrol_detail': current_petrol,
                   'petrol_list': current_petrol.petrols.all(),
                   }
        return context


def cut_date(txt):
    """
    Из заголовка вычленяем дату. Например из текста (txt):
        "Средние  цены на отдельные потребительские товары (услуги)
         по Ненецкому автономному округу на 13 января 2020 года"
    получим "13 января 2020".
    """
    regex = re.compile('\d{1,2}\s[яфмаисонд][а-я]+[а|я]\s\d{4}')
    return re.search(regex, txt).group()


def products_price(news_id, pet_id):
    """ Возвращает: - price по текущему id
                    - price по предыдущей дате
    """
    price_list = ['Говядина', 'Куры охлажденные', 'Колбаса вареная',
                  'Рыба мороженая', 'Молоко питьевое цельное пастеризованное',
                  'Яйца куриные', 'Чай черный байховый', 'Мука пшеничная',
                  'Хлеб из ржаной', 'Рис шлифованный', 'Картофель',
                  'Лук репчатый', 'Огурцы свежие', 'Яблоки',
                  'Майка', 'Мыло хозяйственное', 'Порошок',
                  'Проезд', 'Бензин автомобильный марки АИ-92', 'Плата за жилье',
                  'Отопление, Гкал', 'Водоснабжение холодное, м3', 'Водоотведение, м3',
                  'Водоснабжение горячее, м3', 'Услуги по снабжению']
    pricenews = models.PriceNews.objects.get(id=news_id)
    pricenews_products_all = pricenews.products.all()
    petrolhead = models.PricePetrolHead.objects.get(id=pet_id)
    petrolhead_petrol_all = petrolhead.petrols.all()
    if pricenews.pub_date.year != 2018:
        pre_month = pricenews.pub_date + relativedelta(months=-1)
        previous_pricenews = models.PriceNews.objects.filter(pub_date__lte=pre_month).order_by('-pub_date')[0]
        previous_date = cut_date(previous_pricenews.title)
        previous_products_all = previous_pricenews.products.all()
        previous_petrolhead = models.PricePetrolHead.objects.filter(pub_date__lte=pre_month).order_by('-pub_date')[0]
        previous_petrol_all = previous_petrolhead.petrols.all()
    else:  # дошли до 1-ой строки => предыдущая=текущая
        previous_pricenews = pricenews
        previous_products_all = pricenews_products_all
        previous_petrolhead = petrolhead
        previous_petrol_all = petrolhead_petrol_all

    i = 0
    current_price = [''] * 25
    previous_price = [''] * 25
    for ele in price_list:
        if i == 18:
            current = petrolhead_petrol_all.get(petrol__icontains=ele)
            current_price[i] = current.price
            previous = previous_petrol_all.get(petrol__icontains=ele)
            previous_price[i] = previous.price
            # print(f"{current.petrol},                   {current_price[i]}      {previous_price[i]}")
        elif i == 24:
            current = pricenews_products_all.get(product__icontains=ele)
            current_price[i] = current.price/100
            previous = previous_products_all.get(product__icontains=ele)
            previous_price[i] = previous.price/100
        else:
            current = pricenews_products_all.get(product__icontains=ele)
            current_price[i] = current.price
            previous = previous_products_all.get(product__icontains=ele)
            previous_price[i] = previous.price
        # print(f"{current.product},                   {current_price[i]}      {previous_price[i]}")
        i += 1
    return pricenews, current_price, previous_price, previous_date 


@login_required
def pptx(request):
    news_pk = request.POST.get('news_pk')
    pet_pk = request.POST.get('pet_pk')
    cur_pricenews, cur_price, prev_price, prev_date  = products_price(news_pk, pet_pk)
    file_path = create_pptx.new_pptx(cur_pricenews.title, cur_price, prev_price, prev_date)
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response
    # return render(request, 'price/success.html', {'download':file_path})
