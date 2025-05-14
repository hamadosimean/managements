from django.shortcuts import render,get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from .models import Service,QueueSlot
from rest_framework.permissions import IsAdminUser
from .serializers import ServiceSerializer,QueueSlotSerializer
from .utils import assign_slot_number
from django.utils import timezone
# Create your views here.

# Service ApI View

class ServiceAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self,request):
        data = request.POST
        services = ServiceSerializer(data=data)
        if services.is_valid(raise_exception=True):
            services.save()
        
    def get(self,request):
        try:
            services = Service.objects.all()
        except Exception as e:
           return Response(e, status=status.HTTP_404_NOT_FOUND) 
        serializer = ServiceSerializer(services,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
        
class ServiceAPIDetailView(APIView):
    """Service Api view handling"""
    def get(self,request,id):
        try:
            service = get_object_or_404(Service,id=id)
        except Exception as e:
           return Response(e, status=status.HTTP_404_NOT_FOUND) 
        serializer = ServiceSerializer(service)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class QueueSlotAPIView(APIView):
    """Slot management view"""
    
    def get(self,request):
        slots = QueueSlot.objects.all()
        serializer = QueueSlotSerializer(slots,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
    def post(self,request,*args, **kwargs):
        service_id = request.POST.get('service_id')
        # get service and number to assign
        number = assign_slot_number(service_id=service_id)
        service = Service.objects.get(id=service_id)
        #create slot
        slot = QueueSlot.objects.create(service=service,number=number,status='waiting')
        serializer = QueueSlotSerializer(slot)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
  

class QueueSlotDetailView(APIView):
    
    def get_object(self,id):
        """get queue slot data"""
        queue_slot = get_object_or_404(QueueSlot,id=id)
        self.check_object_permissions(self.request,queue_slot)
        return  queue_slot
    
    def get(self,request,id):
        queue_slot = self.get_object(id=id)
        serializer = QueueSlotSerializer(queue_slot)
        return Response(serializer.data,status=status.HTTP_200_OK)
       
    
    def put(self,request,id):
        data = self.get_object(id=id)
        serializer = QueueSlotSerializer(request.data,data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    
    def patch(self,request,id):
        data = self.get_object(id=id)
        serializer = QueueSlotSerializer(request.data,data=data,partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)
    



# get service count
@api_view()
def get_service_count(request,id):
    today_date = timezone.localdate()
    try:
        service = Service.objects.get(id=id)
        count = QueueSlot.objects.filter(service=service,date_update__date=today_date).count()
    except Service.DoesNotExist:
        return Response({'error':'service not found'},status=status.HTTP_404_NOT_FOUND)
    return Response({"count":count},status=status.HTTP_200_OK)
    



# get current and next queue 
@api_view()
def get_current_and_next_queue(request,id):
    today_date = timezone.localdate()
    try:
        service = Service.objects.get(id=id)
        called = QueueSlot.objects.filter(service=service,date_update__date=today_date,status="called").last()
        next_queue = QueueSlot.objects.filter(service=service,date_update__date=today_date,status="waiting").first()
    except Service.DoesNotExist:
        return Response({'error':'service not found'},status=status.HTTP_404_NOT_FOUND)
    return Response({"current":called.number, "next_queue":next_queue.number},status=status.HTTP_200_OK)



