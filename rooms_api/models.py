from datetime import timedelta
from django.db import models
from django.utils.crypto import get_random_string


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    room_manager = models.ForeignKey(
        'auth.User', related_name="manager_of_rooms", on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'Room: {self.name} room manager: {self.room_manager}'



def generate_password():
    return get_random_string(10)


class Reservation(models.Model):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    training = models.CharField(max_length=156, default='Test')
    rating_choice = (
        (1.0, '1'),
        (2.0, '2'),
        (3.0, '3'),
        (4.0, '4'),
        (5.0, '5'),
    )
    rating = models.FloatField(choices=rating_choice, blank=True, null=True)
    comment = models.TextField(null=True, blank=True)
    room_password = models.CharField(max_length=10, editable=False, default=generate_password)
    owner = models.ForeignKey(
        'auth.User', related_name='user_reservations', on_delete=models.CASCADE)
    status_choice = [
        (0, 'Waiting to be confirmed'),
        (1, 'Confirmed'),
        (2, 'Cancelled'),
        (3, 'Rejected'),
    ]
    reservation_status = models.IntegerField(choices=status_choice, null=False, blank=False, default=0)

    def get_dates(self):
        date_list = []
        current_date = self.date_from
        while current_date <= self.date_to:
            date_list.append(current_date)
            current_date += timedelta(days=1)
        return date_list

