from machine import Pin, time
import sensores as s
from extras.rotary_irq import RotaryIRQ
#caudal
valve = s.Valvula(4)
sensor_caudal = s.Caudalimetro(9)
bomba = s.Bomba(15)
#temperatura
max1 = s.MAX6675(sck=Pin(1), so=Pin(1), cs=Pin(1))  # Sensor 1
max2 = s.MAX6675(sck=Pin(1), so=Pin(1), cs=Pin(1))  # Sensor 2
resistencia = s.resistencia(3)
#nivel
ultrasonic = s.Ultrasonico(12, 13)
hzt1_tanque1 = s.Sensor_switch(6)
hzt2_tanque1 = s.Sensor_switch(7)
hzt1_tanque2 = s.Sensor_switch(8)
hzt2_tanque2 = s.Sensor_switch(9)

sp1_temp = 50
sp2_temp = 25

sp_nivel = 8

btn = Pin(18, Pin.IN, Pin.PULL_UP)#boton del encoder
encoder = RotaryIRQ(pin_num_clk=21,
                pin_num_dt=19,
                min_val=0,
                max_val=25,
                reverse=True,
                range_mode=RotaryIRQ.RANGE_WRAP)

if((max1.error() == 1) or (max2.error() == 1)): #error en el sensor 
    pass
time.sleep(0.25)

while((hzt1_tanque1.state() == 1) and (hzt1_tanque2.state() == 1)): #!Ambos tanques llenos
    pass

while True:
    time.sleep(0.25)
    if((max2.read() >= sp2_temp) and (hzt2_tanque2() != 1)):
        while(ultrasonic.liters() <= 9.5):
            #bomba PENDIENTE
            sensor_caudal.get_lthr()#Obtener litros totales
        while(max1.read()>= sp1_temp):
            resistencia.set_state(1)
        while(hzt2_tanque1 != 1):
            valve.set_state(1)

else:
        pass #Error en pantalla