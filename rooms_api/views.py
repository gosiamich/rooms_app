import datetime

from django.http import Http404
from django.shortcuts import get_list_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rooms_api.models import Reservation, Room
from rooms_api.permissions import IsOwnerOrReadOnly, RoomManagerPermission
from rooms_api.serializers import ReservationSerializer, RoomSerializer, ConfirmationSerializer, \
    FinishReservationSerializer, CancelSerializer, ReservationWithPasswordSerializer


class RoomViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = (IsOwnerOrReadOnly, IsAuthenticated)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'confirm':
            return ConfirmationSerializer
        elif self.action == 'finish':
            return FinishReservationSerializer
        elif self.action == 'cancel':
            return CancelSerializer
        # elif self.action == 'create':
        #     return ReservationCreateSerializer
        return ReservationSerializer

    def destroy(self, request, pk=None, room_pk=None):
        response = {'message': 'Delete function is not offered in this path.'}
        return Response(response, status=status.HTTP_403_FORBIDDEN)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, pk=None, room_pk=None):
        item = get_object_or_404(self.queryset, pk=pk, room__pk=room_pk)
        # breakpoint()
        if item.owner == self.request.user and item.reservation_status == 1:
            serializer = ReservationWithPasswordSerializer(item)
            return Response(serializer.data)
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    def list(self, request, room_pk=None):
        try:
            items = get_list_or_404(self.queryset, room__pk=room_pk)
        except (TypeError, ValueError):
            raise Http404
        else:
            serializer = self.get_serializer(items, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[RoomManagerPermission])
    def confirm(self, request, pk=None, room_pk=None):
        reservation = self.get_object()
        serializer = self.get_serializer(reservation, data=request.data)
        if serializer.is_valid():
            reservation.reservation_status = serializer.validated_data['reservation_status']
            reservation.save()
            return Response({'message': 'Status is changed'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrReadOnly])
    def finish(self, request, pk=None, room_pk=None):
        reservation = self.get_object()
        serializer = self.get_serializer(reservation, data=request.data)
        if serializer.is_valid():
            if reservation.reservation_status == 1 and reservation.date_to < datetime.date.today():
                if not reservation.rating:
                    reservation.rating = serializer.validated_data['rating']
                    serializer.save()
                    return Response({'message': 'The training has been assessed'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'You can add evaluation only once.'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'You can add evaluation after training.'},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None, room_pk=None):
        reservation = self.get_object()
        serializer = self.get_serializer(reservation, data=request.data)
        if serializer.is_valid():
            if serializer.validated_data['reservation_status'] == 2:
                reservation.reservation_status = serializer.validated_data['reservation_status']
                reservation.save()
                return Response({'message': 'Reservation is canceled'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
