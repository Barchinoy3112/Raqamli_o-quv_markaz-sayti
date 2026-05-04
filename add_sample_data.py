#!/usr/bin/env python
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'raqamli_markaz.settings')
django.setup()

from kurslar.models import Talaba, Kurs, Enroll

course_seeds = [
    {
        'nom': 'Python Dasturlash',
        'tavsif': 'Python dasturlash tilini amaliy misollar bilan o\'rganish kursi.',
        'narx': 500000,
        'boshlangan_sana': date(2026, 4, 15),
        'muddat': 60,
    },
    {
        'nom': 'Django Web Framework',
        'tavsif': 'Django framework yordamida to\'liq web ilovalar yaratish.',
        'narx': 750000,
        'boshlangan_sana': date(2026, 5, 1),
        'muddat': 45,
    },
    {
        'nom': 'Frontend React.js',
        'tavsif': 'React.js yordamida zamonaviy va responsiv web interfeyslar yaratish.',
        'narx': 680000,
        'boshlangan_sana': date(2026, 5, 10),
        'muddat': 50,
    },
    {
        'nom': 'Data Analytics (Excel + SQL)',
        'tavsif': 'Excel va SQL orqali ma\'lumotlarni tahlil qilish hamda hisobot tayyorlash.',
        'narx': 620000,
        'boshlangan_sana': date(2026, 5, 18),
        'muddat': 40,
    },
]

courses = {}
for seed in course_seeds:
    kurs, _ = Kurs.objects.get_or_create(nom=seed['nom'], defaults=seed)
    courses[seed['nom']] = kurs

talaba1, _ = Talaba.objects.get_or_create(
    email='ali@example.com',
    defaults={
        'ism': 'Ali',
        'familiya': 'Karimov',
        'telefon': '+998901234567',
        'tugilgan_sana': date(2000, 1, 15),
        'password': '',
    },
)

talaba2, _ = Talaba.objects.get_or_create(
    email='malika@example.com',
    defaults={
        'ism': 'Malika',
        'familiya': 'Tursunova',
        'telefon': '+998907654321',
        'tugilgan_sana': date(1999, 6, 20),
        'password': '',
    },
)

Enroll.objects.get_or_create(talaba=talaba1, kurs=courses['Python Dasturlash'])
Enroll.objects.get_or_create(talaba=talaba2, kurs=courses['Django Web Framework'])
Enroll.objects.get_or_create(talaba=talaba1, kurs=courses['Frontend React.js'])

print('Namuna ma\'lumotlar dublikatlarsiz muvaffaqiyatli qo\'shildi!')