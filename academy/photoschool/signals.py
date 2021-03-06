from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Student, Studying, Program


@receiver(m2m_changed, sender=Student.open_programs.through)
def create_studying(sender, action, instance, pk_set, **kwargs):

    if action == "post_add":
        new_studying = []

        for program in Program.objects.filter(pk__in=pk_set):
            new_studying.append(Studying(student=instance, lesson=program.first_lesson))
        Studying.objects.bulk_create(new_studying)
    elif action == "post_remove":
        Studying.objects.filter(lesson__program__in=pk_set).delete()
