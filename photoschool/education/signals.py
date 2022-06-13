from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from education.models import Student, Studying, Program


@receiver(m2m_changed, sender=Student.open_program.through)
def create_studying(sender, action, instance, pk_set, **kwargs):
    print(action, instance, pk_set)

    if action == "post_add":
        new_studying = list()

        for program in Program.objects.filter(pk__in=pk_set):
            print(program.first_lesson)
            new_studying.append(Studying(student=instance, lesson=program.first_lesson))
        Studying.objects.bulk_create(new_studying)

    # if action == "post_delete":
    #
    #     for program in Program.objects.filter(pk__in=pk_set):
    #         print(program.first_lesson)
    #         new_studying.append(Studying(student=instance, lesson=program.first_lesson))
    #     Studying.objects.filter(pk__in=delitin_list).delete()
