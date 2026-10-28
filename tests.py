import importlib
from unittest import skipUnless

from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import clear_url_caches, reverse
from packaging import version

from janeway import __version__ as janeway_version
from plugins.commission import forms, models, plugin_settings
from submission import models as submission_models
from utils.testing import helpers

# Core only calls the submission_form_init hook from Janeway 1.9.
HAS_SUBMISSION_FORM_INIT_HOOK = (
    version.parse(janeway_version.base_version) >= version.parse('1.9')
)


def create_licence(journal, name, short_name):
    return submission_models.Licence.objects.create(
        journal=journal,
        name=name,
        short_name=short_name,
        url='https://example.com',
    )


def reload_urlconf():
    """
    Reloads the URLconf so URLs for plugins installed after the first
    import of core.include_urls become available.
    """
    clear_url_caches()
    importlib.reload(importlib.import_module(settings.ROOT_URLCONF))
    importlib.reload(importlib.import_module('core.include_urls'))


@override_settings(URL_CONFIG='domain')
class CommissionSectionTests(TestCase):
    """
    Regression tests for openlibhums/commission#8: editors must be able to
    commission articles for sections that are closed for public submission.
    """

    @classmethod
    def setUpTestData(cls):
        helpers.create_press()
        cls.journal, _ = helpers.create_journals()
        helpers.create_roles(['editor', 'author'])
        plugin_settings.install()
        reload_urlconf()
        cls.editor = helpers.create_editor(cls.journal)
        cls.author = helpers.create_author(cls.journal)
        cls.public_section = helpers.create_section(
            cls.journal,
            name='Research Articles',
            plural='Research Articles',
        )
        cls.closed_section = helpers.create_section(
            cls.journal,
            name='Reviews',
            plural='Reviews',
            public_submissions=False,
        )
        cls.commissioned_article = models.CommissionedArticle.objects.create(
            commissioning_editor=cls.editor,
            commissioned_author=cls.author,
            journal=cls.journal,
        )

    def test_form_offers_sections_closed_for_public_submission(self):
        form = forms.CommissionArticle(journal=self.journal)
        self.assertIn(
            self.closed_section,
            form.fields['section'].queryset,
        )
        self.assertIn(
            self.public_section,
            form.fields['section'].queryset,
        )

    def test_form_labels_closed_sections(self):
        form = forms.CommissionArticle(journal=self.journal)
        labels = [
            label for value, label in form.fields['section'].choices if value
        ]
        self.assertIn('Reviews (Public Submission Closed)', labels)
        self.assertIn('Research Articles', labels)

    def test_form_accepts_closed_section(self):
        form = forms.CommissionArticle(
            data={
                'title': 'A Commissioned Review',
                'section': self.closed_section.pk,
            },
            journal=self.journal,
        )
        self.assertTrue(form.is_valid(), form.errors)
        article = form.save()
        self.assertEqual(article.section, self.closed_section)
        self.assertEqual(article.journal, self.journal)

    def test_save_section_accepts_closed_section(self):
        self.client.force_login(self.editor)
        url = reverse(
            'commissioned_article_details',
            kwargs={
                'commissioned_article_id': self.commissioned_article.pk,
            },
        )
        response = self.client.post(
            url,
            data={
                'save_section': '',
                'title': 'A Commissioned Review',
                'section': self.closed_section.pk,
                'deadline': '2026-08-01',
                'submission_deadline': '2026-12-01',
                'additional_information': '',
            },
            SERVER_NAME='testserver',
        )
        self.assertEqual(response.status_code, 302)
        self.commissioned_article.refresh_from_db()
        self.assertEqual(
            self.commissioned_article.article.section,
            self.closed_section,
        )
        self.assertEqual(
            self.commissioned_article.article.owner,
            self.author,
        )

    @skipUnless(
        HAS_SUBMISSION_FORM_INIT_HOOK,
        'Section locking needs the Janeway 1.9 submission_form_init hook',
    )
    def test_commissioned_author_section_is_locked(self):
        article = helpers.create_article(
            self.journal,
            title='A Commissioned Review',
            section=self.closed_section,
            owner=self.author,
        )
        models.CommissionedArticle.objects.create(
            article=article,
            commissioning_editor=self.editor,
            commissioned_author=self.author,
            journal=self.journal,
        )
        licence = create_licence(
            self.journal,
            name='Creative Commons 4',
            short_name='CC4',
        )
        self.client.force_login(self.author)
        url = reverse('submit_info', kwargs={'article_id': article.pk})

        response = self.client.get(url, SERVER_NAME='testserver')
        self.assertEqual(response.status_code, 200)
        section_field = response.context['form'].fields['section']
        self.assertTrue(section_field.disabled)
        self.assertIn(self.closed_section, section_field.queryset)

        # A tampered POST naming a different section must not move the
        # article out of the commissioned section.
        response = self.client.post(
            url,
            data={
                'title': 'A Commissioned Review',
                'section': self.public_section.pk,
                'license': licence.pk,
                'abstract': 'An abstract.',
                'language': 'eng',
            },
            SERVER_NAME='testserver',
        )
        self.assertEqual(response.status_code, 302)
        article.refresh_from_db()
        self.assertEqual(article.section, self.closed_section)

    def test_uncommissioned_author_cannot_pick_closed_section(self):
        article = helpers.create_article(
            self.journal,
            title='An Unsolicited Review',
            owner=self.author,
        )
        licence = create_licence(
            self.journal,
            name='Creative Commons 4',
            short_name='CC4',
        )
        self.client.force_login(self.author)
        response = self.client.post(
            reverse('submit_info', kwargs={'article_id': article.pk}),
            data={
                'title': 'An Unsolicited Review',
                'section': self.closed_section.pk,
                'license': licence.pk,
                'abstract': 'An abstract.',
                'language': 'eng',
            },
            SERVER_NAME='testserver',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('section', response.context['form'].errors)


@override_settings(URL_CONFIG='domain')
class CommissionLegacyViewTests(TestCase):
    """
    Regression tests confirming the legacy commissioning views pass the
    journal to CommissionArticle, which requires it.
    """

    @classmethod
    def setUpTestData(cls):
        helpers.create_press()
        cls.journal, _ = helpers.create_journals()
        helpers.create_roles(['editor', 'author'])
        plugin_settings.install()
        reload_urlconf()
        cls.editor = helpers.create_editor(cls.journal)
        cls.author = helpers.create_author(cls.journal)
        cls.section = helpers.create_section(
            cls.journal,
            name='Reviews',
            plural='Reviews',
            public_submissions=False,
        )

    def test_commission_article_get(self):
        self.client.force_login(self.editor)
        response = self.client.get(
            reverse('commission_article'),
            SERVER_NAME='testserver',
        )
        self.assertEqual(response.status_code, 200)

    def test_commission_article_post_closed_section(self):
        self.client.force_login(self.editor)
        response = self.client.post(
            reverse('commission_article'),
            data={
                'title': 'A Commissioned Review',
                'section': self.section.pk,
            },
            SERVER_NAME='testserver',
        )
        self.assertEqual(response.status_code, 302)
        commissioned_article = models.CommissionedArticle.objects.get(
            commissioning_editor=self.editor,
        )
        self.assertEqual(
            commissioned_article.article.section,
            self.section,
        )

    def test_commissioned_article_get(self):
        article = helpers.create_article(
            self.journal,
            title='A Commissioned Review',
            section=self.section,
            owner=self.author,
        )
        commissioned_article = models.CommissionedArticle.objects.create(
            article=article,
            commissioning_editor=self.editor,
            commissioned_author=self.author,
            journal=self.journal,
        )
        self.client.force_login(self.editor)
        response = self.client.get(
            reverse(
                'commissioned_article',
                kwargs={
                    'commissioned_article_id': commissioned_article.pk,
                },
            ),
            SERVER_NAME='testserver',
        )
        self.assertEqual(response.status_code, 200)
