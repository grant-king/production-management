from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_logo = models.ImageField(default='default.png', upload_to='company_logos')

    def __str__(self):
        return f'{self.user.username} Profile'