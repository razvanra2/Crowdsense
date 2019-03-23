"""
This module represents a device.

Computer Systems Architecture Course
Assignment 1
March 2019
"""

from threading import Event, Thread, Lock
from reusable_barrier import ReusableBarrier

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
        self.devices = None
        self.timestampBarrier = None
        self.setupComplete = Event()
        self.dataLock = Lock()

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
        
        if self.device_id == 0:
            self.timestampBarrier = ReusableBarrier(len(devices))
            for otherDevice in self.devices:
                if otherDevice.device_id != 0:
                    otherDevice.timestampBarrier = self.timestampBarrier
        self.setupComplete.set()
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
        with self.dataLock:
            return self.sensor_data[location] if location in self.sensor_data else None

    def set_data(self, location, data):
        """
        Sets the pollution value stored by this device for the given location.

        @type location: Integer
        @param location: a location for which to set the data

        @type data: Float
        @param data: the pollution value
        """
        with self.dataLock:
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
        self.device.setupComplete.wait()
        self.device.setupComplete.clear()
        while True:
            # get the current neighbourhood
            neighbours = self.device.supervisor.get_neighbours()
            if neighbours is None:
                break

            self.device.script_received.wait()
            self.device.script_received.clear()

            currIterThreads = [None] * 8

            while len(self.device.scripts) > 0:
                threadsToAppend = min(len(self.device.scripts), 8)
                for i in range(threadsToAppend):
                    currIterThreads.append(RunnerThread(self.device.scripts.pop(), 
                    neighbours))
                for i in range(threadsToAppend):
                    if currIterThreads[i] is not None:
                        currIterThreads[i].start()
                for i in range(threadsToAppend):
                    if currIterThreads[i] is not None:
                        currIterThreads[i].join()

                # wait for all devices to finish same timestamp execution
            self.device.script_received.clear()
            self.device.timestampBarrier.wait()