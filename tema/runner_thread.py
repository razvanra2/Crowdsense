from threading import Thread

class RunnerThread(Thread):
    def __init__(self, device, script, neighbours):
        Thread.__init__(self)
        self.device = device
        self.scriptToRun = script
        self.neighbours = neighbours

    def run(self):

        (script, location) = self.scriptToRun
        script_data = []
        with self.device.locationLocks[location]:
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