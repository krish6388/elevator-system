from django.db import models
from .STATUS import Status

# Create your models here.

class Elevator(models.Model):

    # STATUS_CHOICES = (
    #     Status.OPEN,
    #     Status.DOWN,
    #     Status.UP,
    #     Status.STOP
    # )

    elevator_id = models.AutoField(primary_key=True)
    is_available = models.CharField(max_length=122, default="Yes")
    cur_floor = models.IntegerField(default=0)
    status = models.CharField(max_length=122, default=Status.STOP)


class Request(models.Model):

    req_id = models.AutoField(primary_key=True)
    dest_floor = models.IntegerField()
    assigned_elevator_id = models.IntegerField(default=-1)
    is_pending = models.CharField(max_length=12, default='Yes')