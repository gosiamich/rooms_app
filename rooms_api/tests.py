from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import Client
import pytest
from freezegun import freeze_time
from rest_framework import status

from rooms_api.models import Room
from rooms_api.serializers import RoomSerializer


@pytest.mark.django_db
def test_not_login_user_RoomViewSet_list(room):
    client = Client()
    response = client.get(f"/api/rooms/", {}, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_get_room_details_RoomViewSet(client, room, superuser):
    client.force_login(superuser)
    response = client.get(f'/api/rooms/{room.id}/')
    assert response.status_code == 200
    assert response.data == RoomSerializer(instance=room).data


@pytest.mark.django_db
def test_authenticatedUserRoomViewSet_list(client, room, superuser):
    client.force_login(superuser)
    response = client.get(f"/api/rooms/", {}, format='json')
    assert response.status_code == 200
    assert Room.objects.count() == len(response.data)


@pytest.mark.django_db
def test_post_room_RoomViewSet(client, superuser):
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
def test_create_room_wrong_data_RoomViewSet(client, superuser, room):
    client.force_login(superuser)
    new_room = {
        'name': '',
        'room_manager': superuser.id,
    }
    response = client.post("/api/rooms/", new_room, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
def test_create_room_duplicate_name_RoomViewSet(client, superuser, room):
    client.force_login(superuser)
    new_room = {
        'name': 'Yellow',
        'room_manager': superuser.id,
    }
    response = client.post("/api/rooms/", new_room, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError('Find another name.')


@freeze_time('2022-10-06 00:00:00')
@pytest.mark.django_db
def test_create_reservation_ReservationViewSet(client, superuser, room):
    client.force_login(superuser)
    new_reservation = {
        'room': room.id,
        'training': 'WCAG',
        'date_from': '2022-10-25',
        'date_to': '2022-10-25',
    }
    response = client.post("/api/rooms/<pk>/reservations/", new_reservation, format='json')
    assert response.status_code == 201
    for key, value in new_reservation.items():
        assert key in response.data
        assert response.data[key] == value



