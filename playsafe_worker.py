#!/usr/bin/env python

import daemon
import json
import os
import requests
import subprocess
import sys
import time

class PlaySafeClient(object):

    def __init__(self, url):
        self.api_root = url

    def get_jobs(self):
        return [ Job(self, x) for x in requests.get("%s/jobs/" % self.api_root).json() ]

    def get_queued_jobs(self):
        return [ j for j in self.get_jobs() if j.status == 'Queued' ]

    def save_job(self, job):
        requests.patch("%s/jobs/%s" % (self.api_root, job.id),
                data=job.json(), headers={'content-type': 'application/json'})


class Job(object):
    def __init__(self, client, data):
        self.client = client
        for k,v in data.items():
            setattr(self, k, v)

    def save(self):
        self.client.save_job(self)

    def json(self):
        return json.dumps(dict((k,v) for (k,v) in self.__dict__.iteritems() if k != 'client'))


if __name__ == '__main__':
    api_root = sys.argv[1]
    output_dir = sys.argv[2]
    with daemon.DaemonContext(
            stdout=sys.stdout,
            stderr=sys.stderr,
            stdin=sys.stdin,
            working_directory='.'):

        client = PlaySafeClient(api_root)

        while 1:
            jobs = client.get_queued_jobs()
            if jobs:
                job = jobs[0]
                print "Starting download of %s" % job.url
                job.status = "Running"
                job.save()
                command = job.command.split()
                command.append("%s/%s" % (output_dir, job.filename))
                print "Command: %s " % command
                try:
                    subprocess.check_call(command)
                    job.status = "Completed"
                except subprocess.CalledProcessError:
                    job.status = "Failed"
                job.save()
            time.sleep(10)
