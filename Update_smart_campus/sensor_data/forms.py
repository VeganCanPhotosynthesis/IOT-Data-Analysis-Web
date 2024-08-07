from django import forms
from .models import SensorData, VenueEvent

class LocationFilterForm(forms.Form):
    location = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super(LocationFilterForm, self).__init__(*args, **kwargs)
        locations = SensorData.objects.values_list('loc', flat=True).distinct()
        self.fields['location'].choices = [(loc, loc) for loc in locations]



class EventFilterForm(forms.Form):
    venue = forms.ChoiceField(choices=[], required=True)
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=True)
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), required=True)

    def __init__(self, *args, **kwargs):
        super(EventFilterForm, self).__init__(*args, **kwargs)
        venues = VenueEvent.objects.values_list('venue', flat=True).distinct()
        self.fields['venue'].choices = [(venue, venue) for venue in venues]
