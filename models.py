from django.db import models
from django.utils import timezone


class CommissionedArticle(models.Model):
    article = models.ForeignKey('submission.Article')
    commissioning_editor = models.ForeignKey('core.Account')
    commissioned = models.DateTimeField(default=timezone.now)
    
