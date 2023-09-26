class Antenna:
    def __init__(self, antenna_id):
        self.usingPeriod = []
        self.id = antenna_id
        self.frequencyBand = ['S', 'X']

    def clear_usingPeriod(self):
        self.usingPeriod.clear()


class FrequencyConverter:
    def __init__(self, FrequencyConverter_id, FrequencyConverter_rate):
        self.usingPeriod = []
        self.id = FrequencyConverter_id
        self.rate = FrequencyConverter_rate

    def clear_usingPeriod(self):
        self.usingPeriod.clear()


class Demodulator:
    def __init__(self, Demodulator_id, Demodulator_rate):
        self.usingPeriod = []
        self.id = Demodulator_id
        self.rate = Demodulator_rate
        self.minRate = 10

    def clear_usingPeriod(self):
        self.usingPeriod.clear()


class Recorder:
    def __init__(self, Recorder_id, Recorder_type):
        self.usingPeriod = []
        self.id = Recorder_id
        self.type = Recorder_type
        self.singleReteMax = 600
        self.rateSumMax = 1200

    def clear_usingPeriod(self):
        self.usingPeriod.clear()


class Device:
    def __init__(self, Antenna_n, FrequencyConverter_n, Demodulator_n, Recorder_n):
        self.antenna_number = Antenna_n
        self.frequencyConverter_number = FrequencyConverter_n
        self.demodulator_number = Demodulator_n
        self.recorder_number = Recorder_n
        self.antenna_active_number = 0
        # 允许跨矩阵链接次数
        self.Nsp = 1
        self.Nsp_now = 0
        self.antenna = {}
        self.frequencyConverter = {}
        self.demodulator = {}
        self.recorder = {}

    def initial(self):
        for i in range(self.antenna_number):
            antenna = Antenna(i)
            self.antenna[i] = antenna
        for i in range(self.frequencyConverter_number):
            if i >= 2:
                f_id = '1200_' + str(i)
                frequencyConverter = FrequencyConverter(f_id, 1200)
            else:
                f_id = '720_' + str(i)
                frequencyConverter = FrequencyConverter(f_id, 720)
            self.frequencyConverter[i] = frequencyConverter
        for i in range(self.demodulator_number):
            if i < 2:
                d_id = '800_' + str(i)
                demodulator = Demodulator(d_id, 800)
            else:
                d_id = '640_' + str(i)
                demodulator = Demodulator(d_id, 640)
            self.demodulator[i] = demodulator
        for i in range(self.recorder_number):
            if i < 2:
                r_id = 'common_' + str(i)
                recorder_common = Recorder(r_id, 'common')
                self.recorder[i] = recorder_common
            else:
                r_id = 'specialized_' + str(i)
                recorder_specialized = Recorder(r_id, 'specialized')
                self.recorder[i] = recorder_specialized

    def get_device_by_index(self, index, device_type):
        if device_type == 'Ta':
            return self.antenna[index]
        elif device_type == 'Td':
            return self.frequencyConverter[index]
        elif device_type == 'Tm':
            return self.demodulator[index]
        elif device_type == 'Tr':
            return self.recorder[index]

    def clear_device(self):
        for device_type in [self.antenna, self.frequencyConverter, self.demodulator, self.recorder]:
            for _, device in device_type.items():
                device.usingPeriod.clear()

    def copy(self):
        new_device = Device(self.antenna_number, self.frequencyConverter_number, self.demodulator, self.recorder)
        new_device.antenna = {k: v for k, v in self.antenna.items()}
        new_device.frequencyConverter = {k: v for k, v in self.frequencyConverter.items()}
        new_device.demodulator = {k: v for k, v in self.demodulator.items()}
        new_device.recorder = {k: v for k, v in self.recorder.items()}
        return new_device
