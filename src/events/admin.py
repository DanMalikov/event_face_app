from django.contrib import admin

from .models import Event, Registration, Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "event_time", "status", "venue")
    list_filter = ("status", "event_time", "venue")
    search_fields = ("name",)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "event", "full_name", "email", "created_at")
    list_filter = ("event", "created_at")
    search_fields = ("full_name", "email")
