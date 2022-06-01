from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import DocsPost, DocsCategory

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'post_date', 'category', 'slug']
    list_filter = ('category',)
    search_fields = ['title']
    # exclude = ('slug',)
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(DocsPost, PostAdmin)
admin.site.register(DocsCategory, MPTTModelAdmin)
