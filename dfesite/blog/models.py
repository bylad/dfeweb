from datetime import datetime, date
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField
from mptt.models import MPTTModel, TreeForeignKey
import mptt


class Category(MPTTModel):
    class Meta:
        db_table = "category"
        verbose_name_plural = "Разделы"
        verbose_name = "Раздел"
        ordering = ('tree_id', 'level')
    name = models.CharField(max_length=255, verbose_name="Раздел")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name=u'Родитель')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:posts')


mptt.register(Category, order_insertion_by=['name'])


class Post(models.Model):
    class Meta:
        db_table = "post"
        verbose_name_plural = "Статьи"
        verbose_name = "Статья"

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    header_image = models.ImageField(null=True, blank=True, upload_to="blog/images/", verbose_name="Рисунок")
    title_tag = models.CharField(max_length=255, verbose_name="Тег")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    body = RichTextField(blank=True, null=True, verbose_name="Контент")
    post_date = models.DateField(auto_now_add=True, verbose_name="Дата публикации")
    category = models.ForeignKey(Category, blank=True, null=True, related_name='cat', on_delete=models.CASCADE,
                                 verbose_name="Раздел")
    snippet = models.CharField(max_length=255, verbose_name="Аннотация")

    def __str__(self):
        return f"{self.title} | {str(self.author)}"

    def get_absolute_url(self):
        return reverse('blog:posts')
