#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Django
"""
from django.db import models
from django.utils.translation import ugettext_lazy as _

# BaseObject (abstract)
# ----------------------------------------------------------------------------
class BaseObject(models.Model):
    name = models.SlugField(verbose_name=_('Name'), max_length=100, unique=True, help_text=_('The name is only used in admin section. It will not be displayed in site.'))
    disabled = models.BooleanField(verbose_name=_('Disabled'), default=False, help_text=_('If disabled, this object will not be displayed in site and it will not be reachable with the url.'))
    creation = models.DateTimeField(verbose_name=_('Creation date'), auto_now_add=True)
    update = models.DateTimeField(verbose_name=_('Last update'), auto_now=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name
"""
