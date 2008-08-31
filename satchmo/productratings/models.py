from django.contrib.comments.models import Comment
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from satchmo.product.models import Product

class ProductRating(models.Model):
    """A rating attached to a comment"""
    comment = models.OneToOneField(Comment, verbose_name="Rating", primary_key=True)
    rating = models.IntegerField(_("Rating"))

import config