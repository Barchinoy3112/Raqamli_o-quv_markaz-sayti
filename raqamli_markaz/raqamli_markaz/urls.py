"""
URL configuration for raqamli_markaz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('kurslar.urls')),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('manifest.webmanifest', views.manifest_webmanifest, name='manifest_webmanifest'),
    path('sw.js', views.service_worker_js, name='service_worker_js'),
    path('icon.svg', views.app_icon_svg, name='app_icon_svg'),
    path('', views.home, name='home'),
    path('kurslar/', views.kurslar, name='kurslar'),
    path('kurslar/<int:kurs_id>/yozilish/', views.kursga_yozilish, name='kursga_yozilish'),
    path('talabalar/', views.talabalar, name='talabalar'),
    path('enrolls/', views.enrolls, name='enrolls'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
]
