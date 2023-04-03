from django.contrib import admin

from plugins.commission import models


class CommissionArticleAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'journal',
        'commissioning_editor',
        'commissioned_author',
        'commissioned',
    )
    list_filter = (
        'journal',
    )
    raw_id_fields = (
        'article',
        'journal',
        'commissioning_editor',
        'commissioned_author',
    )


for pair in [
    (models.CommissionedArticle, CommissionArticleAdmin),
    (models.CommissionTemplate,),
]:
    admin.site.register(*pair)
