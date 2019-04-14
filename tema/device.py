"""
This module represents a device.

Computer Systems Architecture Course
Assignment 1
March 2019
"""

from threading import Event, Thread, Lock
from reusable_barrier import ReusableBarrier
from runner_thread import RunnerThread
class Device(object):
    """
    Class that represents a device.
    """

    def __init__(self, device_id, sensor_data, supervisor):
        """
        Constructor.

        @type device_id: Integer
        @param device_id: the unique id of this node; between 0 and N-1

        @type sensor_data: List of (Integer, Float)
        @param sensor_data: a list containing (location, data) as measured by this device

        @type supervisor: Supervisor
        @param supervisor: the testing infrastructure's control and validation component
        """
        self.devices = None # list of all the devices
        self.timestamp_barrier = None # barrier used to sync all devices in 1 timestamp
        self.setup_complete = Event() # event used to sync all setups
        self.location_locks = dict() # regional locks

        self.device_id = device_id
        self.sensor_data = sensor_data
        self.supervisor = supervisor
        self.script_received = Event()
        self.scripts = []
        self.thread = DeviceThread(self)
        self.thread.start()

    def __str__(self):
        """
        Pretty prints this device.

        @rtype: String
        @return: a string containing the id of this device
        """
        return "Device %d" % self.device_id

    def setup_devices(self, devices):
        """
        Setup the devices before simulation begins.

        @type devices: List of Device
        @param devices: list containing all devices
        """
        self.devices = devices
        if self.device_id == 0: # use device 0 as master
            # and init all other devices from it
            self.timestamp_barrier = ReusableBarrier(len(devices))
            for device in self.devices:
                for _ in device.sensor_data:
                    self.location_locks[_] = Lock()
            for device in devices:
                device.timestamp_barrier = self.timestamp_barrier
                device.location_locks = self.location_locks
                device.setup_complete.set()
    def assign_script(self, script, location):
        """
        Provide a script for the device to execute.

        @type script: Script
        @param script: the script to execute from now on at each timepoint; None if the
            current timepoint has ended

        @type location: Integer
        @param location: the location for which the script is interested in
        """
        if script is None:
            self.script_received.set()
        else:
            self.scripts.append((script, location))

    def get_data(self, location):
        """
        Returns the pollution value this device has for the given location.

        @type location: Integer
        @param location: a location for which obtain the data

        @rtype: Float
        @return: the pollution value
        """
        return self.sensor_data[location] if location in self.sensor_data else None

    def set_data(self, location, data):
        """
        Sets the pollution value stored by this device for the given location.

        @type location: Integer
        @param location: a location for which to set the data

        @type data: Float
        @param data: the pollution value
        """
        if location in self.sensor_data:
            self.sensor_data[location] = data

    def shutdown(self):
        """
        Instructs the device to shutdown (terminate all threads). This method
        is invoked by the tester. This method must block until all the threads
        started by this device terminate.
        """
        self.thread.join()

class DeviceThread(Thread):
    """
    Class that implements the device's worker thread.
    """

    def __init__(self, device):
        """
        Constructor.

        @type device: Device
        @param device: the device which owns this thread
        """
        Thread.__init__(self, name="Device Thread %d" % device.device_id)
        self.device = device

    def run(self):
        # wait so that all devices complete the setup
        self.device.setup_complete.wait()
        while True:
            # get the current neighbourhood
            neighbours = self.device.supervisor.get_neighbours()
            if neighbours is None:
                break

            self.device.script_received.wait()
            self.device.script_received.clear()

            script_cnt = len(self.device.scripts)
            start = 0
            stop = min(start + 8, start + script_cnt)
            # init all the threads at once
            threads = []
            for i in range(0, script_cnt):
                threads.append(RunnerThread(self.device, self.device.scripts[i], neighbours))
            # then run them all in heaps of 8
            while script_cnt > 0:
                for thread in threads[start:stop]:
                    thread.start()
                for thread in threads[start:stop]:
                    thread.join()

                start = start + min(8, script_cnt)
                stop = min(start + 8, start + script_cnt)
                if script_cnt > 8:
                    script_cnt -= 8
                else:
                    break
            # wait untill all devices completed one timestamp iteration
            self.device.timestamp_barrier.wait()
