from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.core.files.storage import default_storage as storage


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_logo = models.ImageField(default='default.png', upload_to='company_logos')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.company_logo)

        MAX_WIDTH = 300 

        if img.width > MAX_WIDTH:
            resize_ratio = MAX_WIDTH / img.width
            output_size = (int(img.width*resize_ratio), int(img.height*resize_ratio))
            img = img.resize(output_size)
            file_handler = storage.open(self.company_logo.name, "w")
            img.save(file_handler, 'png')
            file_handler.close()            
