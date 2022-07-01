# Generated by Django 3.2.1 on 2022-07-01 05:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photoschool', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='student',
            name='wish_program',
            field=models.ManyToManyField(blank=True, to='photoschool.Program'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='editor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='lesson',
            name='parent',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child', to='photoschool.lesson'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='photoschool.program'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='theme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='photoschool.theme'),
        ),
    ]
