# Generated by Django 3.2 on 2022-06-07 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0003_auto_20220605_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='program',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='theme',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]