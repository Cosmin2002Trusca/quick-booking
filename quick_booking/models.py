from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django import forms
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

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

    # RegexValidator for phone numbers: allows only digits
    phone_validator = RegexValidator(regex=r'^\d+$', message="Phone number must be numeric.")
    customer_phone = models.CharField(max_length=15, blank=True, null=True, validators=[phone_validator], help_text="Enter a valid phone number (digits only).")

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

        super().clean()  # Call parent's clean method

        if self.number_of_guests > self.table.capacity:
            raise ValidationError(f"The table capacity is {self.table.capacity}, please imput a valid guest number.")

        # Ensure booking time is between 9:00 and 22:00
        min_time = timezone.datetime.strptime("09:00", "%H:%M").time()
        max_time = timezone.datetime.strptime("22:00", "%H:%M").time()
        if not (min_time <= self.booking_time <= max_time):
            raise ValidationError("Booking time must be between 09:00 and 22:00.")

        # Check if the booking date and time are in the past
        now = timezone.now()
        booking_datetime = timezone.datetime.combine(self.booking_date, self.booking_time)

        # Make sure booking_datetime is timezone-aware
        if timezone.is_naive(booking_datetime):
            booking_datetime = timezone.make_aware(booking_datetime)

        if booking_datetime < now:
            raise ValidationError("You cannot book a date or time in the past.")

# Form for modify booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'number_of_guests', 'special_request', 'table']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
        }