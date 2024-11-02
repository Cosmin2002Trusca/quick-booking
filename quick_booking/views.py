from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.views import generic
from .models import Booking, Table, BookingForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.utils import timezone

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

            # Check if the selected date and time are in the past
            now = timezone.now()
            
            # Combine booking_date and booking_time into a single datetime object
            booking_datetime = timezone.make_aware(
                timezone.datetime.combine(booking.booking_date, booking.booking_time)
            )

            if booking_datetime < now:
                form.add_error(None, "You cannot book a date or time in the past.")
            
            booking.save()  # Now save it
            messages.success(request, "Your booking was created successfully!")
            return redirect('my_bookings')  # Redirect
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

def custom_login_view(request):
    # Define the form inline within the view
    class CustomLoginForm(forms.Form):
        username = forms.CharField(
            max_length=150,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
        )
        password = forms.CharField(
            widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
        )

    # Handle POST request for login
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('create_booking')  # Redirect to a target page
            else:
                form.add_error(None, "Invalid username or password.")  # Display custom error on form
    else:
        form = CustomLoginForm()  # Initialize an empty form for GET request

    return render(request, 'quick_booking/login.html', {'form': form})

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
            messages.success(request, "Your booking was deleted successfully!")
            return redirect('my_bookings')

        else:
            booking_id = request.POST.get('booking_id')
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            form = BookingForm(request.POST, instance=booking)
            if form.is_valid():
                    form.save()
                    messages.success(request, "Your booking was updated successfully!")
                    return redirect('my_bookings')

    # Create list of tuples with (booking, form) for displaying and editing
    booking_forms = [(booking, BookingForm(instance=booking)) for booking in bookings]

    context = {
        'booking_forms': booking_forms
    }

    return render(request, 'quick_booking/my_bookings.html', context)