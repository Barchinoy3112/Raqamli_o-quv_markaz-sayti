import re
from datetime import date
from xml.sax.saxutils import escape

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Count, Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST
from kurslar.models import Talaba, Kurs, Enroll


def validate_person_name(value, field_label):
    if not value:
        return f'{field_label} kiriting.'
    if len(value) < 2:
        return f'{field_label} kamida 2 ta belgidan iborat bo\'lsin.'
    if len(value) > 100:
        return f'{field_label} 100 ta belgidan oshmasin.'
    if not re.fullmatch(r"[A-Za-zА-Яа-яЁёЎўҚқҒғҲҳІі'` -]+", value):
        return f'{field_label} faqat harflar, bo\'sh joy, tire yoki apostrofdan iborat bo\'lsin.'
    return ''


def normalize_uz_phone(value):
    if not value.isdigit():
        return '', 'Telefon raqamida faqat raqamlar bo\'lishi kerak.'
    if value.startswith('998') and len(value) == 12:
        return f'+{value}', ''
    if len(value) == 9:
        return f'+998{value}', ''
    return '', 'Telefon raqamini 901234567 yoki 998901234567 formatida kiriting.'

def home(request):
    kurslar_list = Kurs.objects.all()
    enrolls_list = Enroll.objects.select_related('kurs')
    course_count = kurslar_list.count()
    total_enrollments = enrolls_list.count()
    active_enrollments = enrolls_list.filter(holat='faol').count()
    completed_courses = enrolls_list.filter(holat='tugagan').count()
    cancelled_enrollments = enrolls_list.filter(holat='bekor_qilingan').count()
    total_duration = sum(kurs.muddat or 0 for kurs in kurslar_list)
    stats = {
        'total_students': Talaba.objects.count(),
        'total_courses': course_count,
        'active_enrollments': active_enrollments,
        'completed_courses': completed_courses,
        'avg_course_duration': round(total_duration / course_count) if course_count else 0,
        'total_revenue': sum(enroll.kurs.narx or 0 for enroll in enrolls_list),
        'cancelled_enrollments': cancelled_enrollments,
        'completion_rate': round((completed_courses / total_enrollments) * 100) if total_enrollments else 0,
    }
    return render(request, 'home.html', {'stats': stats})

def kurslar(request):
    kurslar_list = list(Kurs.objects.all())
    image_map = {
        'python': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?auto=format&fit=crop&w=900&q=80',
        'django': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=900&q=80',
        'react': 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=900&q=80',
        'data': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=80',
        'analytics': 'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?auto=format&fit=crop&w=900&q=80',
        'grafik': 'https://images.unsplash.com/photo-1626785774573-4b799315345d?auto=format&fit=crop&w=900&q=80',
        'photoshop': 'https://images.unsplash.com/photo-1572044162444-ad60f128bdea?auto=format&fit=crop&w=900&q=80',
        'smm': 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&w=900&q=80',
        'marketing': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=900&q=80',
    }
    fallback_images = [
        'https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&w=900&q=80',
        'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=900&q=80',
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80',
    ]
    for idx, kurs in enumerate(kurslar_list):
        lower_name = (kurs.nom or '').lower()
        kurs.image_url = next(
            (url for key, url in image_map.items() if key in lower_name),
            fallback_images[idx % len(fallback_images)],
        )
    enrolled_course_ids = set()
    talaba_id = request.session.get('talaba_id')
    if talaba_id:
        enrolled_course_ids = set(
            Enroll.objects.filter(talaba_id=talaba_id)
            .exclude(holat='bekor_qilingan')
            .values_list('kurs_id', flat=True)
        )
    return render(request, 'kurslar.html', {
        'kurslar': kurslar_list,
        'enrolled_course_ids': enrolled_course_ids,
    })

def talabalar(request):
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Talabalar ro'yxatini ko'rish huquqi faqat adminlarda mavjud.")
        return redirect('home')
    talabalar_list = Talaba.objects.all()
    return render(request, 'talabalar.html', {'talabalar': talabalar_list})

def enrolls(request):
    if request.user.is_staff:
        enrolls_qs = Enroll.objects.select_related('talaba', 'kurs')
    else:
        talaba_id = request.session.get('talaba_id')
        if not talaba_id:
            messages.info(request, "Ro'yxatlarni ko'rish uchun avval tizimga kiring.")
            return redirect('login')
        enrolls_qs = Enroll.objects.filter(talaba_id=talaba_id).select_related('talaba', 'kurs')

    enroll_summary = (
        enrolls_qs.values('kurs_id', 'kurs__nom')
        .annotate(
            total_students=Count('talaba_id', distinct=True),
            active_students=Count('talaba_id', filter=Q(holat='faol'), distinct=True),
            total_enrollments=Count('id'),
        )
        .order_by('kurs__nom')
    )
    total_unique_students = enrolls_qs.values('talaba_id').distinct().count()
    return render(request, 'enrolls.html', {
        'enroll_summary': enroll_summary,
        'total_unique_students': total_unique_students,
    })


@require_POST
def kursga_yozilish(request, kurs_id):
    talaba_id = request.session.get('talaba_id')
    if not talaba_id:
        messages.info(request, 'Kursga yozilish uchun avval tizimga kiring.')
        return redirect('login')

    talaba = Talaba.objects.filter(id=talaba_id).first()
    if not talaba:
        request.session.pop('talaba_id', None)
        messages.error(request, 'Profil topilmadi. Qaytadan tizimga kiring.')
        return redirect('login')

    kurs = get_object_or_404(Kurs, id=kurs_id)
    enroll = Enroll.objects.filter(talaba=talaba, kurs=kurs).first()

    if enroll:
        if enroll.holat == 'bekor_qilingan':
            enroll.holat = 'faol'
            enroll.save(update_fields=['holat'])
            messages.success(request, f'{kurs.nom} kursiga qayta yozildingiz.')
        else:
            messages.info(request, f'Siz {kurs.nom} kursiga allaqachon yozilgansiz.')
    else:
        Enroll.objects.create(talaba=talaba, kurs=kurs, holat='faol')
        messages.success(request, f'{kurs.nom} kursiga muvaffaqiyatli yozildingiz.')

    return redirect('profile')

@never_cache
def register(request):
    errors = {}
    form_data = {}

    if request.method == 'POST':
        if request.user.is_authenticated:
            auth_logout(request)

        form_data = {
            'ism': request.POST.get('ism', '').strip(),
            'familiya': request.POST.get('familiya', '').strip(),
            'email': request.POST.get('email', '').strip().lower(),
            'telefon': request.POST.get('telefon', '').strip(),
            'tugilgan_sana': request.POST.get('tugilgan_sana', '').strip(),
        }
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        birth_date = parse_date(form_data['tugilgan_sana']) if form_data['tugilgan_sana'] else None
        normalized_phone, phone_error = normalize_uz_phone(form_data['telefon'])

        ism_error = validate_person_name(form_data['ism'], 'Ismingizni')
        familiya_error = validate_person_name(form_data['familiya'], 'Familiyangizni')
        if ism_error:
            errors['ism'] = ism_error
        if familiya_error:
            errors['familiya'] = familiya_error
        if not form_data['email']:
            errors['email'] = 'Email manzilini kiriting.'
        elif len(form_data['email']) > 254:
            errors['email'] = 'Email manzili juda uzun.'
        else:
            try:
                validate_email(form_data['email'])
            except ValidationError:
                errors['email'] = 'Email manzili noto\'g\'ri formatda.'
        if form_data['email'] and Talaba.objects.filter(email=form_data['email']).exists():
            errors['email'] = 'Bu email bilan talaba allaqachon ro\'yxatdan o\'tgan.'
        if not form_data['telefon']:
            errors['telefon'] = 'Telefon raqamingizni kiriting.'
        elif phone_error:
            errors['telefon'] = phone_error
        if not birth_date:
            errors['tugilgan_sana'] = 'Tug\'ilgan sanani to\'g\'ri kiriting.'
        elif birth_date >= date.today():
            errors['tugilgan_sana'] = 'Tug\'ilgan sana bugundan oldin bo\'lishi kerak.'
        else:
            age = date.today().year - birth_date.year - ((date.today().month, date.today().day) < (birth_date.month, birth_date.day))
            if age < 5:
                errors['tugilgan_sana'] = 'Talaba yoshi kamida 5 yosh bo\'lishi kerak.'
            elif age > 100:
                errors['tugilgan_sana'] = 'Tug\'ilgan sanani qayta tekshiring.'
        if not password:
            errors['password'] = 'Parol kiriting.'
        elif len(password) < 6:
            errors['password'] = 'Parol kamida 6 ta belgidan iborat bo\'lsin.'
        elif password.isdigit():
            errors['password'] = 'Parol faqat raqamlardan iborat bo\'lmasin.'
        if not password2:
            errors['password2'] = 'Parolni tasdiqlang.'
        elif password != password2:
            errors['password2'] = 'Parollar mos kelmadi.'

        if errors:
            messages.error(request, 'Iltimos, belgilangan xatoliklarni tuzating.')
        else:
            talaba = Talaba.objects.create(
                ism=form_data['ism'],
                familiya=form_data['familiya'],
                email=form_data['email'],
                telefon=normalized_phone,
                tugilgan_sana=birth_date,
                password=make_password(password),
            )
            request.session['talaba_id'] = talaba.id
            messages.success(request, 'Ro\'yxatdan o\'tish muvaffaqiyatli yakunlandi.')
            return redirect('profile')

    return render(request, 'register.html', {'errors': errors, 'form_data': form_data})

@never_cache
def login(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            auth_logout(request)

        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        talaba = Talaba.objects.filter(email=email).first()

        if talaba and (check_password(password, talaba.password) or talaba.password == password):
            if talaba.password == password:
                talaba.password = make_password(password)
                talaba.save(update_fields=['password'])
            request.session['talaba_id'] = talaba.id
            messages.success(request, 'Tizimga muvaffaqiyatli kirdingiz.')
            return redirect('profile')

        messages.error(request, 'Email yoki parol noto\'g\'ri.')

    return render(request, 'login.html')

def profile(request):
    talaba_id = request.session.get('talaba_id')
    if not talaba_id:
        messages.info(request, 'Profilni ko\'rish uchun tizimga kiring.')
        return redirect('login')

    if request.user.is_authenticated:
        auth_logout(request)
        request.session['talaba_id'] = talaba_id

    talaba = Talaba.objects.filter(id=talaba_id).first()
    if not talaba:
        request.session.pop('talaba_id', None)
        messages.error(request, 'Profil topilmadi. Qaytadan tizimga kiring.')
        return redirect('login')

    enrolls_list = Enroll.objects.filter(talaba=talaba).select_related('kurs')
    return render(request, 'profile.html', {'talaba': talaba, 'enrolls': enrolls_list})

def logout(request):
    request.session.pop('talaba_id', None)
    if request.user.is_authenticated:
        auth_logout(request)
    messages.success(request, 'Tizimdan chiqdingiz.')
    return redirect('home')


def robots_txt(request):
    sitemap_url = request.build_absolute_uri(reverse('sitemap_xml'))
    content = "\n".join([
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /api/",
        f"Sitemap: {sitemap_url}",
    ])
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


def sitemap_xml(request):
    page_names = ['home', 'kurslar', 'enrolls', 'register', 'login']
    urls = []
    for name in page_names:
        loc = request.build_absolute_uri(reverse(name))
        urls.append(
            "<url>"
            f"<loc>{escape(loc)}</loc>"
            "<changefreq>weekly</changefreq>"
            "<priority>0.8</priority>"
            "</url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{''.join(urls)}"
        '</urlset>'
    )
    return HttpResponse(xml, content_type='application/xml; charset=utf-8')


def manifest_webmanifest(request):
    manifest = {
        "name": "Raqamli O'quv Markaz",
        "short_name": "RO Markaz",
        "start_url": reverse('home'),
        "scope": "/",
        "display": "standalone",
        "background_color": "#f8fafc",
        "theme_color": "#14532d",
        "description": "Kurslar va ro'yxatdan o'tishlarni boshqarish platformasi.",
        "icons": [
            {"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml"}
        ],
    }
    import json
    return HttpResponse(
        json.dumps(manifest, ensure_ascii=False),
        content_type='application/manifest+json; charset=utf-8',
    )


def service_worker_js(request):
    js = """
const CACHE_NAME = "raqamli-oquv-markaz-v2";
const OFFLINE_URLS = ["/"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(OFFLINE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  const isHtmlNavigation = event.request.mode === "navigate" ||
    event.request.headers.get("accept")?.includes("text/html");
  const hasFormToken = ["/admin/", "/login/", "/register/", "/kurslar/"].some((path) =>
    url.pathname.startsWith(path)
  );
  if (isHtmlNavigation || hasFormToken) return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        if (!response.ok) return response;
        const cloned = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, cloned));
        return response;
      }).catch(() => caches.match("/"));
    })
  );
});
""".strip()
    return HttpResponse(js, content_type='application/javascript; charset=utf-8')


def app_icon_svg(request):
    svg = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#14532d"/>
  <path d="M96 176h320v160H96z" fill="#0f766e"/>
  <path d="M116 196h280v120H116z" fill="#fff" opacity="0.95"/>
  <path d="M160 244h192" stroke="#14532d" stroke-width="24" stroke-linecap="round"/>
  <circle cx="256" cy="128" r="44" fill="#f59e0b"/>
</svg>
""".strip()
    return HttpResponse(svg, content_type='image/svg+xml')
