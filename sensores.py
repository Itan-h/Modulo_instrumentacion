from machine import Pin, UART, PWM
import machine, time

class Ultrasonico:
    def __init__(self, echo, trigger, top=43, echo_timeout = 30000):
        self.echo = Pin(echo, Pin.IN)
        self.trigger = Pin(trigger, Pin.OUT)
        self.echo_timeout = echo_timeout
        self.top = top
        
    def get_distance(self):
        self.trigger.off()
        time.sleep_us(5)
        self.trigger.on()
        time.sleep_us(10)
        self.trigger.off()

        duration = machine.time_pulse_us(self.echo, 1, self.echo_timeout)
        self.distance = 343.2*duration/20000 #cm

        return self.distance
    
    def liters(self, lenght=14.8, width=15, l=0):
        self.volumen = (((lenght*width)*(self.top-self.get_distance()))*0.001)+l #litros para calibrar
        return self.volumen #14.8, 15, 43
    
    def percent(self):
        self.percent1 = (self.volumen*100)/(self.top*15*15*0.001)
        return self.percent1

class Sensor_switch:

    def __init__(self, sensor):
        self.sensor = Pin(sensor, Pin.IN, Pin.PULL_UP)

    def state(self):
        input = not(self.sensor.value())
        return input

class Caudalimetro:
    def __init__(self, rx_pin=3, tx_pin=1):
        self.uart = UART(1, baudrate=115200, tx=tx_pin, rx=rx_pin)
        self.uart.init(115200, bits=8, parity=None, stop=1)
        self.freq = 0
        self.ltprh = 0
        self.get_freq()

    def get_freq(self):
        self.msg=self.uart.readline()
        if self.msg==None:
            pass
        else:
            try:
                self.freq=int(self.msg)
            except:
                pass
        return self.freq

    def get_lthr(self):
        self.ltprh=(self.get_freq()*60)/7.5
        return self.ltprh

class Valvula:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT)

    def set_state(self, bool):
        self.pin.value(bool)

    def get_state(self):
        return self.pin.value()

class Bomba:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin), freq=1000, duty=0)
        self.sp = 0
        self.cv = 0
        self.cv1 = 0
        self.error = 0
        self.error1 = 0
        self.error2 = 0
        #Constantes proporcional, integral y derivativa
        self.Kp = 1
        self.Ki = 3
        self.Kd = 0.05
        self.Tm = 1
    
    def on_pid(self, set_point, procces_v):
        self.sp = set_point
        self.error = self.sp - procces_v
        #Ecuación de diferencias(transformada Z de la ecuacion del control PID)
        self.cv = self.cv1 + (self.Kp + self.Kd / self.Tm) * self.error + (-self.Kp + self.Ki * self.Tm - 2 * self.Kd / self.Tm) * self.error1 + (self.Kd / self.Tm) * self.error2
        self.cv1 = self.cv
        self.error2 = self.error1
        self.error1 = self.error

        if self.cv > 10000:
            self.cv = 10000
        if self.cv < 8:
            self.cv = 8
        
        self.pwm.duty_u16(int(self.cv * (65535 / 10000)))
        
    def off(self):
        self.pwm.duty(0)
        self.cv = 0
        self.cv1 = 0
        self.error = 0
        self.error1 = 0
        self.error2 = 0

    def get_cv(self):
        return self.cv

class MAX6675:
    MEASUREMENT_PERIOD_MS = 220

    def __init__(self, sck, cs, so):
        """
        Creates new object for controlling MAX6675
        :param sck: SCK (clock) pin, must be configured as Pin.OUT
        :param cs: CS (select) pin, must be configured as Pin.OUT
        :param so: SO (data) pin, must be configured as Pin.IN
        """
        # Thermocouple
        self._sck = sck
        self._sck.value(0)

        self._cs = cs
        self._cs.value(1)

        self._so = so
        self._so.value(0)

        self._last_measurement_start = 0
        self._last_read_temp = 0
        self._error = 0

    def _cycle_sck(self):
        self._sck.value(1)
        time.sleep_us(1)
        self._sck.value(0)
        time.sleep_us(1)

    def refresh(self):
        """
        Start a new measurement.
        """
        self._cs.value(0)
        time.sleep_us(10)
        self._cs.value(1)
        self._last_measurement_start = time.ticks_ms()

    def ready(self):
        """
        Signals if measurement is finished.
        :return: True if measurement is ready for reading.
        """
        return time.ticks_ms() - self._last_measurement_start > MAX6675.MEASUREMENT_PERIOD_MS

    def error(self):
        """
        Returns error bit of last reading. If this bit is set (=1), there's problem with the
        thermocouple - it can be damaged or loosely connected
        :return: Error bit value
        """
        return self._error

    def read(self):
        """
        Reads last measurement and starts a new one. If new measurement is not ready yet, returns last value.
        Note: The last measurement can be quite old (e.g. since last call to `read`).
        To refresh measurement, call `refresh` and wait for `ready` to become True before reading.
        :return: Measured temperature
        """
        # Check if new reading is available
        if self.ready():
            # Bring CS pin low to start protocol for reading result of
            # the conversion process. Forcing the pin down outputs
            # first (dummy) sign bit 15.
            self._cs.value(0)
            time.sleep_us(10)

            # Read temperature bits 14-3 from MAX6675.
            value = 0
            for i in range(12):
                # SCK should resemble clock signal and new SO value
                # is presented at falling edge
                self._cycle_sck()
                value += self._so.value() << (11 - i)

            # Read the TC Input pin to check if the input is open
            self._cycle_sck()
            self._error = self._so.value()

            # Read the last two bits to complete protocol
            for i in range(2):
                self._cycle_sck()

            # Finish protocol and start new measurement
            self._cs.value(1)
            self._last_measurement_start = time.ticks_ms()

            self._last_read_temp = value * 0.25

        return self._last_read_temp

class resistencia:
    def __init__(self, pin):
        self.pin=Pin(pin, Pin.OUT)
        
    def set_state(self, bool):
        self.pin.value(bool)

    def get_state(self):
        return self.pin.value()
        