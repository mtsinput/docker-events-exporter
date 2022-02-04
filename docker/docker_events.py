#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from os import environ
import docker
from prometheus_client import start_http_server, Counter

APP_NAME = "Docker events prometheus exporter"
EVENTS = Counter('docker_events',
                 'Docker events',
                 ['event', 'pod', 'env', 'exitcode', 'signal'])

log_date = '{}'.format(datetime.now().strftime('%Y-%m-%d'))


def print_timed(msg):
    to_print = '{} [{}]: {}'.format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'docker_events',
        msg)
    print(to_print)

def logstash_addr():
    if "LOGSTASH_ADDR" in environ:
        return environ["LOGSTASH_ADDR"]
    else:
        return ""

def logstash_port():
    if "LOGSTASH_PORT" in environ:
        return environ["LOGSTASH_PORT"]
    else:
        return ""

def log_to_disk():
    if "LOG_TO_DISK" in environ:
        return environ["LOG_TO_DISK"]
    else:
        return ""

def watch_events():
    client = docker.DockerClient(version='auto',
                                 base_url='unix://var/run/docker.sock')
    for event in client.events(decode=True):
        attributes = event['Actor']['Attributes']
        if log_to_disk().upper() == "TRUE" or log_to_disk().upper() == "YES":
            global log_date, log_file
            if log_date == '{}'.format(datetime.now().strftime('%Y-%m-%d')):
                log_file.write('{} [{}]: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'docker_events',event))
                log_file.write('\n')
            else:
                log_file.close
                log_date = '{}'.format(datetime.now().strftime('%Y-%m-%d'))
                log_file = open("/log-events/docker_event_"+log_date+".log", "a")
                log_file.write('{} [{}]: {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'docker_events',event))
                log_file.write('\n')

        #print_timed(event)
        if event['Type'] == 'network':
            continue
        exit_code = ''
        if 'exitCode' in attributes:
            exit_code =  attributes['exitCode']
        signal = ''
        if 'signal' in attributes:
            signal =  attributes['signal']
        if 'com.docker.swarm.task.id' in attributes:
        #    if attributes['io.kubernetes.container.name'] == 'POD':
        #        continue
        #    if event['status'].startswith(('exec_create', 'exec_detach')):
        #        continue
            msg = '{} on {} ({}) {} ({})'.format(
                event['status'].strip(),
                attributes['com.docker.swarm.task.name'],
                exit_code,
                signal,
                attributes['com.docker.stack.namespace'])
            print_timed(msg)
            pod = attributes['com.docker.swarm.task.name']
        #    if event['status'] == 'oom':
        #        pod = attributes['io.kubernetes.pod.name']
            if 'status' in attributes:
                pod = attributes['com.docker.swarm.task.name']
            EVENTS.labels(event=event['status'].strip(),
                          pod=pod,
                          exitcode=exit_code,
                          signal=signal,
                          env=attributes['com.docker.stack.namespace']).inc()
        if 'image' and 'name' in attributes:
            msg = '{} on {} ({}) {}'.format(
                event['status'].strip(),
                attributes['name'],
                exit_code,
                signal)
            print_timed(msg)
            pod = attributes['name']
        #    if event['status'] == 'oom':
        #        pod = attributes['io.kubernetes.pod.name']
            EVENTS.labels(event=event['status'].strip(),
                          pod=pod,
                          exitcode=exit_code,
                          signal=signal,
                          env='').inc()

if __name__ == '__main__':
    print_timed('Start prometheus client on port 9990')
    start_http_server(9990, addr='0.0.0.0')
    if log_to_disk().upper() == "TRUE" or log_to_disk().upper() == "YES":
        log_file = open("/log-events/docker_event_"+log_date+".log", "a")
    try:
        print_timed('Watch docker events')
        watch_events()
    except docker.errors.APIError:
        pass
