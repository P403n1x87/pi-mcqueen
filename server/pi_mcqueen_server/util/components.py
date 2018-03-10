try:
    import RPi.GPIO as G
except RuntimeError as e:
    G = None
    print("WARNING: ".format(str(e)))
    print("You might only be able to run tests.")


def startup():
    G.setmode(G.BOARD)


def cleanup():
    G.cleanup()


class DCDevice:
    """
    Abstract class for modelling a DC device operated by a single pair of
    input wires.

    This class has no logic, so an actual device should inherit from it and
    declare what to do with the two input wires.
    """

    def __init__(self, in1, in2):
        """
        Maps the input wire to a pair of GPIO pins.

        Args:
            in1 (int): The first input pin.
            in2 (int): The second input pin.
        """

        self.in1 = in1
        self.in2 = in2


class DCMotor(DCDevice):
    """
    A class modelling a DC motor. A threshold value can be passed on
    initialization to define a deadzone in the interval
    [-threshold, threshold].
    """

    def __init__(self, in1, in2, threshold = 0):
        """
        Pass the input pins and a threshold if required.

        Args:
            in1 (int): The first input pin.
            in2 (int): The second input pin.
            threshold (int): The deadzone threshold.
        """
        super().__init__(in1, in2)

        self.threshold = threshold

        for pin in [in1, in2]:
            G.setup(pin, G.OUT)
            G.output(pin, G.LOW)

    def set(self, v):
        """
        Set a value for the DC motor. This is usually in the range [-127, 127],
        with the sign used to determine the polarization of the motor. For
        values that fall within the threshold range, both input wires are set
        to `LOW`.

        Args:
            v (int): The value to set for the DC motor. Only used to control
                the polarization.
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


class Signal:
    """
    Abstract signal class to model a signal sent to a GPIO pin. Any subclass
    must implement the `start` and `stop` methods with the necesary logic to
    start and stop the signal.
    """

    def __init__(self, pin):
        """
        Maps the signal to a GPIO pin.

        Args:
            pin (int): The GPIO to send the signal to.
        """
        self.pin = pin
        G.setup(pin, G.OUT)

    def start(self):
        raise NotImplementedError("bla")

    def stop(self):
        raise NotImplementedError("bla")


class PWMSignal(Signal):
    """
    Class to model a PWM signal. Besides the GPIO pin, one must also specify a
    frequency on initialization.
    """

    def __init__(self, pin, freq):
        """
        The constructor takes the GPIO pin where the signal is to be applied
        and the frequence of the PWM signal. By default, the PWM signal is
        created with a null duty cycle. Use the `set_duty_cycle` method to
        change this value at runtime.

        Args:
            pin (int): The GPIO pin to send the signal to.
            freq (float): The frequency of the PWM signal.
        """
        super().__init__(pin)

        self.freq = freq
        self._pmw = G.PWM(pin, freq)
        self._dc = 0

    def set_duty_cycle(self, dc):
        """
        Sets the duty cycle of the PWM signal.

        Args:
            dc (float): The duty cycle, in the range [0, 100.0]
        """

        self._dc = dc
        self._pmw.ChangeDutyCycle(dc)

    def start(self):
        self._pmw.start(self._dc)

    def stop(self):
        self._pmw.stop()


class HBridge:
    """
    A class that models an H-Bridge. It accepts two `Signal`s and two
    `DCDevice`s.
    """

    def __init__(self, enable1, enable2, device1, device2):
        """
        The constructor holds references to the passed signals and DC devices.
        On start, the signal are started, but the devices have to be operated
        from outside this class, which acts more like a logical container.

        Args:
            enable1 (Signal): The signal to send to ENB1.
            enable2 (Signal): The signal to send to ENB2.
            device1 (DCDevice): The DC device controlled by IN1 and IN2.
            device2 (DCDevice): The DC device controlled by IN3 and IN4.
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
