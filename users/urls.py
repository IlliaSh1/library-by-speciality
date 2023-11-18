from django.urls import path, include

from . import views


urlpatterns = [
    path('', include('django.contrib.auth.urls'), name="index"),
    # path("login/", .as_view(), name="login")
    path('register/', views.Register.as_view(), name='register'),
]
