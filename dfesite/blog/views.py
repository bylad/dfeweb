from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Post, Category
from .forms import CategoryForm, PostForm, EditForm


class BlogListView(ListView):
    model = Post
    template_name = 'blog/blog.html'
    ordering = ['-post_date']
    # ordering = ['-id']

    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(BlogListView, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
        return context

def CategoryView(request, cats):
    category_posts = Post.objects.filter(category__name=cats.replace('-', ' '))
    cat_menu_list = Category.objects.all()
    return render(request, 'blog/categories.html', {'cats': cats.title().replace('-', ' '),
                                                    'category_posts': category_posts,
                                                    'cat_menu_list': cat_menu_list})

class ArticleDetailView(DetailView):
    model = Post
    template_name = 'blog/article_details.html'

    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(ArticleDetailView, self).get_context_data(*args, **kwargs)
        cat_posts = Post.objects.filter(category__name=context['post'].category)
        context["cat_menu"] = cat_menu
        context["cat_posts"] = cat_posts
        return context

class AddPostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/add_post.html'

class AddCategoryView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'blog/add_category.html'

class UpdatePostView(UpdateView):
    model = Post
    form_class = EditForm
    template_name = 'blog/update_post.html'

    def get_context_data(self, *args, **kwargs):
        cat_menu = Category.objects.all()
        context = super(UpdatePostView, self).get_context_data(*args, **kwargs)
        context["cat_menu"] = cat_menu
        return context

class DeletePostView(DeleteView):
    model = Post
    template_name = 'blog/delete_post.html'
    success_url = reverse_lazy('blog:posts')
