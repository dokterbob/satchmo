from django.contrib.comments.models import Comment
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from signals_ahoy.signals import collect_urls
import product
import satchmo_store

class ProductRating(models.Model):
    """A rating attached to a comment"""
    comment = models.OneToOneField(Comment, verbose_name="Rating", primary_key=True)
    rating = models.IntegerField(_("Rating"))

import config
from urls import add_product_urls, add_comment_urls
collect_urls.connect(add_product_urls, sender=product)
collect_urls.connect(add_comment_urls, sender=satchmo_store)