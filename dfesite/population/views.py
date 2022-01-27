import re

from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from pathlib import Path
from transliterate import translit
from . import create_pptx
from . import models


MONTHE = ['январе', 'феврале', 'марте', 'апреле', 'мае', 'июне', 'июле',
          'августе', 'сентябре', 'октябре', 'ноябре', 'декабре']


class PopulationListView(ListView):
    context_object_name = 'population_list'
    model = models.MigrationHead
    paginate_by = 8
    ordering = ['-pub_date']
    template_name = 'population/population_list.html'

class PopulationDetailView(DetailView):
    model = models.MigrationHead
    template_name = 'population/population_detail.html'

    def get_context_data(self, **kwargs):
        all_zagshead = models.ZagsHead.objects.all()
        # Определяем id заголовка новости
        current_migrhead = self.model.objects.get(id=self.kwargs['pk'])
        current_zagshead = None
        title_date = cut_date(current_migrhead)
        for i in range(len(all_zagshead)):
            zags_date = cut_date(all_zagshead[i].zags_title)
            if title_date == zags_date:
                current_zagshead = all_zagshead[i]
                break

        if current_zagshead:
            context = {'migr_titledate': f" в {title_date[2]} {title_date[0]}",
                       'migr_detail': current_migrhead,
                       'migr_list': current_migrhead.migrations.all(),
                       'zags_detail': current_zagshead,
                       'zags_list': current_zagshead.zags.all(),
                       }
            return context
        print("current_zagshead не определен")

def cut_date(txt):
    """
    Из заголовка вычленяем дату. Например из текста (txt):
        "О числе прибывших, выбывших и миграционном приросте (убыли) населения в октябре 2021 года"
    получим "октябре 2021". Ф-я возвращает список: [int_year, int_month, str_month]
    """
    # str_date = re.search(r"\s[яфмаисонд][а-я]+[е]\s\d{4}",  str(txt)).group()
    str_date = re.search(r"\s[яфмаисонд][а-я]+[е]\s\d{4}", translit(str(txt), 'ru')).group().strip().lower()
    mo = [ele for ele in MONTHE if ele in str_date]
    month = MONTHE.index(mo[0])
    year = ''
    try:
        year = re.search(r"\d{4}", str_date).group()
    except Exception as e:
        if hasattr(e, 'message'):
            print("Exception's message:", e.message)
        else:
            print('Exception:', e)
    return [int(year), int(month), mo[0]]


def get_objects(migr_id, zags_id):
    """ Возвращает: заголовки и данные """
    migr_head = models.MigrationHead.objects.get(id=migr_id)
    migr_data = migr_head.migrations.all()
    zags_head = models.ZagsHead.objects.get(id=zags_id)
    zags_data = zags_head.zags.all()
    return migr_head, migr_data.values()[0], zags_head, zags_data.values()[0]


@login_required
def pptx(request):
    migr_pk = request.POST.get('migr_pk')
    zags_pk = request.POST.get('zags_pk')
    migrhead, migrdata, zagshead, zagsdata = get_objects(migr_pk, zags_pk)
    title_date = cut_date(migrhead)

    create_pptx.new_pptx(title_date, migrdata, zagsdata)

    file_path = create_pptx.new_pptx(title_date, migrdata, zagsdata)
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        response['Content-Disposition'] = 'inline; filename=' + Path(file_path).name
        return response
