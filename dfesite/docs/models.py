from datetime import datetime, date
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField
from mptt.models import MPTTModel, TreeForeignKey
from pytils.translit import slugify
import mptt


class DocsCategory(MPTTModel):
    class Meta:
        db_table = "docs_category"
        verbose_name_plural = "Разделы"
        verbose_name = "Раздел"
        ordering = ('tree_id', 'level')
    name = models.CharField(max_length=255, verbose_name="Раздел")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name=u'Родитель')
    slug = models.SlugField(null=False, unique=True, allow_unicode=True, max_length=255)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('docs:category', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


mptt.register(DocsCategory, order_insertion_by=['name'])


class DocsPost(models.Model):
    class Meta:
        db_table = "docs_post"
        verbose_name_plural = "Статьи"
        verbose_name = "Статья"

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    header_image = models.ImageField(null=True, blank=True, upload_to="docs/images/", verbose_name="Рисунок")
    title_tag = models.CharField(max_length=255, verbose_name="Тег")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    body = RichTextField(blank=True, null=True, verbose_name="Контент")
    post_date = models.DateField(auto_now_add=True, verbose_name="Дата публикации")
    category = TreeForeignKey(DocsCategory, blank=True, null=True, related_name='cat', on_delete=models.CASCADE,
                              verbose_name="Раздел")
    snippet = models.CharField(max_length=255, verbose_name="Аннотация")
    slug = models.SlugField(null=False, unique=True, allow_unicode=True, max_length=255)

    def __str__(self):
        return f"{self.title} | {str(self.author)}"

    def get_absolute_url(self):
        return reverse('docs:posts', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

