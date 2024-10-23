from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.views import generic
from .models import Booking, Table, BookingForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

# Create your views here.

# Booking

@login_required
def create_booking(request):
    class InlineBookingForm(forms.ModelForm):
        class Meta:
            model = Booking
            fields = [
                'customer_name', 'customer_email', 'customer_phone',
                'table', 'booking_date', 'booking_time', 
                'number_of_guests', 'special_request'
            ]

    if request.method == 'POST':
        form = InlineBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)  # Don't save yet
            booking.user = request.user  # Associate the booking with the logged-in user
            booking.save()  # Now save it
            return redirect('my_bookings')  # Redirect to home or success page
    else:
        form = InlineBookingForm()

    return render(request, 'quick_booking/reservation_form.html', {'form': form})

# Authentification

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Create the user
            login(request, user)  # Log in the user immediately
            return redirect('create_booking')  # Redirect to booking page
    else:
        form = UserCreationForm()

    return render(request, 'quick_booking/register.html', {'form': form})

# Landing

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('create_booking')  # If logged in, redirect to booking page
    return render(request, 'quick_booking/landing_page.html')  # Otherwise, show landing page

# modify bookings

@login_required
def my_bookings(request):
    """View to display and edit or delete user's bookings."""
    # Fetch all bookings for the currently logged-in user based on their User object
    bookings = Booking.objects.filter(user=request.user)

    # If POST, handle form submissions for editing or deleting
    if request.method == 'POST':
        if 'delete_booking' in request.POST:
            booking_id = request.POST.get('booking_id')
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            booking.delete()
            return redirect('my_bookings')

        else:
            booking_id = request.POST.get('booking_id')
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            form = BookingForm(request.POST, instance=booking)
            if form.is_valid():
                form.save()
                return redirect('my_bookings')

    # Create list of tuples with (booking, form) for displaying and editing
    booking_forms = [(booking, BookingForm(instance=booking)) for booking in bookings]

    context = {
        'booking_forms': booking_forms
    }

    return render(request, 'quick_booking/my_bookings.html', context)