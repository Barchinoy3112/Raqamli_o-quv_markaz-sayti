from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Talaba, Kurs, Enroll


class TalabaSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Talaba
        fields = '__all__'

    def create(self, validated_data):
        pwd = validated_data.pop('password', None)
        if pwd is not None:
            validated_data['password'] = make_password(pwd)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        pwd = validated_data.pop('password', None)
        if pwd is not None:
            instance.password = make_password(pwd)
        return super().update(instance, validated_data)

class KursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kurs
        fields = '__all__'

class EnrollSerializer(serializers.ModelSerializer):
    talaba = TalabaSerializer(read_only=True)
    kurs = KursSerializer(read_only=True)

    class Meta:
        model = Enroll
        fields = '__all__'