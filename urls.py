from django.urls import re_path

from plugins.commission import views

urlpatterns = [
    re_path(r'^$',
        views.index,
        name='commission_index'),
    re_path(r'^manager/$',
        views.manager,
        name='commission_manager'),
    re_path(r'^manager/templates/$',
        views.section_template,
        name='commission_templates'),
    re_path(r'^manager/templates/new/$',
        views.section_template_form,
        name='commission_section_template_form_new'),
    re_path(r'^manager/templates/(?P<section_template_id>\d+)/$',
        views.section_template_form,
        name='commission_section_template_form'),


    re_path(r'^declined/$',
        views.declined_commissions,
        name='commission_declined'),
    re_path(r'^old/$',
        views.commission_article,
        name='commission_article'),
    re_path(r'^(?P<commissioned_article_id>\d+)/$',
        views.commissioned_article,
        name='commissioned_article'),

    re_path(r'^new/$',
        views.commission_article_owner,
        name='commission_article_owner'),
    re_path(r'^(?P<commissioned_article_id>\d+)/details/$',
        views.commissioned_article_details,
        name='commissioned_article_details'),
    re_path(r'^(?P<commissioned_article_id>\d+)/author/decision/$',
        views.commissioned_author_decision,
        name='commissioned_author_decision'),
    re_path(r'^reminders/$',
        views.commission_reminders,
        name='commission_reminders'),
    re_path(r'^(?P<commissioned_article_id>\d+)/reminders/preview/(?P<type_of_reminder>[\w-]+)/$',
        views.commission_preview_reminder,
        name='commission_preview_reminder'),
]
