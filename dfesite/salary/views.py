import os
from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from . import models
from . import create_pptx
from . import fill_salary

MONTHS = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль',
          'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь']

# Create your views here.
class SalaryListView(ListView):
    context_object_name = 'news_list'
    model = models.SalaryNews
    paginate_by = 6
    ordering = ['-pub_date']

class SalaryDetailView(DetailView):
    model = models.SalaryNews
    template_name = 'salary/salarynews_detail.html'

    def get_context_data(self, **kwargs):
        # context = super().get_context_data()
        # Определяем id заголовка новости, затем таблицу, отнсящуюся к ней
        current_salarynews = models.SalaryNews.objects.get(id=self.kwargs['pk'])
        context = {
                    'salarynews_detail': current_salarynews,
                    'salarydetail_list': current_salarynews.salary_set.all().order_by('id'),
                    'salaryhead_list': current_salarynews.salaryhead_set.all(),
                   }
        return context

def zp(news_id):
    """ Возвращает: - price по текущему id
                    - price по предыдущей дате
    """
    activity_list = ['Всего',
                     'сельское, лесное хозяйство, охота',
                     'добыча полезных ископаемых',
                     'обеспечение электрической энергией, газом',
                     'строительство',
                     'образование',
                     'деятельность в области здравоохранения',
                     'деятельность гостиниц и предприятий',
                     'деятельность в области культуры, спорта']
    salarynews = models.SalaryNews.objects.get(id=news_id)
    salary_all = salarynews.salary_set.all()
    salarynews_date = fill_salary.cut_date(salarynews.title)  # datetime(2020, 09, ...)
    if salarynews_date.year != 2018:
        previous_date = f'{MONTHS[salarynews_date.month - 1]} {salarynews_date.year - 1}'  # 'сентябрь 2019'
        previous_salarynews = models.SalaryNews.objects.get(title__icontains=previous_date)
        previous_salary_all = previous_salarynews.salary_set.all()
    else:  # дошли до 1-ой строки => предыдущая=текущая
        previous_salarynews = salarynews
        previous_salary_all = salary_all

    current_zp = [''] * 9
    previous_zp = [''] * 9
    for i, ele in enumerate(activity_list):
        current = salary_all.get(employer__icontains=ele)
        previous = previous_salary_all.get(employer__icontains=ele)
        if salarynews_date.month == 1:
            if i == 0:
                current_zp[i] = format(round(current.current, 2), ".2f")
                previous_zp[i] = format(round(previous.current, 2), ".2f")
            else:
                current_zp[i] = round(current.current/1000, 1)
                previous_zp[i] = round(previous.current/1000, 1)
        else:
            if i == 0:
                current_zp[i] = format(round(current.period, 2), ".2f")
                previous_zp[i] = format(round(previous.period, 2), ".2f")
            else:
                current_zp[i] = round(current.period/1000, 1)
                previous_zp[i] = round(previous.period/1000, 1)
    return salarynews_date, current_zp, previous_zp


@login_required
def pptx(request):
    news_pk = request.POST.get('news_pk')
    cur_salarynews_date, cur_zp, prev_zp = zp(news_pk)
    file_path = create_pptx.new_pptx(cur_salarynews_date, cur_zp, prev_zp)
    with open(file_path, 'rb') as fh:
        response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response

    # return render(request, 'price/success.html', {'download':file_path})
