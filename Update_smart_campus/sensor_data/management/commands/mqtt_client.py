# sensor_data/management/commands/mqtt_client.py
import json
import paho.mqtt.client as mqtt
from django.core.management.base import BaseCommand
from sensor_data.models import SensorData

class Command(BaseCommand):
    help = 'Runs the MQTT client to collect sensor data'

    def handle(self, *args, **options):
        mqtt_broker = "broker.hivemq.com"
        mqtt_port = 1883
        mqtt_topic_A = "iot/sensor-A"
        team_number = "A04"

        def on_connect(client, userdata, flags, rc):
            print(f"Connected with result code {rc}")
            client.subscribe(mqtt_topic_A)

        def on_message(client, userdata, msg):
            try:
                data = json.loads(msg.payload.decode())
                print(f"Received message: {data}")  # Debug print
                SensorData.objects.create(
                    node_id=data['node_id'],
                    loc=data['loc'],
                    temp=float(data.get('temp', 0)),
                    hum=float(data.get('hum', 0)),
                    light=float(data.get('light', 0)),
                    snd=float(data.get('snd', 0))
                )
                print(f"Saved data: {data}")  # Debug print
            except Exception as e:
                print(f"Error processing message: {e}")

        client = mqtt.Client(client_id=team_number, protocol=mqtt.MQTTv311)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(mqtt_broker, mqtt_port)
        client.loop_forever()
