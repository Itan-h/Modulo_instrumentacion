from machine import Pin
import machine, time

class Ultrasonico:

    def __init__(self, echo, trigger, echo_timeout):
        self.echo = Pin(echo, Pin.IN)
        self.trigger = Pin(trigger, Pin.OUT)
        self.echo_timeout = echo_timeout

    def measure(self):
        self.trigger.off()
        time.sleep_us(5)
        self.trigger.on()
        time.sleep_us(10)
        self.trigger.off()

        duration = machine.time_pulse_us(self.echo, 1, self.echo_timeout)
        distance = 343.2*duration/20000

        return distance

class Sensor_switch:

    def __init__(self, sensor):
        self.sensor = Pin(sensor, Pin.IN, Pin.PULL_UP)

    def state(self):
        input = not(self.sensor.value())
        return input