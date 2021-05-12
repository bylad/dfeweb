from django.db import models

# Create your models here.
class IndustryNews(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=256)
    href = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.title

class IndustryIndexHead(models.Model):
    objects = models.Manager()
    industrynews = models.ForeignKey(IndustryNews, related_name='index_head', on_delete=models.CASCADE)
    month_year = models.CharField(max_length=150)
    pre_year = models.CharField(max_length=50)
    cur_year = models.CharField(max_length=50)
    pre_cur = models.CharField(max_length=150)

class IndustryProductionHead(models.Model):
    objects = models.Manager()
    industrynews = models.ForeignKey(IndustryNews, related_name='production_head', on_delete=models.CASCADE)
    cur_year = models.CharField(max_length=50)
    pre_cur = models.CharField(max_length=150)

class IndustryIndex(models.Model):
    objects = models.Manager()
    industrynews = models.ForeignKey(IndustryNews, related_name='news', on_delete=models.CASCADE)
    production_index = models.CharField(max_length=256)
    pre_year_index = models.FloatField('preceed')
    cur_year_index = models.FloatField('current')
    pre_cur_index = models.FloatField('preceed-current')

    def __str__(self):
        return self.production_index

class IndustryProduction(models.Model):
    objects = models.Manager()
    industrynews = models.ForeignKey(IndustryNews, related_name='production', on_delete=models.CASCADE)
    industry_production = models.CharField(max_length=256)
    cur_year_production = models.FloatField('current')
    pre_cur_production = models.FloatField('preceed-current')

    def __str__(self):
        return self.industry_production

