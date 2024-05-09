from django.conf.urls import url

from plugins.commission import views

urlpatterns = [
    url(r'^$',
        views.index,
        name='commission_index'),
    url(r'^manager/$',
        views.manager,
        name='commission_manager'),
    url(r'^manager/templates/$',
        views.section_template,
        name='commission_templates'),
    url(r'^manager/templates/new/$',
        views.section_template_form,
        name='commission_section_template_form_new'),
    url(r'^manager/templates/(?P<section_template_id>\d+)/$',
        views.section_template_form,
        name='commission_section_template_form'),


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
    url(r'^reminders/$',
        views.commission_reminders,
        name='commission_reminders'),
    url(r'^(?P<commissioned_article_id>\d+)/reminders/preview/(?P<type_of_reminder>[\w-]+)/$',
        views.commission_preview_reminder,
        name='commission_preview_reminder'),
]
