from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import Client
import pytest
from freezegun import freeze_time

from rooms_api.models import Room


@pytest.mark.django_db
def test_not_login_user_RoomViewSet_list(room):
    client = Client()
    response = client.get(f"/api/rooms/", {}, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_authenticatedUserRoomViewSet_list(client, room, superuser):
    client.force_login(superuser)
    response = client.get(f"/api/rooms/", {}, format='json')
    assert response.status_code == 200
    assert Room.objects.count() == len(response.data)


@pytest.mark.django_db
def test_create_room_RoomViewSet(client, superuser):
    client.force_login(superuser)
    new_room = {
        'name': 'New room',
        'room_manager': superuser.id,
    }
    response = client.post("/api/rooms/", new_room, format='json')
    assert response.status_code == 201
    for key, value in new_room.items():
        assert key in response.data
        assert response.data[key] == value

@pytest.mark.django_db
def test_create_room_wrong_name_RoomViewSet(client, superuser, room):
    client.force_login(superuser)
    with pytest.raises(ValueError) as wrong_name:
        new_room = {
            'name': 'Yellow',
            'room_manager': superuser.id,
        }
        response = client.post("/api/rooms/", new_room, format='json')
    assert wrong_name.value.message('finish must occur after start')



@freeze_time('2022-10-06 00:00:00')
@pytest.mark.django_db
def test_create_resrvation_ReservationViewSet(client, superuser, room):
    client.force_login(superuser)
    new_reservation = {
        'room': room.id,
        'training': 'WCAG',
        'date_from':'2022-10-25',
        'date_to':'2022-10-25',
    }
    response = client.post("/api/rooms/<pk>/reservations/", new_reservation, format='json')
    assert response.status_code == 201
    for key, value in new_reservation.items():
        assert key in response.data
        assert response.data[key] == value

@pytest.mark.django_db
def test_create_resrvation_value_error_ReservationViewSet(client, superuser, room):
    with pytest.raises(ValueError) as wrong_dates:
        client.force_login(superuser)
        new_reservation = {
            'room': room.id,
            'training': 'WCAG',
            'date_to':'2022-10-25',
            'date_from':'2022-10-27',
        }
        response = client.post("/api/rooms/<pk>/reservations/", new_reservation, format='json')
    assert wrong_dates.value.message('finish must occur after start')
