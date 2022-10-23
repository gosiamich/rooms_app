import datetime
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from rooms_api.models import Room, Reservation


class RoomSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, validators=[
        UniqueValidator(
            queryset=Room.objects.all(),
            message='Find another name.'
        )]
                                 )

    class Meta:
        model = Room
        fields = ['name', 'pk', 'room_manager']


class ReservationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Reservation
        fields = ['pk', 'room', 'owner', 'date_from', 'date_to', 'training', 'reservation_status', 'comment', 'rating']
        read_only_fields = ['reservation_status', 'owner', 'rating']

    def validate(self, data):
        """
        Check that start is before finish and there are no other reservation at this period.
        """
        if data['date_from'] > data['date_to']:
            raise serializers.ValidationError('Finish must occur after start')
        data
        if data['date_from'] < datetime.date.today():
            raise serializers.ValidationError('Enter dates from future')
        data
        if len(Reservation.objects.filter(room=data['room'], reservation_status__in=[1, ])
                       .filter(date_from__gte=data['date_from'], date_to__lte=data['date_to'])) > 0:
            raise serializers.ValidationError('Room is reserved at this term')
        return data


class ReservationWithPasswordSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Reservation
        fields = ['pk', 'room', 'owner', 'training', 'date_from', 'date_to',
                  'reservation_status', 'comment', 'room_password', 'rating']
        read_only_fields = ['owner',]


class ConfirmationSerializer(serializers.ModelSerializer):
    reservation_status = serializers.ChoiceField(choices=(
        (1, 'Confirmed'),
    )
    )

    class Meta:
        model = Reservation
        fields = ['reservation_status']


class FinishReservationSerializer(serializers.ModelSerializer):
    rating = serializers.ChoiceField(choices=Reservation.rating_choice)

    class Meta:
        model = Reservation
        fields = ['rating']


class CancelSerializer(serializers.ModelSerializer):
    reservation_status = serializers.ChoiceField(choices=(
        (0, 'Waiting to be confirmed'),
        (2, 'Cancelled'),
    )
    )

    class Meta:
        model = Reservation
        fields = ['reservation_status']
