from django.contrib import admin
from .models import Service, QueueSlot, Company

# Register your models here.

admin.site.register(Service)
admin.site.register(QueueSlot)
admin.site.register(Company)
