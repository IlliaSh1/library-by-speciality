from django.urls import path

from . import views

from django.contrib.auth.decorators import login_required

app_name = "lib_by_spec"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    # path("<int:pk>/to_favorite", login_required(views.FavoriteView), 
    #      name="favorite_book")
    path("<int:pk>/to_favorite", views.ToFavorite, 
         name="favorite_book")
]

