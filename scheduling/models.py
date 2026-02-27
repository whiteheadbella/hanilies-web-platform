from django.db import models
from django.contrib.auth.models import User
from orders.models import Booking

class Schedule(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    task = models.CharField(max_length=200)
    status = models.CharField(max_length=50)
