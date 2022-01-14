from django.contrib import admin
from . import models

# Register your models here.
class MigrationHeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'migration_title', 'pub_date']

class MigrationDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'migrationhead', 'arrived', 'departed', 'gain']

class ZagsHeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'zags_title', 'pub_date']

class ZagsDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'zagshead', 'born', 'died', 'wedd', 'divorce']


admin.site.register(models.MigrationHead, MigrationHeadAdmin)
admin.site.register(models.MigrationData, MigrationDataAdmin)
admin.site.register(models.ZagsHead, ZagsHeadAdmin)
admin.site.register(models.ZagsData, ZagsDataAdmin)
