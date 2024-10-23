from django.contrib import admin
from .models import Table, Booking

# Register your models here.

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'table', 'booking_date', 'booking_time', 'number_of_guests')
    list_filter = ('booking_date', 'table')
    search_fields = ('customer_name', 'customer_email')