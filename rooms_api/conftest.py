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
def simple_user():
    return User.objects.create_user(username='ktos', password='nowy')


@pytest.fixture
def room(user):
    return Room.objects.create(name="Yellow", room_manager=user)


@pytest.fixture
def room_simple_user(simple_user):
    return Room.objects.create(name='Grey', room_manager=simple_user)


@pytest.fixture
def reservation(room, user):
    return Reservation.objects.create(training="Grey",
                                      date_from='2022-09-25',
                                      date_to='2022-09-25',
                                      owner=user,
                                      room=room)


@pytest.fixture
def reservation2(room, user):
    return Reservation.objects.create(training="Grey",
                                      date_from='2022-09-24',
                                      date_to='2022-09-24',
                                      reservation_status=1,
                                      room_password="MWuiSh079S",
                                      owner=user,
                                      room=room)

@pytest.fixture
def reservation_with_rating(room, user):
    return Reservation.objects.create(training="Grey",
                                      date_from='2022-09-24',
                                      date_to='2022-09-24',
                                      reservation_status=1,
                                      room_password="MWuiSh079S",
                                      owner=user,
                                      rating=1.0,
                                      room=room)
