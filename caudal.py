from machine import UART,Pin, PWM

class caudalimetro():
    def __init__(self, rx_pin=3, tx_pin=1):
        self.uart = UART(1, baudrate=115200, tx=tx_pin, rx=rx_pin)
        self.uart.init(115200, bits=8, parity=None, stop=1)
        self.freq = 0
        self.ltprh = 0
        self.accumulated = 0
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


class valvula():
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.OUT)

    def set_state(self, bool):
        self.pin.value(bool)

    def get_state(self):
        return self.pin.value()

class bomba():
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin), freq=1000, duty=0)
        self.sp = 0
        self.cv = 0
        self.cv1 = 0
        self.error = 0
        self.error1 = 0
        self.error2 = 0

        self.Kp = 10
        self.Ki = 20
        self.Kd = 0.01
        self.Tm = 0.25
    
    def on_pid(self, set_point, procces_v):
        self.sp = set_point
        self.error = self.sp - procces_v
        
        self.cv = self.cv1 + (self.Kp + self.Kd / self.Tm) * self.error + (-self.Kp + self.Ki * self.Tm - 2 * self.Kd / self.Tm) * self.error1 + (self.Kd / self.Tm) * self.error2
        self.cv1 = self.cv
        self.error2 = self.error1
        self.error1 = self.error

        if self.cv > 360:
            self.cv = 360
        if self.cv < 8:
            self.cv = 8
        
        self.pwm.duty_u16(int(self.cv * (65535 / 360)))
        
    def off(self):
        self.pwm.duty(0)

    def get_cv(self):
        return self.cv