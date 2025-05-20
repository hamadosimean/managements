from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# company models


class Company(models.Model):
    DOMAINS = (
        ("tech", "Technologie"),
        ("health", "Sante"),
        ("education", "Education"),
        ("finance", "Finance"),
        ("breeding", "Elevage"),
        ("justice", "Justice"),
        ("other", "Autres"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=225)
    domain = models.CharField(choices=DOMAINS)
    email = models.CharField(max_length=225, unique=True)
    description = models.TextField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + " " + self.domain


# services


class Service(models.Model):
    """services models"""

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=225)
    description = models.TextField(null=True, blank=True)
    display = models.BooleanField(default=1)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Service:  " + self.name


class QueueSlot(models.Model):
    """QueueSlot model"""

    STATUS = (
        ("waiting", "Waiting"),
        ("called", "Called"),
        ("served", "Served"),
        ("cancelled", "Cancel"),
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    status = models.TextField(choices=STATUS)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            "Service: "
            + str(self.service.name)
            + "  "
            + "Queue Number: "
            + str(self.number)
        )
