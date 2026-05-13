from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class TalabaManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email manzili talab qilinadi')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Talaba(AbstractUser):
    email = models.EmailField(unique=True)
    telefon = models.CharField(max_length=15, blank=True)
    tugilgan_sana = models.DateField(null=True, blank=True)
    
    objects = TalabaManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    class Meta:
        verbose_name = 'Talaba'
        verbose_name_plural = 'Talabalar'


class Kurs(models.Model):
    nom = models.CharField(max_length=200)
    tavsif = models.TextField()
    narx = models.DecimalField(max_digits=10, decimal_places=2)
    boshlangan_sana = models.DateField()
    muddat = models.IntegerField(help_text="Kurs muddati kunlarda")
    # Maksimal studentlar soni; None yoki 0 — cheklov yo'q
    capacity = models.IntegerField(null=True, blank=True, default=None, help_text="0 yoki bo'sh — cheklov yo'q")

    def __str__(self):
        return self.nom

    @property
    def spots_left(self):
        from .models import Enroll

        if not self.capacity:
            return None
        active = Enroll.objects.filter(kurs=self, holat='faol').count()
        return max(self.capacity - active, 0)

    @property
    def is_full(self):
        left = self.spots_left
        return left == 0 if left is not None else False

class Enroll(models.Model):
    talaba = models.ForeignKey(Talaba, on_delete=models.CASCADE)
    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE)
    royxatdan_otish_sanasi = models.DateTimeField(auto_now_add=True)
    holat = models.CharField(max_length=20, choices=[
        ('faol', 'Faol'),
        ('tugagan', 'Tugagan'),
        ('bekor_qilingan', 'Bekor qilingan'),
    ], default='faol')

    def __str__(self):
        return f"{self.talaba} - {self.kurs}"
