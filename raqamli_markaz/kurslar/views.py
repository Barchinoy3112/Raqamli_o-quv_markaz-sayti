from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Talaba, Kurs, Enroll
from .serializers import TalabaSerializer, KursSerializer, EnrollSerializer
from .permissions import IsOwnerOrAdmin


class TalabaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Talaba (Student) objects.
    Only admins can view/edit all students.
    Regular users can only view/edit their own profile.
    """
    queryset = Talaba.objects.all()
    serializer_class = TalabaSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'email']
    ordering = ['-date_joined']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Talaba.objects.all()
        return Talaba.objects.filter(id=self.request.user.id)


class KursViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Kurs (Course) objects.
    Only authenticated users can view courses.
    """
    queryset = Kurs.objects.all()
    serializer_class = KursSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'tavsif']
    ordering_fields = ['boshlangan_sana', 'narx']
    ordering = ['boshlangan_sana']


class EnrollViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Enroll (Enrollment) objects.
    Users can only view/manage their own enrollments.
    Admins can view/manage all enrollments.
    """
    queryset = Enroll.objects.all()
    serializer_class = EnrollSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['talaba__email', 'kurs__nom']
    ordering_fields = ['royxatdan_otish_sanasi', 'holat']
    ordering = ['-royxatdan_otish_sanasi']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Enroll.objects.all()
        return Enroll.objects.filter(talaba=self.request.user)
