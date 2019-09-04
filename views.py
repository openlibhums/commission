from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages

from plugins.commission import forms, models, utils
from security.decorators import editor_user_required
from submission.forms import AuthorForm
from submission import logic
from utils import shared
from security.decorators import has_journal


@has_journal
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


@has_journal
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


@has_journal
@editor_user_required
def commissioned_article(request, commissioned_article_id):
    commissioned_article = get_object_or_404(
        models.CommissionedArticle,
        pk=commissioned_article_id,
    )
    success = True

    form = forms.CommissionArticle(instance=commissioned_article.article)
    existing_author_form = forms.ExistingAuthor()
    author_form = AuthorForm()

    if request.POST:
        
        if 'existing_author' in request.POST:
            existing_author_form = forms.ExistingAuthor(request.POST)
            if existing_author_form.is_valid():
                author = existing_author_form.cleaned_data.get('author')
                commissioned_article.article.authors.add(author)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Author added to the article.',
                )

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

        if 'delete_author' in request.POST:
            delete_author_id = request.POST.get('delete_author')
            utils.remove_author_from_article(
                request,
                commissioned_article.article,
                delete_author_id
            )

        if 'add_author' in request.POST:
            author_form = AuthorForm(request.POST)
            modal = 'author'

            author_exists = logic.check_author_exists(request.POST.get('email'))
            if author_exists:
                commissioned_article.article.authors.add(author_exists)
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    '%s added to the article' % author_exists.full_name(),
                )
            else:
                if author_form.is_valid():
                    new_author = author_form.save(commit=False)
                    new_author.username = new_author.email
                    new_author.set_password(shared.generate_password())
                    new_author.save()
                    new_author.add_account_role(
                        role_slug='author',
                        journal=request.journal,
                    )
                    commissioned_article.article.authors.add(new_author)
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        '%s added to the article' % new_author.full_name(),
                    )

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
        'article_form': form,
        'existing_author_form': existing_author_form,
        'form': author_form,
    }

    return render(request, template, context)
