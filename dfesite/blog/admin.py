from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Post, Category

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'post_date', 'category']
    list_filter = ('category',)
    search_fields = ['title']


admin.site.register(Post, PostAdmin)
admin.site.register(Category, MPTTModelAdmin)
