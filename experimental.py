import os
import requests
from flask import Flask, render_template, jsonify
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

device_status = defaultdict(lambda: {
    "state_changes": []  # Stores tuples of (state, timestamp)
})

SAUCE_USERNAME = os.getenv("SFDC_SAUCE_USERNAME")
SAUCE_ACCESS_KEY = os.getenv("SFDC_SAUCE_ACCESS_KEY")
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

    # Prepare devices with their current state and duration
    current_time = datetime.now()
    device_summary = []
    for descriptor, status in device_status.items():
        if status["state_changes"]:
            current_state, timestamp = status["state_changes"][-1]
            state_timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            duration = (current_time - state_timestamp).total_seconds() // 60  # Duration in minutes
            device_summary.append({
                "descriptor": descriptor,
                "current_state": current_state,
                "duration": int(duration)  # Convert to int for display
            })

    # Sort devices with offline at the top, then other states, and available at the bottom
    def state_sort_key(device):
        state_priority = {"offline": 0, "rebooting": 1, "cleaning": 2, "maintenance": 3, "in_use": 4, "available": 5}
        return (state_priority.get(device["current_state"].lower(), 4), device["duration"])

    device_summary.sort(key=state_sort_key)

    return render_template('experimental.html', device_summary=device_summary)

@app.route('/status-data')
def status_data():
    """Serve state change data as JSON."""
    return jsonify(device_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080, debug=True)
