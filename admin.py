from django.contrib import admin
from .models import TimeTable, Person

@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date')

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'time_table', 'send_notifications')
