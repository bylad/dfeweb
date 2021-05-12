from django.contrib import admin
from . import models

# Register your models here.
class IndustryNewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'pub_date']

class IndustryIndexAdmin(admin.ModelAdmin):
    list_display = ['id', 'production_index', 'pre_year_index', 'cur_year_index', 'pre_cur_index']


admin.site.register(models.IndustryNews, IndustryNewsAdmin)
admin.site.register(models.IndustryIndex, IndustryIndexAdmin)
admin.site.register(models.IndustryProduction)
