FROM python:3.8-alpine

ADD docker /opt/events-notifier
WORKDIR /opt/events-notifier
RUN mkdir /log-events

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "./docker_events.py"]
