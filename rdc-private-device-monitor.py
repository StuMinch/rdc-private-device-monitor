import os
import requests
from flask import Flask, render_template, jsonify
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

device_status = defaultdict(lambda: {
    "state_changes": []  # Stores tuples of (state, timestamp)
})

SAUCE_USERNAME = os.getenv("SAUCE_USERNAME")
SAUCE_ACCESS_KEY = os.getenv("SAUCE_ACCESS_KEY")
SAUCE_API_URL = "https://api.us-west-1.saucelabs.com/v1/rdc/devices/status"
AUTH = (SAUCE_USERNAME, SAUCE_ACCESS_KEY)

def fetch_device_status():
    response = requests.get(SAUCE_API_URL, auth=AUTH)
    if response.status_code == 200:
        # Filter devices to only include those where isPrivateDevice is True
        devices = response.json().get("devices", [])
        return [device for device in devices if device.get("isPrivateDevice")]
    return []

def update_device_status(devices):
    for device in devices:
        descriptor = device["descriptor"]
        state = device["state"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Record state change
        if not device_status[descriptor]["state_changes"] or device_status[descriptor]["state_changes"][-1][0] != state:
            device_status[descriptor]["state_changes"].append((state, timestamp))

@app.route('/')
def index():
    devices = fetch_device_status()
    update_device_status(devices)
    return render_template('index-plotly.html')

@app.route('/status-data')
def status_data():
    """Serve state change data as JSON."""
    return jsonify(device_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True)
