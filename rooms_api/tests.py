from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import Client
import pytest
from freezegun import freeze_time
from rest_framework import status

from rooms_api.models import Room, Reservation
from rooms_api.serializers import RoomSerializer, ReservationSerializer, ReservationWithPasswordSerializer


@pytest.mark.django_db
def test_not_login_user_RoomViewSet_list(room):
    client = Client()
    response = client.get(f"/api/rooms/", {}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_list_authenticatedUserRoomViewSet(client, room, superuser):
    client.force_login(superuser)
    response = client.get(f"/api/rooms/", {}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert Room.objects.count() == len(response.data)


@pytest.mark.django_db
def test_get_room_details_RoomViewSet(client, room, user):
    client.force_login(user)
    response = client.get(f'/api/rooms/{room.id}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data == RoomSerializer(instance=room).data


@pytest.mark.django_db
def test_post_room_RoomViewSet(client, user):
    client.force_login(user)
    new_room = {
        'name': 'New room',
        'room_manager': user.id,
    }
    response = client.post("/api/rooms/", new_room, format='json')
    assert response.status_code == status.HTTP_201_CREATED
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


@pytest.mark.django_db
def test_update_RoomViewSet(client, user, room):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/", {}, format='json')
    input_data = response.data
    input_data["name"] = 'New name'
    response = client.put(f"/api/rooms/{room.id}/", input_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    room.refresh_from_db()
    assert room.name == 'New name'


@pytest.mark.django_db
def test_update_duplicate_name_RoomViewSet(client, user, room, room_simple_user):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/", {}, format='json')
    input_data = response.data
    input_data["name"] = 'Grey'
    response = client.put(f"/api/rooms/{room.id}/", input_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError("Find another name.")


"""Testing reservations"""

@pytest.mark.django_db
def test_not_authorized_list_ReservationViewSet(client, room, reservation):
    response = client.get(f"/api/rooms/{room.id}/reservations/", {}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_list_ReservationViewSet(client, user, room, reservation):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/reservations/", {}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert Reservation.objects.count() == len(response.data)


@pytest.mark.django_db
def test_delete_reservation_ReservationViewSet(client, user, room, reservation):
    client.force_login(user)
    response = client.delete(f"/api/rooms/{room.id}/reservations/{reservation.id}/", format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(ValidationError):
        raise ValidationError("Delete function is not offered in this path.")


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
    assert response.status_code == status.HTTP_201_CREATED
    for key, value in new_reservation.items():
        assert key in response.data
        assert response.data[key] == value


@freeze_time('2022-10-06 00:00:00')
@pytest.mark.django_db
def test_create_reservation_empty_data_ReservationViewSet(client, superuser, room):
    client.force_login(superuser)
    new_reservation = {
        'room': room.id,
        'training': '',
        'date_from': '2022-10-04',
        'date_to': '2022-10-04',
    }
    response = client.post("/api/rooms/<pk>/reservations/", new_reservation, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@freeze_time('2022-10-06 00:00:00')
@pytest.mark.django_db
def test_create_reservation_invalid_dates_ReservationViewSet(client, superuser, room):
    client.force_login(superuser)
    new_reservation = {
        'room': room.id,
        'training': 'Test',
        'date_from': '2022-10-30',
        'date_to': '2022-10-20',
    }
    response = client.post("/api/rooms/<pk>/reservations/", new_reservation, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError('Finish must occur after start')


@freeze_time('2022-10-06 00:00:00')
@pytest.mark.django_db
def test_create_reservation_dates_from_past_ReservationViewSet(client, superuser, room):
    client.force_login(superuser)
    new_reservation = {
        'room': room.id,
        'training': 'Test',
        'date_from': '2022-08-30',
        'date_to': '2022-09-20',
    }
    response = client.post("/api/rooms/<pk>/reservations/", new_reservation, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError("Enter dates from future")


@freeze_time('2022-09-9 00:00:00')
@pytest.mark.django_db
def test_create_reservation_conflicting_dates_ReservationViewSet(client, superuser, room, reservation2):
    client.force_login(superuser)
    new_reservation = {
        'room': room.id,
        'training': 'Test',
        'date_from': '2022-9-24',
        'date_to': '2022-9-24',
    }
    response = client.post("/api/rooms/<pk>/reservations/", new_reservation, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError('Room is reserved at this term')


@pytest.mark.django_db
def test_get_reservation_details_ReservationViewSet(client, room, reservation, user):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/reservations/{reservation.id}/", format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data == ReservationSerializer(instance=reservation).data


@pytest.mark.django_db
def test_get_reservation_details_with_password_ReservationViewSet(client, room, reservation2, user):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/reservations/{reservation2.id}/", format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data == ReservationWithPasswordSerializer(instance=reservation2).data
    for field in ("room_password",):
        assert field in response.data


@pytest.mark.django_db
def test_forbidden_update_ReservationViewSet(client, simple_user, room, reservation):
    """Simple user is not owner of reservation."""
    client.force_login(simple_user)
    response = client.get(f"/api/rooms/{room.id}/reservations/{reservation.id}/", format='json')
    input_data = response.data
    input_data["comment"] = 'New comment'
    response = client.put(f"/api/rooms/{room.id}/reservations/{reservation.id}/", input_data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    reservation.refresh_from_db()
    assert reservation.comment != "New comment"


@freeze_time('2022-08-06 00:00:00')
@pytest.mark.django_db
def test_update_ReservationViewSet(client, user, room, reservation):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/reservations/{reservation.id}/", format='json')
    input_data = response.data
    input_data["comment"] = 'adding comment'
    response = client.put(f"/api/rooms/{room.id}/reservations/{reservation.id}/", input_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    reservation.refresh_from_db()
    assert reservation.comment == 'adding comment'

@freeze_time('2022-08-06 00:00:00')
@pytest.mark.django_db
def test_invalid_dates_update_ReservationViewSet(client, user, room, reservation):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/reservations/{reservation.id}/", format='json')
    input_data = response.data
    input_data["date_from"] = '2022-10-15'
    input_data["date_to"] = '2022-10-05'
    response = client.put(f"/api/rooms/{room.id}/reservations/{reservation.id}/", input_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError('Finish must occur after start')

@freeze_time('2022-08-06 00:00:00')
@pytest.mark.django_db
def test_past_dates_update_ReservationViewSet(client, user, room, reservation):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/reservations/{reservation.id}/", format='json')
    input_data = response.data
    input_data["date_from"] = '2022-07-15'
    input_data["date_to"] = '2022-07-15'
    response = client.put(f"/api/rooms/{room.id}/reservations/{reservation.id}/", input_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError('Enter dates from future')

@freeze_time('2022-08-06 00:00:00')
@pytest.mark.django_db
def test_conflicting_dates_update_ReservationViewSet(client, user, room, reservation, reservation2):
    client.force_login(user)
    response = client.get(f"/api/rooms/{room.id}/reservations/{reservation.id}/", format='json')
    input_data = response.data
    input_data["date_from"] = '2022-09-24'
    input_data["date_to"] = '2022-09-24'
    response = client.put(f"/api/rooms/{room.id}/reservations/{reservation.id}/", input_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError('Room is reserved at this term')


@pytest.mark.django_db
def test_forbidden_finish_ReservationViewSet(client, simple_user, room, reservation):
    """Only reservation's owner can add rating."""
    finish_url = f"/api/rooms/{room.id}/reservations/{reservation.id}/finish/"
    client.force_login(simple_user)
    response = client.post(finish_url, format='json')
    input_data = response.data
    input_data["rating"] = 2.0
    response = client.post(finish_url, input_data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    reservation.refresh_from_db()
    assert not reservation.rating

@pytest.mark.django_db
@freeze_time('2022-10-06 00:00:00')
def test_attemp_before_training_finish_ReservationViewSet(client, user, room, reservation):
    """Rating may be added after event"""
    finish_url = f"/api/rooms/{room.id}/reservations/{reservation.id}/finish/"
    client.force_login(user)
    response = client.post(finish_url, format='json')
    input_data = response.data
    input_data["rating"] = 2.0
    response = client.post(finish_url, input_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError('You can add evaluation after training.')
    assert not reservation.rating


@pytest.mark.django_db
@freeze_time('2022-08-06 00:00:00')
def test_second_attemp_finish_ReservationViewSet(client, user, room, reservation_with_rating):
    """Rating may be added after event"""
    finish_url = f"/api/rooms/{room.id}/reservations/{reservation_with_rating.id}/finish/"
    client.force_login(user)
    response = client.post(finish_url, format='json')
    input_data = response.data
    input_data["rating"] = 5.0
    response = client.post(finish_url, input_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    with pytest.raises(ValidationError):
        raise ValidationError('You can add evaluation only once.')
    assert reservation_with_rating.rating == 1.0


@freeze_time('2022-09-28 00:00:00')
@pytest.mark.django_db
def test_finish_ReservationViewSet(client, user, room, reservation2):
    finish_url = f"/api/rooms/{room.id}/reservations/{reservation2.id}/finish/"
    client.force_login(user)
    response = client.post(finish_url, format='json')
    input_data = response.data
    input_data["rating"] = 2.0
    response = client.post(finish_url, input_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    reservation2.refresh_from_db()
    assert reservation2.rating == 2.0


@pytest.mark.django_db
def test_forbidden_confirm_ReservationViewSet(client, simple_user, room, reservation):
    confirm_url = f"/api/rooms/{room.id}/reservations/{reservation.id}/confirm/"
    client.force_login(simple_user)
    response = client.post(confirm_url, format='json')
    input_data = response.data
    input_data["reservation_status"] = 1
    response = client.post(confirm_url, input_data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    reservation.refresh_from_db()
    assert reservation.reservation_status == 0


@pytest.mark.django_db
def test_confirm_ReservationViewSet(client, user, room, reservation):
    confirm_url = f"/api/rooms/{room.id}/reservations/{reservation.id}/confirm/"
    client.force_login(user)
    response = client.post(confirm_url, format='json')
    input_data = response.data
    input_data["reservation_status"] = 1
    response = client.post(confirm_url, input_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    reservation.refresh_from_db()
    assert reservation.reservation_status == 1


@pytest.mark.django_db
def test_forbidden_cancel_ReservationViewSet(client, simple_user, room, reservation):
    cancel_url = f"/api/rooms/{room.id}/reservations/{reservation.id}/cancel/"
    client.force_login(simple_user)
    response = client.post(cancel_url, format='json')
    input_data = response.data
    input_data["reservation_status"] = 2
    response = client.post(cancel_url, input_data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    reservation.refresh_from_db()
    assert reservation.reservation_status == 0


@pytest.mark.django_db
def test_cancel_ReservationViewSet(client, user, room, reservation):
    cancel_url = f"/api/rooms/{room.id}/reservations/{reservation.id}/cancel/"
    client.force_login(user)
    response = client.post(cancel_url, format='json')
    input_data = response.data
    input_data["reservation_status"] = 2
    response = client.post(cancel_url, input_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    reservation.refresh_from_db()
    assert reservation.reservation_status == 2
