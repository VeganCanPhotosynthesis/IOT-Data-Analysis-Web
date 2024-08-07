from django.shortcuts import render
from .models import SensorData, VenueEvent
from .forms import LocationFilterForm, EventFilterForm
from django.db.models import Avg
from django.utils.text import slugify
from django.utils.timezone import localtime, make_aware
from datetime import datetime
import pytz
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import urllib.parse
from io import BytesIO


def homepage(request):
    return render(request, 'sensor_data/homepage.html')

def sensor_data_list(request):
    form = LocationFilterForm(request.GET or None)
    data = SensorData.objects.all().order_by('-timestamp')

    if form.is_valid():
        location = form.cleaned_data.get('location')
        if location:
            data = data.filter(loc=location)

    # Convert timestamps to Hong Kong time
    for item in data:
        item.timestamp_hk = localtime(item.timestamp, pytz.timezone('Asia/Hong_Kong'))

    return render(request, 'sensor_data/sensor_data_list.html', {'data': data, 'form': form})

def dashboard(request):
    data = SensorData.objects.all().order_by('-timestamp')
    locations = SensorData.objects.values_list('loc', flat=True).distinct()

    # Get selected location from request
    selected_location_slug = request.GET.get('location')
    selected_location = None

    location_data = {}
    for location in locations:
        location_slug = slugify(location)
        if location_slug == selected_location_slug:
            selected_location = location
        location_data[location_slug] = {
            'location': location,
            'data': list(data.filter(loc=location).values('timestamp', 'temp', 'hum', 'light', 'snd', 'loc'))
        }

    if selected_location:
        filtered_data = data.filter(loc=selected_location)
    else:
        selected_location_slug = slugify(locations[0]) if locations else None
        filtered_data = data.filter(loc=locations[0]) if locations else data

    avg_temp = filtered_data.aggregate(Avg('temp'))['temp__avg'] or 0
    avg_hum = filtered_data.aggregate(Avg('hum'))['hum__avg'] or 0
    avg_light = filtered_data.aggregate(Avg('light'))['light__avg'] or 0
    avg_snd = filtered_data.aggregate(Avg('snd'))['snd__avg'] or 0

    # Format averages to 2 decimal places
    avg_temp = f"{avg_temp:.2f}"
    avg_hum = f"{avg_hum:.2f}"
    avg_light = f"{avg_light:.2f}"
    avg_snd = f"{avg_snd:.2f}"

    # Prepare data for the chart
    timestamps = [entry['timestamp'] for entry in filtered_data.values('timestamp')]
    temps = [entry['temp'] for entry in filtered_data.values('temp')]
    hums = [entry['hum'] for entry in filtered_data.values('hum')]
    lights = [entry['light'] for entry in filtered_data.values('light')]

    # Create a line chart using Matplotlib
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, temps, label='Temperature', color='red')
    plt.plot(timestamps, hums, label='Humidity', color='blue')
    plt.plot(timestamps, lights, label='Light Intensity', color='#007bff')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.title('Sensor Data Chart')
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save the chart to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Encode the image to base64
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    context = {
        'locations': locations,
        'selected_location_slug': selected_location_slug,
        'avg_temp': avg_temp,
        'avg_hum': avg_hum,
        'avg_light': avg_light,
        'avg_snd': avg_snd,
        'location_data': location_data,
        'selected_location': selected_location,
        'image_base64': image_base64,
    }

    return render(request, 'sensor_data/dashboard.html', context)

def event_data(request):
    form = EventFilterForm(request.GET or None)
    events = VenueEvent.objects.none()
    sensor_data = SensorData.objects.none()
    averages = {'avg_temp': 0, 'avg_hum': 0, 'avg_light': 0, 'avg_snd': 0}

    if form.is_valid():
        venue = form.cleaned_data.get('venue')
        start_time = form.cleaned_data.get('start_time')
        end_time = form.cleaned_data.get('end_time')

        if venue and start_time and end_time:
            events = VenueEvent.objects.filter(venue=venue, start_time__gte=start_time, end_time__lte=end_time)
            sensor_data = SensorData.objects.filter(loc=venue, timestamp__gte=start_time, timestamp__lte=end_time)
            
            # Calculate averages
            averages = sensor_data.aggregate(
                avg_temp=Avg('temp'),
                avg_hum=Avg('hum'),
                avg_light=Avg('light'),
                avg_snd=Avg('snd')
            )

    context = {
        'form': form,
        'events': events,
        'sensor_data': sensor_data,
        'averages': averages
    }

    return render(request, 'sensor_data/event_data.html', context)

def data_analysis(request):
    # Read the sensor data
    file_path = r"C:\Users\ic2140\Desktop/sensor_data_sensordata.csv"
    df = pd.read_csv(file_path)

    # Calculate summary statistics for numeric columns only
    numeric_columns = ['temp', 'hum', 'light', 'snd']
    summary_stats = df[numeric_columns].describe().to_dict()

    # Convert timestamps to a readable format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Time series plot
    plt.figure(figsize=(14, 7))
    for column in numeric_columns:
        plt.plot(df['timestamp'], df[column], label=column)
    plt.legend()
    plt.title('Time Series Plot')
    plt.xlabel('Timestamp')
    plt.ylabel('Sensor Readings')
    
    # Format the x-axis labels
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))  # Show a maximum of 10 ticks
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    time_series_plot = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    
    # Correlation matrix plot
    plt.figure(figsize=(10, 8))
    corr_matrix = df[numeric_columns].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')
    plt.title('Correlation Matrix')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    corr_matrix_plot = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    
    # Location-based analysis
    location_stats = df.groupby('loc')[numeric_columns].mean().to_dict(orient='index')

    context = {
        'summary_stats': summary_stats,
        'time_series_plot': f"data:image/png;base64,{time_series_plot}",
        'corr_matrix_plot': f"data:image/png;base64,{corr_matrix_plot}",
        'location_stats': location_stats,
    }
    return render(request, 'sensor_data/data_analysis.html', context)
