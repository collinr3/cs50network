
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("posts", views.get_posts, name="posts"),
    path("following", views.get_following, name="following"),
    path("read", views.read, name="read"),
    path("like", views.like, name="like"),
    path("follow", views.follow, name="follow"),
    path("update", views.update, name="update"),
]
