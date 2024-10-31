from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django import forms

# Create your models here.

# Table

class Table(models.Model):
    """Represents a restaurant table."""
    number = models.PositiveIntegerField(unique=True)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"Table {self.number} (Capacity: {self.capacity})"

# Booking

class Booking(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')

    """Represents a customer reservation."""
    # Basic customer details
    customer_name = models.CharField(max_length=50)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15, blank=True, null=True)

    # Reservation details
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    number_of_guests = models.PositiveIntegerField()

    # Optional special requests or comments
    special_request = models.TextField(blank=True, null=True)

    # Auto timestamp when the booking was made
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensures no double-booking for the same table at the same time
        unique_together = ('table', 'booking_date', 'booking_time')
        ordering = ['booking_date', 'booking_time']

    def __str__(self):
        return f"Booking for {self.customer_name} on {self.booking_date} at {self.booking_time}"

    def clean(self):
        if self.number_of_guests > self.table.capacity:
            raise ValidationError(f"The table capacity is {self.table.capacity}, please imput a valid guest number.")

# Form for modify booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'number_of_guests', 'special_request', 'table']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
        }