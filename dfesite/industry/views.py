import os
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . import models
from . import create_pptx, send_msg


# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'

class IndustryNewsListView(ListView):
    context_object_name = 'news_list'
    model = models.IndustryNews
    paginate_by = 6
    ordering = ['-pub_date']

class IndustryNewsDetailView(DetailView):
    model = models.IndustryNews
    template_name = 'industry/industrynews_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # Определяем id заголовка новости, затем список с таблицами, отнсящимися к ней
        current_industrynews = models.IndustryNews.objects.get(id=self.kwargs['pk'])
        context = {'industry_detail': current_industrynews,
                   'index_list': current_industrynews.news.all(),
                   'production_list': current_industrynews.production.all(),
                   'index_head': current_industrynews.index_head.all(),
                   'production_head': current_industrynews.production_head.all(),
                   }
        return context


@login_required
def pptx(request):
    production_type_list = ['Электроэнергия', 'Пар и', 'Изделия хлебобулочные недлит', 'Молоко',
                            'Нефть', 'Кондитерские', 'Масло', 'Оленина']

    news_id = request.POST.get('news_pk')
    current_industrynews = models.IndustryNews.objects.get(id=news_id)
    index = current_industrynews.news.get(production_index__contains='Индекс').pre_cur_index
    production_all = current_industrynews.production.all()
    i = 0
    production_cur_year = [''] * 8
    for ele in production_type_list:
        x = production_all.get(industry_production__contains=ele)
        if i < 4:
            production_cur_year[i] = str(x.cur_year_production * 1000)
        else:
            production_cur_year[i] = str(x.cur_year_production)
        i += 1
    # print(f'current_industrynews.title={current_industrynews.title}')
    file_path = create_pptx.new_pptx(production_cur_year, index, current_industrynews.title)
    # send_msg.sending('industry', news_id, current_industrynews.title)
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response

    # return render(request, 'industry/success.html', {'download':file_path})

# fill_stat_news.populate()
