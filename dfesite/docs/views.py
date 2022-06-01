
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CategoryForm, PostForm, EditForm
from .models import DocsPost, DocsCategory
from pathlib import PurePath


class DocsListView(ListView):
    model = DocsPost
    template_name = 'docs/docs.html'
    ordering = ['-id']

    def get_context_data(self, *args, **kwargs):
        cat_menu = DocsCategory.objects.all()
        context = super(DocsListView, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
        category_roots = DocsCategory.objects.filter(parent=None)
        context["categories"] = category_roots.get_descendants(include_self=True)
        return context

class CategoryView(ListView):
    model = DocsCategory
    template_name = 'docs/categories.html'
    # ordering = ['-post_date']
    # ordering = ['-id']

    def get_context_data(self, *args, **kwargs):
        cat_menu_list = DocsCategory.objects.all()
        context = super(CategoryView, self).get_context_data(*args, **kwargs)
        category_posts = DocsPost.objects.filter(category__slug=self.kwargs['slug'])
        context["cat_menu"] = cat_menu_list
        context['category_posts'] = category_posts
        path_slug = PurePath(self.request.path).name
        cat = DocsCategory.objects.filter(slug=path_slug)[0]
        context['cat'] = cat
        context['children'] = cat.get_children()
        return context


class ArticleDetailView(DetailView):
    model = DocsPost
    template_name = 'docs/article_details.html'

    def get_context_data(self, *args, **kwargs):
        cat_menu = DocsCategory.objects.all()
        context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)
        cat_posts = DocsPost.objects.filter(category__name=context['docspost'].category)
        context["cat_menu"] = cat_menu
        context["cat_posts"] = cat_posts
        return context

class AddPostView(CreateView):
    model = DocsPost
    form_class = PostForm
    template_name = 'docs/add_post.html'

    def get_success_url(self):
        return reverse_lazy('docs:category', kwargs={'slug': self.object.category.slug})

    def get_context_data(self, **kwargs):
        cat_menu = DocsCategory.objects.all()
        context = super(AddPostView, self).get_context_data(**kwargs)
        context["cat_menu"] = cat_menu
        return context


class AddCategoryView(CreateView):
    model = DocsCategory
    form_class = CategoryForm
    template_name = 'docs/add_category.html'

    def get_context_data(self, **kwargs):
        cat_menu = DocsCategory.objects.all()
        context = super(AddCategoryView, self).get_context_data(**kwargs)
        context["cat_menu"] = cat_menu
        return context

class UpdatePostView(UpdateView):
    model = DocsPost
    form_class = EditForm
    template_name = 'docs/update_post.html'

    def get_success_url(self):
        return reverse_lazy('docs:category', kwargs={'slug': self.object.category.slug})

    def get_context_data(self, *args, **kwargs):
        cat_menu = DocsCategory.objects.all()
        context = super(UpdatePostView, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
        return context

class DeletePostView(DeleteView):
    model = DocsPost
    template_name = 'docs/delete_post.html'
    success_url = reverse_lazy('docs:posts')

    def get_context_data(self, **kwargs):
        cat_menu = DocsCategory.objects.all()
        context = super(DeletePostView, self).get_context_data(**kwargs)
        context["cat_menu"] = cat_menu
        return context

