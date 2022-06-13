# Generated by Django 3.2 on 2022-06-12 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0016_studying_program'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studying',
            name='lesson',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='studying', to='education.lesson'),
        ),
    ]