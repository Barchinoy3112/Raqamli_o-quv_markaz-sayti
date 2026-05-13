from rest_framework import serializers
from .models import Talaba, Kurs, Enroll


class TalabaSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Talaba
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'full_name', 'telefon', 'tugilgan_sana']
        read_only_fields = ['id', 'full_name']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Talaba.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


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
