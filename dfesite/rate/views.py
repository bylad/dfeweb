import os
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from plotly.offline import plot
import plotly.graph_objects as go
from . import models, create_xlsx
from django.conf import settings

MEDIA = settings.MEDIA_DIR

# Create your views here.
class DailyListView(ListView):
    template_name = 'rate/daily_list.html'
    model = models.Daily
    daily = models.Daily.objects.all()
    n = len(daily)
    x_data = [] * n
    y_data = [] * n
    first_usd = "%.2f" % daily.first().usd
    first_date = daily.first().date
    for i in range(n):
        x_data.insert(i, daily[i].date)
        y_data.insert(i, daily[i].usd)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines', name='rate', opacity=0.8))
    fig.update_layout(
        title={
            'text': 'Динамика курса $ с 2018 года по настоящее время',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        }
    )
    plot_div = plot(fig, output_type='div')

    extra_context = {'da': daily, 'first_usd': float(first_usd), 'first_date': first_date, 'plot_div': plot_div}
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super(DailyListView, self).get_context_data(**kwargs)
        paginator = Paginator(self.daily, self.paginate_by)
        page = self.request.GET.get('page')
        try:
            days = paginator.page(page)
        except PageNotAnInteger:
            days = paginator.page(1)
        except EmptyPage:
            days = paginator.page(paginator.num_pages)
        context['all'] = days
        return context

class MonthlyListView(ListView):
    template_name = 'rate/monthly_list.html'
    context_object_name = 'monthly'
    model = models.Monthly
    paginate_by = 15
    ordering = ['-date']
    monthly = model.objects.all()
    m = len(monthly)
    xm_data = [] * m
    ym_data = [] * m
    zm_data = [] * m
    for j in range(m):
        xm_data.insert(j, monthly[j].date)
        ym_data.insert(j, monthly[j].usd)
        zm_data.insert(j, monthly[j].oil)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xm_data, y=zm_data, mode='lines', name='Нефть', opacity=0.8))
    fig.add_trace(go.Scatter(x=xm_data, y=ym_data, mode='lines', name='USD', opacity=0.8))
    fig.update_layout(
        title={
            'text': 'Динамика курса доллара и нефти "Юралс"',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
        }
    )
    plot_divm = plot(fig, output_type='div')

    extra_context = {'plot_divm': plot_divm}


class ChartView(TemplateView):
    template_name = 'rate/chart.html'
    model = models.Daily
    daily = models.Daily.objects.all()
    n = len(daily)
    x_data = [] * n
    y_data = [] * n
    for i in range(n):
        x_data.insert(i, daily[i].date)
        y_data.insert(i, daily[i].usd)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_data, y=y_data, mode='lines', name='rate', opacity=0.8))
    fig.update_layout(title='Динамика курса доллара')
    plot_div = plot(fig, output_type='div')

    monthly = models.Monthly.objects.all()
    m = len(monthly)
    xm_data = [] * m
    ym_data = [] * m
    zm_data = [] * m
    for j in range(m):
        xm_data.insert(j, monthly[j].date)
        ym_data.insert(j, monthly[j].usd)
        zm_data.insert(j, monthly[j].oil)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xm_data, y=zm_data, mode='lines', name='Нефть', opacity=0.8))
    fig.add_trace(go.Scatter(x=xm_data, y=ym_data, mode='lines', name='USD', opacity=0.8))
    fig.update_layout(title='Динамика курса доллара и нефти марки "Юралс"')
    plot_divm = plot(fig, output_type='div')
    extra_context = {'da': daily, 'plot_div': plot_div, 'plot_divm': plot_divm}


@login_required
def xlsx(request):
    print("IP Address for debug-toolbar: " + request.META['REMOTE_ADDR'])

    file_path = os.path.join(MEDIA, 'rate', 'usd_urals.xlsx')
    if request.method == 'POST':
        file_path = create_xlsx.xl_insert()
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    return render(request, 'rate/success.html', {'download': file_path})


# fill_rate.populate()
