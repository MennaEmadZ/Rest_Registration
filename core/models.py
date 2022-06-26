from django.contrib.auth.models import User
from django.db import models
from django.db.models import DateField

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = DateField()

    def create(self, user,  birth_date):
        self.user = user
        self. birth_date = birth_date
        return self
