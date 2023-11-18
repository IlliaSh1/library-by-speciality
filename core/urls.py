from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='core/index.html'), name='home'),
    path('admin/', admin.site.urls),

    path('users/', include("users.urls")),
    path('lib/', include("lib_by_spec.urls"), name="lib"),
    path('parser/', include("book_parser.urls"), name="parser"),
    path('disciplines/', include("discipline_selection.urls"), name="disciplines"),
    # path("debug/", include("debug_toolbar.urls")),
]
