from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Service,QueueSlot

## User serializer
class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name','last_name','username','email']

## services serializer
class ServiceSerializer(serializers.ModelSerializer):
    user = UserSerializers()
    class Meta:
        model = Service
        fields = ['user','name','description']
        
class QueueSlotSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name',read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = QueueSlot
        fields = ['service_id','number','service_name','status']
        read_only_fields = ['number']
        