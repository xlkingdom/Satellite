class Task:
    def __init__(self, k, Priority, Start_Time, End_Time, Satellite_Name, Signal_rate, Input, Output):
        self.id = k
        self.priority = Priority
        self.window_start_time = Start_Time
        self.start_time = self.window_start_time + 120
        self.window_end_time = End_Time
        self.end_time = self.window_end_time - 120
        self.satellite = Satellite_Name
        self.signal_rate = Signal_rate
        self.freq_input = Input
        self.freq_output = Output
        self.Xs = False
        self.isExert = True
        # 该任务所能分配的天线
        self.Ta_table = []
        # 该任务所能分配的变频器
        self.Td_1200_table = []
        self.Td_720_table = []
        # 该任务所能分配的解调器
        self.Tm_table = []
        self.Tm_800_table = []
        self.Tm_640_table = []
        # 该任务所能分配的记录器
        self.Tr_table = []
        self.Ta = -1
        self.Td = -1
        self.Tm = -1
        self.Tr = -1
        self.distributionPlan = []
        self.errorMessage = ''

    def Device_Table(self, devices):
        devices.initial()
        self.Ta_table.extend(devices.antenna)
        for i in devices.demodulator:
            rate = self.freq_output
            if rate == 800:
                if devices.demodulator[i].rate == 800:
                    self.Tm_800_table.append(i)
            else:
                if devices.demodulator[i].rate == 640:
                    self.Tm_640_table.append(i)
                if devices.demodulator[i].rate == 800:
                    self.Tm_800_table.append(i)
        for i in devices.frequencyConverter:
            rate = self.freq_input
            if rate == 1200:
                if devices.frequencyConverter[i].rate == 1200:
                    self.Td_1200_table.append(i)
            else:
                if devices.frequencyConverter[i].rate == 1200:
                    self.Td_1200_table.append(i)
                if devices.frequencyConverter[i].rate == 720:
                    self.Td_720_table.append(i)
        if 'HJ' in self.satellite:
            for i in devices.recorder:
                if self.signal_rate <= devices.recorder[i].singleReteMax:
                    if devices.recorder[i].type == 'common':
                        self.Tr_table.append(i)
        else:
            for i in devices.recorder:
                if self.signal_rate <= devices.recorder[i].singleReteMax:
                    self.Tr_table.append(i)
        return devices

    def Update_DeviceInfo(self, task):
        self.Ta = task.Ta
        self.Td = task.Td
        self.Tm = task.Tm
        self.Tr = task.Tr

    def task_clear(self):
        self.Ta = -1
        self.Td = -1
        self.Tm = -1
        self.Tr = -1
        self.Xs = False
        self.isExert = True

