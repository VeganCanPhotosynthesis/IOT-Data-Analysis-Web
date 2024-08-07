from django.db import models
from datetime import timezone, timedelta
# sensor_data/models.py


class SensorData(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    loc = models.CharField(max_length=100)
    temp = models.FloatField()
    hum = models.FloatField()
    light = models.FloatField()
    snd = models.FloatField()
    node_id = models.CharField(max_length=100)
def timestamp_hk(self):
    # Define the offset for Hong Kong time (UTC+8)
    hk_offset = timezone(timedelta(hours=8))
    return self.timestamp.astimezone(hk_offset)
    
class VenueEvent(models.Model):
    venue = models.CharField(max_length=100)
    event_name = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
