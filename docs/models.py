from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from subscriptions.fields import JSONField
from django.apps import apps

class Category(models.Model):
    name = models.CharField('Category', max_length=30)
    content_type = models.ForeignKey(ContentType)
    filter_condition = JSONField(default="{}", help_text=_(u"Django ORM compatible lookup kwargs which are used to get the list of objects."))
    user_link = models.CharField(_(u"Link to User table"), max_length=64, help_text=_(u"Name of the model field which links to the User table.  'No-link' means this is the User table."), default="No-link")
          
    def __unicode__(self):
        return self.name

    def _get_filter(self):
        # simplejson likes to put unicode objects as dictionary keys
        # but keyword arguments must be str type
        fc = {}
        for k,v in self.filter_condition.iteritems():
            fc.update({str(k): v})
        return fc

    def object_list(self):
        return self.content_type.model_class()._default_manager.filter(**self._get_filter())

    def object_count(self):
        return self.object_list().count()

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ('name',)
    
    def clean (self):
        if self.user_link == "No-link":
            if self.content_type.model == "user":
                pass
            else:
                raise ValidationError(
                    _("Must specify the field that links to the user table.")
                    )
        else:
            if not hasattr(apps.get_model(self.content_type.app_label, self.content_type.model), self.user_link):
                raise ValidationError(
                    _("Must specify the field that links to the user table.")
                    )
    
class Subscription(models.Model):
    name = models.CharField('Subscription', max_length=60)
    cost = models.DecimalField('Price', max_digits=6, decimal_places=2, default=0.00)
    start_date = models.DateField('Start Date')
    end_date = models.DateField('End Date')
    category = models.ManyToManyField(
        Category,
        through         = 'SubscriptionCategory',
        related_name    = 'category',
        verbose_name    = 'Membership Category',
        help_text       = 'Membership Categories included in the Subscription'
        )
    
    def __unicode__(self):
        return u'%s' % (self.name)
    
    def clean (self):
        if self.start_date > self.end_date:
            raise ValidationError(
                _("Start Date must be earlier than End Date"),
                )
        
    def is_live(self):
        if self.end >= datetime.datetime.now().date():
            return True
        else:
            return False
    
class SubscriptionCategory (models.Model):
    subscription = models.ForeignKey(
        Subscription,
        verbose_name    = 'Subscription',
        help_text       = 'A class of membership (which could include several members, eg Family).',
    )
    category = models.ForeignKey(
        Category,
        verbose_name    = 'Category',
        help_text       = 'A class of member (eg adult)',
    )
    
    def __unicode__(self):
        return self.subscription.name + ' ' + self.category.name + ' link'
    
class MySubs(models.Model):
    user = models.ForeignKey(User)
    sub = models.ForeignKey(Subscription)
    token = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)
