from django.contrib import admin
from . import models

# Register your models here.
class DailyAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'usd']

class MonthlyAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'oil', 'usd']


admin.site.register(models.Daily, DailyAdmin)
admin.site.register(models.Monthly, MonthlyAdmin)
