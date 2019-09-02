from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages

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
    success = True

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
                'commissioned_article',
                kwargs={'commissioned_article_id': com_article.pk}
            )
        )

    template = 'commission/commission_article.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@editor_user_required
def commissioned_article(request, commissioned_article_id):
    commissioned_article = get_object_or_404(
        models.CommissionedArticle,
        pk=commissioned_article_id,
    )
    success = True

    form = forms.CommissionArticle(instance=commissioned_article.article)

    if request.POST:

        if 'article' in request.POST:
            form = forms.CommissionArticle(
                request.POST,
                instance=commissioned_article.article,
            )

            if form.is_valid():
                form.save()

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Article saved.'
                )
            else:
                success = False

        if 'author' in request.POST:
            pass

        if success:
            return redirect(
                reverse(
                    'commissioned_article',
                    kwargs={'commissioned_article_id': commissioned_article.pk}
                )
            )

    template = 'commission/commissioned_article.html'
    context = {
        'commissioned_article': commissioned_article,
        'article': commissioned_article.article,
        'form': form,
    }

    return render(request, template, context)
