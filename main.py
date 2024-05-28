from machine import Pin, time
import sensores as s
from extras.rotary_irq import RotaryIRQ
#caudal
valve = s.Valvula(4)
sensor = s.Caudalimetro(9)
bomba = s.Bomba(15)
#temperatura
max1 = s.MAX6675(sck=Pin(1), so=Pin(1), cs=Pin(1))  # Sensor 1
max2 = s.MAX6675(sck=Pin(1), so=Pin(1), cs=Pin(1))  # Sensor 2
resistencia1 = s.resistencia(3)
#nivel
ultrasonic = s.Ultrasonico(12, 13)
hzt1_tanque1 = s.Sensor_switch(6)
hzt2_tanque1 = s.Sensor_switch(7)
hzt1_tanque2 = s.Sensor_switch(8)
hzt2_tanque2 = s.Sensor_switch(9)

btn = Pin(18, Pin.IN, Pin.PULL_UP)#boton del encoder
encoder = RotaryIRQ(pin_num_clk=21,
              pin_num_dt=19,
              min_val=0,
              max_val=25,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_WRAP)

while True:

    time.sleep(0.25)