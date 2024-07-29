from django.urls import path
from blog import views


urlpatterns = [
    path('', views.post_list.as_view(), name="post_list"),
    path('about/', views.about.as_view(), name="about"),

]