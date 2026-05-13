from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Talaba, Kurs, Enroll


@admin.register(Talaba)
class TalabaAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'get_full_name', 'telefon', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('first_name', 'last_name', 'telefon', 'tugilgan_sana')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Kurs)
class KursAdmin(admin.ModelAdmin):
    list_display = ('nom', 'narx', 'boshlangan_sana', 'muddat')
    search_fields = ('nom', 'tavsif')
    list_filter = ('boshlangan_sana',)


@admin.register(Enroll)
class EnrollAdmin(admin.ModelAdmin):
    list_display = ('get_talaba', 'get_kurs', 'holat', 'royxatdan_otish_sanasi')
    list_filter = ('holat', 'royxatdan_otish_sanasi')
    search_fields = ('talaba__email', 'talaba__username', 'kurs__nom')
    ordering = ('-royxatdan_otish_sanasi',)
    
    def get_talaba(self, obj):
        return f"{obj.talaba.get_full_name()} ({obj.talaba.email})"
    get_talaba.short_description = 'Talaba'
    
    def get_kurs(self, obj):
        return obj.kurs.nom
    get_kurs.short_description = 'Kurs'
