"""
This module represents a runner-worker thread for a device with
8 workers.
"""
from threading import Thread

class RunnerThread(Thread):
    """
    Runner thread is used by device to run a script on.
    it acquires the regional lock and then does its job.
    """
    def __init__(self, device, script, neighbours):
        Thread.__init__(self)
        self.device = device
        self.script_to_run = script
        self.neighbours = neighbours

    def run(self):
        (script, location) = self.script_to_run
        script_data = []
        # lock region as to be the only device in location to run
        with self.device.location_locks[location]:
            for device in self.neighbours:
                data = device.get_data(location)
                if data is not None:
                    script_data.append(data)
            data = self.device.get_data(location)
            if data is not None:
                script_data.append(data)
            if script_data != []:
                result = script.run(script_data)
                for device in self.neighbours:
                    device.set_data(location, result)
                    self.device.set_data(location, result)
