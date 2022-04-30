from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:TITLE>", views.search, name="search"),
    path("new", views.new_page, name="new_page"),
    path("edit/<str:TITLE>", views.edit_page, name="edit_page"),
    path("random", views.random, name="random")
]
