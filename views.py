from django.shortcuts import render, reverse, redirect, get_object_or_404

from plugins.commission import forms, models
from security.decorators import editor_user_required


@editor_user_required
def index(request):
    """
    Displays a list of reports for a user to select.
    :param request: HttpRequest object
    :return: HttpResponse or HttpRedirect
    """
    commissioned_articles = models.CommissionedArticle.objects.all()
    template = 'commission/index.html'
    context = {
        'commissioned_articles': commissioned_articles,
    }
    return render(request, template, context)


@editor_user_required
def commission_article(request):
    """
    Allows an editor to commission an article.
    :param request: HttpRequest
    :return: HttpResponse
    """
    form = forms.CommissionArticle()

    if request.POST:
        form = forms.CommissionArticle(request.POST)
        if form.is_valid():
            _article = form.save()
            com_article, c = models.CommissionedArticle.objects.get_or_create(
                article=_article,
                commissioning_editor=request.user
            )
            return redirect(
                reverse(
                    'commission_index',
                )
            )

    template = 'commission/commission_article.html'
    context = {
        'form': form,
    }

    return render(request, template, context)
