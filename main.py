from machine import Pin, time
import sensores as s
from extras.rotary_irq import RotaryIRQ
import network
from extras import BlynkLib
import urequests
import time
import machine
#-----------------------------------------------------------------------------------------------
#caudal
valve = s.Valvula(4)
sensor = s.Caudalimetro(9)
bomba = s.Bomba(15)
#temperatura
max1 = s.MAX6675(sck=Pin(1), so=Pin(1), cs=Pin(1))  # Sensor 1
max2 = s.MAX6675(sck=Pin(1), so=Pin(1), cs=Pin(1))  # Sensor 2
resistencia1 = s.resistencia(3)
#nivel
ultrasonic_1 = s.Ultrasonico(12, 13)
ultrasonic_2 = s.Ultrasonico(12, 13)
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
#-----------------------------------------------------------------------------------------------

# WiFi credentials
ssid = 'POCO X4 GT'
password = '234567890'
# ThingSpeak API key y URL
thingspeak_api_key = 'FD2XVQKL2G0RA56X'
thingspeak_url = "https://api.thingspeak.com/update?api_key=" + thingspeak_api_key + "&field1=0"
# Blynk credentials
auth_blynk = "610DmxAtbBJc9c2GVez6WD7DjIuzm1dE"
# Initialize Blynk
blynk = BlynkLib.Blynk(auth_blynk)
# Connect to WiFi
red = network.WLAN(network.STA_IF)
red.active(True)
red.connect(ssid, password)

while not red.isconnected():
    pass

print('Conexión correcta')
print(red.ifconfig())

ultima_peticion = 0
intervalo_peticiones = 10

def reconectar():
    print('Fallo de conexión. Reconectando...')
    time.sleep(10)
    machine.reset()

def blink():
    global tempe1
    global tempe2
    global ult1
    global ult2
    global caudal

    tempe1=max1.read()
    tempe2=max2.read()
    ult1=ultrasonic_1.liters()
    ult2=ultrasonic_1.liters()
    caudal=sensor.get_lthr()

    try:
        if (time.time() - ultima_peticion) > intervalo_peticiones:
            tempe1=round(tempe1, 1)
            tempe2=round(tempe2, 1)
            ult1=round(ult1, 1)
            ult2=round(ult2, 1)
            caudal=round(caudal, 1)
                      
            
            # Actualizar ThingSpeak
            thingspeak_url_update = thingspeak_url + "&field1=" + str(tempe1) + "&field2=" + str(tempe2) + "&field3=" + str(ult1) + "&field4=" + str(ult2) + "&field5=" + str(caudal)
            respuesta_thingspeak = urequests.get(thingspeak_url_update)
            print("Respuesta ThingSpeak:", respuesta_thingspeak.status_code)
            respuesta_thingspeak.close()
            
            # Actualizar Blynk
            blynk.virtual_write(0, tempe1)  # Virtual pin 0 para temperatura1
            blynk.virtual_write(1, tempe2)   # Virtual pin 1 para temperatura2
            blynk.virtual_write(2, ult1)  # Virtual pin 2 para ultrasonico1
            blynk.virtual_write(3, ult2)  # Virtual pin 3 para ultrasonico2
            blynk.virtual_write(4, caudal)  # Virtual pin 4 para caaudal
            ultima_peticion = time.time()
            blynk.run()

    except OSError as e:
        reconectar()
#-----------------------------------------------------------------------------------------------
while True:
    time.sleep(0.25)
    blink()