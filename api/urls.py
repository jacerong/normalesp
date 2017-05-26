from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    url(r'^spell_checking/$', views.spell_checking),
]

urlpatterns = format_suffix_patterns(urlpatterns)
