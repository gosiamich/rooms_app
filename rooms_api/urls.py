from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework import routers
from rest_framework_nested import routers
from rooms_api import views


router = SimpleRouter()
router.register('rooms', views.RoomViewSet, basename='rooms')
rooms_router = routers.NestedSimpleRouter(
    router,
    r'rooms',
    lookup='room')

rooms_router.register(
    r'reservations',
    views.ReservationViewSet,
basename='reservations'
)
app_name = 'rooms_api'

urlpatterns = [
    path('', include(router.urls)),
    path('', include(rooms_router.urls)),
]
