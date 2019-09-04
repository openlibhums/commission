from core import models

from django.contrib import messages


def remove_author_from_article(request, article, author_id):
    try:
        author = models.Account.objects.get(pk=author_id)
    except models.Account.DoesNotExist:
        messages.add_message(
            request,
            messages.WARNING,
            'Author with this ID was not found.'
        )
        return

    if author not in article.authors.all():
        messages.add_message(
            request,
            messages.WARNING,
            'This author is not in the list of authors for this article.'
        )
    else:
        article.authors.remove(author)
        messages.add_message(
            request,
            messages.SUCCESS,
            'Author removed from article.'
        )
