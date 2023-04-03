from django import forms

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
        fields = ('deadline',)
        widgets = {
            'deadline': HTMLDateInput,
        }


class ExistingAuthor(forms.Form):
    author = forms.ModelChoiceField(
        queryset=core_models.Account.objects.all()
    )