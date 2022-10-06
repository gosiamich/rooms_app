from django.contrib import admin

# Register your models here.
from .models import Room, Reservation

admin.site.register(Room)
admin.site.register(Reservation)