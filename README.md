# RDC Private Device Monitor

## Running in a virtualenv without using Docker

Open Terminal.app and create the following environment variables and replace the values with the customers Sauce creds:

- SAUCE_USERNAME=your_sauce_username
- SAUCE_ACCESS_KEY=your_sauce_access_key

Create the virtual environment:
```python3 -m venv venv```

Activate the virtual environment:
```source venv/bin/activate```

Install the requirements:
```pip install -r requirements.txt```

Run the app:
```python rdc-private-device-monitor.py```

## Using Docker Compose

Open Terminal.app and create the following environment variables and replace the values with the customers Sauce creds and your own Docker username:

- SAUCE_USERNAME=your_sauce_username
- SAUCE_ACCESS_KEY=your_sauce_access_key
- DOCKER_USERNAME=your_docker_username

Then cd into the rdc-private-device-monitor directory and build the Docker image:

```docker buildx build -t $DOCKER_USERNAME/rdc-private-device-monitor:0.0.1 . ```

Update the image reference in the compose.yaml

```image: "$DOCKER_USERNAME/rdc-private-device-monitor:0.0.1"```
