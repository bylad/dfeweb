import re

from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from pathlib import Path
from dfesite.constants import MONTH
from . import create_pptx
from . import models

# Create your views here.
class SubsidyListView(ListView):
    context_object_name = 'newshead_list'
    model = models.NewsHead
    paginate_by = 8
    ordering = ['-pub_date']
    template_name = 'subsidy/subsidy_list.html'

class SubsidyDetailView(DetailView):
    model = models.NewsHead
    template_name = 'subsidy/subsidy_detail.html'

    def get_context_data(self, **kwargs):
        subsidy_float, benefit_float = [], []
        subsidy_int, benefit_int = [], []
        # Определяем id заголовка новости
        current_newshead = self.model.objects.get(id=self.kwargs['pk'])
        for ele in current_newshead.subsidies.all():
            if "единиц" in ele.subsidy_name:
                subsidy_int.append((ele.subsidy_name, round(ele.subsidy_value)))
            else:
                subsidy_float.append((ele.subsidy_name, ele.subsidy_value))

        for ele in current_newshead.benefits.all():
            if "численность" in ele.benefit_name.lower():
                benefit_int.append((ele.benefit_name, round(ele.benefit_value)))
            else:
                benefit_float.append((ele.benefit_name, ele.benefit_value))
        context = {'news_detail': current_newshead,
                   'subsidy_int': subsidy_int,
                   'subsidy_float': subsidy_float,
                   'benefit_int': benefit_int,
                   'benefit_float': benefit_float,
                   }
        return context


def get_period(txt):
    period_list = []
    try:
        find_out = re.search(r"[яфмаисонд][а-я]+[ьйт]\s*-\s*[яфмаисонд][а-я]+[ьйт]", txt).group()
        period_list = [MONTH.index(ele) + 1 for ele in MONTH if ele in find_out]
        period_list.append(re.search(r"\d{4}", txt).group())
    except AttributeError:
        period_list.append(re.search(r"\d{4}", txt).group())

    if len(period_list) == 1:
        period_str = f"{period_list[0]} год"
        period_4filename = f"1-12_{period_list[0]}"
    elif period_list[1] == 3:
        period_str = f"{period_list[1]} месяца {period_list[2]} года"
        period_4filename = f"1-{period_list[1]}_{period_list[2]}"
    else:
        period_str = f"{period_list[1]} месяцев {period_list[2]} года"
        period_4filename = f"1-{period_list[1]}_{period_list[2]}"

    return [period_str, period_4filename]


def get_data(news_id):
    """ Возвращает: - период заголовка в виде строки '9 месяцев 2021 года'
                    - данные в виде словаря all_dict, где заменяются на цифры значения ключей """
    all_dict = {'subsidy_average': 'среднемесячный размер начисленных субсидий',
                'subsidy_accrued': 'сумма субсидий',
                'subsidy_percent': 'в процентах',
                'subsidy_families': 'единиц',
                'benefit_average': 'среднемесячный размер социальной поддержки',
                'benefit_compensate': 'возмещено',
                'benefit_funds': 'объем средств',
                'benefit_number': 'численность граждан'}
    news_head = models.NewsHead.objects.get(id=news_id)
    subsidy_data = news_head.subsidies.all()
    benefit_data = news_head.benefits.all()
    for k, v in all_dict.items():
        for sub in subsidy_data.values():
            if v in sub['subsidy_name'].lower():
                if v == 'единиц':
                    all_dict[k] = round(sub['subsidy_value'])
                else:
                    all_dict[k] = sub['subsidy_value']
        for ben in benefit_data.values():
            if v in ben['benefit_name'].lower():
                if v == 'численность граждан':
                    all_dict[k] = round(ben['benefit_value'])
                else:
                    all_dict[k] = ben['benefit_value']
    title_period = get_period(news_head.news_title)
    return title_period, all_dict


@login_required
def pptx(request):
    news_pk = request.POST.get('news_pk')
    news_period, suben_dict = get_data(news_pk)
    file_path = create_pptx.new_pptx(news_period, suben_dict)
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        response['Content-Disposition'] = 'inline; filename=' + Path(file_path).name
        return response
