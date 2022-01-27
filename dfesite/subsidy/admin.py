from django.contrib import admin
from . import models

# Register your models here.
class NewsHeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'news_title', 'pub_date', 'subsidy_period']

class SubsidyDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'newshead_id', 'subsidy_name', 'subsidy_value']

class BenefitDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'newshead_id', 'benefit_name', 'benefit_value']


admin.site.register(models.NewsHead, NewsHeadAdmin)
admin.site.register(models.SubsidyData, SubsidyDataAdmin)
admin.site.register(models.BenefitData, BenefitDataAdmin)
