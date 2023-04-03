from django.conf.urls import url

from plugins.commission import views

urlpatterns = [
    url(r'^$',
        views.index,
        name='commission_index'),
    url(r'^declined/$',
        views.declined_commissions,
        name='commission_declined'),
    url(r'^old/$',
        views.commission_article,
        name='commission_article'),
    url(r'^(?P<commissioned_article_id>\d+)/$',
        views.commissioned_article,
        name='commissioned_article'),

    url(r'^new/$',
        views.commission_article_owner,
        name='commission_article_owner'),
    url(r'^(?P<commissioned_article_id>\d+)/details/$',
        views.commissioned_article_details,
        name='commissioned_article_details'),
    url(r'^(?P<commissioned_article_id>\d+)/author/decision/$',
        views.commissioned_author_decision,
        name='commissioned_author_decision'),
]
