from django.urls import path
from . import views

from pathlib import Path
app_name = Path(__file__).parent.name

urlpatterns = [
    path('', views.PostList.as_view(), name="post_list"),
    path('draft/', views.DraftList.as_view(), name="draft_list"),

    path('post/<int:pk>/', views.PostDetail.as_view(), name="post_detail"),
    path('post/create/', views.PostCreate.as_view(), name="post_create"),
    path('post/<int:pk>/update/', views.PostUpdate.as_view(), name="post_update"),
    path('post/<int:pk>/delete/', views.PostDelete.as_view(), name="post_delete"),
    path('post/<int:pk>/publish/', views.post_publish, name="post_publish"),

    # path('post/<int:post_pk>/comment/', views.add_comment_to_post, name="add_comment_to_post"),
    path('post/<int:post_pk>/comment/', views.CommentCreate.as_view(), name="add_comment_to_post"),

    path('comment/<int:pk>/approve/', views.comment_approve, name="comment_approve"),
    path('comment/<int:pk>/remove/', views.comment_remove, name="comment_remove"),

    path('about/', views.About.as_view(), name="about"),
    path('message/<str:msg>/', views.Message.as_view(), name="message"),

]