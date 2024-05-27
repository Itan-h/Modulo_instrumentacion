from machine import Pin, SPI, UART, PWM
import machine, time, st7789

# FUENTES DISPONIBLES
# import vga1_8x8 as font
# import vga2_8x8 as font
#import vga1_8x16 as font           
# import vga2_8x16 as font
# import vga1_16x16 as font
# import vga2_16x16 as font
# import vga1_bold_16x16 as font
# import vga2_bold_16x16 as font
import vga1_16x32 as font1
# import vga2_16x32 as font 
import vga1_bold_16x32 as font2
# import vga2_bold_16x32 as font

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

class Display:
    def __init__(self, sck, mosi, miso, reset, dc, cs, backlight, id = 0, baudrate = 30000000, polarity = 0, phase = 0, bits = 8, firstbit = 0):
        self.tft = st7789.ST7789(SPI(id, baudrate = baudrate, polarity = polarity, phase = phase, bits = bits, firstbit = firstbit, sck = Pin(sck), 
                    mosi = Pin(mosi), miso = Pin(miso)), 240, 320, reset = Pin(reset, Pin.OUT), dc = Pin(dc, Pin.OUT), cs = Pin(cs, Pin.OUT), 
                    backlight = Pin(backlight, Pin.OUT), rotation = 0)
        
        self.tft.init()
    
    def data_discrete(self, x, y, r, g, b, label, value , xl, yl, xv, yv, width = 210, height = 50):
        self.tft.fill_rect(x, y, width, height, st7789.color565(r, g, b))
        self.tft.text(font1, label, xl, yl, st7789.WHITE)
        self.tft.text(font2, value, xv, yv, st7789.WHITE)


    def data_logic(self, x, y, label, xl, yl, state, width = 50, height = 50):
        if state == 1:
            self.tft.fill_rect(x, y, width, height, st7789.GREEN)
        else:
            self.tft.fill_rect(x, y, width, height, st7789.RED)
        
        self.tft.text(font2, label, xl, yl, st7789.WHITE)

class Caudalimetro:
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

        self.Kp = 1
        self.Ki = 3
        self.Kd = 0.05
        self.Tm = 1
    
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
