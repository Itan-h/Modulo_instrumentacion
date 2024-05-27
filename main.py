from machine import SPI,Pin
import st7789
import time
import vga1_bold_16x32 as font
import caudal
from rotary_irq import RotaryIRQ

valve = caudal.valvula(4)
sensor = caudal.caudalimetro()
bomba = caudal.bomba(15)

btn = Pin(18, Pin.IN, Pin.PULL_UP)#boton del encoder
encoder = RotaryIRQ(pin_num_clk=21,
              pin_num_dt=19,
              min_val=0,
              max_val=25,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_WRAP)

tft = st7789.ST7789(
    SPI(2, baudrate=30000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(23)),
    240,
    320,
    reset=Pin(5, Pin.OUT),
    cs=Pin(16, Pin.OUT),
    dc=Pin(17, Pin.OUT),
    rotation=0
   # buffer_size=240*200*2
    )
tft.init()

while True:
    time.sleep(0.25)