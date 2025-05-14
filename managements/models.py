from django.db import models
from django.contrib.auth.models import User
# Create your models here.

#services 

class Service(models.Model):
    """ services models"""
    user = models.ForeignKey(User,on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    description = models.TextField(null=True,blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return "Service:  " + self.name
    
    
class QueueSlot(models.Model):
    """QueueSlot model"""
    
    STATUS = (
        ('waiting', 'Waiting'),
        ('called', 'Called'),
    )
    service = models.ForeignKey(Service,on_delete=models.CASCADE)
    number = models.PositiveIntegerField(unique_for_date=True)
    status = models.TextField(choices=STATUS)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    def __str__(self):
        return "Service: " + self.service.name + "  " + 'Queue Number: ' + str(self.number) 
    