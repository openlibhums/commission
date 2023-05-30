from django import forms

from django_summernote.widgets import SummernoteWidget

from submission import models
from core import models as core_models
from plugins.commission import models as comm_models
from utils.forms import HTMLDateInput


class CommissionArticle(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.journal = kwargs.pop('journal')
        super(CommissionArticle, self).__init__(*args, **kwargs)
        self.fields[
            'section'].queryset = models.Section.objects.filter(
            journal=self.journal,
            public_submissions=True,
        )

    def save(self, commit=True):
        article = super(CommissionArticle, self).save(commit=False)
        article.journal = self.journal

        if commit:
            article.save()

        return article

    class Meta:
        model = models.Article
        fields = (
            'title',
            'section',
        )

        help_texts = {
            'owner': 'The owner must be an existing user. You can add a new '
                     'user from the manager area.',
        }


class DeadlineForm(forms.ModelForm):
    class Meta:
        model = comm_models.CommissionedArticle
        fields = ('deadline', 'submission_deadline', 'additional_information')
        widgets = {
            'deadline': HTMLDateInput,
            'submission_deadline': HTMLDateInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deadline'].required = True


class ExistingAuthor(forms.Form):
    author = forms.ModelChoiceField(
        queryset=core_models.Account.objects.all()
    )


class CommissionTemplateForm(forms.ModelForm):
    class Meta:
        model = comm_models.CommissionTemplate
        fields = (
            'name',
            'section',
            'template',
            'sent_on_acceptance',
        )
        widgets = {
            'template': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        self.journal = kwargs.pop('journal')
        super(CommissionTemplateForm, self).__init__(*args, **kwargs)
        self.fields[
            'section'].queryset = models.Section.objects.filter(
            journal=self.journal,
        )
