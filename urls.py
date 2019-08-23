from django.conf.urls import url

from plugins.commission import views

urlpatterns = [
    url(r'^$',
        views.index,
        name='commission_index'),
    url(r'^new/$',
        views.commission_article,
        name='commission_article'),
]
