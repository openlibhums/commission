from django.conf.urls import url

from plugins.commission import views

urlpatterns = [
    url(r'^$',
        views.index,
        name='commission_index'),
    url(r'^new/$',
        views.commission_article,
        name='commission_article'),
    url(r'^(?P<commissioned_article_id>\d+)/$',
        views.commissioned_article,
        name='commissioned_article'),
]
