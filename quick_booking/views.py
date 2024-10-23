from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def my_quick_booking(request):
    return HttpResponse("Hello, Quick Booking!")