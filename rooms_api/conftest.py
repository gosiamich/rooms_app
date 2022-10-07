import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rooms_api.models import Room, Reservation


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def superuser():
    return User.objects.create_superuser(username='super', password='super')


@pytest.fixture
def user():
    return User.objects.create_user(username='gosia', password='gosia')


@pytest.fixture
def client():
    client = APIClient()
    return client


@pytest.fixture
def room(user):
    return Room.objects.create(name="Yellow", room_manager=user)


@pytest.fixture
def reservation(room, user):
    return Reservation.objects.create(training="Grey",
                                      date_from= '2022-9-25',
                                      date_to='2022-9-25',
                                      owner=user,
                                      room=room)
