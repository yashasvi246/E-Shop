# Generated by Django 2.2.14 on 2021-05-17 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20210517_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='offer_value',
            field=models.IntegerField(default=10),
        ),
    ]
