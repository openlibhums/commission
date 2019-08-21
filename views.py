from django.shortcuts import render, reverse, redirect, get_object_or_404

from security.decorators import editor_user_required


@editor_user_required
def index(request):
    """
    Displays a list of reports for a user to select.
    :param request: HttpRequest object
    :return: HttpResponse or HttpRedirect
    """
    template = 'commission/index.html'
    context = {}
    return render(request, template, context)
