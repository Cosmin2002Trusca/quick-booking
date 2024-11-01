from . import views
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register, create_booking, landing_page, custom_login_view

urlpatterns = [
    path('', landing_page, name='landing_page'),  # Landing page
    path('register/', register, name='register'),  # Registration view
    path('login/', custom_login_view, name='login'),  # Login view
    path('logout/', LogoutView.as_view(next_page='landing_page'), name='logout'),  # Logout view
    path('booking/', create_booking, name='create_booking'), #Booking
    path('bookings/', views.my_bookings, name='my_bookings'),  # My Bookings view
]