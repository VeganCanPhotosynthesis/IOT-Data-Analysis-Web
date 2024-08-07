import pandas as pd
from django.core.management.base import BaseCommand
from sensor_data.models import VenueEvent
from django.utils.timezone import make_aware
import pytz

class Command(BaseCommand):
    help = 'Import venue events from an Excel file'

    def handle(self, *args, **kwargs):
        file_path = r"C:\Users\ic2140\Desktop\Venue-Event GRPA.xlsx"
        df = pd.read_excel(file_path)
        
        # Rename the columns to meaningful names
        df.columns = ['venue', 'date', 'start_time', 'end_time', 'event_name', 'instructor']
        
        # Drop the first row if it is a header-like row
        df = df.iloc[1:]
        
        # Convert the date column to string before concatenation
        df['date'] = df['date'].astype(str)
        
        # Convert time columns to string
        df['start_time'] = df['start_time'].astype(str)
        df['end_time'] = df['end_time'].astype(str)
        
        # Combine date and time columns into datetime
        df['start_time'] = pd.to_datetime(df['date'] + ' ' + df['start_time'])
        df['end_time'] = pd.to_datetime(df['date'] + ' ' + df['end_time'])
        
        VenueEvent.objects.all().delete()  # Clear existing data

        for _, row in df.iterrows():
            event = VenueEvent(
                event_name=row['event_name'],
                venue=row['venue'],
                start_time=make_aware(row['start_time'], timezone=pytz.timezone('Asia/Hong_Kong')),
                end_time=make_aware(row['end_time'], timezone=pytz.timezone('Asia/Hong_Kong'))
            )
            event.save()

        self.stdout.write(self.style.SUCCESS('Successfully imported venue events'))
