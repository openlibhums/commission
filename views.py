from uuid import uuid4

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from plugins.commission import (
    forms,
    models,
    logic as commission_logic,
    plugin_settings,
)
from security.decorators import editor_user_required, any_editor_user_required
from submission.forms import AuthorForm
from submission import logic
from utils import shared, notify_helpers, setting_handler
from security.decorators import has_journal
from core import models as core_models, forms as core_forms


@has_journal
@any_editor_user_required
def index(request):
    """
    Displays a list of reports for a user to select.
    :param request: HttpRequest object
    :return: HttpResponse or HttpRedirect
    """
    commissioned_articles = models.CommissionedArticle.objects.all().exclude(
        author_decision_editor_check=True,
    )
    if request.user.is_section_editor(request) and not request.user.is_editor(request):
        commissioned_articles = commissioned_articles.filter(
            commissioning_editor=request.user,
        )
    template = 'commission/index.html'
    context = {
        'commissioned_articles': commissioned_articles,
    }
    return render(request, template, context)


@has_journal
@editor_user_required
def declined_commissions(request):
    """
    Displays a list of reports for a user to select.
    :param request: HttpRequest object
    :return: HttpResponse or HttpRedirect
    """
    commissioned_articles = models.CommissionedArticle.objects.filter(
        author_decision_editor_check=True,
    )
    template = 'commission/index.html'
    context = {
        'declined_articles': True,
        'commissioned_articles': commissioned_articles,
    }
    return render(request, template, context)


@has_journal
@any_editor_user_required
def declined_commissions(request):
    """
    Displays a list of reports for a user to select.
    :param request: HttpRequest object
    :return: HttpResponse or HttpRedirect
    """
    commissioned_articles = models.CommissionedArticle.objects.filter(
        author_decision_editor_check=True,
    )
    if request.user.is_section_editor(request) and not request.user.is_editor(request):
        commissioned_articles = commissioned_articles.filter(
            commissioning_editor=request.user,
        )
    template = 'commission/index.html'
    context = {
        'declined_articles': True,
        'commissioned_articles': commissioned_articles,
    }
    return render(request, template, context)


@has_journal
@any_editor_user_required
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
@any_editor_user_required
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
            commission_logic.remove_author_from_article(
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

        if 'send_message' in request.POST:
            message = request.POST.get('message')
            notify_helpers.send_email_with_body_from_user(
                request,
                'Commissioned Article',
                commissioned_article.article.owner.email,
                message,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Message sent.',
            )
            commissioned_article.message_sent = timezone.now()
            commissioned_article.save()

        if success:
            return redirect(
                reverse(
                    'commissioned_article',
                    kwargs={'commissioned_article_id': commissioned_article.pk}
                )
            )

    rendered_template = commission_logic.render_commission_email(
        request,
        commissioned_article,
    )

    template = 'commission/commissioned_article.html'
    context = {
        'commissioned_article': commissioned_article,
        'article': commissioned_article.article,
        'article_form': form,
        'existing_author_form': existing_author_form,
        'form': author_form,
        'rendered_template': rendered_template,
    }

    return render(request, template, context)


@has_journal
@any_editor_user_required
def commission_article_owner(request):
    """
    Allows an editor to set up a commissioned article's owner.
    """
    new_author_form = core_forms.QuickUserForm()

    if request.POST:
        owner = None
        if 'save_new_author' in request.POST:
            new_author_form = core_forms.QuickUserForm(
                request.POST,
            )
            if new_author_form.is_valid():
                owner = new_author_form.save()
                owner.set_password(shared.generate_password())
                owner.is_active = True
                owner.save()
                owner.add_account_role('author', request.journal)

        elif 'select_author' in request.POST:
            owner_id = request.POST.get('select_author')
            owner = get_object_or_404(
                core_models.Account,
                pk=owner_id,
            )
            owner.add_account_role('author', request.journal)

        if owner:
            comm_article = models.CommissionedArticle.objects.create(
                commissioning_editor=request.user,
                commissioned_author=owner,
                journal=request.journal,
            )
            return redirect(
                reverse(
                    'commissioned_article_details',
                    kwargs={
                        'commissioned_article_id': comm_article.pk,
                    }
                )
            )

    template = 'commission/commission_article_owner.html'
    context = {
        'new_author_form': new_author_form,
    }
    return render(
        request,
        template,
        context,
    )


@has_journal
@any_editor_user_required
def commissioned_article_details(request, commissioned_article_id):
    comm_article = get_object_or_404(
        models.CommissionedArticle,
        pk=commissioned_article_id,
    )

    duplicate_commissions = models.CommissionedArticle.objects.filter(
        commissioned_author=comm_article.commissioned_author,
    ).exclude(
        pk=comm_article.pk,
    )

    article_form = forms.CommissionArticle(
        instance=comm_article.article,
        journal=request.journal,
    )
    deadline_form = forms.DeadlineForm(
        instance=comm_article,
    )

    if request.POST:
        if 'html' in request.POST:
            email_content = request.POST.get('html')
            template_identifier = request.POST.get('template_id', 'default')

            if not template_identifier == 'default':
                template = get_object_or_404(
                    models.CommissionTemplate,
                    pk=template_identifier,
                )
                subject = template.subject
            else:
                subject = f'{request.journal.name} Commissioned Article'

            cc = request.journal.get_setting(
                group_name='plugin:commission',
                setting_name='commission_cc_address'
            )

            notify_helpers.send_email_with_body_from_user(
                request,
                subject,
                comm_article.commissioned_author.email,
                email_content,
                cc=[cc],
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Message sent.',
            )
            comm_article.message_sent = timezone.now()
            comm_article.save()
            return redirect(
                reverse(
                    'commissioned_article_details',
                    kwargs={
                        'commissioned_article_id': comm_article.pk,
                    }
                )
            )

        if 'cancel_commission' in request.POST:
            if comm_article.article:
                notify_helpers.send_email_with_body_from_setting_template(
                    request=request,
                    template='commission_withdrawn_email',
                    subject='Commission Cancelled',
                    to=comm_article.commissioned_author.email,
                    context={'commissioned_article': comm_article},
                    plugin=plugin_settings.CommissionPlugin.get_self(),
                )
                comm_article.article.delete()
            comm_article.delete()
            return redirect(
                reverse(
                    'commission_index'
                )
            )
        if 'archive_commission' in request.POST:
            comm_article.author_decision_editor_check = True
            comm_article.save()
            messages.add_message(
                request,
                messages.INFO,
                'Commission has been archived.'
            )
            return redirect(
                reverse(
                    'commission_index'
                )
            )
        if 'save_section' in request.POST:
            article_form = forms.CommissionArticle(
                request.POST,
                instance=comm_article.article,
                journal=request.journal,
            )
            deadline_form = forms.DeadlineForm(
                request.POST,
                instance=comm_article,
            )
            if article_form.is_valid() and deadline_form.is_valid():
                deadline_form.save()
                article = article_form.save(commit=False)
                article.owner = comm_article.commissioned_author
                article.save()
                comm_article.article = article
                comm_article.save()

                messages.add_message(
                    request,
                    messages.SUCCESS,
                    'Details saved.',
                )
                return redirect(
                    reverse(
                        'commissioned_article_details',
                        kwargs={
                            'commissioned_article_id': comm_article.pk,
                        }
                    )
                )

    template = 'commission/commission_article_details.html'
    context = {
        'comm_article': comm_article,
        'duplicate_commissions': duplicate_commissions,
        'article_form': article_form,
        'deadline_form': deadline_form,
        'rendered_templates': commission_logic.get_rendered_templates(
            request,
            comm_article,
        ),

    }
    return render(
        request,
        template,
        context,
    )


@has_journal
@login_required
def commissioned_author_decision(request, commissioned_article_id):
    comm_article = get_object_or_404(
        models.CommissionedArticle,
        pk=commissioned_article_id,
        commissioned_author=request.user,
        author_decision__isnull=True,
    )
    if request.POST:
        if 'accept' in request.POST:
            comm_article.author_decision = 'accepted'
            comm_article.send_author_notification_email(
                request,
            )
            messages.add_message(
                request,
                messages.INFO,
                'Thanks for letting us know that you can undertake a '
                'submission. You will find the article under "Incomplete '
                'Submissions"',
            )
        if 'decline' in request.POST:
            comm_article.author_decision = 'declined'
            messages.add_message(
                request,
                messages.INFO,
                'Thanks for letting us know that you cannot undertake a '
                'submission.',
            )

        comm_article.author_decision_date = timezone.now()
        comm_article.save()

        # Send email to editor
        email_context = {
            'commissioned_article': comm_article,
        }
        log_dict = {
            'target': comm_article.article,
            'types': 'Commission',
            'level': 'Info',
            'action_text': 'Commission Article email sent.',
        }
        notify_helpers.send_email_with_body_from_setting_template(
            request=request,
            template='commission_author_decision_made',
            subject=f'{request.journal.name} Commissioned Article',
            to=comm_article.commissioning_editor.email,
            context=email_context,
            plugin=plugin_settings.CommissionPlugin.get_self(),
            log_dict=log_dict,
        )
        return redirect(
            reverse(
                'core_dashboard',
            )
        )

    template = 'commission/commission_author_decision.html'
    context = {
        'comm_article': comm_article,
        'instructions': setting_handler.get_setting(
            setting_group_name='plugin:commission',
            setting_name='commission_author_decision_text',
            journal=request.journal,
        ).processed_value,
    }
    return render(
        request,
        template,
        context,
    )


@has_journal
@editor_user_required
def section_template(request):
    """
    Displays a list of section templates
    """
    section_templates = models.CommissionTemplate.objects.filter(
        section__journal=request.journal,
    )
    if request.POST and 'delete' in request.POST:
        id_to_delete = request.POST.get('delete')
        object_to_delete = get_object_or_404(
            models.CommissionTemplate,
            pk=id_to_delete,
            section__journal=request.journal,
        )
        object_to_delete.delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            'Template deleted',
        )
        return redirect(reverse('commission_templates'))
    template = 'commission/section_templates.html'
    context = {
        'section_templates': section_templates,
    }
    return render(
        request,
        template,
        context,
    )


@has_journal
@editor_user_required
def section_template_form(request, section_template_id=None):
    if section_template_id:
        section = get_object_or_404(
            models.CommissionTemplate,
            pk=section_template_id,
        )
    else:
        section = None

    form = forms.CommissionTemplateForm(
        instance=section,
        journal=request.journal,
    )
    if request.POST:
        form = forms.CommissionTemplateForm(
            request.POST,
            instance=section,
            journal=request.journal,
        )
        if form.is_valid():
            form.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                'Saved',
            )
            return redirect(
                reverse(
                    'commission_templates',
                )
            )
    template = 'commission/section_template_form.html'
    context = {
        'section': section,
        'form': form,
        'default_template': setting_handler.get_setting(
            'plugin:commission',
            'commission_article',
            request.journal,
        ).processed_value,
    }
    return render(
        request,
        template,
        context,
    )


@has_journal
@editor_user_required
def manager(request):
    """
    Displays a list of settings for editing.
    """
    settings = commission_logic.get_settings(request.journal)

    setting_group = 'plugin:commission'
    manager_form = core_forms.GeneratedSettingForm(
        settings=settings
    )
    if request.POST:
        manager_form = core_forms.GeneratedSettingForm(
            request.POST,
            settings=settings,
        )
        if manager_form.is_valid():
            manager_form.save(
                group=setting_group,
                journal=request.journal,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Form saved.',
            )
            return redirect(
                reverse('commission_manager')
            )

    template = 'commission/manager.html'
    context = {
        'manager_form': manager_form,
    }
    return render(
        request,
        template,
        context,
    )