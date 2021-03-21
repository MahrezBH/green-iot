from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db import models
from django.urls import reverse
import uuid
import datetime
from django.utils.translation import ugettext_lazy as _
from datetime import date

class User(AbstractUser):
    name = CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    role = CharField(max_length=256)
    email = models.EmailField(_('email address'), unique=True)
    paid_until = models.DateField(null=True, blank=True)
    stripe_customer = CharField(max_length=160,default=None,null=True,blank=True)
    stripe_subscription = CharField(max_length=160,default=None,null=True,blank=True)
    plan =  CharField(max_length=160,default=None,null=True,blank=True)
    def delete_user(self):
        return reverse("staff:delete-user", args=[self.uuid])
    
    def is_paid(self, current_date = datetime.date.today()):
        if not self.paid_until:
            return False
        return current_date < self.paid_until
    
    def set_paid_until(self, paid_until):
        self.paid_until = date.fromtimestamp(int(paid_until))
        self.save()