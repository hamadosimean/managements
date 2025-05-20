from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import Service, QueueSlot, Company


## User serializer
class UserSerializers(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]
        extra_kwargs = {
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


# company serializer


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "domain",
            "email",
            "description",
            "date_creation",
        ]
        extra_kwargs = {
            "date_creation": {"read_only": True},
            "email": {"required": True},
            "domain": {"required": True},
            "name": {"required": True},
        }


## services serializer
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "display",
            "name",
            "description",
            "date_creation",
        ]
        read_only_fields = ["id", "date_creation", "date_update"]


class QueueSlotSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    # service_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = QueueSlot
        fields = [
            "id",
            "number",
            "service_name",
            "status",
        ]
        read_only_fields = ["id", "number", "date_creation", "date_update"]
