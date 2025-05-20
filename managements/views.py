from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    AllowAny,
    SAFE_METHODS,
)
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .permissions import IsOwner, IsUser
from .models import Service, QueueSlot, Company
from .serializers import (
    ServiceSerializer,
    QueueSlotSerializer,
    CompanySerializer,
    UserSerializers,
)
from .utils import assign_slot_number
from django.utils import timezone


# register view
@api_view(["POST"])
def register_view(request):
    serializer = UserSerializers(data=request.data)
    if serializer.is_valid(raise_exception=True):
        # check if the email and username already exists
        if User.objects.filter(email=serializer.validated_data["email"]).exists():
            return Response(
                {"details": "This email is already used"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=serializer.validated_data["username"]).exists():
            return Response(
                {"details": "This username is already used"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # create the user
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # create the token
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"user": serializer.data, "token": token.key},
                status=status.HTTP_201_CREATED,
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------- Authentication----------------------------------


# login view
@api_view(["POST"])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    print(username)
    print(password)
    if not username or not password:
        return Response(
            {"details": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    print(user)
    if not user:
        return Response(
            {"details": "Username or password is incorrect"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.is_active:
        return Response(
            {"details": "Your account has been deactivated"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"access_token": token.key}, status=status.HTTP_200_OK)


# ---------------------------users views-----------------------------------
class UserDetailAPIView(APIView):
    """Users api views logic"""

    def get_permissions(self):
        if self.request in SAFE_METHODS:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser | IsUser]
        return super().get_permissions()

    def get_object(self, userId):
        """Get user data and return it"""
        user = get_object_or_404(User, id=userId)
        self.check_object_permissions(self.request, user)
        return user

    def get(self, request, userId):
        """Return user data"""
        user = self.get_object(userId=userId)
        serializer = UserSerializers(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, userId):
        """Partial updatebof user data"""
        user = self.get_object(userId=userId)
        serializer = UserSerializers(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "User has been updated successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.detailss, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, userId):
        """Deletion of a user"""
        user = self.get_object(userId=userId)
        if user is not None:
            return Response(
                {"message": "User has been deleted successfully"},
                status=status.HTTP_200_OK,
            )
        return Response({"details": "No such user"}, status=status.HTTP_404_NOT_FOUND)


# ----------------------------Company views--------------------------------------
# company view
class CompanyAPIView(APIView):
    """Company api views"""

    def post(self, request, userId):
        """save company data"""
        if str(request.user.id) != str(userId):
            return Response(
                {"details": "You are not allowed to perform this operation"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Check if the user already has a company
        if Company.objects.filter(user=request.user).exists():
            return Response(
                {"details": "You already have a company registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, userId):
        """retreive all company data"""
        if str(request.user.id) != str(userId):
            return Response(
                {"details": "You are not allowed to perform this operation"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        company = get_object_or_404(Company, user_id=userId)
        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)


# company detail view
class CompanyDetailView(APIView):

    def get_object(self, userId):
        company = get_object_or_404(Company, user_id=userId)
        self.check_object_permissions(self.request, company)
        return company

    def get(self, request, userId):
        instance = self.get_object(userId)
        serializer = CompanySerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, userId):
        instance = self.get_object(userId)
        serializer = CompanySerializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, userId):
        instance = self.get_object(userId)
        serializer = CompanySerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, userId):
        instance = self.get_object(userId)
        instance.delete()
        return Response(
            {"message": "Company deleted successfully"},
            status=status.HTTP_200_OK,
        )


# -------------------------------Services----------------------------------------
# Service API View
class ServiceAPIView(APIView):

    def post(self, request, userId):
        """Adding a service"""
        if str(request.user.id) != str(userId):
            return Response(
                {"details": "You are not allowed to perform this operation"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # get the company
        company = get_object_or_404(Company, user_id=userId)

        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(company=company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.details, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, userId):
        """Getting services"""
        if str(request.user.id) != str(userId):
            return Response(
                {"details": "You are not allowed to perform this operation"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        # get the company
        services = Service.objects.select_related("company").filter(
            company__user__id=int(userId)
        )
        if services.exists():
            serializer = ServiceSerializer(services, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"details": "No services yet!!"}, status=403)


# show only services to display
@api_view(["GET"])
def displayed_services(request, userId):
    """Getting services"""
    if str(request.user.id) != str(userId):
        return Response(
            {"details": "You are not allowed to perform this operation"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    # get the company
    services = Service.objects.select_related("company").filter(
        company__user__id=int(userId), display=True
    )

    if services.exists():
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response({"details": "No services yet!!"}, status=403)


# service detailview, get,put,patch and delete
class ServiceDetailAPIView(APIView):

    def get_object(self, userId, serviceId):

        service = get_object_or_404(
            Service.objects.select_related("company"),
            id=serviceId,
            company__user_id=userId,
        )
        self.check_object_permissions(self.request, service)
        return service

    def get(self, request, userId, serviceId):
        instance = self.get_object(userId, serviceId)
        serializer = ServiceSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, userId, serviceId):
        instance = self.get_object(userId, serviceId)
        serializer = ServiceSerializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, userId, serviceId):
        instance = self.get_object(userId, serviceId)
        serializer = ServiceSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, userId, serviceId):
        instance = self.get_object(userId, serviceId)
        instance.delete()
        return Response(
            {"message": "Service deleted successfully"},
            status=status.HTTP_200_OK,
        )


# --------------------------------------QueueSlot--------------------------------


class QueueSlotAPIView(APIView):
    serializer_class = QueueSlotSerializer

    def get(self, request, userId, serviceId):
        slots = QueueSlot.objects.filter(service_id=serviceId)
        serializer = QueueSlotSerializer(slots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, userId, serviceId):
        # service_id = request.data.get("service_id")
        number = assign_slot_number(service_id=serviceId)
        service = get_object_or_404(Service, id=serviceId)
        slot = QueueSlot.objects.create(
            service=service, number=number, status="waiting"
        )
        serializer = QueueSlotSerializer(slot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QueueSlotDetailView(APIView):
    # serializer_class = QueueSlotSerializer
    def get_object(self, serviceId, slotId):
        queue_slot = QueueSlot.objects.select_related("service").get(
            service_id=serviceId, id=slotId
        )

        self.check_object_permissions(self.request, queue_slot)
        return queue_slot

    def get(self, request, userId, serviceId, slotId):
        queue_slot = self.get_object(serviceId=serviceId, slotId=slotId)
        serializer = QueueSlotSerializer(queue_slot)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, userId, serviceId, slotId):
        instance = self.get_object(serviceId=serviceId, slotId=slotId)
        serializer = QueueSlotSerializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, userId, serviceId, slotId):
        instance = self.get_object(serviceId=serviceId, slotId=slotId)
        serializer = QueueSlotSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# Get queue count for a given service
@api_view()
def get_service_count(request, userId, serviceId):
    today_date = timezone.localdate()
    try:
        service = Service.objects.get(id=serviceId)
        count = QueueSlot.objects.filter(
            service=service, date_update__date=today_date
        ).count()
    except Service.DoesNotExist:
        return Response(
            {"details": "Service not found"}, status=status.HTTP_404_NOT_FOUND
        )
    return Response({"count": count}, status=status.HTTP_200_OK)


# Get waiting count
@api_view()
def get_waiting_count(request, userId, serviceId):
    today_date = timezone.localdate()
    try:
        service = Service.objects.get(id=serviceId)
        count = QueueSlot.objects.filter(
            service=service, date_update__date=today_date, status="waiting"
        ).count()
    except Service.DoesNotExist:
        return Response(
            {"details": "Service not found"}, status=status.HTTP_404_NOT_FOUND
        )
    return Response({"count": count}, status=status.HTTP_200_OK)


# Get current and next queue
@api_view()
def get_current_and_next_queue(request, userId, serviceId):
    today_date = timezone.localdate()
    try:
        service = Service.objects.get(id=serviceId)
        called = QueueSlot.objects.filter(
            service=service, date_update__date=today_date, status="called"
        ).last()
        next_queue = QueueSlot.objects.filter(
            service=service, date_update__date=today_date, status="waiting"
        ).first()
    except Service.DoesNotExist:
        return Response(
            {"details": "Service not found"}, status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            "current": called.number if called else None,
            "next_queue": next_queue.number if next_queue else None,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
def action(request, userId, serviceId, slotId):
    """Take action: validate or cancel a queue number"""

    if str(request.user.id) != str(userId):
        return Response(
            {"details": "You are not allowed to perform this operation"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    today_date = timezone.localdate()

    # Get the actual Service instance
    service = get_object_or_404(Service, id=serviceId)

    # Filter the queue slot
    queue_slot = QueueSlot.objects.filter(
        service=service, date_update__date=today_date, status="called"
    ).last()

    if not queue_slot:
        return Response(
            {"details": "No matching queue slot found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    queue_slot.status = request.data.get("status")
    queue_slot.save()

    return Response(
        {"message": "Action performed successfully"}, status=status.HTTP_200_OK
    )
