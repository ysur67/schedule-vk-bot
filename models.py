from django.db import models
from django import utils
import uuid
from datetime import date

class TimeTable(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for timetable")

    name = models.CharField(
        max_length=100,
        help_text="Name of timetable",
        unique=False
    )

    date = models.DateField(
        default = utils.timezone.now
    )

    def __str__(self):
        return f"{self.id} {self.name}"

class Person(models.Model):
    id = models.PositiveIntegerField(
        primary_key = True,
        help_text = "User ID from VK"
    )

    time_table = models.ForeignKey('TimeTable',
    on_delete=models.SET_NULL,
    null=True,
    unique=False,
    )
    

    send_notifications = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id} {self.send_notifications}"
