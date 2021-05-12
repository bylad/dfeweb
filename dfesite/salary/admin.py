from django.contrib import admin
from . import models

# Register your models here.
class SalaryNewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'pub_date']

class SalaryHeadAdmin(admin.ModelAdmin):
    list_display = ['salarynews_id', 'current_my', 'period_mmy', 'pre_month', 'pre_year', 'pre_period', 'middle']

class SalaryAdmin(admin.ModelAdmin):
    list_display = ['id', 'salarynews_id', 'employer', 'current', 'pre_month', 'pre_year', 'period', 'pre_period', 'middle']

admin.site.register(models.SalaryNews, SalaryNewsAdmin)
admin.site.register(models.SalaryHead, SalaryHeadAdmin)
admin.site.register(models.Salary, SalaryAdmin)
