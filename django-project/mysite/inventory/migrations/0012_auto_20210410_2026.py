# Generated by Django 3.1.6 on 2021-04-11 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_auto_20210410_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='label',
            field=models.SlugField(null=True, unique=True),
        ),
    ]
