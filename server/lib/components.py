import RPi.GPIO as G

G.setmode(G.BOARD)


def cleanup():
    G.cleanup()

class DCDevice:

    def __init__(self, in1, in2, threshold=0):
        """
        Pass the input pins and the threshold.
        """

        self.in1 = in1
        self.in2 = in2
        self.threshold = threshold

        G.setup(self.in1, G.OUT)
        G.setup(self.in2, G.OUT)
        G.output(self.in1, G.LOW)
        G.output(self.in2, G.LOW)

    def set(self, v):
        """
        Set how the device behaves.
        If value passed is negative, turn in one direction, else the other.
        Has to be out of threshold.
        """

        if v > self.threshold:
            G.output(self.in1, G.HIGH)
            G.output(self.in2, G.LOW)
        elif v < - self.threshold:
            G.output(self.in1, G.LOW)
            G.output(self.in2, G.HIGH)
        else:
            G.output(self.in1, G.LOW)
            G.output(self.in2, G.LOW)

        return



class DCMotor(DCDevice):

    pass


class Signal:

    def __init__(self, pin):

        self.pin = pin
        G.setup(pin, G.OUT)

    def start(self):

        raise NotImplementedError("bla")

    def stop(self):

        raise NotImplementedError("bla")


class PMWSignal(Signal):

    def __init__(self, pin, freq):
        super().__init__(pin)
        self.freq = freq
        self._pmw = G.PWM(pin, freq)
        self._dc = 0

    def set_duty_cycle(self, dc):
        self._dc = dc
        self._pmw.ChangeDutyCycle(dc)

    def start(self):

        # start the PMW signal
        self._pmw.start(self._dc)

    def stop(self):
        self._pmw.stop()


class HBridge:

    def __init__(self, enable1, enable2, device1, device2):
        """
        Pass ...
        """

        self.enable1 = enable1
        self.enable2 = enable2
        self.device1 = device1
        self.device2 = device2

    def start(self):
        self.enable1.start()
        self.enable2.start()

    def stop(self):
        self.enable1.stop()
        self.enable2.stop()
