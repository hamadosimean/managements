from django.urls import path
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView,SpectacularRedocView
from . import views
urlpatterns = [
    path('slot-management',views.QueueSlotAPIView.as_view()),
    path('slot-detail/<int:id>',views.QueueSlotDetailView.as_view()),
    # get service count
    path('service-count/<int:id>',views.get_service_count),
    #get current queue
    path('current-next-queue/<int:id>',views.get_current_and_next_queue),
    
    # documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
   
]