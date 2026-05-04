from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Talaba, Kurs, Enroll
from .serializers import TalabaSerializer, KursSerializer, EnrollSerializer

class TalabaViewSet(viewsets.ModelViewSet):
    queryset = Talaba.objects.all()
    serializer_class = TalabaSerializer
    permission_classes = [IsAdminUser]

class KursViewSet(viewsets.ModelViewSet):
    queryset = Kurs.objects.all()
    serializer_class = KursSerializer
    permission_classes = [IsAdminUser]

class EnrollViewSet(viewsets.ModelViewSet):
    queryset = Enroll.objects.all()
    serializer_class = EnrollSerializer
    permission_classes = [IsAdminUser]
