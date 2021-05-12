from django.contrib import admin
from . import models

# Register your models here.
class PriceNewsAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'pub_date']

class PriceDataAdmin(admin.ModelAdmin):
    list_display = ['pricenews', 'product', 'price']

class PricePetrolHeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'petrol_title', 'pub_date']

class PricePetrolDataAdmin(admin.ModelAdmin):
    list_display = ['pricepetrolhead', 'petrol', 'price']

admin.site.register(models.PriceNews, PriceNewsAdmin)
admin.site.register(models.PriceData, PriceDataAdmin)
admin.site.register(models.PricePetrolHead, PricePetrolHeadAdmin)
admin.site.register(models.PricePetrolData, PricePetrolDataAdmin)
