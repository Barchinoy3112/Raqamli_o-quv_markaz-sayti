from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import Talaba, Kurs, Enroll


class AuthAndEnrollFlowTests(TestCase):
	def setUp(self):
		self.client = Client()
		# create a sample course
		self.kurs = Kurs.objects.create(
			nom='Test Kurs',
			tavsif='Test tavsif',
			narx=100.00,
			boshlangan_sana=timezone.now().date(),
			muddat=10,
		)

	def test_register_creates_user_and_logs_in(self):
		url = reverse('register')
		data = {
			'first_name': 'Test',
			'last_name': 'User',
			'username': 'testuser',
			'email': 'testuser@example.com',
			'telefon': '901234567',
			'tugilgan_sana': '1990-01-01',
			'password': 'safepassword123',
			'password2': 'safepassword123',
		}
		resp = self.client.post(url, data, follow=True)
		# after registration should redirect to profile
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(Talaba.objects.filter(email='testuser@example.com').exists())
		# client should be authenticated
		user = Talaba.objects.get(email='testuser@example.com')
		self.assertTrue(user.is_authenticated)

	def test_login_with_email(self):
		# create user
		user = Talaba.objects.create_user(
			username='loginuser',
			email='loginuser@example.com',
			password='securepass123'
		)
		url = reverse('login')
		resp = self.client.post(url, {'email': 'loginuser@example.com', 'password': 'securepass123'}, follow=True)
		self.assertEqual(resp.status_code, 200)
		# check that user is in session
		self.assertTrue('_auth_user_id' in self.client.session)

	def test_kursga_yozilish_creates_enroll(self):
		# create and login user
		user = Talaba.objects.create_user(
			username='enrolluser',
			email='enroll@example.com',
			password='enrollpass123'
		)
		self.client.login(email='enroll@example.com', password='enrollpass123')
		enroll_url = reverse('kursga_yozilish', args=[self.kurs.id])
		resp = self.client.post(enroll_url, follow=True)
		self.assertEqual(resp.status_code, 200)
		self.assertTrue(Enroll.objects.filter(talaba=user, kurs=self.kurs).exists())

	def test_capacity_prevents_enrollment(self):
		# create a course with capacity 1
		self.kurs.capacity = 1
		self.kurs.save()

		# first user enrolls
		user1 = Talaba.objects.create_user(username='u1', email='u1@example.com', password='pass12345')
		self.client.login(email='u1@example.com', password='pass12345')
		self.client.post(reverse('kursga_yozilish', args=[self.kurs.id]), follow=True)
		self.client.logout()

		# second user should not be able to enroll
		user2 = Talaba.objects.create_user(username='u2', email='u2@example.com', password='pass67890')
		self.client.login(email='u2@example.com', password='pass67890')
		self.client.post(reverse('kursga_yozilish', args=[self.kurs.id]), follow=True)
		active = Enroll.objects.filter(kurs=self.kurs, holat='faol').count()
		self.assertEqual(active, 1)

