from django.urls import path
from docs.views import DocsListView, ArticleDetailView, AddPostView, UpdatePostView, \
                       DeletePostView, AddCategoryView, CategoryView

app_name = 'docs'

urlpatterns = [
    path('', DocsListView.as_view(), name='posts'),
    path('article/<slug:slug>', ArticleDetailView.as_view(), name='article-detail'),
    path('add_post/', AddPostView.as_view(), name='add_post'),
    path('add_category/', AddCategoryView.as_view(), name='add_category'),
    path('article/edit/<slug:slug>', UpdatePostView.as_view(), name='update_post'),
    path('article/<slug:slug>/remove', DeletePostView.as_view(), name='delete_post'),
    path('category/<slug:slug>/', CategoryView.as_view(), name='category'),
]
