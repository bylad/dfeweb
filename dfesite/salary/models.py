import math
from django.db import models

# Create your models here.
class SalaryNews(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=256)
    href = models.CharField(max_length=256)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.title


class SalaryHead(models.Model):
    objects = models.Manager()
    salarynews = models.ForeignKey(SalaryNews, on_delete=models.CASCADE)
    current_my = models.CharField(max_length=30)
    period_mmy = models.CharField(max_length=50)
    # current = models.CharField(max_length=30)  # рублей
    pre_month = models.CharField(max_length=30)
    pre_year = models.CharField(max_length=30)
    # period = models.CharField(max_length=30)  # рублей
    pre_period = models.CharField(max_length=30)
    middle = models.CharField(max_length=200)


class Salary(models.Model):
    objects = models.Manager()
    salarynews = models.ForeignKey(SalaryNews, on_delete=models.CASCADE)
    employer = models.CharField(max_length=256)
    current = models.FloatField()
    pre_month = models.FloatField()
    pre_year = models.FloatField()
    period = models.FloatField()
    pre_period = models.FloatField()
    middle = models.FloatField()

    def get_nan_current(self):
        if math.isnan(self.current):
            return 0

    def get_nan_pre_month(self):
        if math.isnan(self.pre_month):
            return 0

    def get_nan_pre_year(self):
        if math.isnan(self.pre_year):
            return 0

    def get_nan_period(self):
        if math.isnan(self.period):
            return 0

    def get_nan_pre_period(self):
        if math.isnan(self.pre_period):
            return 0

    def get_nan_middle(self):
        if math.isnan(self.middle):
            return 0

    def __str__(self):
        return self.employer

