from django.db import models

# Create your models here.
class NewsHead(models.Model):
    objects = models.Manager()
    news_title = models.CharField(max_length=256)
    href = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')
    subsidy_period = models.CharField(max_length=50)  # январь-сентябрь 2020

    def __str__(self):
        return self.news_title

class SubsidyData(models.Model):
    objects = models.Manager()
    newshead = models.ForeignKey(NewsHead, related_name='subsidies', on_delete=models.CASCADE)
    subsidy_name = models.CharField(max_length=256)
    subsidy_value = models.FloatField()

    def __str__(self):
        return self.subsidy_name

class BenefitData(models.Model):
    objects = models.Manager()
    newshead = models.ForeignKey(NewsHead, related_name='benefits', on_delete=models.CASCADE)
    benefit_name = models.CharField(max_length=256)
    benefit_value = models.FloatField()

    def __str__(self):
        return self.benefit_name
