from .models import QueueSlot
from django.utils import timezone


def assign_slot_number(service_id):
    today = timezone.localdate()
    last_slot = QueueSlot.objects.filter(date_creation__date=today,service_id=service_id).order_by("-number").first()
    return last_slot.number + 1 if last_slot else 1