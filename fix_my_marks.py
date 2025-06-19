import os
import random

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from datacenter.models import Schoolkid, Lesson, Commendation, Mark, Chastisement

COMMENDATION_TEXTS = [
    "Молодец!",
    "Отличная работа!",
    "Ты справился даже с трудным заданием!",
    "Продолжай в том же духе!",
    "Горжусь твоими успехами!",
    "Умничка!",
    "Так держать!",
    "Очень креативный подход!",
    "Потрясающий результат!",
    "Очень стараешься — это заметно!",
]


def fix_marks(schoolkid):
    Mark.objects.filter(schoolkid=schoolkid, points__in=[2, 3]).update(points=5)


def remove_chastisements(schoolkid):
    all_records = Chastisement.objects.filter(schoolkid=schoolkid)
    all_records.delete()


def create_commendation(schoolkid):
    lessons = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter
    )

    subjects = lessons.values_list('subject', flat=True).distinct()

    last = Commendation.objects.filter(schoolkid=schoolkid).order_by('-created').first()
    if last:
        last_subject_id = last.subject.id
        subjects = [s for s in subjects if s != last_subject_id] or list(subjects)

    subject_id = random.choice(subjects)
    lesson = lessons.filter(subject__id=subject_id).order_by('?').first()

    Commendation.objects.create(
        text=random.choice(COMMENDATION_TEXTS),
        created=lesson.date,
        schoolkid=schoolkid,
        subject=lesson.subject,
        teacher=lesson.teacher
    )


def main():
    name_fragment = input('Введите имя ученика: ')
    matching_kids = Schoolkid.objects.filter(full_name__contains=name_fragment)

    if not matching_kids.exists():
        print(f'Ученик с именем "{name_fragment}" не найден.')
    elif matching_kids.count() > 1:
        print(f'Найдено несколько учеников по фрагменту "{name_fragment}":')
        for kid in matching_kids:
            print(f' - {kid.full_name}')
        print('Введите имя одного из этих учеников.')
    else:
        school_kid = matching_kids.first()
        print(f'Ученик найден: {school_kid.full_name}. Вношу изменения...')
        fix_marks(school_kid)
        remove_chastisements(school_kid)
        create_commendation(school_kid)
        print('Изменения внесены.')


if __name__ == '__main__':
    main()
