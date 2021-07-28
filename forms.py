from django import forms

from submission import models
from core.middleware import GlobalRequestMiddleware
from core import models as core_models, forms as core_forms


class CommissionArticle(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CommissionArticle, self).__init__(*args, **kwargs)
        request = GlobalRequestMiddleware.get_current_request()
        self.fields['section'].queryset = models.Section.objects.filter(
            journal=request.journal,
            public_submissions=True,
        )

        self.fields['license'].queryset = models.Licence.objects.filter(
            journal=request.journal,
            available_for_submission=True,
        )

    class Meta:
        model = models.Article
        fields = (
            'title',
            'abstract',
            'owner',
            'language',
            'section',
            'license',
        )

        help_texts = {
            'owner': 'The owner must be an existing user. You can add a new '
                     'user from the manager area.',
        }


class ExistingAuthor(forms.Form):
    author = forms.ModelChoiceField(
        queryset=core_models.Account.objects.all()
    )
