from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db import models
from django.urls import reverse
import uuid

class User(AbstractUser):
    name = CharField(max_length=255)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    role = CharField(max_length=256)
    
    def delete_user(self):
        return reverse("staff:delete-user", args=[self.uuid])