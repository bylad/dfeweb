from django.urls import path
from blog.views import BlogListView, ArticleDetailView, AddPostView, UpdatePostView, \
                        DeletePostView, AddCategoryView, CategoryView

app_name = 'blog'

urlpatterns = [
    path('', BlogListView.as_view(), name='posts'),
    path('article/<int:pk>', ArticleDetailView.as_view(), name='article-detail'),
    path('add_post/', AddPostView.as_view(), name='add_post'),
    path('add_category/', AddCategoryView.as_view(), name='add_category'),
    path('article/edit/<int:pk>', UpdatePostView.as_view(), name='update_post'),
    path('article/<int:pk>/remove', DeletePostView.as_view(), name='delete_post'),
    path('category/<str:cats>/', CategoryView, name='category'),
]