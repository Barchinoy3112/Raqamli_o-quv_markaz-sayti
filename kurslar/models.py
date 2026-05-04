from django.db import models

class Talaba(models.Model):
    ism = models.CharField(max_length=100)
    familiya = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128, default='')
    telefon = models.CharField(max_length=15)
    tugilgan_sana = models.DateField()

    def __str__(self):
        return f"{self.ism} {self.familiya}"

class Kurs(models.Model):
    nom = models.CharField(max_length=200)
    tavsif = models.TextField()
    narx = models.DecimalField(max_digits=10, decimal_places=2)
    boshlangan_sana = models.DateField()
    muddat = models.IntegerField(help_text="Kurs muddati kunlarda")

    def __str__(self):
        return self.nom

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
