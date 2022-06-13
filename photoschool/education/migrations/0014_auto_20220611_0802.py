# Generated by Django 3.2 on 2022-06-11 08:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0013_auto_20220610_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='program',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lesson', to='education.program'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='theme',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lesson', to='education.theme'),
        ),
    ]