# Generated by Django 3.2 on 2022-06-08 13:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('education', '0007_alter_student_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='open_program',
            field=models.ManyToManyField(blank=True, null=True, related_name='students', to='education.Program'),
        ),
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.customuser'),
        ),
    ]